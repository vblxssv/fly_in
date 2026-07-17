from abc import ABC, abstractmethod
from src.models.state import SimulationState
from typing import List
from heapq import heappop, heappush
from src.models.zone import ZoneType
from typing import Dict, Optional, Tuple


class IAlgorithm(ABC):
    @abstractmethod
    def calculate_path(self, state: SimulationState, start: str) -> List[str]:
        pass


class Dijkstra(IAlgorithm):
    def _get_cost(self, type: ZoneType) -> float:
        match type:
            case ZoneType.NORMAL:
                return 1.0
            case ZoneType.RESTRICTED:
                return 2.0
            case ZoneType.PRIORITY:
                return 0.99
            case ZoneType.BLOCKED:
                return float("inf")

    def calculate_path(self, state: SimulationState, start: str) -> List[str]:
        graph = state.graph
        end = graph.end

        distances: dict[str, float] = {
            zone: float("inf")
            for zone in graph.zones
        }

        previous: dict[str, str | None] = {
            zone: None
            for zone in graph.zones
        }

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

                new_dist = current_dist + self._get_cost(next_zone.type)

                if new_dist < distances[edge.target]:
                    distances[edge.target] = new_dist
                    previous[edge.target] = current
                    heappush(queue, (new_dist, edge.target))

        if distances[end] == float("inf"):
            return []

        path: List[str] = []
        current: str | None = end

        while current:
            path.append(current)
            current = previous[current]

        return path[::-1]
