from src.models import Move, SimulationState

from abc import ABC, abstractmethod
from typing import List


class ILogger(ABC):
    @abstractmethod
    def log_turn(
        self,
        moves: List[Move],
        state_before: SimulationState,
        state_after: SimulationState,
    ) -> None:
        pass

    @abstractmethod
    def finalize(self) -> None:
        pass
