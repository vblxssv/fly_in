from .drone import DroneStatus

from pydantic import BaseModel


class Move(BaseModel):
    drone_id: int
    action: DroneStatus
    target: str
