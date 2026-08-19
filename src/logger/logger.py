from src.models import SpaceTimeState, Location

from typing import List, Dict
from abc import ABC, abstractmethod
from enum import Enum


class LoggerMode(str, Enum):
    """Enumerate supported destinations for simulation output."""

    FILE = "file"
    CONSOLE = "console"


class IWriter(ABC):
    """Define the interface for writing formatted simulation turns."""

    @staticmethod
    @abstractmethod
    def log(turns: List[str]) -> None:
        """Write formatted simulation turns to an output destination."""
        ...


class FileWriter(IWriter):
    """Write simulation turns to a text file."""

    @staticmethod
    def log(turns: List[str], path: str = "output.txt") -> None:
        """Write formatted simulation turns to a text file."""
        with open(path, "w") as f:
            f.write("\n".join(turns) + "\n")


class ConsoleWriter(IWriter):
    """Write simulation turns to standard output."""

    @staticmethod
    def log(turns: List[str]) -> None:
        """Print formatted simulation turns to standard output."""
        for line in turns:
            print(line)


class Logger:
    """Format drone paths and dispatch them to an output writer."""

    def __init__(self,
                 mode: LoggerMode) -> None:
        """Initialize a logger using the writer selected by ``mode``."""
        self._writer = (FileWriter()
                        if mode == LoggerMode.FILE else ConsoleWriter())

    def log(self, paths: Dict[int, List[SpaceTimeState]]) -> None:
        """Format drone paths and send the resulting turns to the writer."""
        turns = self._build_turns(paths)
        self._writer.log(turns)

    @staticmethod
    def _format_movement(drone_id: int,
                         prev_state: SpaceTimeState,
                         state: SpaceTimeState) -> str:
        """Format one drone state transition for the output log."""
        if state.location == Location.EDGE:
            label = f"{prev_state.zone_target}-{state.zone_target}"
        else:
            label = state.zone_target

        return f"D{drone_id}-{label}"

    @staticmethod
    def _is_stationary(prev_state: SpaceTimeState,
                       state: SpaceTimeState) -> bool:
        """Return whether two consecutive states keep a drone in one zone."""
        return (
            state.location == Location.ZONE
            and prev_state.location == Location.ZONE
            and state.zone_target == prev_state.zone_target
        )

    def _build_turns(self,
                     paths: Dict[int, List[SpaceTimeState]]) -> List[str]:
        """Build one formatted movement line for each active turn."""
        if not paths:
            return []

        max_length = max(len(path) for path in paths.values()) - 1
        turns: List[str] = []

        for turn_index in range(1, max_length + 1):
            movements: List[str] = []
            for drone_id, path in paths.items():
                if turn_index >= len(path):
                    continue
                prev_state = path[turn_index - 1]
                state = path[turn_index]

                if self._is_stationary(prev_state, state):
                    continue

                movements.append(
                    self._format_movement(drone_id, prev_state, state)
                )
            if movements:
                turns.append(" ".join(movements))

        return turns
