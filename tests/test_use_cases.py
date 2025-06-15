import asyncio
import csv
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from loguru import logger

from src.backend.premier_league_api.sportdb import SportDBApi
from src.configuration import Configuration
from src.prototype import PremierLeagueAgent
from tests.example_user_queries import BASE_USER_QUERIES, IRRELEVANT_USER_QUERIES, NOT_PREMIER_LEAGUE_TEAMS_QUERIES

class TestResult(BaseModel):
    query: str
    answer: str
    success: bool

def save_results(results: list[TestResult], filename: str = "tests/test_results.csv") -> None:
    with open(filename, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["query", "answer", "success"])
        for result in results:
            writer.writerow([result.query, result.answer, result.success])

# TODO use pytest
async def test_use_cases(should_save_results: bool = False):
    config = Configuration.load()
    config.logging_level = "DEBUG"
    # TODO use mocked api with local data & create a new class for it
    squad_api = SportDBApi(config.THE_SPORT_API_KEY.get_secret_value())
    agent = PremierLeagueAgent(config.model_name, squad_api)
    results = []
    
    logger.info("Testing use cases... BASE_USER_QUERIES")
    
    for query in BASE_USER_QUERIES:
        response = await agent._invoke(HumanMessage(content=query))
        logger.info(f"Query: {query}\n Success: {response.success}")
        results.append(TestResult(query=query, answer=response.answer, success=response.success))


    logger.info("Testing use cases... IRRELEVANT_USER_QUERIES")
    for query in IRRELEVANT_USER_QUERIES:
        response = await agent._invoke(HumanMessage(content=query))
        logger.info(f"Query: {query}\n Success: {response.success}")
        results.append(TestResult(query=query, answer=response.answer, success=response.success))

    logger.info("Testing use cases... NOT_PREMIER_LEAGUE_TEAMS_QUERIES")
    for query in NOT_PREMIER_LEAGUE_TEAMS_QUERIES:
        response = await agent._invoke(HumanMessage(content=query))
        logger.info(f"Query: {query}\n Success: {response.success}")
        results.append(TestResult(query=query, answer=response.answer, success=response.success))

    if should_save_results:
        save_results(results)

if __name__ == "__main__":
    asyncio.run(test_use_cases(should_save_results=False))
