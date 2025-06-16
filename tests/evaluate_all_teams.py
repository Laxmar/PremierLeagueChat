import asyncio
from pathlib import Path

from langchain_core.messages.human import HumanMessage
from loguru import logger

from src.backend.premier_league_api.sportdb import SportDBApi
from src.backend.premier_league_api.local import LocalPremierLeagueApi
from src.configuration import Configuration
from src.backend.agent import PremierLeagueAgent
from src.utils.logger import setup_logger

# NOTE: With current settings it doesn't work for sunderland - TODO improve
async def evaluate_all_teams(use_local_api: bool = True) -> None:
    config = Configuration.load()
    config.logging_level = "INFO" # 'DEBUG
    setup_logger(config.logging_level, Path("tests/all_teams_eval.log"))
    
    if use_local_api:
        squad_api = LocalPremierLeagueApi(json_path="tests/data/squads.json")
    else:
        squad_api = SportDBApi(config.THE_SPORT_API_KEY.get_secret_value())
        
    agent = PremierLeagueAgent(config.model_name, squad_api)
    BASE_QUERY = "Please list all the current senior squad members for the {team_name} men's team"
    for team in squad_api.get_teams():
        query = BASE_QUERY.format(team_name=team)
        response, state = await agent.send_message(HumanMessage(content=query))
        logger.info(f"Query: {query}\n Response: {response}\n Success: {state.success}")
        

if __name__ == "__main__":
    asyncio.run(evaluate_all_teams())
