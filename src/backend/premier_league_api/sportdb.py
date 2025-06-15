from datetime import date
from http import HTTPStatus

import httpx
from httpx_retries import Retry, RetryTransport
from loguru import logger

from src.backend.premier_league_api.base import IPremierLeagueApi
from src.backend.premier_league_api.exceptions import APIError, TeamNotFound
from src.backend.squad import Player, Squad


class SportDBApi(IPremierLeagueApi):
    
    class Endpoints:
        TEAM_SQUAD: str = "list/players/{team_id}"
    
    # Get Premier League ID
    # https://www.thesportsdb.com/api/v2/json/search/league/english_premier_league
    # Premier League ID: 4328
    # Get Teams: https://www.thesportsdb.com/api/v2/json/list/teams/4328
    """Cached Premier League teams to IDs"""
    _PREMIERE_LEAGUE_TEAMS_TO_ID = {
        "wolverhampton wanderers": "133599",
        "fulham": "133600",
        "aston villa": "133601",
        "liverpool": "133602",
        "sunderland": "133603",
        "arsenal": "133604",
        "chelsea": "133610",
        "manchester united": "133612",
        "manchester city": "133613",
        "everton": "133615",
        "tottenham hotspur": "133616",
        "brighton and hove albion": "133619",
        "burnley": "133623",
        "crystal palace": "133632",
        "leeds united": "133635",
        "west ham united": "133636",
        "nottingham forest": "133720",
        "bournemouth": "134301",
        "brentford": "134355",
        "newcastle united": "134777"
    }
        
    def __init__(self, api_key: str, 
                 timeout_seconds: int = 2, 
                 max_retries: int = 3, 
                 backoff_factor: float = 0.5):
        """Initialize the API client
        
        Args:
            api_key (str): API key
            timeout_seconds (int, optional): Timeout in seconds. Defaults to 2.
            max_retries (int, optional): Maximum number of retries. Defaults to 3.
            backoff_factor (float, optional): Backoff, retries over a longer period of time, Defaults to 0.5.
        """
        self._base_url = "https://www.thesportsdb.com/api/v2/json"
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._backoff_factor = backoff_factor
        self._api_key = api_key
        self._headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
    
    def get_teams(self) -> list[str]:
        """ Returns list of Premier League team names for season 2025/2026
        
        Returns:
            list[str]: List of Premier League team names
        Example:
            ["manchester united", "manchester city", "liverpool", ...]
        """
        return list(self._PREMIERE_LEAGUE_TEAMS_TO_ID.keys())
        
    async def get_team_squad(self, team_name: str) -> Squad:
        """ Returns squad of a team
        
        Args:
            team_name (str): Name of the team, lowercase with spaces
                Example: "manchester united"
        
        Returns:
            Squad: Squad of the team
        """
        team_id = self._PREMIERE_LEAGUE_TEAMS_TO_ID.get(team_name)
        if not team_id:
            raise TeamNotFound(f"Team {team_name} not found")
        
        url = self.Endpoints.TEAM_SQUAD.format(team_id=team_id)
        response = await self._base_request(url)
        
        players = response.get("list", [])
        if not players:
            msg = f'Players for team {team_name} not found'
            logger.error(msg)
            raise APIError(msg)
        
        squad = Squad(name=team_name, players=[Player(
            name=player.get("strPlayer", ""),
            date_of_birth=date.fromisoformat(player.get("dateBorn", "")),
            position=player.get("strPosition", ""),
        ) for player in players])
        return squad
    
    async def _base_request(self, endpoint: str) -> dict:
        """Base request to the API with retry
        
        Returns:
            dict: Response from the API
        Raises:
            APIError: If the request fails
        """
        url = f"{self._base_url}/{endpoint}"
        logger.trace(f"Fetching team squad from {url}")
        
        transport = RetryTransport(retry=Retry(total=self._max_retries, backoff_factor=self._backoff_factor))
        async with httpx.AsyncClient(transport=transport) as client:
            response = await client.get(url, headers=self._headers, timeout=self._timeout_seconds)
        
        if response.status_code != HTTPStatus.OK:
            msg = f'Failed to fetch team squad from {url}, status code: {response.status_code}'
            logger.error(msg)
            raise APIError(msg)
        
        return response.json()
    
