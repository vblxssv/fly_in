from pydantic import BaseModel, Field
from typing import Tuple
from enum import Enum
from math import ceil


class ZoneType(str, Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"

    @property
    def priority(self) -> float:
        return {
            ZoneType.NORMAL: 1.0,
            ZoneType.RESTRICTED: 2.0,
            ZoneType.PRIORITY: 0.99,
            ZoneType.BLOCKED: float("inf"),
        }[self]

    @property
    def cost(self) -> int:
        return ceil(self.priority)


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
    CYAN = "cyan"
    YELLOW = "yellow"
    NONE = "none"

    @property
    def rgb(self) -> tuple[int, int, int]:
        return {
            ZoneColor.RED: (220, 60, 60),
            ZoneColor.GREEN: (80, 200, 100),
            ZoneColor.BLUE: (70, 130, 200),
            ZoneColor.PURPLE: (160, 90, 200),
            ZoneColor.BLACK: (40, 40, 40),
            ZoneColor.BROWN: (140, 90, 50),
            ZoneColor.ORANGE: (230, 140, 50),
            ZoneColor.MAROON: (128, 0, 0),
            ZoneColor.GOLD: (212, 175, 55),
            ZoneColor.DARKRED: (139, 0, 0),
            ZoneColor.VIOLET: (200, 120, 220),
            ZoneColor.CRIMSON: (220, 20, 60),
            ZoneColor.CYAN: (60, 200, 200),
            ZoneColor.YELLOW: (230, 220, 60),
            ZoneColor.RAINBOW: (255, 105, 180),
            ZoneColor.NONE: (70, 130, 200),
        }[self]


class Zone(BaseModel):
    name: str = Field(pattern=r"^[^-]+$")
    pos: Tuple[int, int]
    type: ZoneType = ZoneType.NORMAL
    max_drones: int = 1
    color: ZoneColor = ZoneColor.NONE
