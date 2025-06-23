import asyncio
import csv
from pathlib import Path
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from loguru import logger

from src.backend.premier_league_api.sportdb import SportDBApi
from src.backend.premier_league_api.local import LocalPremierLeagueApi
from src.configuration import Configuration
from src.backend.agent import PremierLeagueAgent
from src.utils.logger import setup_logger
from tests.evaluation_queries import BASE_USER_QUERIES, DIFFRENT_LANGUAGES_QUERIES, IRRELEVANT_USER_QUERIES, NOT_PREMIER_LEAGUE_TEAMS_QUERIES, UNCLEAR_TEAMS_QUERIES

class TestResult(BaseModel):
    query: str
    answer: str
    clarification_request: str = ''
    success: bool

def save_results(results: list[TestResult], filename: str = "tests/evaluation_results.csv") -> None:
    with open(filename, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["query", "clarification_request", "success"])
        # for now don't save answers beacause too long, use log file instead
        for result in results:
            writer.writerow([result.query, result.clarification_request, result.success])

# TODO consider using pytest
async def test_use_cases(should_save_results: bool = False, use_local_api: bool = True):
    config = Configuration.load()
    config.LOGGING_LEVEL = "INFO" # 'DEBUG
    setup_logger(config.LOGGING_LEVEL, Path("tests/evaluation.log"))
    
    if use_local_api:
        squad_api = LocalPremierLeagueApi(json_path="tests/data/squads.json")
    else:
        squad_api = SportDBApi(config.THE_SPORT_API_KEY.get_secret_value())
        
    agent = PremierLeagueAgent(config.MODEL_NAME, squad_api)
    results = []
    
    logger.info("\n\nTesting use cases... BASE_USER_QUERIES")
    
    for query in BASE_USER_QUERIES:
        response, state = await agent.send_message(HumanMessage(content=query))
        logger.info(f"Query: {query}\n Response: {response}\n Success: {state.success}")
        assert state.answer
        results.append(TestResult(query=query, answer=state.answer, success=state.success))

    logger.info("\n\nTesting use cases... IRRELEVANT_USER_QUERIES")
    for query in IRRELEVANT_USER_QUERIES:
        response, state = await agent.send_message(HumanMessage(content=query))
        logger.info(f"Query: {query}\n Response: {response}\n Success: {state.success}")
        assert state.answer
        results.append(TestResult(query=query, answer=state.answer, success=state.success))

    logger.info("\n\nTesting use cases... NOT_PREMIER_LEAGUE_TEAMS_QUERIES")
    for query in NOT_PREMIER_LEAGUE_TEAMS_QUERIES:
        response, state = await agent.send_message(HumanMessage(content=query))
        logger.info(f"Query: {query}\n Response: {response}\n Success: {state.success}")
        assert state.answer
        results.append(TestResult(query=query, answer=state.answer, success=state.success))

    logger.info("\n\nTesting use cases... UNCLEAR_TEAMS_QUERIES")
    # Require improving prompts to handle typos, currently the results can be improved using higher temperature
    for query in UNCLEAR_TEAMS_QUERIES:
        response, state = await agent.send_message(HumanMessage(content=query))
        logger.info(f"Query: {query}\n Response: {response}\n Success: {state.success}")
        answer = state.answer if state.answer else ""
        clarification_request = state.clarification_request if state.clarification_request else ""
        results.append(TestResult(query=query, answer=answer, clarification_request=clarification_request, success=state.success))

    logger.info("\n\nTesting use cases... DIFFRENT_LANGUAGES_QUERIES, it require improving prompts to handle different languages")
    for query in DIFFRENT_LANGUAGES_QUERIES:
        response, state = await agent.send_message(HumanMessage(content=query))
        logger.info(f"Query: {query}\n Response: {response}\n Success: {state.success}")
        answer = state.answer if state.answer else ""
        clarification_request = state.clarification_request if state.clarification_request else ""
        results.append(TestResult(query=query, answer=answer, clarification_request=clarification_request, success=state.success))

    if should_save_results:
        save_results(results)

if __name__ == "__main__":
    asyncio.run(test_use_cases(should_save_results=True, use_local_api=True))
