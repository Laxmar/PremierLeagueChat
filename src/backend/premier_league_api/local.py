from datetime import date
import json

from loguru import logger

from src.backend.premier_league_api.base import IPremierLeagueApi
from src.backend.premier_league_api.exceptions import TeamNotFound
from src.backend.squad import Player, Squad

class LocalPremierLeagueApi(IPremierLeagueApi):
    """Local Premier League API that loads squads from a cached JSON file."""

    def __init__(self, json_path: str):
        """Load squads from a JSON file.

        Args:
            json_path (str): Path to JSON file produced by download utility.
        """

        self._json_path = json_path
        with open(json_path, "r", encoding="utf-8") as fp:
            self._data: dict[str, list[dict]] = json.load(fp)

    def get_teams(self) -> list[str]:
        """Return list of available Premier League team names."""
        return list(self._data.keys())

    async def get_team_squad(self, team_name: str) -> Squad:
        """Return the squad for the given team from the local cache.

        Args:
            team_name (str): Team name in lowercase with spaces.
        Returns:
            Squad: Team squad built from cached JSON.
        Raises:
            TeamNotFound: If the team is not present in the JSON file.
        """
        players_raw = self._data.get(team_name)
        if players_raw is None:
            msg = f"Team {team_name} not found in local data"
            logger.error(msg)
            raise TeamNotFound(msg)

        players = [
            Player(
                name=p["name"],
                date_of_birth=date.fromisoformat(p["date_of_birth"]),
                position=p["position"],
            )
            for p in players_raw
        ]
        return Squad(name=team_name, players=players)