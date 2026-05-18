from typing import Tuple
from enum import Enum
from pydantic import BaseModel, Field


class ZoneType(str, Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class ZoneColor(str, Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    NONE = "none"


class Zone(BaseModel):
    name: str = Field(pattern=r"^[^-]+$")
    pos: Tuple[int, int]
    type: ZoneType = ZoneType.NORMAL
    max_drones: int = 1
    color: ZoneColor = ZoneColor.NONE

    def __str__(self) -> str:
        colors = {
            "green": "\033[92m",
            "blue": "\033[94m",
            "red": "\033[91m",
            "none": "\033[0m"
        }
        reset = "\033[0m"
        bold = "\033[1m"
        gray = "\033[90m"
        zone_color = colors.get(self.color.value, reset)
        return (
            f"{zone_color}🌍 {bold}[Zone: {self.name}]{reset}\n"
            f" {gray}├──{reset} Coordinates: {bold}{self.pos}{reset}\n"
            f" {gray}├──{reset} Type:        {bold}{self.type.value}{reset}\n"
            f" {gray}├──{reset} Max Drones: {bold}{self.max_drones}{reset}\n"
            f" {gray}└──{reset} Color:       {zone_color}"
            f"{self.color.value}{reset}\n"
        )
