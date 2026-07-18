from abc import ABC, abstractmethod
from src.models.frame import Frame
from typing import List


class IRenderer(ABC):
    @abstractmethod
    def play(self, frames: List[Frame]) -> None:
        """Play back a full recorded simulation, frame by frame."""
        pass
