from src.input import Parser, Validator, Line

from src.algorithm import Dijkstra, SpaceTimeAStar, A_Star
from src.renderer import ArcadeRenderer, ConsoleRenderer
from src.logger import ConsoleLogger, FileLogger
from src.algorithm import ReservationTable
from src.models import GraphFactory

from typing import List
import argparse


class Application:
    def __init__(self, args: argparse.Namespace) -> None:
        content: List[Line] = Parser.parse(args.map)
        Validator.validate(content)
        self.graph = GraphFactory.build(content)
        print(self.graph)


    def run(self) -> None:
        table = ReservationTable(graph=self.graph)
        path = SpaceTimeAStar.calculate_path(self.graph, "start", "end", table)
