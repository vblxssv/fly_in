from src.models import Graph, ZoneType, SpaceTimeState, Location
from typing import List, Set, Dict
from .dijkstra import Dijkstra
from .reservation_table import ReservationTable

import heapq


class A_Star:
    @staticmethod
    def reconstruct_path(came_from: Dict[str, str], current: str) -> List[str]:
        path = []

        while current in came_from:
            path.append(current)
            current = came_from[current]

        path.append(current)
        path.reverse()

        return path

    @staticmethod
    def calculate_path(graph: Graph, start: str, end: str) -> List[str]:
        visited: Set[str] = set()  # Посещенные вершины, те к которым уже найден кратчайший путь
        candidates = []  # Очередь с приоритетом
        g_score = {start: 0}
        heuristic: Dict[str, float] = Dijkstra.calculate(graph, end) # Эвристика от конца

        came_from: Dict[str, str] = {}
        heapq.heappush(candidates, (0, start))

        while candidates:
            current_f, current = heapq.heappop(candidates)

            if current in visited: # если посещали - пропустить
                continue

            visited.add(current) # Иначе добавить и работать

            if current == end:
                return A_Star.reconstruct_path(came_from, current)

            for neighbor in graph.get_neighbors(current):

                zone = graph.get_zone(neighbor)

                if zone.type == ZoneType.BLOCKED:
                    continue

                new_g = g_score[current] + zone.priority

                if new_g < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = new_g

                    new_f = new_g + heuristic[neighbor]

                    heapq.heappush(
                        candidates,
                        (new_f, neighbor)
                    )
        return []


class SpaceTimeAStar:
    @staticmethod
    def get_neighbors(
        graph: Graph,
        current: SpaceTimeState
    ) -> List[SpaceTimeState]:

        neighbors: List[SpaceTimeState] = []

        if current.location == Location.ZONE:
            neighbors.append(
                SpaceTimeState(
                    location=Location.ZONE,
                    name=current.name,
                    time=current.time + 1
                )
            )
            for zone_name in graph.get_neighbors(current.name):
                zone = graph.get_zone(zone_name)

                if zone.type == ZoneType.BLOCKED:
                    continue

                if zone.type == ZoneType.RESTRICTED:
                    neighbors.append(
                        SpaceTimeState(
                            location=Location.EDGE,
                            name=zone.name,
                            time=current.time + 1
                        )
                    )
                else:
                    neighbors.append(
                        SpaceTimeState(
                            location=Location.ZONE,
                            name=zone.name,
                            time=current.time + 1
                        )
                    )
        elif current.location == Location.EDGE:
            neighbors.append(
                SpaceTimeState(
                    location=Location.EDGE,
                    name=current.name,
                    time=current.time + 1
                )
            )
            neighbors.append(
                SpaceTimeState(
                    location=Location.ZONE,
                    name=current.name,
                    time=current.time + 1
                )
            )
        return neighbors

    @staticmethod
    def reconstruct_path(
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
    def calculate_path(
        graph: Graph,
        start: str,
        end: str,
        table: ReservationTable
    ) -> List[SpaceTimeState]:

        start_state = SpaceTimeState(
            location=Location.ZONE,
            name=start,
            time=0
        )

        visited: Set[SpaceTimeState] = set()

        candidates = []

        counter = 0

        g_score: Dict[SpaceTimeState, float] = {
            start_state: 0
        }

        came_from: Dict[SpaceTimeState, SpaceTimeState] = {}

        # эвристика до цели
        heuristic: Dict[str, float] = Dijkstra.calculate(
            graph,
            end
        )


        heapq.heappush(
            candidates,
            (
                0,
                counter,
                start_state
            )
        )


        while candidates:

            current_f, _, current = heapq.heappop(
                candidates
            )


            if current in visited:
                continue


            # цель достигнута только в зоне
            if (
                current.location == Location.ZONE
                and current.name == end
            ):
                return SpaceTimeAStar.reconstruct_path(
                    came_from,
                    current
                )


            visited.add(current)


            for neighbor in SpaceTimeAStar.get_neighbors(
                graph,
                current
            ):

                # проверка конфликтов
                if not table.is_free(
                    current,
                    neighbor
                ):
                    continue


                new_g = g_score[current] + 1


                if new_g < g_score.get(
                    neighbor,
                    float("inf")
                ):

                    came_from[neighbor] = current

                    g_score[neighbor] = new_g


                    new_f = (
                        new_g
                        +
                        heuristic.get(
                            neighbor.name,
                            float("inf")
                        )
                    )


                    counter += 1

                    heapq.heappush(
                        candidates,
                        (
                            new_f,
                            counter,
                            neighbor
                        )
                    )
        return []