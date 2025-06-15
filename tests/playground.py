import asyncio


from pydeck.bindings.json_tools import json
from src.backend.formulate_answer import build_formulate_answer_prompt
from src.backend.premier_league_api.sportdb import SportDBApi
from src.backend.squad import Squad
from src.prototype import PremierLeagueAgent
from src.configuration import Configuration
from langchain_core.messages import HumanMessage



async def main():
    config = Configuration.load()
    squad_api = SportDBApi(config.THE_SPORT_API_KEY.get_secret_value())
    agent = PremierLeagueAgent(config.model_name, squad_api)
    agent.save_graph_as_image("docs/agent_graph.png")
    
    message = HumanMessage(content="What is the squad of the Manchester United?") 
    # message = HumanMessage(content="What are goalkeepers of the Manchester United?") 
    # message = HumanMessage(content="What are defenders of the Manchester United?") 
    # message = HumanMessage(content="What is the squad of the Bank?") 
    # message = HumanMessage(content="What is the weather in Warsaw?") 
    # response = await agent.ask(message)
    # save response as json
    
    # load response from json
    with open("response.json", "r") as f:
        response = json.load(f)
    squad = Squad(name="Manchester United", players=response)
        
    prompt = build_formulate_answer_prompt(squad, message.content)
    
    response = agent._model.invoke(prompt)
    
    print(response.content)
    
if __name__ == "__main__":
    asyncio.run(main())