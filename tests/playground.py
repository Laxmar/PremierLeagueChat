from src.prototype import PremierLeagueAgent
from src.configuration import Configuration
from langchain_core.messages import HumanMessage

def main():
    config = Configuration.load()
    agent = PremierLeagueAgent(config.model_name)
    agent.save_graph_as_image("docs/agent_graph.png")
    
    message = HumanMessage(content="What is the squad of the Manchester United?") 
    # message = HumanMessage(content="What is the squad of the Bank?") 
    # message = HumanMessage(content="What is the weather in Warsaw?") 
    response = agent.ask(message)
    print(response)