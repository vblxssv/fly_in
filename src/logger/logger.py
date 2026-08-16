from src.models import SpaceTimeState

from typing import List, Dict
from abc import ABC, abstractmethod
from enum import Enum


class LoggerMode(str, Enum):
    FILE = "file"
    CONSOLE = "console"


class IWriter(ABC):
    @staticmethod
    @abstractmethod
    def log(turns: List[str]) -> None:
        ...


class FileWriter(IWriter):
    @staticmethod
    def log(turns: List[str], path: str = "output.txt") -> None:
        with open(path, "w") as f:
            f.write("\n".join(turns) + "\n")


class ConsoleWriter(IWriter):
    @staticmethod
    def log(turns: List[str]) -> None:
        for line in turns:
            print(line)


class Logger:
    def __init__(self,
                 mode: LoggerMode) -> None:
        self._writer = (FileWriter()
                        if mode == LoggerMode.FILE else ConsoleWriter())

    def log(self, paths: Dict[int, List[SpaceTimeState]]) -> None:
        turns = self._build_turns(paths)
        self._writer.log(turns)

    def _build_turns(self,
                     paths: Dict[int, List[SpaceTimeState]]) -> List[str]:
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
                if state.zone_target == prev_state.zone_target:
                    continue
                movements.append(f"D{drone_id}-{state.zone_target}")
            if movements:
                turns.append(" ".join(movements))

        return turns
