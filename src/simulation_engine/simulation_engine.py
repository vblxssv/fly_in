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
        print(self.state.graph)

        path = self.algorithm.calculate_path(self.state, self.state.graph.start)
        print(path)
