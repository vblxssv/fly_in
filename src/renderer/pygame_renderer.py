from collections import deque
from math import cos, sin, pi, ceil
from typing import Dict, List, Tuple

import pygame

from src.models.frame import Frame
from src.models.state import SimulationState
from src.models.move import Move
from src.models.drone import DroneStatus
from src.renderer.renderer import IRenderer


class PyGameRenderer(IRenderer):

    WINDOW_SIZE = (1300, 900)
    BACKGROUND = (18, 18, 22)
    ZONE_COLOR = (70, 130, 200)
    ZONE_COLOR_BLOCKED = (90, 90, 90)
    ZONE_COLOR_RESTRICTED = (200, 120, 60)
    ZONE_COLOR_PRIORITY = (120, 200, 120)
    EDGE_COLOR = (90, 90, 100)
    EDGE_COLOR_ACTIVE = (230, 200, 80)
    DRONE_COLOR = (240, 240, 240)
    DRONE_COLOR_DELIVERED = (100, 220, 140)
    TEXT_COLOR = (230, 230, 230)

    ZONE_RADIUS = 34
    DRONE_RADIUS = 6
    MARGIN = 90

    STEPS_PER_TURN = 24  # animation sub-steps used to interpolate one turn
    FRAME_MS = 30  # ms per animation sub-step -> ~0.7s per turn at 24 steps

    def __init__(self) -> None:
        self._screen = None
        self._font = None
        self._small_font = None
        self._clock = None

    # ------------------------------------------------------------------ #
    # IRenderer interface
    # ------------------------------------------------------------------ #

    def play(self, frames: List[Frame]) -> None:
        if not frames:
            return

        pygame.init()
        self._screen = pygame.display.set_mode(self.WINDOW_SIZE)
        pygame.display.set_caption("Fly-in simulation")
        self._font = pygame.font.SysFont("consolas", 16)
        self._small_font = pygame.font.SysFont("consolas", 13)
        self._clock = pygame.time.Clock()

        positions = self._layout_positions(frames[0].state)

        try:
            for i in range(len(frames) - 1):
                if not self._play_transition(frames[i], frames[i + 1], positions, i + 1, len(frames)):
                    return  # window closed early

            self._render_static(frames[-1], positions, len(frames), len(frames))
            self._wait_for_close()
        finally:
            pygame.quit()

    # ------------------------------------------------------------------ #
    # Layout: same BFS-columns idea as the console renderer, mapped to px
    # ------------------------------------------------------------------ #

    def _layout_positions(self, state: SimulationState) -> Dict[str, Tuple[int, int]]:
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
        for name, depth in sorted(visited.items(), key=lambda kv: (kv[1], kv[0])):
            while len(columns) <= depth:
                columns.append([])
            columns[depth].append(name)

        width, height = self.WINDOW_SIZE
        usable_w = width - 2 * self.MARGIN
        usable_h = height - 2 * self.MARGIN
        n_cols = max(1, len(columns))

        positions: Dict[str, Tuple[int, int]] = {}
        for col_idx, col in enumerate(columns):
            x = self.MARGIN + (usable_w * col_idx // max(1, n_cols - 1)) if n_cols > 1 else width // 2
            n_rows = max(1, len(col))
            for row_idx, name in enumerate(col):
                y = self.MARGIN + (usable_h * row_idx // max(1, n_rows - 1)) if n_rows > 1 else height // 2
                positions[name] = (x, y)

        return positions

    # ------------------------------------------------------------------ #
    # Transit progress helpers
    # ------------------------------------------------------------------ #

    def _compute_transit_fractions(
        self, state: SimulationState, moves: List[Move]
    ) -> Dict[int, Tuple[float, float, str, str]]:
        """
        For every drone moving this turn (whether it is already IN_TRANSIT
        going into the turn, or it starts transit THIS turn per `moves`),
        compute the overall fraction of the edge covered *before* this
        turn's update (frac_start) and *after* this turn's update
        (frac_end). This lets a multi-turn transit (e.g. a 2-turn
        restricted zone) animate as one continuous move split across
        turns, and lets a 1-turn transit (normal/priority zone) still
        animate fully during its single turn -- even though the engine
        may resolve it to WAITING-at-destination within that same turn's
        internal update, before the *next* frame's snapshot is taken.
        """
        fractions: Dict[int, Tuple[float, float, str, str]] = {}
        moves_by_drone = {m.drone_id: m for m in moves if m.action == DroneStatus.IN_TRANSIT}

        for drone in state.drones:
            if drone.status == DroneStatus.IN_TRANSIT and drone.current_edge_target is not None:
                # Already mid-transit going into this turn (multi-turn edge).
                target = drone.current_edge_target
                zone = state.graph.zones[target]
                total_duration = max(1, ceil(zone.type.cost))

                elapsed_before = max(0, min(total_duration, total_duration - drone.turns_remaining))
                elapsed_after = min(total_duration, elapsed_before + 1)

                fractions[drone.id] = (
                    elapsed_before / total_duration,
                    elapsed_after / total_duration,
                    drone.current_zone,
                    target,
                )
            elif drone.status == DroneStatus.WAITING:
                # Not moving yet in this snapshot -- but might start this turn.
                move = moves_by_drone.get(drone.id)
                if move is None:
                    continue

                target = move.target
                zone = state.graph.zones[target]
                total_duration = max(1, ceil(zone.type.cost))
                elapsed_after = min(total_duration, 1) / total_duration

                fractions[drone.id] = (
                    0.0,
                    elapsed_after,
                    drone.current_zone,
                    target,
                )

        return fractions

    # ------------------------------------------------------------------ #
    # Animating one turn: interpolate from frame -> next_frame
    # ------------------------------------------------------------------ #

    def _play_transition(
        self,
        frame: Frame,
        next_frame: Frame,
        positions: Dict[str, Tuple[int, int]],
        turn_index: int,
        total_turns: int,
    ) -> bool:
        started = [m for m in frame.moves if m.action == DroneStatus.IN_TRANSIT]
        transit_fracs = self._compute_transit_fractions(frame.state, frame.moves)

        for step in range(self.STEPS_PER_TURN):
            if not self._pump_events():
                return False

            progress = step / (self.STEPS_PER_TURN - 1)
            self._screen.fill(self.BACKGROUND)
            self._draw_zones(frame.state, positions, highlight={m.target for m in started} if progress > 0.05 else set())
            self._draw_edges(frame.state, positions, highlight_edges={
                frozenset({self._drone_zone(frame.state, m.drone_id), m.target}) for m in started
            })
            self._draw_drones(frame.state, positions, transit_fracs, progress)
            self._draw_hud(frame.state, turn_index, total_turns, started)

            pygame.display.flip()
            self._clock.tick(1000 // self.FRAME_MS)

        return True

    def _render_static(self, frame: Frame, positions: Dict[str, Tuple[int, int]], turn_index: int, total_turns: int) -> None:
        self._pump_events()
        self._screen.fill(self.BACKGROUND)
        self._draw_zones(frame.state, positions, highlight=set())
        self._draw_edges(frame.state, positions, highlight_edges=set())
        self._draw_drones(frame.state, positions, {}, 0.0)
        self._draw_hud(frame.state, turn_index, total_turns, [])
        self._draw_summary(frame.state)
        pygame.display.flip()

    # ------------------------------------------------------------------ #
    # Drawing helpers
    # ------------------------------------------------------------------ #

    def _draw_zones(self, state: SimulationState, positions, highlight: set) -> None:
        drones_by_zone = self._drones_in_zone(state)

        for name, zone in state.graph.zones.items():
            x, y = positions[name]
            color = {
                "blocked": self.ZONE_COLOR_BLOCKED,
                "restricted": self.ZONE_COLOR_RESTRICTED,
                "priority": self.ZONE_COLOR_PRIORITY,
            }.get(zone.type.value, self.ZONE_COLOR)

            radius = self.ZONE_RADIUS + (6 if name in highlight else 0)
            width = 0 if name not in highlight else 3
            pygame.draw.circle(self._screen, color, (x, y), self.ZONE_RADIUS)
            if name in highlight:
                pygame.draw.circle(self._screen, self.EDGE_COLOR_ACTIVE, (x, y), radius, width=4)

            count = len(drones_by_zone.get(name, []))
            label = self._font.render(name, True, self.TEXT_COLOR)
            occ = self._small_font.render(f"{count}/{zone.max_drones}", True, self.TEXT_COLOR)
            self._screen.blit(label, label.get_rect(center=(x, y - 10)))
            self._screen.blit(occ, occ.get_rect(center=(x, y + 10)))

    def _draw_edges(self, state: SimulationState, positions, highlight_edges: set) -> None:
        graph = state.graph
        in_flight = self._drones_in_flight_by_edge(state)
        seen = set()

        for source in graph.adjacency_list:
            for edge in graph.adjacency_list[source]:
                key = frozenset({source, edge.target})
                if key in seen:
                    continue
                seen.add(key)

                a, b = sorted(key)
                if a not in positions or b not in positions:
                    continue

                color = self.EDGE_COLOR_ACTIVE if key in highlight_edges else self.EDGE_COLOR
                pygame.draw.line(self._screen, color, positions[a], positions[b], width=3 if key in highlight_edges else 2)

                occupancy = len(in_flight.get(key, []))
                mid = ((positions[a][0] + positions[b][0]) // 2, (positions[a][1] + positions[b][1]) // 2)
                label = self._small_font.render(f"{occupancy}/{edge.capacity}", True, self.TEXT_COLOR)
                self._screen.blit(label, label.get_rect(center=mid))

    def _draw_drones(
        self,
        state: SimulationState,
        positions,
        transit_fracs: Dict[int, Tuple[float, float, str, str]],
        progress: float,
    ) -> None:
        # A drone counts as "moving this frame" if it has a transit fraction
        # entry -- this includes drones whose `status` is still WAITING in
        # this snapshot but which start transit THIS turn (their status
        # only flips to IN_TRANSIT in the *next* snapshot). Relying on
        # `status == IN_TRANSIT` alone would miss exactly that case and
        # draw them as stationary for the whole turn, then jump them to
        # the destination on the next frame (teleport).
        moving_ids = set(transit_fracs.keys())

        # Group stationary drones per zone to spread them out visually.
        stationary_by_zone: Dict[str, List] = {}
        for drone in state.drones:
            if drone.id in moving_ids:
                continue
            if drone.status in (DroneStatus.WAITING, DroneStatus.DELIVERED):
                stationary_by_zone.setdefault(drone.current_zone, []).append(drone)

        for zone_name, drones in stationary_by_zone.items():
            if zone_name not in positions:
                continue
            cx, cy = positions[zone_name]
            self._scatter_draw(drones, cx, cy)

        for drone in state.drones:
            frac_info = transit_fracs.get(drone.id)
            if frac_info is None:
                continue

            frac_start, frac_end, src, dst = frac_info
            if src not in positions or dst not in positions:
                continue

            # Interpolate only across the slice of the edge covered THIS
            # turn (frac_start -> frac_end), not the whole src->dst span.
            overall_frac = frac_start + (frac_end - frac_start) * progress

            x1, y1 = positions[src]
            x2, y2 = positions[dst]
            x = x1 + (x2 - x1) * overall_frac
            y = y1 + (y2 - y1) * overall_frac
            pygame.draw.circle(self._screen, self.DRONE_COLOR, (int(x), int(y)), self.DRONE_RADIUS)
            label = self._small_font.render(f"D{drone.id}", True, self.DRONE_COLOR)
            self._screen.blit(label, label.get_rect(center=(int(x), int(y) - 14)))

    def _scatter_draw(self, drones: List, cx: int, cy: int) -> None:
        n = len(drones)
        for i, drone in enumerate(drones):
            if n == 1:
                ox, oy = 0, 0
            else:
                angle = (2 * pi * i) / n
                r = self.ZONE_RADIUS * 0.5
                ox, oy = int(r * cos(angle)), int(r * sin(angle))
            color = self.DRONE_COLOR_DELIVERED if drone.status == DroneStatus.DELIVERED else self.DRONE_COLOR
            pygame.draw.circle(self._screen, color, (cx + ox, cy + oy), self.DRONE_RADIUS)

    def _draw_hud(self, state: SimulationState, turn_index: int, total_turns: int, started: List[Move]) -> None:
        title = self._font.render(f"Turn {state.turn}  (frame {turn_index}/{total_turns})", True, self.TEXT_COLOR)
        self._screen.blit(title, (16, 12))

        if started:
            parts = ", ".join(f"D{m.drone_id}->{m.target}" for m in started)
            moving = self._small_font.render(f"Moving: {parts}", True, self.EDGE_COLOR_ACTIVE)
            self._screen.blit(moving, (16, self.WINDOW_SIZE[1] - 28))

    def _draw_summary(self, state: SimulationState) -> None:
        delivered = sum(1 for d in state.drones if d.status == DroneStatus.DELIVERED)
        text = self._font.render(
            f"Simulation finished: {delivered}/{len(state.drones)} delivered in {state.turn} turns. "
            f"Close window to exit.",
            True,
            self.TEXT_COLOR,
        )
        self._screen.blit(text, (16, self.WINDOW_SIZE[1] - 28))

    # ------------------------------------------------------------------ #
    # Event handling
    # ------------------------------------------------------------------ #

    def _pump_events(self) -> bool:
        """Process the event queue; return False if the user closed the window."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
        return True

    def _wait_for_close(self) -> None:
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    waiting = False
            self._clock.tick(30)

    # ------------------------------------------------------------------ #
    # Data helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _drones_in_zone(state: SimulationState) -> Dict[str, List]:
        result: Dict[str, List] = {}
        for d in state.drones:
            if d.status in (DroneStatus.WAITING, DroneStatus.DELIVERED):
                result.setdefault(d.current_zone, []).append(d)
        return result

    @staticmethod
    def _drones_in_flight_by_edge(state: SimulationState) -> Dict[frozenset, List]:
        result: Dict[frozenset, List] = {}
        for d in state.drones:
            if d.status == DroneStatus.IN_TRANSIT and d.current_edge_target is not None:
                key = frozenset({d.current_zone, d.current_edge_target})
                result.setdefault(key, []).append(d)
        return result

    @staticmethod
    def _drone_zone(state: SimulationState, drone_id: int) -> str:
        for d in state.drones:
            if d.id == drone_id:
                return d.current_zone
        raise ValueError(f"No drone with id {drone_id}")