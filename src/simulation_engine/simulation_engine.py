from src.algorithm import SpaceTimeAStar, Dijkstra, ReservationTable
from src.models import Graph, SpaceTimeState
from pydantic import BaseModel
from typing import Dict, List


class SimulationResult(BaseModel):
    graph: Graph
    paths: Dict[int, List[SpaceTimeState]]
    reservations: ReservationTable


class Engine:
    def __init__(self, graph: Graph, drones: int):
        self.graph = graph
        self.drones = drones
        self.heuristics = Dijkstra.calculate(graph, graph.get_end())
        self.table = ReservationTable(graph=graph)

    def run(self) -> SimulationResult:
        paths: Dict[int, List[SpaceTimeState]] = {}
        graph = self.graph

        for drone in range(self.drones):
            path = SpaceTimeAStar.calculate_path(
                graph, graph.get_start(), graph.get_end(),
                self.table, self.heuristics)
            paths[drone] = path
            self.table.reserve_path(path, drone)
        return SimulationResult(graph=graph,
                                paths=paths,
                                reservations=self.table)
