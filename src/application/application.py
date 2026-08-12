from src.input import Parser, Validator, Line
from src.simulation_engine import Engine
from src.models import GraphFactory
from src.renderer import ArcadeRenderer
from typing import List

import argparse

from src.models import Layout, Drone, DronesFactory


class Application:
    def __init__(self, args: argparse.Namespace) -> None:
        content: List[Line] = Parser.parse(args.map)
        Validator.validate(content)
        graph = GraphFactory.build(content)
        self.graph = graph
        self.engine = Engine(graph, int(content[0].arguments[1]))
        self.layout = Layout(graph, 1700, 1000)
        self.renderer = ArcadeRenderer()

    def run(self) -> None:
        result = self.engine.run()

        max_length = max(map(len, result.values())) - 1
        print(f"Turns: {max_length}")

        drones: List[Drone] = DronesFactory.build(result, self.layout)
        self.renderer.play(self.graph, drones, self.layout)
