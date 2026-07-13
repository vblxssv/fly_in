from src.models.zone import Zone
from src.models.graph import Graph
from src.models.drone import Drone, DroneStatus
from typing import List, Dict, Any


class GraphFactory:
    @staticmethod
    def build(content: Dict[Any, Any]) -> Graph:
        graph = Graph()

        for hub_data in content["hubs"]:
            meta = hub_data["meta"]
            zone = Zone(
                name=hub_data["name"],
                pos=(hub_data["coords"]["x"], hub_data["coords"]["y"]),
                type=meta.get("zone", "normal"),
                max_drones=int(meta.get("max_drones", 1)),
                color=meta.get("color", "none"),
            )
            graph.add_zone(zone)

            if hub_data["type"] == "start_hub":
                graph.start = zone.name
            elif hub_data["type"] == "end_hub":
                graph.end = zone.name

        for conn_data in content["connections"]:
            meta = conn_data["meta"]
            graph.add_edge(
                source=conn_data["from"],
                target=conn_data["to"],
                capacity=int(meta.get("max_link_capacity", 1)),
            )

        return graph


class DroneFactory:
    @staticmethod
    def create_drones(amount: int, start_zone: str) -> List[Drone]:
        drones = [
            Drone(id=i, status=DroneStatus.WAITING, current_zone=start_zone)
            for i in range(1, amount + 1)
        ]
        return drones
