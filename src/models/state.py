from src.models.graph import Graph
from src.models.drone import Drone
from pydantic import BaseModel, ConfigDict
from typing import Dict


class SimulationState(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    graph: Graph
    drones: Dict[int, Drone]
    turn: int
