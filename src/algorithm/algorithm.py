from abc import ABC, abstractmethod
from src.models.move import Move
from src.models.state import SimulationState
from typing import List


class IAlgorithm(ABC):
    @abstractmethod
    def compute_turn(self, state: SimulationState) -> List[Move]:
        pass


class Algo1(IAlgorithm):
    def compute_turn(self, state: SimulationState) -> List[Move]:
        return []


class Algo2(IAlgorithm):
    pass
