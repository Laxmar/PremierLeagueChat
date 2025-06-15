from collections import defaultdict
import enum

from datetime import date   
from pydantic import BaseModel

class PlayersGroup(enum.StrEnum):
    Goalkeepers = "Goalkeepers"
    Manager = "Manager"
    Defenders = "Defenders"
    Midfielders = "Midfielders"
    Forwards = "Forwards"
    Others = "Others"

ALL_PLAYER_GROUPS = list(PlayersGroup)

POSITION_TO_PLAYER_GROUP = {
    "Goalkeeper": PlayersGroup.Goalkeepers,
    "Manager": PlayersGroup.Manager,
    "Defender": PlayersGroup.Defenders,
    "Centre-Back": PlayersGroup.Defenders,
    "Left-Back": PlayersGroup.Defenders,
    "Right-Back": PlayersGroup.Defenders,
    "Attacking Midfield": PlayersGroup.Midfielders,
    "Central Midfield": PlayersGroup.Midfielders,
    "Defensive Midfield": PlayersGroup.Midfielders,
    "Centre-Forward": PlayersGroup.Forwards,
    "Right Winger": PlayersGroup.Forwards,
    "Left Wing": PlayersGroup.Forwards,
}

class Player(BaseModel):
    name: str
    date_of_birth: date
    position: str

class Squad(BaseModel):
    name: str
    players: list[Player]
    
    def get_player_group(self) -> dict[PlayersGroup, list[Player]]:
        """Groups players by their positions."""
        grouped = defaultdict(list)
        for player in self.players:
            group = POSITION_TO_PLAYER_GROUP.get(player.position, PlayersGroup.Others)
            grouped[group].append(player)
        return grouped
    