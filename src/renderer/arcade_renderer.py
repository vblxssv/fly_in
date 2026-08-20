from src.models import Drone, Graph, Layout

from typing import List
import arcade


class ArcadeRenderer:
    """Launch an Arcade-based graphical simulation renderer."""

    def play(self, graph: Graph, drones: List[Drone], layout: Layout) -> None:
        """Open the simulation window and start the Arcade event loop."""
        _SimulationWindow(graph, drones, layout)
        arcade.run()


class _SimulationWindow(arcade.Window):
    """Render and control playback of one planned drone simulation."""

    def __init__(
        self,
        graph: Graph,
        drones: List[Drone],
        layout: Layout,
    ) -> None:
        """Create a window with simulation data and playback state."""
        super().__init__(layout.width, layout.height, "Fly-in simulation")
        arcade.set_background_color((228, 247, 247, 0))

        # Data
        self._graph = graph
        self._drones = drones
        self._layout = layout

        # Time / speed
        self._min_speed = 0.2   # turns/sec
        self._max_speed = 10.0  # turns/sec
        self._speed = 1.0       # turns/sec
        self._speed_step = 0.2

        self._frame_index = 0
        self._elapsed_time = 0.0

        # Total turns
        self._total_turns = max(len(d.path) for d in self._drones) - 1

        # Simulation state
        self._paused = False
        self._finished = False

        # Statistics
        self._moved_per_turn = self._compute_moved_per_turn()
        self._avg_turns_per_drone = self._compute_avg_turns_per_drone()

    def _compute_moved_per_turn(self) -> List[int]:
        """Count drones that change position during each simulation turn."""
        moved = []

        for turn in range(self._total_turns):
            count = 0

            for drone in self._drones:
                if turn + 1 >= len(drone.path):
                    continue

                start = drone.path[turn]
                end = drone.path[turn + 1]

                if start != end:
                    count += 1

            moved.append(count)

        return moved

    def _compute_avg_turns_per_drone(self) -> float:
        """Return the average path length in turns across all drones."""
        if not self._drones:
            return 0.0

        total = sum(len(drone.path) - 1 for drone in self._drones)

        return total / len(self._drones)

    @property
    def _turn_time(self) -> float:
        """Return the duration of one turn at the current playback speed."""
        return 1.0 / self._speed

    @property
    def _current_turn(self) -> int:
        """Return the one-based turn number displayed in the HUD."""
        return min(
            self._frame_index + 1,
            self._total_turns,
        )

    @property
    def _moved_this_turn(self) -> int:
        """Return how many drones move during the displayed turn."""
        if not self._moved_per_turn:
            return 0

        index = min(
            self._frame_index,
            self._total_turns - 1,
        )

        return self._moved_per_turn[index]

    @property
    def _progress(self) -> float:
        """Return fractional progress through the current turn."""
        return self._elapsed_time / self._turn_time

    def _draw_connections(self) -> None:
        """Draw every graph connection as a line between zone positions."""
        for connection in self._graph.connections.keys():
            zone_a, zone_b = connection

            x1, y1 = self._layout.positions[zone_a]
            x2, y2 = self._layout.positions[zone_b]

            arcade.draw_line(
                x1,
                y1,
                x2,
                y2,
                arcade.color.GRAY,
                3,
            )

    def _draw_zones(self) -> None:
        """Draw all zones with their configured colors and labels."""
        radius = 14

        for zone_name, zone in self._graph.zones.items():
            x, y = self._layout.positions[zone_name]

            arcade.draw_circle_filled(
                x,
                y,
                radius,
                zone.rgb,
            )

            arcade.draw_circle_outline(
                x,
                y,
                radius,
                arcade.color.BLACK,
                2,
            )

            arcade.draw_text(
                zone_name,
                x,
                y + 30,
                arcade.color.BLACK,
                12,
                anchor_x="center",
                rotation=45,
            )

    def _draw_graph(self) -> None:
        """Draw the static graph connections and zones."""
        self._draw_connections()
        self._draw_zones()

    def _draw_drones(self) -> None:
        """Draw drones interpolated between positions for the current turn."""
        progress = self._progress

        for drone in self._drones:
            if self._frame_index + 1 >= len(drone.path):
                continue

            start = drone.path[self._frame_index]
            end = drone.path[self._frame_index + 1]

            x = start[0] + (end[0] - start[0]) * progress
            y = start[1] + (end[1] - start[1]) * progress

            size = 14

            arcade.draw_triangle_filled(
                x,
                y + size,
                x - size,
                y - size,
                x + size,
                y - size,
                drone.color,
            )

            arcade.draw_triangle_outline(
                x,
                y + size,
                x - size,
                y - size,
                x + size,
                y - size,
                arcade.color.BLACK,
            )

    def _draw_hud(self) -> None:
        """Draw playback statistics and controls status in the window."""
        lines = [
            f"Turn: {self._current_turn}/{self._total_turns}",
            f"Moved this turn: {self._moved_this_turn}/{len(self._drones)}",
            f"Avg turns/drone: {self._avg_turns_per_drone:.2f}",
            f"Speed: {self._speed:.1f} turn/s",
        ]

        if self._paused:
            lines.append("[PAUSE]")

        y = self.height - 25

        for line in lines:
            arcade.draw_text(
                line,
                self.width - 15,
                y,
                arcade.color.BLACK,
                14,
                anchor_x="right",
            )

            y -= 20

    def on_draw(self) -> None:
        """Render the current simulation frame."""
        self.clear()

        self._draw_graph()
        self._draw_drones()
        self._draw_hud()

    def _update_frame(self, delta_time: float) -> None:
        """Advance playback according to elapsed time and current speed."""
        if self._paused or self._finished:
            return

        self._elapsed_time += delta_time

        while self._elapsed_time >= self._turn_time:
            self._elapsed_time -= self._turn_time
            self._frame_index += 1

            if self._frame_index >= self._total_turns:
                self._frame_index = self._total_turns
                self._elapsed_time = 0.0
                self._finished = True
                break

    def on_update(self, delta_time: float) -> None:
        """Handle Arcade's periodic update callback."""
        self._update_frame(delta_time)

    def _restart(self) -> None:
        """Reset playback to the initial simulation state."""
        self._frame_index = 0
        self._elapsed_time = 0.0
        self._paused = False
        self._finished = False

    def _increase_speed(self) -> None:
        """Increase playback speed while preserving turn progress."""
        old_progress = self._progress
        self._speed = min(self._max_speed, self._speed + self._speed_step)
        self._elapsed_time = old_progress * self._turn_time

    def _decrease_speed(self) -> None:
        """Decrease playback speed while preserving turn progress."""
        old_progress = self._progress
        self._speed = max(self._min_speed, self._speed - self._speed_step)
        self._elapsed_time = old_progress * self._turn_time

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Handle pause, restart, close, and speed keyboard controls."""
        if key == arcade.key.SPACE:
            if not self._finished:
                self._paused = not self._paused

        elif key == arcade.key.R:
            self._restart()

        elif key == arcade.key.ESCAPE:
            self.close()

        elif key == arcade.key.UP:
            self._increase_speed()

        elif key == arcade.key.DOWN:
            self._decrease_speed()
