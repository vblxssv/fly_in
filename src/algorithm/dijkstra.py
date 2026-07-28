import heapq
from typing import Dict, List, Tuple
from src.models import Graph, Zone, ZoneType


class Dijkstra:
    @staticmethod
    def calculate(graph: Graph, target_zone: str) -> Dict[str, float]:
        """Finds reversed paths"""
        reversed_adj: Dict[str, List[str]] = {z: [] for z in graph.zones}
        for u, edges in graph.adjacency_list.items():
            for edge in edges:
                reversed_adj[edge.target].append(u)

        heuristics: Dict[str, float] = {zone: float('inf') for zone in graph.zones}
        heuristics[target_zone] = 0.0

        pq: List[Tuple[float, str]] = [(0.0, target_zone)]

        while pq:
            current_dist, current_node = heapq.heappop(pq)

            if current_dist > heuristics[current_node]:
                continue

            for prev_node in reversed_adj.get(current_node, []):
                prev_zone = graph.zones[prev_node]

                if prev_zone.type == ZoneType.BLOCKED:
                    continue

                step_cost = graph.zones[current_node].priority
                new_dist = current_dist + step_cost

                if new_dist < heuristics[prev_node]:
                    heuristics[prev_node] = new_dist
                    heapq.heappush(pq, (new_dist, prev_node))

        return heuristics


if __name__ == "__main__":
    import importlib

    parser_mod = importlib.import_module("src.input")
    models_mod = importlib.import_module("src.models")

    state = models_mod.StateFactory.build(parser_mod.Parser.parse("test_map.txt"))
    
    # Теперь передаем просто строку!
    res = Dijkstra.calculate(state.graph, state.graph.end)
    print(res)

