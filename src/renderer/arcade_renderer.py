import arcade
from src.renderer.renderer import IRenderer
from src.models.frame import Frame
from src.models.graph import Graph
from src.models.drone import Drone, DroneStatus
from typing import List, Dict, Tuple, Set
from src.renderer.animation_drone import AnimDrone
import math
import random


class ArcadeRenderer(IRenderer):
    def play(self, frames: List[Frame]) -> None:
        _SimulationWindow(frames)
        arcade.run()


class _SimulationWindow(arcade.Window):
    def __init__(self, frames: List[Frame]) -> None:
        super().__init__(1600, 900, "Fly-in simulation")
        arcade.set_background_color((228, 247, 247, 0))
        # arcade.set_background_color(arcade.color.BLACK)

        # Data
        self._frames = frames
        self._positions = self._screen_positions(self._frames[0].state.graph)

        # Time
        self._turn_time = 0.5
        self._frame_index = 0
        self._elapsed_time = 0

        # Visual
        self._ZONE_RADIUS = 15

        # Animation
        self._anim_drones: Dict[int, AnimDrone] = {}
        self._start_turn(self._frames[0])
        self._is_paused = False

    @property
    def finished(self) -> bool:
        return self._frame_index == len(self._frames) - 1

    def _screen_positions(self, graph: Graph) -> Dict[str, Tuple[int, int]]:
        zones = list(graph.zones.values())
        xs = [z.pos[0] for z in zones]
        ys = [z.pos[1] for z in zones]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        margin = 80
        usable_w = self.width - 2 * margin
        usable_h = self.height - 2 * margin

        def scale(
            value: float,
            lo: float,
            hi: float,
            out_lo: float,
            out_hi: float,
        ) -> float:
            if hi == lo:
                return (out_lo + out_hi) / 2
            return out_lo + (value - lo) / (hi - lo) * (out_hi - out_lo)

        positions: Dict[str, Tuple[int, int]] = {}
        for name, zone in graph.zones.items():
            x = scale(zone.pos[0], min_x, max_x, margin, margin + usable_w)
            y = scale(zone.pos[1], min_y, max_y, margin, margin + usable_h)
            positions[name] = (int(x), int(y))

        return positions

    def _draw_zones(self, graph: Graph) -> None:
        for name, zone in graph.zones.items():
            x, y = self._positions[name]

            arcade.draw_circle_filled(x, y, self._ZONE_RADIUS, zone.color.rgb)
            arcade.draw_circle_outline(
                x, y, self._ZONE_RADIUS, arcade.color.BLACK)

    def _draw_edges(self, graph: Graph) -> None:
        seen: Set[frozenset[str]] = set()

        for source in graph.adjacency_list:
            for edge in graph.adjacency_list[source]:
                key = frozenset({source, edge.target})
                if key in seen:
                    continue
                seen.add(key)

                a, b = sorted(key)
                x1, y1 = self._positions[a]
                x2, y2 = self._positions[b]

                arcade.draw_line(x1, y1, x2, y2, arcade.color.BLACK,
                                 line_width=2)

    def _draw_graph(self, graph: Graph) -> None:
        self._draw_edges(graph)
        self._draw_zones(graph)

    def _draw_drone(self, x: float, y: float,
                    color: tuple[int, int, int]
                    | arcade.types.Color = arcade.color.BLACK) -> None:
        size = 20
        x1 = x
        y1 = y + size
        x2 = x - size * math.sqrt(3) / 2
        y2 = y - size / 2
        x3 = x + size * math.sqrt(3) / 2
        y3 = y - size / 2

        arcade.draw_triangle_filled(x1, y1, x2, y2, x3, y3, color)
        arcade.draw_triangle_outline(x1, y1, x2, y2, x3, y3,
                                     arcade.color.BLACK)

    def _draw_drones(self, drones: List[Drone]) -> None:
        for drone in drones:
            if drone.id in self._anim_drones.keys():
                x, y = self._anim_drones[drone.id].current_pos
            else:
                x, y = self._positions[drone.current_zone]

            random.seed(drone.id)
            drone_color: tuple[int, int, int] = (
                random.randint(50, 220),
                random.randint(50, 220),
                random.randint(50, 220)
            )
            self._draw_drone(x, y, drone_color)

    def on_draw(self) -> None:
        self.clear()

        frame = self._frames[self._frame_index]
        self._draw_graph(frame.state.graph)
        self._draw_drones(list(frame.state.drones.values()))

    def _update_frame_index(self, delta_time: float) -> None:
        self._elapsed_time += delta_time

        if self._elapsed_time >= self._turn_time:
            self._elapsed_time -= self._turn_time

            if self._frame_index < len(self._frames) - 1:
                self._frame_index += 1
                self._start_turn(self._frames[self._frame_index])

    def _start_turn(self, frame: Frame) -> None:

        for anim in self._anim_drones.values():
            anim.advance_turn()
        for key in list(self._anim_drones.keys()):
            if frame.state.drones[key].status != DroneStatus.IN_TRANSIT:
                del self._anim_drones[key]
        for move in frame.moves:
            if move.action == DroneStatus.IN_TRANSIT:
                drone: Drone = frame.state.drones[move.drone_id]
                if not drone:
                    raise ValueError("Error: didnt find drone")
                self._anim_drones[move.drone_id] = AnimDrone(
                    move.drone_id, self._positions[drone.current_zone],
                    self._positions[move.target],
                    frame.state.graph.zones[drone.get_next_zone()].type.cost
                )

    def on_update(self, delta_time: float) -> None:
        if self._is_paused:
            return
        if not self.finished:
            self._update_frame_index(delta_time)
        for anim in self._anim_drones.values():
            anim.advance_time(delta_time, self._turn_time)

    def reset(self) -> None:
        self._frame_index = 0
        self._elapsed_time = 0
        self._anim_drones.clear()
        self._start_turn(self._frames[0])
        self._is_paused = False

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.ESCAPE:
            arcade.close_window()
        elif symbol == arcade.key.R:
            self.reset()
        elif symbol == arcade.key.SPACE:
            self._is_paused = not self._is_paused
