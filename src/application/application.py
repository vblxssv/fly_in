from src.simulation_engine.simulation_engine import SimulationEngine
from src.algorithm.algorithm import Algo1
from src.renderer.renderer import ConsoleRenderer
from src.models.state import SimulationState
from src.models.factory import GraphFactory, DroneFactory
from src.parser.parser import Parser


class Application:
    def __init__(self, map_path: str) -> None:
        self.map_path = map_path

    def run(self) -> None:
        content = Parser.parse(self.map_path)
        graph = GraphFactory.build(content=content)

        drones = DroneFactory.create_drones(
            amount=content["nb_drones"],
            start_zone=graph.start
        )

        state = SimulationState(graph=graph, drones=drones, turn=0)

        engine = SimulationEngine(algorithm=Algo1(),
                                  renderer=ConsoleRenderer(),
                                  state=state)
        engine.run()
