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
        self.layout = Layout(graph, 1500, 1000)

    def run(self) -> None:
        result = self.engine.run()

        drones: List[Drone] = DronesFactory.build(result.paths, self.layout)

        for drone in drones:
            print(drone)
        print(len(drones))

        renderer = ArcadeRenderer()
        renderer.play(self.graph, drones, self.layout)
