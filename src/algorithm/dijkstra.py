from src.models import ZoneType, SimulationState
from .algorithm import IAlgorithm

from heapq import heappop, heappush
from typing import List, Set, FrozenSet, Optional


class Dijkstra(IAlgorithm):
    def calculate_path(
        self,
        state: SimulationState,
        start: str,
        blocked_edges: Optional[Set[FrozenSet[str]]] = None,
    ) -> List[str]:
        graph = state.graph
        end = graph.end
        blocked_edges = blocked_edges or set()

        distances: dict[str, float] = {z: float("inf") for z in graph.zones}
        previous: dict[str, str | None] = {z: None for z in graph.zones}
        queue: list[tuple[float, str]] = [(0.0, start)]
        distances[start] = 0.0

        while queue:
            current_dist, current = heappop(queue)
            if current_dist > distances[current]:
                continue
            if current == end:
                break

            for edge in graph.adjacency_list.get(current, []):
                next_zone = graph.zones[edge.target]

                if next_zone.type == ZoneType.BLOCKED:
                    continue

                if frozenset({current, edge.target}) in blocked_edges:
                    continue

                new_dist = current_dist + next_zone.type.priority
                if new_dist < distances[edge.target]:
                    distances[edge.target] = new_dist
                    previous[edge.target] = current
                    heappush(queue, (new_dist, edge.target))

        if distances[end] == float("inf"):
            return []

        path: List[str] = []
        curr: str | None = end
        while curr:
            path.append(curr)
            curr = previous[curr]
        return path[::-1]
