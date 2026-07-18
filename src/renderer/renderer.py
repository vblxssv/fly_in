from abc import ABC, abstractmethod
from src.models.frame import Frame
from typing import List


class IRenderer(ABC):
    @abstractmethod
    def render(self, frames: List[Frame]) -> None:
        pass


class ConsoleRenderer(IRenderer):
    @abstractmethod
    def render(self, frames: List[Frame]) -> None:
        pass


class PyGameRenderer(IRenderer):
    @abstractmethod
    def render(self, frames: List[Frame]) -> None:
        pass
