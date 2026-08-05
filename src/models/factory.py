from .drone import Drone, DroneStatus
from .graph import Graph
from .zone import Zone, ZoneType, ZoneColor
from .state import SimulationState
from .connection import Connection
from src.input import Line

from typing import Dict, List


class GraphFactory:
    @staticmethod
    def _build_zone(line: Line) -> Zone:
        name = line.arguments[1]
        pos = (int(line.arguments[2]), int(line.arguments[3]))

        zone_type = ZoneType(line.meta.get("zone", ZoneType.NORMAL.value))
        max_drones = int(line.meta.get("max_drones", 1))
        color = ZoneColor(line.meta.get("color", ZoneColor.BLUE.value))

        return Zone(name=name,
                    pos=pos,
                    type=zone_type,
                    max_drones=max_drones,
                    color=color)

    @staticmethod
    def _build_connection(line: Line) -> Connection:
        source, target = line.arguments[1].split("-")
        capacity = int(line.meta.get("max_link_capacity", 1))
        return Connection(
            zones=frozenset({source, target}),
            capacity=capacity,
        )

    @staticmethod
    def build(lines: List[Line]) -> Graph:
        graph = Graph()
        for line in lines:
            if (line.arguments[0] == "hub:"
               or line.arguments[0] == "start_hub:"
               or line.arguments[0] == "end_hub:"):
                graph.add_zone(GraphFactory._build_zone(line))
            elif line.arguments[0] == "connection:":
                graph.add_connection(GraphFactory._build_connection(line))
        return graph
