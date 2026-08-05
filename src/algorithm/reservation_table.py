from pydantic import BaseModel, Field
from typing import Dict, Tuple, Set, List
from src.models import SpaceTimeState, Location, Graph, Zone


class ReservationTable(BaseModel):
    graph: Graph
    zones: Dict[Tuple[str, int], Set[int]] = Field(default_factory=dict)
    edges: Dict[Tuple[frozenset[str], int],
                Set[int]] = Field(default_factory=dict)

    def _check_zone(self, neighbor: SpaceTimeState) -> bool:
        zone = self.graph.get_zone(neighbor.zone_target)
        reserved = self.zones.get(
            neighbor.zone_time,
            []
        )
        return len(reserved) < zone.max_drones

    def _get_edge_key(self,
                      current: SpaceTimeState,
                      neighbor: SpaceTimeState
                      ) -> tuple[frozenset[str], int]:
        return (
            frozenset({
                current.zone_target,
                neighbor.zone_target
            }),
            neighbor.time
        )

    def _check_connection(self, source: SpaceTimeState,
                          target: SpaceTimeState) -> bool:
        connection = self.graph.get_connection(source.zone_target,
                                               target.zone_target)
        reserved = self.edges.get(self._get_edge_key(source, target),
                                  [])
        return len(reserved) < connection.capacity

    def is_free(self,
                current: SpaceTimeState,
                neighbor: SpaceTimeState
                ) -> bool:

        # ожидание в зоне
        if (
            current.location == Location.ZONE
            and neighbor.location == Location.ZONE
            and current.zone_target == neighbor.zone_target
        ):
            return self._check_zone(neighbor)

        # обычный переход зона -> зона
        if (
            current.location == Location.ZONE
            and neighbor.location == Location.ZONE
        ):
            return (
                self._check_connection(current, neighbor)
                and self._check_zone(neighbor)
            )

        # вход на связь
        if (
            current.location == Location.ZONE
            and neighbor.location == Location.EDGE
        ):
            return self._check_connection(current, neighbor)

        # ожидание на связи
        # if (
        #     current.location == Location.EDGE
        #     and neighbor.location == Location.EDGE
        # ):
        #     return self._check_connection(current, neighbor)

        # выход со связи
        if (
            current.location == Location.EDGE
            and neighbor.location == Location.ZONE
        ):
            return self._check_zone(neighbor)

        return False

    def reserve_path(self, path: List[SpaceTimeState], drone_id: int) -> None:
        ...
