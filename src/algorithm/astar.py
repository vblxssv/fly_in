from src.models import Graph, ZoneType, ZoneRole, SpaceTimeState, Location
from src.models import Zone
from typing import List, Set, Dict
from .reservation_table import ReservationTable

import heapq


class SpaceTimeAStar:
    @staticmethod
    def _reconstruct_path(
        came_from: Dict[SpaceTimeState, SpaceTimeState],
        current: SpaceTimeState
    ) -> List[SpaceTimeState]:

        path = [current]

        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()

        return path

    @staticmethod
    def _get_neighbors(graph: Graph,
                       current: SpaceTimeState) -> List[SpaceTimeState]:
        result: List[SpaceTimeState] = []

        if current.location == Location.ZONE:
            result.append(SpaceTimeState(  # Остаюсь в той же зоне
                location=Location.ZONE,
                zone_target=current.zone_target,
                time=current.time + 1
            ))
            neighbor_zones = graph.get_neighbors(current.zone_target)
            for neighbor in neighbor_zones:
                zone: Zone = graph.get_zone(neighbor)

                # Зона требует перехода в связь
                if zone.type == ZoneType.RESTRICTED:
                    result.append(SpaceTimeState(
                        location=Location.EDGE,
                        zone_target=neighbor,
                        time=current.time + 1
                    ))

                # Обычный переход в зону на некст ходу
                elif (zone.type in (ZoneType.NORMAL, ZoneType.PRIORITY)
                        or zone.role == ZoneRole.END):
                    result.append(SpaceTimeState(
                        location=Location.ZONE,
                        zone_target=neighbor,
                        time=current.time + 1
                    ))
        elif current.location == Location.EDGE:
            #  Могу либо остаться в зоне или перейти на некст
            # result.append(SpaceTimeState(  # Остаюсь на связи
            #     location=Location.EDGE,
            #     zone_target=current.zone_target,
            #     time=current.time + 1
            # ))

            result.append(SpaceTimeState(  # переход на некст
                location=Location.ZONE,
                zone_target=current.zone_target,
                time=current.time + 1
            ))

        return result

    @staticmethod
    def calculate_path(graph: Graph, start: str,
                       end: str, table: ReservationTable,
                       heuristic: Dict[str, float]) -> List[SpaceTimeState]:

        visited: Set[SpaceTimeState] = set()
        candidates: List[tuple[float, int, SpaceTimeState]] = []
        came_from: Dict[SpaceTimeState, SpaceTimeState] = {}
        counter = 0

        start_state = SpaceTimeState(
            location=Location.ZONE,
            zone_target=start,
            time=0
        )

        g_score: Dict[SpaceTimeState, float] = {
            start_state: 0
        }

        heapq.heappush(candidates, (0, counter, start_state))

        while candidates:
            current_f, _, current = heapq.heappop(candidates)

            if current in visited:
                continue

            visited.add(current)

            if (current.location == Location.ZONE
                    and current.zone_target == end):
                return SpaceTimeAStar._reconstruct_path(came_from, current)

            all_neighbors = SpaceTimeAStar._get_neighbors(graph, current)

            for neighbor in all_neighbors:
                zone: Zone = graph.get_zone(neighbor.zone_target)

                if zone.type == ZoneType.BLOCKED:
                    continue

                if not table.is_free(current, neighbor):
                    continue

                if (current.location == Location.ZONE
                        and neighbor.location == Location.ZONE
                        and current.zone_target == neighbor.zone_target):
                    neighbor_g = g_score[current] + 1
                else:
                    neighbor_g = (
                        g_score[current]
                        + zone.priority
                    )

                if g_score.get(neighbor, float("inf")) <= neighbor_g:
                    continue

                came_from[neighbor] = current
                g_score[neighbor] = neighbor_g

                f_score = neighbor_g + heuristic.get(neighbor.zone_target,
                                                     float("inf"))
                counter += 1
                heapq.heappush(candidates, (f_score, counter, neighbor))
        return []
