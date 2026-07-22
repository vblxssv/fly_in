from collections import deque
import os
import sys
import time
import subprocess
from typing import Dict, List, Optional, Set

from src.models.drone import Drone, DroneStatus
from src.models.frame import Frame
from src.models.move import Move
from src.models.zone import Zone
from src.models.state import SimulationState
from src.renderer.renderer import IRenderer


class ConsoleRenderer(IRenderer):
    STEP_DELAY = 0.6
    BOX_WIDTH = 16
    COL_GAP = 4

    def play(self, frames: List[Frame]) -> None:
        if not frames:
            print("Nothing to play: no frames recorded.")
            return

        total = len(frames)
        for i, frame in enumerate(frames, start=1):
            self._render_frame(
                frame.state, frame.moves, turn_label=f"{i}/{total}"
            )

        self._clear_screen()
        print("=== Simulation finished ===\n")
        self._print_zone_grid(frames[-1].state, highlight_zones=set())
        print()
        self._print_summary(frames[-1].state)

    def _render_frame(
        self,
        state: SimulationState,
        moves: List[Move],
        turn_label: Optional[str] = None,
    ) -> None:
        label = turn_label if turn_label is not None else str(state.turn)

        self._draw(state, moves, label, highlighted=False)
        time.sleep(self.STEP_DELAY)

        started = [m for m in moves if m.action == DroneStatus.IN_TRANSIT]
        if started:
            self._draw(state, moves, label, highlighted=True)
            time.sleep(self.STEP_DELAY)

    def _draw(
        self,
        state: SimulationState,
        moves: List[Move],
        label: str,
        highlighted: bool,
    ) -> None:
        started = [m for m in moves if m.action == DroneStatus.IN_TRANSIT]
        highlight_zones: Set[str] = (
            {m.target for m in started}
            if highlighted
            else set()
        )

        self._clear_screen()
        print(f"=== Turn {state.turn}  (frame {label}) ===\n")
        self._print_zone_grid(state, highlight_zones)
        print()
        self._print_moves_line(moves, active=highlighted)

    def _layout_columns(self, state: SimulationState) -> List[List[str]]:
        graph = state.graph
        visited: Dict[str, int] = {}

        if graph.start and graph.start in graph.zones:
            queue = deque([(graph.start, 0)])
            visited[graph.start] = 0
            while queue:
                name, depth = queue.popleft()
                for edge in graph.adjacency_list.get(name, []):
                    if edge.target not in visited:
                        visited[edge.target] = depth + 1
                        queue.append((edge.target, depth + 1))

        max_depth = max(visited.values(), default=-1)
        for name in graph.zones:
            if name not in visited:
                max_depth += 1
                visited[name] = max_depth

        columns: List[List[str]] = []
        for name, depth in sorted(
            visited.items(), key=lambda kv: (kv[1], kv[0])
        ):
            while len(columns) <= depth:
                columns.append([])
            columns[depth].append(name)

        return columns

    def _print_zone_grid(
        self, state: SimulationState, highlight_zones: Set[str]
    ) -> None:
        graph = state.graph
        columns = self._layout_columns(state)
        drones_by_zone = self._drones_by_zone(state)

        col_boxes: List[List[List[str]]] = [
            [
                self._zone_box(
                    graph.zones[name],
                    drones_by_zone.get(name, []),
                    name in highlight_zones,
                )
                for name in col
            ]
            for col in columns
        ]

        max_rows = max((len(c) for c in col_boxes), default=0)
        gap = " " * self.COL_GAP
        box_height = 3  # Вернули корректную высоту (верх, середина, низ)

        for row in range(max_rows):
            for line_idx in range(box_height):
                pieces: List[str] = []
                for boxes in col_boxes:
                    if row < len(boxes):
                        pieces.append(boxes[row][line_idx])
                    else:
                        pieces.append(" " * (self.BOX_WIDTH + 2))
                print(gap.join(pieces))
            print()

    def _zone_box(
        self, zone: Zone, drones: List[Drone], highlighted: bool
    ) -> List[str]:
        width = self.BOX_WIDTH
        name = (
            zone.name
            if len(zone.name) <= width - 2
            else zone.name[: width - 5] + "..."
        )
        marker = {
            "restricted": "*",
            "priority": "!",
            "blocked": "#",
        }.get(zone.type.value, "")

        title = f" {name}{marker} ".center(width)

        corner = "*" if highlighted else "+"
        top = corner + "-" * width + corner
        mid = "|" + title + "|"
        bottom = corner + "-" * width + corner  # Восстановили нижнюю границу

        if highlighted:
            mid = "|" + title[:-2] + "<<|"

        return [top, mid, bottom]

    def _print_moves_line(self, moves: List[Move], active: bool) -> None:
        started = [m for m in moves if m.action == DroneStatus.IN_TRANSIT]
        if not started:
            print("No drones starting a new transit this turn.")
            return

        parts = [f"D{m.drone_id} -> {m.target}" for m in started]
        prefix = "Moving now: " if active else "About to move: "
        print(prefix + ", ".join(parts))

    def _print_summary(self, state: SimulationState) -> None:
        delivered = [
            d for d in state.drones.values()
            if d.status == DroneStatus.DELIVERED
        ]
        print(
            f"Delivered {len(delivered)}/{len(state.drones)} drones "
            f"in {state.turn} turns."
        )

    @staticmethod
    def _drones_by_zone(
        state: SimulationState,
    ) -> Dict[str, List[Drone]]:
        result: Dict[str, List[Drone]] = {}
        for d in state.drones.values():
            if d.status in (DroneStatus.WAITING, DroneStatus.DELIVERED):
                result.setdefault(d.current_zone, []).append(d)
        return result

    @staticmethod
    def _drones_in_flight_by_edge(
        state: SimulationState,
    ) -> Dict[frozenset[str], List[Drone]]:
        result: Dict[frozenset[str], List[Drone]] = {}
        for d in state.drones.values():
            if (
                d.status == DroneStatus.IN_TRANSIT
                and d.current_edge_target is not None
            ):
                key = frozenset({d.current_zone, d.current_edge_target})
                result.setdefault(key, []).append(d)
        return result

    @staticmethod
    def _drone_by_id(state: SimulationState, drone_id: int) -> Drone:
        if drone_id in state.drones:
            return state.drones[drone_id]
        raise ValueError(f"No drone with id {drone_id}")

    @staticmethod
    def _clear_screen() -> None:
        command = "cls" if os.name == "nt" else "clear"
        subprocess.run(command, shell=True)
        sys.stdout.flush()
