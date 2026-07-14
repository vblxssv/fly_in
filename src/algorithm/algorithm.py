from abc import ABC, abstractmethod
from src.models.move import Move
from src.models.state import SimulationState
from typing import List


class IAlgorithm(ABC):
    @abstractmethod
    def calculate_path(self, state: SimulationState, start: str) -> List[str]:
        pass


class Dijkstra(IAlgorithm):
    def calculate_path(self, state: SimulationState, start: str) -> List[str]:
        return []


class Algo2(IAlgorithm):
    pass
















