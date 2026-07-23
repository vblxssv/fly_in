from .state import SimulationState
from .move import Move

from dataclasses import dataclass
from typing import List


@dataclass
class Frame:
    state: SimulationState
    moves: List[Move]
