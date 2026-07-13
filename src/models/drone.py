from enum import Enum
from pydantic import BaseModel


class DroneStatus(str, Enum):
    WAITING = "waiting"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"


class Drone(BaseModel):
    id: int
    status: DroneStatus = DroneStatus.WAITING
    current_zone: str | None = None
    current_edge_target: str | None = None
    turns_remaining: int = 0
