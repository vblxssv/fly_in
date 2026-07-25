from src.input import Parser, Validator, Line
from src.models import StateFactory, SimulationState, Frame
from src.algorithm import Dijkstra, AStar
from src.renderer import ArcadeRenderer, ConsoleRenderer
from src.logger import ConsoleLogger, FileLogger
from src.simulation_engine import SimulationEngine

from typing import List
import argparse


class Application:
    def __init__(self, args: argparse.Namespace) -> None:
        content: List[Line] = Parser.parse(args.map)
        Validator.validate(content)
        state: SimulationState = StateFactory.build(content)
        algo = (Dijkstra()
                if args.algorithm == "dijkstra" else AStar())

        self._renderer = (ConsoleRenderer()
                          if args.renderer == "console" else ArcadeRenderer())
        logger = (ConsoleLogger()
                  if args.logger == "console" else FileLogger("sim.log"))
        self._engine = SimulationEngine(algo, state, logger)

    def run(self) -> None:
        frames: List[Frame] = self._engine.run()
        self._renderer.play(frames)
