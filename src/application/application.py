from src.models import SimulationState, GraphFactory, DroneFactory, Frame
from src.renderer import ConsoleRenderer, ArcadeRenderer
from src.simulation_engine import SimulationEngine
from src.algorithm import Dijkstra
from src.parser import Parser

from typing import List, Dict, Any
import argparse


class Application:
    def __init__(self, args: argparse.Namespace) -> None:
        content: Dict[str, Any] = Parser.parse(args.map)
        graph = GraphFactory.build(content)
        drones = DroneFactory.create_drones(content["nb_drones"], graph.start)
        state = SimulationState(graph=graph, drones=drones, turn=0)

        algo = (Dijkstra()
                if args.algorithm == "dijkstra" else Dijkstra())

        self._renderer = (ConsoleRenderer()
                          if args.renderer == "console" else ArcadeRenderer())

        self._engine = SimulationEngine(algo, state)

    def run(self) -> None:
        frames: List[Frame] = self._engine.run()
        print(f"Total turns: {len(frames)}")
        self._renderer.play(frames)
