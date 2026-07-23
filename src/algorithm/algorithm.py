from src.models import SimulationState

from abc import ABC, abstractmethod
from typing import List, Set, FrozenSet, Optional


class IAlgorithm(ABC):
    @abstractmethod
    def calculate_path(
        self,
        state: SimulationState,
        start: str,
        blocked_edges: Optional[Set[FrozenSet[str]]] = None,
    ) -> List[str]:
        pass
