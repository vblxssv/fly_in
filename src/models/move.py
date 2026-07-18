from pydantic import BaseModel
from src.models.drone import DroneStatus


class Move(BaseModel):
    drone_id: int
    action: DroneStatus
    target: str
