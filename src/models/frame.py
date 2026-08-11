from dataclasses import dataclass
from typing import Tuple, List, Dict

from src.models import SpaceTimeState
from .layout import Layout


@dataclass
class Move:
    drone_id: int
    source: Tuple[int, int]
    target: Tuple[int, int]
    progress: float


@dataclass
class Frame:
    moves: List[Move]


class FrameFactory:
    @staticmethod
    def build(paths: Dict[int, List[SpaceTimeState]],
              layout: Layout) -> List[Frame]:
        ...
