from src.backend.premier_league_api.sportdb import SportDBApi
from src.prototype import PremierLeagueAgent
from src.configuration import Configuration
from langchain_core.messages import HumanMessage

def main():
    config = Configuration.load()
    squad_api = SportDBApi(config.THE_SPORT_API_KEY.get_secret_value())
    agent = PremierLeagueAgent(config.model_name, squad_api)
    agent.save_graph_as_image("docs/agent_graph.png")
    
    message = HumanMessage(content="What is the squad of the Manchester United?") 
    # message = HumanMessage(content="What is the squad of the Bank?") 
    # message = HumanMessage(content="What is the weather in Warsaw?") 
    response = agent.ask(message)
    print(response)