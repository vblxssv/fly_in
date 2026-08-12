from src.models import Drone, Graph, Layout

from typing import List
import arcade


class ArcadeRenderer:
    def play(self, graph: Graph, drones: List[Drone], layout: Layout) -> None:
        _SimulationWindow(graph, drones, layout)
        arcade.run()


class _SimulationWindow(arcade.Window):
    def __init__(self, graph: Graph,
                 drones: List[Drone], layout: Layout) -> None:
        super().__init__(layout.width, layout.height, "Fly-in simulation")
        arcade.set_background_color((228, 247, 247, 0))

        # Data
        self._graph = graph
        self._drones = drones
        self._layout = layout

        # Time
        self._turn_time = 1
        self._frame_index = 0
        self._elapsed_time = 0.0

    @property
    def _progress(self) -> float:
        return self._elapsed_time / self._turn_time

    def _draw_connections(self) -> None:
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

    # def _draw_zones(self) -> None:
    #     for zone_name, zone in self._graph.zones.items():
    #         x, y = self._layout.positions[zone_name]

    #         arcade.draw_circle_filled(
    #             x,
    #             y,
    #             20,
    #             zone.color.rgb
    #         )
    def _draw_zones(self) -> None:
        radius = 14

        for zone_name, zone in self._graph.zones.items():
            x, y = self._layout.positions[zone_name]

            arcade.draw_circle_filled(
                x,
                y,
                radius,
                zone.color.rgb,
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
        self._draw_connections()
        self._draw_zones()

    def _draw_drones(self) -> None:
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

    def on_draw(self) -> None:
        self.clear()
        self._draw_graph()
        self._draw_drones()
        # print(f"Current Frame {self._frame_index}")

    def _update_frame(self, delta_time: float) -> None:
        self._elapsed_time += delta_time
        if self._elapsed_time >= self._turn_time:
            self._frame_index += 1
            self._elapsed_time -= self._turn_time

    def on_update(self, delta_time: float) -> None:
        self._update_frame(delta_time)
