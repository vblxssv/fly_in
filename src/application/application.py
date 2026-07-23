from src.models import SimulationState, GraphFactory, DroneFactory, Frame
from src.renderer import ConsoleRenderer, ArcadeRenderer
from src.simulation_engine import SimulationEngine
from src.algorithm import Dijkstra, AStar
from src.parser import Parser
from src.logger import ConsoleLogger, FileLogger

from typing import List, Dict, Any
import argparse


class Application:
    def __init__(self, args: argparse.Namespace) -> None:
        content: Dict[str, Any] = Parser.parse(args.map)
        graph = GraphFactory.build(content)
        drones = DroneFactory.create_drones(content["nb_drones"], graph.start)
        state = SimulationState(graph=graph, drones=drones, turn=0)

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
