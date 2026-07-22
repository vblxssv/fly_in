from src.algorithm.algorithm import IAlgorithm
from src.models.state import SimulationState
from src.models.frame import Frame
from typing import List, Dict
from src.models.move import Move
from src.models.drone import DroneStatus, Drone
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

    def _calculate_moves(self) -> List[Move]:
        reserved_edges: Dict[frozenset[str], int] = {}  # edge - drones
        graph = self.state.graph
        moves: List[Move] = []

        # ========= Основной цикл ==========
        for drone in self.state.drones.values():
            if drone.status != DroneStatus.WAITING:
                continue

            try:
                next_zone = drone.get_next_zone()
            except ValueError:
                continue

            edge_key = frozenset({drone.current_zone, next_zone})
            if (graph.get_edge(drone.current_zone, next_zone).capacity
                > self._get_edge_occupancy(drone.current_zone, next_zone) +
                    reserved_edges.get(edge_key, 0)):

                reserved_edges[edge_key] = reserved_edges.get(edge_key, 0) + 1
                moves.append(Move(drone_id=drone.id,
                                  action=DroneStatus.IN_TRANSIT,
                                  target=next_zone))
            else:
                # ВОТ СЮДА РЕПЛАНИНГ ВЬЕБАТЬ ПОТОМ
                moves.append(Move(drone_id=drone.id,
                                  action=DroneStatus.WAITING,
                                  target=drone.current_zone))
        # ==================================
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
