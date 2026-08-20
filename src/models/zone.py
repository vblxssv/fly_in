from pydantic import BaseModel, Field
from typing import Tuple
from enum import Enum
from PIL import ImageColor


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


class Zone(BaseModel):
    """Represent a capacity-limited zone in the routing graph."""

    name: str = Field(pattern=r"^[^-]+$")
    pos: Tuple[int, int]
    type: ZoneType = ZoneType.NORMAL
    role: ZoneRole = ZoneRole.NORMAL
    max_drones: int = Field(gt=0)
    color: str = Field(default="none", pattern=r"^\S+$")

    @property
    def priority(self) -> float:
        """Return this zone's pathfinding cost multiplier."""
        return self.type.priority

    @property
    def rgb(self) -> tuple[int, int, int]:
        """Convert the configured color name to an RGB tuple for rendering."""
        try:
            color = ImageColor.getrgb(self.color)
            return color[0], color[1], color[2]
        except ValueError:
            return (70, 130, 200)
