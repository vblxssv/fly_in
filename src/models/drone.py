from .layout import Layout
from .space_time_state import SpaceTimeState, Location


from dataclasses import dataclass
from typing import List, Tuple, Dict
import random


@dataclass
class Drone:
    drone_id: int
    path: List[Tuple[int, int]]
    color: Tuple[int, int, int]


class DronesFactory:
    @staticmethod
    def build(paths: Dict[int, List[SpaceTimeState]],
              layout: Layout) -> List[Drone]:
        drones: List[Drone] = []
        for drone_id, path in paths.items():
            points: List[Tuple[int, int]] = []
            for i, state in enumerate(path):
                if state.location == Location.ZONE:
                    point = layout.positions[state.zone_target]
                elif state.location == Location.EDGE:
                    previous_state = path[i - 1]
                    previous_point = layout.positions[
                        previous_state.zone_target]
                    next_point = layout.positions[state.zone_target]
                    point = ((previous_point[0] + next_point[0]) // 2,
                             (previous_point[1] + next_point[1]) // 2)
                points.append(point)
            color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255),
            )
            drones.append(Drone(drone_id=drone_id, path=points, color=color))
        return drones
