from src.input import Parser, Content
from src.simulation_engine import Engine
from src.renderer import ArcadeRenderer
from src.models import GraphFactory, DronesFactory, Layout

import argparse


class Application:
    def __init__(self, args: argparse.Namespace) -> None:
        self.content: Content = Parser.parse(args.map)
        self.graph = GraphFactory.build(self.content)
        self.layout = Layout(self.graph, 700, 600)
        self.engine = Engine(self.graph, self.content.nb_drones)
        self.renderer = ArcadeRenderer()

    def run(self) -> None:
        result = self.engine.run()
        drones = DronesFactory.build(result, self.layout)
        self.renderer.play(self.graph, drones, self.layout)

