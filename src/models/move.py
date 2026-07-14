from pydantic import BaseModel
from enum import Enum, auto


class MoveAction(Enum):
    MOVE_TO = auto()
    ENTER_CONNECTION = auto()
    WAIT = auto()


class Move(BaseModel):
    drone_id: int
    action: MoveAction
    target: str
