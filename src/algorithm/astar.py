from src.models import ZoneType, SimulationState
from .algorithm import IAlgorithm

from heapq import heappop, heappush
from typing import List, Set, FrozenSet, Optional, Dict


class AStar(IAlgorithm):
    MIN_STEP_COST: float = ZoneType.PRIORITY.priority  # 0.99

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

        def heuristic(zone_name: str) -> float:
            x1, y1 = graph.zones[zone_name].pos
            x2, y2 = graph.zones[end].pos
            dist = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
            return dist * self.MIN_STEP_COST

        g_score: Dict[str, float] = {z: float("inf") for z in graph.zones}
        g_score[start] = 0.0

        f_score: Dict[str, float] = {z: float("inf") for z in graph.zones}
        f_score[start] = heuristic(start)

        previous: Dict[str, Optional[str]] = {z: None for z in graph.zones}

        counter = 0
        open_set: list[tuple[float, int, str]] = [(
            f_score[start], counter, start)]
        open_set_members: Set[str] = {start}
        closed_set: Set[str] = set()

        while open_set:
            _, _, current = heappop(open_set)
            open_set_members.discard(current)

            if current == end:
                break

            if current in closed_set:
                continue
            closed_set.add(current)

            for edge in graph.adjacency_list.get(current, []):
                next_zone = graph.zones[edge.target]

                if next_zone.type == ZoneType.BLOCKED:
                    continue

                if frozenset({current, edge.target}) in blocked_edges:
                    continue

                if edge.target in closed_set:
                    continue

                tentative_g = g_score[current] + next_zone.type.priority

                if tentative_g < g_score[edge.target]:
                    previous[edge.target] = current
                    g_score[edge.target] = tentative_g
                    f_score[edge.target] = tentative_g + heuristic(edge.target)

                    if edge.target not in open_set_members:
                        counter += 1
                        heappush(open_set,
                                 (f_score[edge.target], counter, edge.target))
                        open_set_members.add(edge.target)

        if g_score[end] == float("inf"):
            return []

        path: List[str] = []
        curr: Optional[str] = end
        while curr:
            path.append(curr)
            curr = previous[curr]

        return path[::-1]
