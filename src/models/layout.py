from .graph import Graph

from typing import Dict, Tuple


class Layout:
    def __init__(self, graph: Graph, width: int, height: int) -> None:
        self._positions = self._build_coordinates(graph, width, height)

    @staticmethod
    def _build_coordinates(
        graph: Graph,
        width: int,
        height: int,
    ) -> Dict[str, Tuple[int, int]]:
        zones = list(graph.zones.values())

        xs = [zone.pos[0] for zone in zones]
        ys = [zone.pos[1] for zone in zones]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        margin = 80

        usable_width = width - 2 * margin
        usable_height = height - 2 * margin

        def scale(
            value: float,
            source_min: float,
            source_max: float,
            target_min: float,
            target_max: float,
        ) -> float:
            if source_max == source_min:
                return (target_min + target_max) / 2

            return target_min + (
                (value - source_min)
                / (source_max - source_min)
                * (target_max - target_min)
            )

        positions: Dict[str, Tuple[int, int]] = {}

        for name, zone in graph.zones.items():
            x = scale(
                zone.pos[0],
                min_x,
                max_x,
                margin,
                margin + usable_width,
            )
            y = scale(
                zone.pos[1],
                min_y,
                max_y,
                margin,
                margin + usable_height,
            )

            positions[name] = (int(x), int(y))

        return positions

    @property
    def positions(self) -> Dict[str, Tuple[int, int]]:
        return self._positions
