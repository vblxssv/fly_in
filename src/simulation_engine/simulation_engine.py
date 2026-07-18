from src.algorithm.algorithm import IAlgorithm
from src.renderer.renderer import IRenderer
from src.models.state import SimulationState
from src.models.frame import Frame
from typing import List
from src.models.move import Move


class SimulationEngine:
    def __init__(self, algorithm: IAlgorithm, renderer: IRenderer,
                 state: SimulationState) -> None:
        self.algorithm = algorithm
        self.renderer = renderer
        self.state = state

    def _get_zone_occupancy(self, zone: str) -> int:
        return 0

    def _get_edge_occupancy(self, source: str, target: str) -> int:
        return 0

    def _calculate_moves(self) -> List[Move]:
        return []

    def _apply_moves(self, moves: List[Move]) -> None:
        pass

    def run(self) -> List[Frame]:
        return []
