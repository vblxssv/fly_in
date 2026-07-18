from abc import ABC, abstractmethod
from src.models.move import Move
from src.models.state import SimulationState
from typing import List


class IRenderer(ABC):
    @abstractmethod
    def render(self, state: SimulationState, moves: List[Move]) -> None:
        pass


class ConsoleRenderer(IRenderer):
    def render(self, state: SimulationState, moves: List[Move]) -> None:
        pass


class PyGameRenderer(IRenderer):
    def render(self, state: SimulationState, moves: List[Move]) -> None:
        pass
