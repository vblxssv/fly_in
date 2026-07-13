from src.models.factory import GraphFactory, DroneFactory
# from src.renderer.renderer import Renderer
from src.parser.parser import Parser
from src.models.drone import Drone
from src.models.graph import Graph


class Application:
    def __init__(self, map_path: str) -> None:
        self.map_path = map_path
        self.graph: Graph | None = None
        self.drones: list[Drone] | None = None

    def run(self) -> None:
        self._load()
        print(self.graph)

    def _load(self) -> None:
        content = Parser.parse(self.map_path)
        print(content)
        self.graph = GraphFactory.build(content)
        self.drones = DroneFactory.create_drones(
            amount=content["nb_drones"],
            start_zone=self.graph.start,
        )
