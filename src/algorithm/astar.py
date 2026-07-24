from src.models import ZoneType, SimulationState
from .algorithm import IAlgorithm

from heapq import heappop, heappush
from typing import Dict, List, Optional, Set, FrozenSet


class AStar(IAlgorithm):
    MIN_STEP_COST = ZoneType.PRIORITY.priority

    def calculate_path(
        self,
        state: SimulationState,
        start: str,
        blocked_edges: Optional[Set[FrozenSet[str]]] = None,
    ) -> List[str]:
        graph = state.graph
        end = graph.end
        blocked_edges = blocked_edges or set()

        if start not in graph.zones or end not in graph.zones:
            return []

        def heuristic(zone: str) -> float:
            x1, y1 = graph.zones[zone].pos
            x2, y2 = graph.zones[end].pos
            return ((((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5)
                    * self.MIN_STEP_COST)

        g_score: Dict[str, float] = {
            zone: float("inf") for zone in graph.zones
        }
        previous: Dict[str, Optional[str]] = {
            zone: None for zone in graph.zones
        }

        g_score[start] = 0.0

        counter = 0
        open_set: list[tuple[float, int, str]] = []
        heappush(open_set, (heuristic(start), counter, start))

        closed: Set[str] = set()

        while open_set:
            f_current, _, current = heappop(open_set)

            if current in closed:
                continue

            expected_f = g_score[current] + heuristic(current)
            if f_current > expected_f:
                continue

            if current == end:
                break

            closed.add(current)

            for edge in graph.adjacency_list.get(current, []):

                if frozenset({current, edge.target}) in blocked_edges:
                    continue

                zone = graph.zones[edge.target]

                if zone.type == ZoneType.BLOCKED:
                    continue

                if edge.target in closed:
                    continue

                tentative_g = g_score[current] + zone.type.priority

                if tentative_g < g_score[edge.target]:
                    g_score[edge.target] = tentative_g
                    previous[edge.target] = current

                    counter += 1
                    heappush(
                        open_set,
                        (
                            tentative_g + heuristic(edge.target),
                            counter,
                            edge.target,
                        ),
                    )

        if g_score[end] == float("inf"):
            return []

        path: List[str] = []
        current: Optional[str] = end

        while current is not None:
            path.append(current)
            current = previous[current]

        return path[::-1]
