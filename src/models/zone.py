from typing import Tuple
from enum import Enum
from pydantic import BaseModel, Field


class ZoneType(str, Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"

    @property
    def cost(self) -> float:
        return {
            ZoneType.NORMAL: 1.0,
            ZoneType.RESTRICTED: 2.0,
            ZoneType.PRIORITY: 0.99,
            ZoneType.BLOCKED: float("inf"),
        }[self]


class ZoneColor(str, Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    PURPLE = "purple"
    BLACK = "black"
    BROWN = "brown"
    ORANGE = "orange"
    MAROON = "maroon"
    GOLD = 'gold'
    DARKRED = 'darkred'
    VIOLET = 'violet'
    CRIMSON = 'crimson'
    RAINBOW = 'rainbow'
    NONE = "none"


class Zone(BaseModel):
    name: str = Field(pattern=r"^[^-]+$")
    pos: Tuple[int, int]
    type: ZoneType = ZoneType.NORMAL
    max_drones: int = 1
    color: ZoneColor = ZoneColor.NONE
