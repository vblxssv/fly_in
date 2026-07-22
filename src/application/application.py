from src.simulation_engine.simulation_engine import SimulationEngine
from src.algorithm.algorithm import Dijkstra
from src.renderer.arcade_renderer import ArcadeRenderer
from src.renderer.console_renderer import ConsoleRenderer
from src.models.state import SimulationState
from src.models.factory import GraphFactory, DroneFactory
from src.parser.parser import Parser
from typing import List, Dict, Any
from src.models.frame import Frame


class Application:
    def __init__(self, map_path: str) -> None:
        content: Dict[str, Any] = Parser.parse(map_path)
        graph = GraphFactory.build(content)
        drones = DroneFactory.create_drones(content["nb_drones"], graph.start)
        state = SimulationState(graph=graph, drones=drones, turn=0)
        self._renderer = ArcadeRenderer()
        self._engine = SimulationEngine(Dijkstra(), state)

    def run(self) -> None:
        frames: List[Frame] = self._engine.run()
        self._renderer.play(frames)
