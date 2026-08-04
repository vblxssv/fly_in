from src.input import Parser, Validator, Line
from src.models import StateFactory, SimulationState, Frame
from src.algorithm import Dijkstra, SpaceTimeAStar
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
        heurisics = Dijkstra.calculate(self.state.graph, self.state.graph.end)
        for k, v in heurisics.items():
            print(k, v)
        table = ReservationTable()

        try:
            for i in range(5):
                SpaceTimeAStar.add_path(i, self.state.graph, table, heurisics,
                                        self.state.graph.start, self.state.graph.end)
        except:
            pass
        print(table)
