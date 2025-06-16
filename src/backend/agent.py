from dataclasses import dataclass
from random import randint
from typing import cast
from langchain_core.runnables.config import RunnableConfig
from langgraph.types import Command
from loguru import logger

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from src.backend.prompts.formulate_answer import build_formulate_answer_prompt
from src.backend.prompts.clarify_team_name import CLARIFY_TEAM_NAME_PROMPT
from src.backend.prompts.interpret_user_clarification import INTERPRET_USER_CLARIFICATION_PROMPT
from src.backend.premier_league_api.base import IPremierLeagueApi
from src.backend.squad import Squad


# TODO find a better way to handle Nones or add checking everywhere
# TODO consider using UpdateCommands instead of returning AgentState
@dataclass(kw_only=True)
class AgentState:
    user_query: HumanMessage # TODO use plain string to avoid multiple casting
    team_name: str | None = None
    squad: Squad | None = None
    answer: str | None = None
    clarification_request: str | None = None
    clarification_response: str | None = None
    team_found: bool = False
    valid: bool = False
    success: bool = False


# TODO Replace hardcoded Nodes and Edges names with constants/enums
# TODO consider creating Nodes class and moving prompts to this classes
class PremierLeagueAgent:
    """A class which implements a logic of responding to user queries about Premier League teams squads."""
    
    def __init__(self, model_name: str, squad_api: IPremierLeagueApi):
        """ Initialize the agent with a model name and a squad API 
        To better understand the flow of the agent check the /docs folder. Especialy the graph.png file.
        
        Args:
            model_name: name of the OpenAI model to use
            squad_api: squad API to use
        """
        self._model = ChatOpenAI(model=model_name)
        self._squad_api = squad_api
        self._config: RunnableConfig = {"configurable": {"thread_id": str(randint(0, 1000))}} 
        graph = StateGraph(AgentState)
        memory = MemorySaver()
        
        # Nodes:
        graph.add_node("Validate", self._validate_query)
        graph.add_node("ExtractTeam", self._extract_team)
        graph.add_node("Clarify", self._ask_for_clarification)
        graph.add_node("UserClarify", self._handle_user_clarification)
        graph.add_node("GetSquad", self._search_squad)
        graph.add_node("FormulateResponse", self._formulate_response)
        graph.set_entry_point("Validate")
        
        # Edges:
        # TODO refactor to make it cleaner
        graph.add_conditional_edges("Validate", 
            lambda state: "valid" if state.valid else "invalid",
            {
                "valid": "ExtractTeam",
                "invalid": END
            })
        
        graph.add_conditional_edges("ExtractTeam", 
            lambda state: "team_found" if state.team_found else "not_found",
            {
                "team_found": "GetSquad",
                "not_found": "Clarify"
            })
        
        graph.add_edge("Clarify", "UserClarify") 
        
        graph.add_conditional_edges("UserClarify", 
            lambda state: "team_found" if state.team_found else "unknown",
            {
                "team_found": "GetSquad",
                "unknown": END
            }
        )
        
        graph.add_edge("GetSquad", "FormulateResponse")
        graph.set_finish_point("FormulateResponse")
        
        self._graph = graph.compile(checkpointer=memory, interrupt_before=['UserClarify'])
       
    async def send_message(self, user_message: HumanMessage) -> str:
        """
        Send a message to the agent and return the agent response.
        The response can be either final answer or clarification request.
        
        Args:
            user_message: user message
        
        Returns:
            str: final answer or clarification request   
        """
        logger.debug(f'user_message: {user_message}')
        
        # Handle the clarification Flow - TODO consider extracting to a separate method
        graph_states = self._graph.get_state(self._config).values
        clarification_needed = not graph_states.get('answer', None) and graph_states.get("clarification_request", None)
        logger.debug(f'clarification_needed: {clarification_needed}')
        
        if clarification_needed:
            self._graph.update_state(self._config, {"clarification_response": user_message.content})
            result = await self._graph.ainvoke(Command(resume=user_message.content), config=self._config)
            answer = AgentState(**result).answer
            logger.debug(f'answer: {answer}')
            return cast(str, answer)
        
        # Handle the normal Flow
        result = await self._invoke(user_message)
        logger.debug(f'result: {result}')
        if result.clarification_request:
            return result.clarification_request
        
        logger.debug(f'answer: {result.answer}')
        return cast(str, result.answer)

    def save_graph_as_image(self, name: str = "graph.png"):
        """Save graph as image """
        bytes = self._graph.get_graph(xray=True).draw_mermaid_png()
        with open(name, "wb") as f:
            f.write(bytes)
    
    async def _invoke(self, user_query: HumanMessage) -> AgentState:
        """Invoke the agent with a user query

        Args:
            user_query: user query which should be about Premier League team squad
        
        Returns:
            AgentState: agent state
        """
        logger.debug(f'user_query: {user_query}')
        result = await self._graph.ainvoke(AgentState(user_query=user_query), config=self._config)
        return AgentState(**result)
      
    def _validate_query(self, state: AgentState) -> AgentState:
        """It validates if the user query is about a Premier League team squad.
        
        Args:
            state: agent state
        
        Returns:
            AgentState: agent state with valid flag
        """
        query = state.user_query.content
        system_prompt = """
        Determine if user is asking about a Premier League team squad.
        Answer only YES or NO.
        """
        response = self._model.invoke(f"{system_prompt}\nUser Query: {query}")
        logger.debug(f'response: {response.content}')
        
        if "yes" in cast(str, response.content).lower():
            state.valid = True
        else:
            state.valid = False
            state.answer = "I cannot help you with that. Please ask a question regarding Premier League teams."
        return state

    async def _extract_team(self, state: AgentState) -> AgentState:
        """It tries to extract the team name from the user query.
        If the team is not found, it returns None.
        
        Args:
            state: agent state
        
        Returns:
            AgentState: agent state with extracted team name and team found flag
        """
        query = state.user_query.content
        
        system_prompt = """
        Extract the team names from user query if any.
        Just output the team name, no extra words.
        """
        response = self._model.invoke(f"{system_prompt}\nUser Query: {query}")
        
        team_name = cast(str, response.content).strip().lower()
        logger.debug(f'team_name: {team_name}')

        is_found = team_name in self._squad_api.get_teams()
        logger.debug(f'is_found: {is_found}')
        
        state.team_name = team_name
        state.team_found = is_found
        return state

    def _ask_for_clarification(self, state: AgentState) -> AgentState:
        """If the team is not found, it asks for clarification.
        It tries guess the most likely team name from the user query.
        
        Args:
            state: agent state
        
        Returns:
            AgentState: agent state with clarification request
        """
        clubs = self._squad_api.get_teams()
        prompt = CLARIFY_TEAM_NAME_PROMPT.format(clubs=clubs, user_prompt=state.user_query.content)
        response = self._model.invoke(prompt)
        state.clarification_request = cast(str, response.content)
        return state
    
    def _handle_user_clarification(self, state: AgentState) -> AgentState:
        """It handles the user clarification.
        Based on the clarification request and the clarification response it tries to guess the most likely team name.
        If the team is not found, it save the answer and finish the flow.
        
        Args:
            state: agent state
        
        Returns:
            AgentState: agent state with clarification request
        """
        prompt = INTERPRET_USER_CLARIFICATION_PROMPT.format(
            clarification_request=state.clarification_request,
            clarification_response=state.clarification_response
        )
        response = self._model.invoke(prompt)
        state.team_name = cast(str, response.content).strip().lower()
        state.team_found = state.team_name in self._squad_api.get_teams()
        
        if not state.team_found:
            state.answer = "Sorry, I could not find the team you were asking about."
            state.success = False
            return state
        
        return state
    
    async def _search_squad(self, state: AgentState) -> AgentState:
        if not state.team_name:
            raise ValueError('Something went wrong. The team name should be set in this node.')
        
        squad = await self._squad_api.get_team_squad(state.team_name)
        logger.debug(f'squad: {squad}')
        state.squad = squad
        return state
    
    # TODO stream the response
    def _formulate_response(self, state: AgentState) -> AgentState:
        if not state.squad:
            raise ValueError('Something went wrong. The squad should be set in this node.')
        
        prompt = build_formulate_answer_prompt(state.squad, cast(str, state.user_query.content))
        response = self._model.invoke(prompt)
        
        state.answer = cast(str, response.content)
        state.success = True
        return state