from .drone import Drone, DroneStatus
from .graph import Graph
from .zone import Zone, ZoneType, ZoneColor
from .state import SimulationState
from src.input import Line

from typing import Dict, List


class StateFactory:
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
    def _build_drones(amount: int, start_zone: str) -> Dict[int, Drone]:
        return {
            i: Drone(
                id=i,
                status=DroneStatus.WAITING,
                current_zone=start_zone
            )
            for i in range(1, amount + 1)
        }

    @staticmethod
    def build(lines: List[Line]) -> SimulationState:
        zone_lines: List[Line] = list(
            filter(lambda line: line.arguments[0] in
                   ["hub:", "start_hub:", "end_hub:"], lines))
        connection_lines: List[Line] = list(
            filter(lambda line: line.arguments[0] == "connection:", lines))
        nb_drones_line: Line = next(
            (line for line in lines if line.arguments[0] == "nb_drones:"))
        nb_drones: int = int(nb_drones_line.arguments[1])

        graph: Graph = Graph()
        for line in zone_lines:
            graph.add_zone(StateFactory._build_zone(line))
            if line.arguments[0] == "start_hub:":
                graph.start = line.arguments[1]
            elif line.arguments[0] == "end_hub:":
                graph.end = line.arguments[1]
        for line in connection_lines:
            source, target = line.arguments[1].split("-")
            graph.add_edge(
                source,
                target,
                int(line.meta.get("max_link_capacity", 1))
            )
        drones = StateFactory._build_drones(nb_drones, graph.start)
        return SimulationState(graph=graph,
                               turn=0,
                               drones=drones)
