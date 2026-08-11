from .layout import Layout
from .space_time_state import SpaceTimeState

from dataclasses import dataclass
from typing import List, Tuple, Dict


@dataclass
class Drone:
    drone_id: int
    path: List[Tuple[int, int]]
    time_start: float
    time_end: float

    def get_current_position(self, current_time: float) -> Tuple[int, int]:
        ...


class DronesFactory:
    @staticmethod
    def build(paths: Dict[int, List[SpaceTimeState]],
              layout: Layout) -> List[Drone]:
        ...
