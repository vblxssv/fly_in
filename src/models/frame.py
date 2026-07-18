from src.models.state import SimulationState
from src.models.move import Move
from dataclasses import dataclass
from typing import List


@dataclass
class Frame:
    state: SimulationState
    moves: List[Move]
