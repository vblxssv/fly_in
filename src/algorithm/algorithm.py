from src.models import SimulationState

from abc import ABC, abstractmethod
from typing import List


class IAlgorithm(ABC):
    @abstractmethod
    def calculate_path(self, state: SimulationState, start: str) -> List[str]:
        pass
