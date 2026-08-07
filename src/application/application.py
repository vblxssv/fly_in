from src.input import Parser, Validator, Line
from src.simulation_engine import Engine
from src.models import GraphFactory

from typing import List
from itertools import pairwise
import argparse


class Application:
    def __init__(self, args: argparse.Namespace) -> None:
        content: List[Line] = Parser.parse(args.map)
        Validator.validate(content)
        graph = GraphFactory.build(content)
        self.engine = Engine(graph, int(content[0].arguments[1]))

    def run(self) -> None:
        result = self.engine.run()
        path = result.paths[0]
        for curr, next in pairwise(path):
            print(curr)
            print(next)
            print("=" * 40)
