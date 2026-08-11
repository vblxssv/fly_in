from src.input import Parser, Validator, Line
from src.simulation_engine import Engine
from src.models import GraphFactory

from typing import List
from itertools import pairwise
import argparse
from src.models import FrameFactory, Frame
from src.models import Layout


class Application:
    def __init__(self, args: argparse.Namespace) -> None:
        content: List[Line] = Parser.parse(args.map)
        Validator.validate(content)
        graph = GraphFactory.build(content)
        self.engine = Engine(graph, int(content[0].arguments[1]))
        self.layout = Layout(graph, 1000, 600)

    def run(self) -> None:
        result = self.engine.run()
        
