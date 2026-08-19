from src.input import Parser, Content
from src.simulation_engine import Engine
from src.renderer import ArcadeRenderer
from src.models import GraphFactory, DronesFactory, Layout
from src.logger import Logger, LoggerMode
import argparse


class Application:
    """Coordinate parsing, routing, logging, and rendering of a simulation."""

    def __init__(self, args: argparse.Namespace) -> None:
        """Initialize application services from parsed command-line options."""
        self.content: Content = Parser.parse(args.map)
        self.graph = GraphFactory.build(self.content)
        self.layout = Layout(self.graph, 1600, 900)
        self.engine = Engine(self.graph, self.content.nb_drones)
        self.renderer = ArcadeRenderer()
        self.logger = Logger(LoggerMode(args.logger))

    def run(self) -> None:
        """Run the simulation, log its result, and show the renderer."""
        result = self.engine.run()
        self.logger.log(result)
        drones = DronesFactory.build(result, self.layout)
        self.renderer.play(self.graph, drones, self.layout)
