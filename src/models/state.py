from .graph import Graph
from .drone import Drone
from typing import Dict

from pydantic import BaseModel, ConfigDict


class SimulationState(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    graph: Graph
    drones: Dict[int, Drone]
    turn: int
