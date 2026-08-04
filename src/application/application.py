from src.input import Parser, Validator, Line
from src.models import StateFactory, SimulationState, Frame
from src.algorithm import Dijkstra, SpaceTimeAStar, A_Star
from src.renderer import ArcadeRenderer, ConsoleRenderer
from src.logger import ConsoleLogger, FileLogger
from src.algorithm import ReservationTable

from typing import List
import argparse


class Application:
    def __init__(self, args: argparse.Namespace) -> None:
        content: List[Line] = Parser.parse(args.map)
        Validator.validate(content)
        self.state: SimulationState = StateFactory.build(content)

    def run(self) -> None:
        reserv_table = ReservationTable(graph=self.state.graph)
        path = SpaceTimeAStar.calculate_path(self.state.graph, self.state.graph.start, self.state.graph.end, reserv_table)
        print(path)
