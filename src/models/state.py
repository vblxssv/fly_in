from src.models.graph import Graph
from src.models.drone import Drone
from pydantic import BaseModel, ConfigDict
from typing import List


class SimulationState(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    graph: Graph
    drones: List[Drone]
    turn: int
