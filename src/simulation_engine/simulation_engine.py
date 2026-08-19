from src.algorithm import SpaceTimeAStar, Dijkstra, ReservationTable
from src.models import Graph, SpaceTimeState
from typing import Dict, List


class Engine:
    """Schedule and reserve paths for all drones in a graph."""

    def __init__(self, graph: Graph, drones: int) -> None:
        """Initialize routing state for the graph and requested drone count."""
        self.graph = graph
        self.drones = drones
        self.heuristics = Dijkstra.calculate(graph, graph.get_end())
        self.table = ReservationTable(graph=graph)

    def run(self) -> Dict[int, List[SpaceTimeState]]:
        """Plan and reserve one path for every drone."""
        if self.heuristics[self.graph.get_start()] == float("inf"):
            raise ValueError("There is no path between start and end")
        paths: Dict[int, List[SpaceTimeState]] = {}
        graph = self.graph

        for drone in range(1, self.drones + 1):
            path = SpaceTimeAStar.calculate_path(
                graph, graph.get_start(), graph.get_end(),
                self.table, self.heuristics)
            paths[drone] = path
            self.table.reserve_path(path, drone)
        return paths
