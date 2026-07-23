from pydantic import BaseModel
from typing import List
from enum import Enum


class DroneStatus(str, Enum):
    WAITING = "waiting"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"


class Drone(BaseModel):
    id: int
    status: DroneStatus = DroneStatus.WAITING
    current_zone: str
    current_edge_target: str | None = None
    turns_remaining: int = 0
    path: List[str] = []

    def get_next_zone(self) -> str:
        if len(self.path) == 0:
            raise ValueError("Empty path")

        idx: int = self.path.index(self.current_zone)
        if idx + 1 >= len(self.path):
            raise ValueError("Already at end of path")

        return self.path[idx + 1]
