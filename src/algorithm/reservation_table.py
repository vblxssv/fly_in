from pydantic import BaseModel, Field
from typing import Dict, Tuple, Set, List
from src.models import SpaceTimeState, Location, Graph, ZoneRole
from itertools import pairwise


class ReservationTable(BaseModel):
    graph: Graph
    zones: Dict[Tuple[str, int], Set[int]] = Field(default_factory=dict)
    edges: Dict[Tuple[frozenset[str], int],
                Set[int]] = Field(default_factory=dict)

    def _check_zone(self, neighbor: SpaceTimeState) -> bool:
        zone = self.graph.get_zone(neighbor.zone_target)
        reserved: Set[int] = self.zones.get(
            neighbor.zone_time,
            set()
        )
        return len(reserved) < zone.max_drones

    def _get_edge_key(self,
                      current: SpaceTimeState,
                      neighbor: SpaceTimeState
                      ) -> tuple[frozenset[str], int]:
        return (
            frozenset({current.zone_target, neighbor.zone_target}),
            neighbor.time
        )

    def _check_connection(self, source: SpaceTimeState,
                          target: SpaceTimeState) -> bool:
        connection = self.graph.get_connection(source.zone_target,
                                               target.zone_target)
        key = self._get_edge_key(source, target)
        if len(self.edges.get(key, set())) >= connection.capacity:
            return False

        if target.location == Location.EDGE:
            next_key = (key[0], key[1] + 1)
            if len(self.edges.get(next_key, set())) >= connection.capacity:
                return False

        return True

    def _reserve_connection(self, first: SpaceTimeState,
                            second: SpaceTimeState,
                            drone_id: int) -> None:
        key = self._get_edge_key(first, second)
        if key not in self.edges:
            self.edges[key] = set()
        self.edges[key].add(drone_id)

        if second.location == Location.EDGE:
            next_key = (key[0], key[1] + 1)
            if next_key not in self.edges:
                self.edges[next_key] = set()
            self.edges[next_key].add(drone_id)

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

        # выход со связи
        if (
            current.location == Location.EDGE
            and neighbor.location == Location.ZONE
        ):
            return self._check_zone(neighbor)

        return False

    def _reserve_zone(self, zone: SpaceTimeState, drone_id: int) -> None:
        target = self.graph.get_zone(zone.zone_target)
        if target.role in (ZoneRole.END, ZoneRole.START):
            return
        key = zone.zone_time

        if key not in self.zones:
            self.zones[key] = set()

        self.zones[key].add(drone_id)

    def reserve_path(self, path: List[SpaceTimeState], drone_id: int) -> None:
        for curr, next in pairwise(path):
            if (curr.location == Location.ZONE
                    and next.location == Location.ZONE):
                self._reserve_zone(next, drone_id)
                if curr.zone_target != next.zone_target:
                    self._reserve_connection(curr, next, drone_id)
            elif (curr.location == Location.ZONE
                    and next.location == Location.EDGE):
                self._reserve_connection(curr, next, drone_id)
            elif (curr.location == Location.EDGE
                    and next.location == Location.ZONE):
                self._reserve_zone(next, drone_id)

    def __str__(self) -> str:
        lines = ["Reservation Table"]

        lines.append("\nZones:")
        if self.zones:
            for (zone, time), drones in sorted(self.zones.items(),
                                               key=lambda x: x[0][1]):
                lines.append(
                    f"  t={time:<3} {zone:<10} -> drones {sorted(drones)}"
                )
        else:
            lines.append("  empty")

        lines.append("\nEdges:")
        if self.edges:
            for (edge, time), drones in sorted(self.edges.items(),
                                               key=lambda x: x[0][1]):
                zones = " <-> ".join(sorted(edge))
                lines.append(
                    f"  t={time:<3} {zones:<15} -> drones {sorted(drones)}"
                )
        else:
            lines.append("  empty")

        return "\n".join(lines)
