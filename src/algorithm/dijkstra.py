import heapq
from typing import Dict, List, Tuple
from src.models import Graph, ZoneType


class Dijkstra:
    @staticmethod
    def calculate(graph: Graph, target_zone: str) -> Dict[str, float]:
        reversed_adj: Dict[str, List[str]] = {
            zone: [] for zone in graph.zones
        }

        for source, neighbors in graph.adjacency_list.items():
            for target in neighbors:
                reversed_adj[target].append(source)

        distances: Dict[str, float] = {
            zone: float("inf") for zone in graph.zones
        }
        distances[target_zone] = 0

        pq: List[Tuple[float, str]] = [(0, target_zone)]

        while pq:
            current_cost, current = heapq.heappop(pq)

            if current_cost != distances[current]:
                continue
            for previous in reversed_adj[current]:
                previous_zone = graph.get_zone(previous)

                if previous_zone.type == ZoneType.BLOCKED:
                    continue
                edge_cost = graph.get_zone(current).priority

                new_cost = current_cost + edge_cost

                if new_cost < distances[previous]:
                    distances[previous] = new_cost
                    heapq.heappush(pq, (new_cost, previous))

        return distances
