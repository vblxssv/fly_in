from pydantic import BaseModel, Field
from typing import Tuple
from enum import Enum


class ZoneType(str, Enum):
    """Enumerate zone traversal types and their routing behavior."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"

    @property
    def priority(self) -> float:
        """Return the pathfinding cost multiplier for this zone type."""
        return {
            ZoneType.NORMAL: 1.0,
            ZoneType.RESTRICTED: 2.0,
            ZoneType.PRIORITY: 0.99,
            ZoneType.BLOCKED: float("inf"),
        }[self]


class ZoneRole(str, Enum):
    """Enumerate the special role assigned to a zone."""

    NORMAL = "hub"
    START = "start_hub"
    END = "end_hub"


class ZoneColor(str, Enum):
    """Enumerate the supported zone colors for graphical rendering."""

    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    PURPLE = "purple"
    MAGENTA = 'magenta'
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
    LIME = 'lime'
    NONE = "none"

    @property
    def rgb(self) -> tuple[int, int, int]:
        """Return the RGB tuple used to render this color."""
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
            ZoneColor.LIME: (191, 255, 0),
            ZoneColor.MAGENTA: (255, 0, 255)
        }[self]


class Zone(BaseModel):
    """Represent a capacity-limited zone in the routing graph."""

    name: str = Field(pattern=r"^[^-]+$")
    pos: Tuple[int, int]
    type: ZoneType = ZoneType.NORMAL
    role: ZoneRole = ZoneRole.NORMAL
    max_drones: int = Field(gt=0)
    color: ZoneColor = ZoneColor.NONE

    @property
    def priority(self) -> float:
        """Return this zone's pathfinding cost multiplier."""
        return self.type.priority
