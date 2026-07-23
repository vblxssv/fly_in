from src.models import Frame

from abc import ABC, abstractmethod
from typing import List


class IRenderer(ABC):
    @abstractmethod
    def play(self, frames: List[Frame]) -> None:
        """Play back a full recorded simulation, frame by frame."""
        pass
