from pydantic import BaseModel
from typing import Tuple
from enum import Enum


class Location(Enum):
    """Identify whether a state is in a zone or traversing an edge."""

    ZONE = "zone"
    EDGE = "edge"


class SpaceTimeState(BaseModel):
    """Represent a drone's location target at a discrete simulation time."""

    location: Location
    zone_target: str
    time: int

    class Config:
        """Configure immutable space-time state models."""

        frozen = True

    @property
    def zone_time(self) -> Tuple[str, int]:
        """Return the state key used for zone-time reservations."""
        return (self.zone_target, self.time)
