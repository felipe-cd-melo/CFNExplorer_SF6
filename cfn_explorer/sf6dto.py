from dataclasses import dataclass
from datetime import datetime

@dataclass
class player:
    id: int
    name: str
    platform: int
    home: int
    crossplay: bool
    favcontent: int
    playtime: int
    lastplayed: int

@dataclass
class playerchar:
    player: int
    char: int
    control: int
    league_rank: int
    lp: int
    mr: int


