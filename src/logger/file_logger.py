from .logger import ILogger
from src.models import Move, SimulationState, DroneStatus

from typing import List, TextIO


class FileLogger(ILogger):
    def __init__(self, path: str) -> None:
        self._file: TextIO = open(path, "w", encoding="utf-8")

    def log_turn(
        self,
        moves: List[Move],
        state_before: SimulationState,
        state_after: SimulationState,
    ) -> None:
        parts: List[str] = []

        for move in moves:
            if move.action not in (DroneStatus.IN_TRANSIT,
                                   DroneStatus.DELIVERED):
                continue

            drone_after = state_after.drones.get(move.drone_id)
            if drone_after is None:
                continue

            if drone_after.status == DroneStatus.DELIVERED:
                parts.append(f"D{move.drone_id}-{move.target}")
            elif drone_after.status == DroneStatus.IN_TRANSIT:
                drone_before = state_before.drones.get(move.drone_id)
                source = (drone_before.current_zone
                          if drone_before else drone_after.current_zone)
                parts.append(f"D{move.drone_id}-{source}-{move.target}")
            elif drone_after.status == DroneStatus.WAITING:
                parts.append(f"D{move.drone_id}-{move.target}")

        if parts:
            self._file.write(" ".join(parts) + "\n")

    def finalize(self) -> None:
        self._file.close()
