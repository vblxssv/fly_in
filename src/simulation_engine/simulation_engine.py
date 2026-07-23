from src.models import DroneStatus, Drone, Move, Frame, SimulationState
from src.algorithm import IAlgorithm
from typing import List, Dict, Set, FrozenSet
from math import ceil


class SimulationEngine:
    def __init__(self, algorithm: IAlgorithm,
                 state: SimulationState) -> None:
        self.algorithm = algorithm
        self.state = state

    def _snapshot(self) -> SimulationState:
        return self.state.model_copy(deep=True)

    def _all_delivered(self) -> bool:
        return all(drone.status == DroneStatus.DELIVERED
                   for drone in self.state.drones.values())

    def _get_zone_occupancy(self, zone: str) -> int:
        return sum(
            1 for d in self.state.drones.values()
            if d.status == DroneStatus.WAITING and d.current_zone == zone
        )

    def _get_edge_occupancy(self, source: str, target: str) -> int:
        key = frozenset({source, target})
        return sum(
            1
            for d in self.state.drones.values()
            if d.status == DroneStatus.IN_TRANSIT
            and d.current_edge_target is not None
            and frozenset({d.current_zone, d.current_edge_target}) == key
        )

    def _congested_edges(
        self, reserved: Dict[frozenset, int]
    ) -> Set[FrozenSet[str]]:
        congested: Set[FrozenSet[str]] = set()
        graph = self.state.graph
        for source, edges in graph.adjacency_list.items():
            for edge in edges:
                key = frozenset({source, edge.target})
                occ = self._get_edge_occupancy(source, edge.target)
                occ += reserved.get(key, 0)
                if occ >= edge.capacity:
                    congested.add(key)
        return congested

    def _path_cost(self, path: List[str]) -> float:
        graph = self.state.graph
        total = 0.0
        for zone_name in path[1:]:
            total += graph.zones[zone_name].type.priority
        return total


    def _try_replan(
        self, drone: Drone, reserved_edges: Dict[frozenset, int]
    ) -> str | None:
        graph = self.state.graph
        blocked = self._congested_edges(reserved_edges)

        new_tail = self.algorithm.calculate_path(
            self.state, drone.current_zone, blocked
        )
        if not new_tail or len(new_tail) < 2:
            return None

        idx = drone.path.index(drone.current_zone)
        candidate_path = drone.path[:idx] + new_tail

        if candidate_path == drone.path:
            return None

        next_zone = new_tail[1]
        edge_key = frozenset({drone.current_zone, next_zone})
        capacity = graph.get_edge(next_zone, drone.current_zone).capacity
        occ = self._get_edge_occupancy(drone.current_zone, next_zone)
        occ += reserved_edges.get(edge_key, 0)

        if occ >= capacity:
            return None 

        drone.path = candidate_path
        return next_zone

    def _calculate_moves(self) -> List[Move]:
        reserved_edges: Dict[frozenset[str], int] = {}
        graph = self.state.graph
        moves: List[Move] = []

        for drone in self.state.drones.values():
            if drone.status != DroneStatus.WAITING:
                continue

            try:
                next_zone = drone.get_next_zone()
            except ValueError:
                continue

            edge_key = frozenset({drone.current_zone, next_zone})
            capacity = graph.get_edge(drone.current_zone, next_zone).capacity
            occupied = (self._get_edge_occupancy(drone.current_zone, next_zone)
                        + reserved_edges.get(edge_key, 0))

            if capacity > occupied:
                reserved_edges[edge_key] = reserved_edges.get(edge_key, 0) + 1
                moves.append(Move(drone_id=drone.id,
                                  action=DroneStatus.IN_TRANSIT,
                                  target=next_zone))
                continue

            replanned_target = self._try_replan(drone, reserved_edges)
            if replanned_target is not None:
                key = frozenset({drone.current_zone, replanned_target})
                reserved_edges[key] = reserved_edges.get(key, 0) + 1
                moves.append(Move(drone_id=drone.id,
                                  action=DroneStatus.IN_TRANSIT,
                                  target=replanned_target))
                continue

            moves.append(Move(drone_id=drone.id,
                              action=DroneStatus.WAITING,
                              target=drone.current_zone))
        return moves

    def _start_transit(self, drone: Drone, target: str) -> None:
        zone = self.state.graph.zones[target]
        drone.status = DroneStatus.IN_TRANSIT
        drone.current_edge_target = target
        drone.turns_remaining = max(1, ceil(zone.type.priority))

    def _progress_transit(self, drone: Drone) -> None:
        if drone.turns_remaining > 0:
            drone.turns_remaining -= 1

        if drone.turns_remaining <= 0:
            target = drone.current_edge_target
            if target is None:
                raise ValueError("There is no drone target zone")
            zone = self.state.graph.zones[target]

            if self._get_zone_occupancy(target) < zone.max_drones:
                drone.current_zone = target
                drone.current_edge_target = None

                if target == self.state.graph.end:
                    drone.status = DroneStatus.DELIVERED
                else:
                    drone.status = DroneStatus.WAITING

    def _apply_moves(self, moves: List[Move]) -> None:
        moves_by_drone = {m.drone_id: m for m in moves}

        for drone in self.state.drones.values():
            if drone.status == DroneStatus.IN_TRANSIT:
                self._progress_transit(drone)
            elif drone.status == DroneStatus.WAITING:
                move = moves_by_drone.get(drone.id)
                if move is not None and move.action == DroneStatus.IN_TRANSIT:
                    self._start_transit(drone, move.target)
                    self._progress_transit(drone)

    def run(self) -> List[Frame]:
        golden_path: List[str] = self.algorithm.calculate_path(
            self.state, self.state.graph.start)

        for d in self.state.drones.values():
            d.path = golden_path

        frames: List[Frame] = []
        MAX_TURNS = 1000

        while not self._all_delivered() and self.state.turn < MAX_TURNS:
            moves = self._calculate_moves()
            frames.append(Frame(state=self._snapshot(), moves=moves))
            self._apply_moves(moves)
            self.state.turn += 1
        frames.append(Frame(state=self._snapshot(), moves=[]))
        return frames
