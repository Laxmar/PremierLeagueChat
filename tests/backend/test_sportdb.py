import pytest

from src.configuration import Configuration

from src.backend.premier_league_api.sportdb import SportDBApi
from src.backend.premier_league_api.exceptions import APIError, TeamNotFound

_SKIP_INTEGRATION_TEST = True
"""Turn the integration tests manually"""

@pytest.fixture(scope="module")
def get_api_key():
    try:
        config = Configuration.load()
        return config.THE_SPORT_API_KEY.get_secret_value()
    except Exception:
        return None


@pytest.mark.asyncio
@pytest.mark.skipif(_SKIP_INTEGRATION_TEST, reason="Skipping integration tests")
async def test_get_team_squad_success(get_api_key):
    """Successfully fetch squad for a valid Premier League team name."""
    api = SportDBApi(api_key=get_api_key)

    squad = await api.get_team_squad("manchester united")

    assert squad.name == "manchester united"
    # Basic sanity checks – the squad should have players with names and positions
    assert squad.players, "Squad should contain at least one player"
    assert all(p.name for p in squad.players)
    assert all(p.position for p in squad.players)


@pytest.mark.asyncio
@pytest.mark.skipif(_SKIP_INTEGRATION_TEST, reason="Skipping integration tests")
async def test_get_team_squad_team_not_found(get_api_key):
    """Requesting a squad for a team that is not in the hard-coded mapping should raise TeamNotFound."""
    api = SportDBApi(api_key=get_api_key)

    with pytest.raises(TeamNotFound):
        await api.get_team_squad("invalid team")


@pytest.mark.asyncio
async def test_get_team_squad_api_error():
    """An APIError from the underlying HTTP call should propagate out of get_team_squad."""
    api = SportDBApi(api_key="wrong key")

    with pytest.raises(APIError):
        await api.get_team_squad("manchester united")


if __name__ == "__main__":
    pytest.main([__file__])