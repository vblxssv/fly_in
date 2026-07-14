from src.algorithm.algorithm import IAlgorithm
from src.renderer.renderer import IRenderer
from src.models.state import SimulationState


class SimulationEngine:
    def __init__(self, algorithm: IAlgorithm, renderer: IRenderer,
                 state: SimulationState) -> None:
        self.algorithm = algorithm
        self.renderer = renderer
        self.state = state

    def run(self):
        print("Pizda")
        print(self.state.graph)

        for drone in self.state.drones:
            print(drone)
