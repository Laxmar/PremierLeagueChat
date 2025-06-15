from datetime import date   

from pydantic import BaseModel


class Player(BaseModel):
    name: str
    date_of_birth: date
    position: str

class Squad(BaseModel):
    name: str
    players: list[Player]