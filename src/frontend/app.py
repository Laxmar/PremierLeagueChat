import asyncio

from langchain.globals import set_verbose, set_debug
from langchain_core.messages import HumanMessage
import streamlit as st

from src.backend.agent import PremierLeagueAgent
from src.backend.premier_league_api.sportdb import SportDBApi
from src.backend.premier_league_api.exceptions import APIError
from src.utils.logger import setup_logger
from src.configuration import Configuration

_AGENT_SESSION_KEY = "agent"

# TODO extract hardcoded strings to constants
class ChatUI:
    """Simple chat UI written in streamlit"""
    
    WELCOME_MESSAGE: str = ('Hey there! I am a Premier League assistant. I can answer only a questions regarding Premier League teams for season 2025/2026. \n \
            I know only senior squad members. I work best with English, and will answer in English.')
            
    EXAMPLE_MESSAGES: str = 'You can start with "What is the squad of the Manchester United?" or What are defenders of the Manchester United?"'

    def __init__(self, agent: PremierLeagueAgent):
        """Initialize the UI and save agent to session state if not already present
            and prepare initial messages
        """
        
        st.set_page_config(page_title="Premier League Chat", page_icon="⚽")
        if _AGENT_SESSION_KEY not in st.session_state:
            
            st.session_state[_AGENT_SESSION_KEY] = agent
            st.session_state.messages = [
                {"role": "assistant", "content": self.WELCOME_MESSAGE},
                {"role": "assistant", "content": self.EXAMPLE_MESSAGES}
            ]
        
    async def run(self):
        st.title("Premier League Chat")

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
                    response = ""
                    try:
                        response, _ = await st.session_state.agent.send_message(message)
                    except APIError:
                        response = "Sorry, I cannot connect to the API. Please try again later."
                    finally:
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
    
def main():
    """streamlit run src/frontend/streamlit_app.py"""
    ui = None
    
    is_setup_completed = _AGENT_SESSION_KEY in st.session_state
    if not is_setup_completed:
        config = Configuration.load()
        setup_logger(config.logging_level)
        
        if config.langraph_debug:
            set_verbose(True)
            set_debug(True)
            
        squad_api = SportDBApi(config.THE_SPORT_API_KEY.get_secret_value())
        agent = PremierLeagueAgent(config.model_name, squad_api)
        ui = ChatUI(agent)
        # agnet is saved to session state in PrototypeUI constructor
    else:
        ui = ChatUI(st.session_state[_AGENT_SESSION_KEY])
    
    asyncio.run(ui.run())

if __name__ == "__main__":
    main()
    