from pydantic import BaseModel
from typing import Tuple
from enum import Enum


class Location(Enum):
    ZONE = "zone"
    EDGE = "edge"


class SpaceTimeState(BaseModel):
    location: Location
    zone_target: str
    time: int

    class Config:
        frozen = True

    @property
    def zone_time(self) -> Tuple[str, int]:
        return (self.zone_target, self.time)
