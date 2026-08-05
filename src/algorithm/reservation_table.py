from pydantic import BaseModel, Field
from typing import Dict, Tuple, Set, List
from src.models import SpaceTimeState, Location, Graph


class ReservationTable(BaseModel):
    graph: Graph

    zones: Dict[Tuple[str, int], Set[int]] = Field(
        default_factory=dict
    )

    edges: Dict[Tuple[frozenset[str], int], Set[int]] = Field(
        default_factory=dict
    )

    def _is_zone_free(
        self,
        state: SpaceTimeState
    ) -> bool:
        zone = self.graph.get_zone(state.name)

        reserved = self.zones.get(
            (state.name, state.time),
            set()
        )

        return len(reserved) < zone.max_drones

    def _is_edge_free(
        self,
        current: SpaceTimeState,
        target: SpaceTimeState
    ) -> bool:

        edge = self.graph.get_edge(
            target.name,
            current.name
        )

        reserved = self.edges.get(
            (
                frozenset({
                    current.name,
                    target.name
                }),
                target.time
            ),
            set()
        )

        return len(reserved) < edge.capacity

    def is_free(
        self,
        current: SpaceTimeState,
        neighbor: SpaceTimeState
    ) -> bool:

        if neighbor.location == Location.ZONE:
            return self._is_zone_free(neighbor)

        if neighbor.location == Location.EDGE:
            return self._is_edge_free(
                current,
                neighbor
            )

        return False

    def reserve_path(
        self,
        drone_id: int,
        path: List[SpaceTimeState]
    ) -> None:

        for i, state in enumerate(path):

            if state.location == Location.ZONE:

                key = (
                    state.name,
                    state.time
                )

                if key not in self.zones:
                    self.zones[key] = set()

                self.zones[key].add(drone_id)


            elif state.location == Location.EDGE:

                previous = path[i - 1]

                edge = frozenset({
                    previous.name,
                    state.name
                })

                key = (
                    edge,
                    state.time
                )

                if key not in self.edges:
                    self.edges[key] = set()

                self.edges[key].add(drone_id)


