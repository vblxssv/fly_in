import heapq
from math import ceil
from typing import Dict, List, Tuple, Optional

from src.models import Graph, ZoneType
from .reservation_table import ReservationTable

TimeNode = Tuple[str, int]


class SpaceTimeAStar:
    _GOAL_SAFETY_HORIZON = 200

    @staticmethod
    def add_path(
        drone_id: int,
        graph: Graph,
        table: ReservationTable,
        heuristic: Dict[str, float],
        start: str,
        goal: str,
    ) -> None:
        """
        Plan a collision-free path for `drone_id` from `start` (time 0)
        to `goal`, respecting everything already reserved in `table`.
        Mutates `table` in place by reserving the found path.
        Raises ValueError if no path exists.
        """
        if start not in graph.zones or goal not in graph.zones:
            raise ValueError(f"Unknown zone: {start} or {goal}")

        start_node: TimeNode = (start, 0)

        open_heap: List[Tuple[float, float, str, int]] = [
            (heuristic.get(start, 0.0), 0.0, start, 0)
        ]
        came_from: Dict[TimeNode, TimeNode] = {}
        best_g: Dict[TimeNode, float] = {start_node: 0.0}
        closed: set = set()

        while open_heap:
            _, g, zone, time = heapq.heappop(open_heap)
            node: TimeNode = (zone, time)

            if node in closed:
                continue
            closed.add(node)

            if zone == goal and SpaceTimeAStar._goal_is_safe(
                table, graph, goal, time
            ):
                path = SpaceTimeAStar._reconstruct(came_from, node)
                table.reserve_path(drone_id, path)
                return

            SpaceTimeAStar._expand_wait(
                graph, table, heuristic, came_from, best_g, open_heap,
                zone, time, g,
            )
            SpaceTimeAStar._expand_moves(
                graph, table, heuristic, came_from, best_g, open_heap,
                zone, time, g,
            )

        raise ValueError(
            f"No path found for drone {drone_id} from {start} to {goal}"
        )

    # ------------------------------------------------------------------
    # Expansion helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _expand_wait(
        graph: Graph,
        table: ReservationTable,
        heuristic: Dict[str, float],
        came_from: Dict[TimeNode, TimeNode],
        best_g: Dict[TimeNode, float],
        open_heap: List[Tuple[float, float, str, int]],
        zone: str,
        time: int,
        g: float,
    ) -> None:
        zone_model = graph.zones[zone]
        next_time = time + 1

        if not table.is_zone_free(zone, next_time, zone_model.max_drones):
            return

        SpaceTimeAStar._relax(
            came_from, best_g, open_heap, heuristic,
            from_node=(zone, time),
            to_zone=zone,
            to_time=next_time,
            new_g=g + 1.0,
        )

    @staticmethod
    def _expand_moves(
        graph: Graph,
        table: ReservationTable,
        heuristic: Dict[str, float],
        came_from: Dict[TimeNode, TimeNode],
        best_g: Dict[TimeNode, float],
        open_heap: List[Tuple[float, float, str, int]],
        zone: str,
        time: int,
        g: float,
    ) -> None:
        for neighbor in graph.get_neighbors(zone):
            neighbor_zone = graph.zones[neighbor]

            if neighbor_zone.type == ZoneType.BLOCKED:
                continue

            edge = graph.get_edge(neighbor, zone)
            travel_time = max(1, ceil(neighbor_zone.type.priority))
            arrival_time = time + travel_time

            if not table.is_edge_free(
                zone, neighbor, time, travel_time, edge.capacity
            ):
                continue
            if not table.is_zone_free(
                neighbor, arrival_time, neighbor_zone.max_drones
            ):
                continue

            SpaceTimeAStar._relax(
                came_from, best_g, open_heap, heuristic,
                from_node=(zone, time),
                to_zone=neighbor,
                to_time=arrival_time,
                new_g=g + neighbor_zone.type.priority,
            )

    @staticmethod
    def _relax(
        came_from: Dict[TimeNode, TimeNode],
        best_g: Dict[TimeNode, float],
        open_heap: List[Tuple[float, float, str, int]],
        heuristic: Dict[str, float],
        from_node: TimeNode,
        to_zone: str,
        to_time: int,
        new_g: float,
    ) -> None:
        to_node: TimeNode = (to_zone, to_time)

        if new_g >= best_g.get(to_node, float("inf")):
            return

        best_g[to_node] = new_g
        came_from[to_node] = from_node
        f = new_g + heuristic.get(to_zone, float("inf"))
        heapq.heappush(open_heap, (f, new_g, to_zone, to_time))

    # ------------------------------------------------------------------
    # Goal validation / reconstruction
    # ------------------------------------------------------------------

    @staticmethod
    def _goal_is_safe(
        table: ReservationTable,
        graph: Graph,
        goal: str,
        arrival_time: int,
    ) -> bool:
        """
        A path that reaches `goal` at `arrival_time` is only valid if
        the drone can stay there afterwards without being displaced by
        an existing reservation. We check a bounded horizon rather than
        "forever", since the table only ever holds finite reservations.
        """
        goal_zone = graph.zones[goal]
        horizon = arrival_time + SpaceTimeAStar._GOAL_SAFETY_HORIZON

        for t in range(arrival_time, horizon):
            if not table.is_zone_free(goal, t, goal_zone.max_drones):
                return False
        return True

    @staticmethod
    def _reconstruct(
        came_from: Dict[TimeNode, TimeNode],
        end_node: TimeNode,
    ) -> List[TimeNode]:
        path: List[TimeNode] = [end_node]
        current = end_node

        while current in came_from:
            current = came_from[current]
            path.append(current)

        path.reverse()
        return path
