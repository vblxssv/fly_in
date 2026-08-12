from src.models import SpaceTimeState

from typing import List, Dict
from abc import ABC
from enum import Enum


class LoggerMode(Enum, str):
    FILE = "file"
    CONSOLE = "console"


class IWriter(ABC):
    @staticmethod
    def log(turns: List[str]) -> None:
        pass


class FileWriter(IWriter):
    @staticmethod
    def log(turns: List[str]) -> None:
        pass


class ConsoleWriter(IWriter):
    @staticmethod
    def log(turns: List[str]) -> None:
        pass


class Logger(ABC):
    def __init__(self, paths: Dict[int, List[SpaceTimeState]],
                 mode: LoggerMode) -> None:
        self._turns = self._build_turns(paths)
        self._writer = (FileWriter()
                        if mode == LoggerMode.FILE else ConsoleWriter())

    def log(self) -> None:
        self._writer.log(self._turns)
