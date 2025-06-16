import asyncio
import json
from pathlib import Path

from loguru import logger

from src.configuration import Configuration
from src.backend.premier_league_api.exceptions import APIError
from src.backend.premier_league_api.sportdb import SportDBApi

async def _fetch_squads_async(api_key: str) -> dict[str, list[dict]]:
    """Fetch squads for all Premier League teams using the public SportDB API.

    Args:
        api_key (str): API key

    Returns:
        dict[str, list[dict]]: Squads for all Premier League teams
    """
    api = SportDBApi(api_key)
    teams = api.get_teams()
    logger.info(f"Fetching squads for {len(teams)} teams")
    
    squads = {}
    for team in teams:
        logger.info(f"Fetching squad for team {team}")
        try:
            squad = await api.get_team_squad(team)
            squads[team] = [
                {
                    "name": player.name,
                    "date_of_birth": player.date_of_birth.isoformat(),
                    "position": player.position,
                }
                for player in squad.players
            ]
        except APIError as e:
            logger.error(f"Failed to fetch squad for team {team}: {e}")
    return squads

def fetch_squads(api_key: str, output_file: Path) -> None:
    """Fetch squads for all Premier League teams and save to a JSON file.

    Args:
        api_key (str): API key
        output_file (Path): Path to the output JSON file
    """
    squads = asyncio.run(_fetch_squads_async(api_key))
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(squads, f, indent=4, ensure_ascii=False)

def main() -> None:
    config = Configuration.load()
    output_dir = Path("tests/data")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "squads.json"
    fetch_squads(config.THE_SPORT_API_KEY.get_secret_value(), output_file)

if __name__ == "__main__":
    main()
