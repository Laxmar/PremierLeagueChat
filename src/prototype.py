import asyncio
from dataclasses import dataclass
from loguru import logger

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain.globals import set_verbose, set_debug
import streamlit as st

from src.backend.premier_league_api.base import IPremierLeagueApi
from src.backend.premier_league_api.sportdb import SportDBApi
from src.backend.premier_league_api.exceptions import APIError
from src.backend.squad import Squad
from src.utils.logger import setup_logger
from src.configuration import Configuration

# TODO find a better way to handle Nones or add checking everywhere
@dataclass(kw_only=True)
class AgentState:
    user_query: HumanMessage
    team_name: str | None = None
    squad: Squad | None = None
    answer: str | None = None
    team_found: bool = False
    valid: bool = False
    success: bool = False

# TODO create a UpdateCommands instead of returning AgentState
# TODO Replace hardcoded Nodes and Edges names with constants/enums
class PremierLeagueAgent:
    
    def __init__(self, model_name: str, squad_api: IPremierLeagueApi):
        self._model = ChatOpenAI(model=model_name)
        self._squad_api = squad_api
        graph = StateGraph(AgentState)
        
        # Nodes:
        graph.add_node("Validate", self._validate_query)
        graph.add_node("ExtractTeam", self._extract_team)
        graph.add_node("Clarify", self._ask_for_clarification)
        graph.add_node("GetSquad", self._search_squad)
        graph.add_node("FormulateResponse", self._formulate_response)
        graph.set_entry_point("Validate")
        
        # Edges:
        graph.add_conditional_edges("Validate", 
            lambda state: "valid" if state.valid else "invalid",
            {"valid": "ExtractTeam", "invalid": END})
        graph.add_conditional_edges("ExtractTeam", 
            lambda state: "team_found" if state.team_found else "not_found",
            {"team_found": "GetSquad", "not_found": "Clarify"})
        graph.add_edge("Clarify", END) # TODO ask user for clarification
        graph.add_edge("GetSquad", "FormulateResponse")
        graph.set_finish_point("FormulateResponse")
        
        self._graph = graph.compile()
        
    async def ask(self, user_query: HumanMessage) -> str:
        """Ask the agent a question and return the final answer"""
        logger.debug(f'ask() user_query: {user_query}')
        result = await self._invoke(user_query)
        logger.debug(f'ask() result: {result}')
        return  result.answer
        
    async def _invoke(self, user_query: HumanMessage) -> AgentState:
        """Invoke the agent with a user query"""
        result = await self._graph.ainvoke(AgentState(user_query=user_query))
        return AgentState(**result)

    def save_graph_as_image(self, name: str = "graph.png"):
        """Save graph as image """
        bytes = self._graph.get_graph(xray=True).draw_mermaid_png()
        with open(name, "wb") as f:
            f.write(bytes)

    async def _extract_team(self, state: AgentState) -> AgentState:
        query = state.user_query.content
        system_prompt = """
        Extract the team names from user query if any.
        Just output the team name, no extra words.
        """
        response = self._model.invoke(f"{system_prompt}\nUser Query: {query}")
        team_name = response.content.strip().lower()
        logger.debug(f'extract_team() team_name: {team_name}')

        is_found = team_name in self._squad_api.get_teams()
        logger.debug(f'extract_team() is_found: {is_found}')
        
        state.team_name = team_name
        state.team_found = is_found
        return state
        
    def _validate_query(self, state: AgentState) -> AgentState:
        query = state.user_query.content
        system_prompt = """
        Determine if user is asking about a Premier League team squad.
        Answer only YES or NO.
        """
        response = self._model.invoke(f"{system_prompt}\nUser Query: {query}")
        logger.debug(f'validate_query() response: {response.content}')
        
        if "yes" in response.content.lower():
            state.valid = True
        else:
            state.valid = False
            state.answer = "I cannot help you with that. Please ask a question regarding Premier League teams."
        return state

    def _ask_for_clarification(self, state: AgentState) -> AgentState:
        # TODO try find suggest team name based on extract team name - aka fixing typos
        state.answer = "Team not found. Sorry can you try again?"
        return state
    
    async def _search_squad(self, state: AgentState) -> AgentState:
        squad = await self._squad_api.get_team_squad(state.team_name)
        state.squad = squad
        return state
    
    def _formulate_response(self, state: AgentState) -> AgentState:
        squad = state.squad
        answer = f"The squad of {state.team_name.upper()} is {squad.players}"
        # TODO use LLM to formulate response based suited for the user query
        state.answer = answer
        state.success = True
        return state


class PrototypeUI:
    WELCOME_MESSAGE: str = ('Hey there! I am a Premier League assistant. I can answer only a questions regarding Premier League teams for season 2025/2026. \n \
            I know only senior squad members. I work best with English, and will answer in English.')
            
    EXAMPLE_MESSAGES: str = 'You can start with "What is the squad of the Manchester United?" or "What is the squad of the Liverpool?"'

    def __init__(self, agent: PremierLeagueAgent):
        st.set_page_config(page_title="Premier League Chat", page_icon="⚽")
        if 'agent' not in st.session_state:
            
            st.session_state['agent'] = agent
            st.session_state.messages = [
                {"role": "assistant", "content": self.WELCOME_MESSAGE},
                {"role": "assistant", "content": self.EXAMPLE_MESSAGES}
            ]
        
    async def run(self):
        st.title("Premier League Chat Prototype")

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("What is the squad of the Manchester United?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message = HumanMessage(content=prompt)
                with st.spinner("Assitant is searching for the squad..."):
                    try:
                        response = await st.session_state.agent.ask(message)
                    except APIError:
                        response = 'Sorry, I cannot connect to the API. Please try again later.'
                    finally:
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
    
def main():
    """streamlit run src/prototype.py"""
    config = Configuration.load()
    setup_logger(config.logging_level)
    if config.langraph_debug:
        set_verbose(True)
        set_debug(True)
    
    squad_api = SportDBApi(config.THE_SPORT_API_KEY.get_secret_value())
    agent = PremierLeagueAgent(config.model_name, squad_api)
    ui = PrototypeUI(agent)
    asyncio.run(ui.run())

if __name__ == "__main__":
    main()
    