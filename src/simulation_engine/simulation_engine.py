from src.algorithm import SpaceTimeAStar, Dijkstra, ReservationTable
from src.models import Graph, SpaceTimeState
from typing import Dict, List


class Engine:
    def __init__(self, graph: Graph, drones: int):
        self.graph = graph
        self.drones = drones
        self.heuristics = Dijkstra.calculate(graph, graph.get_end())
        self.table = ReservationTable(graph=graph)

    def run(self) -> Dict[int, List[SpaceTimeState]]:
        if self.heuristics[self.graph.get_start()] == float("inf"):
            raise ValueError("There is no path between start and end")
        paths: Dict[int, List[SpaceTimeState]] = {}
        graph = self.graph

        for drone in range(self.drones):
            path = SpaceTimeAStar.calculate_path(
                graph, graph.get_start(), graph.get_end(),
                self.table, self.heuristics)
            paths[drone] = path
            self.table.reserve_path(path, drone)
        return paths
