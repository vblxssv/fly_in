from src.models.zone import Zone
from src.models.graph import Graph
from src.parser.parser import Parser


class GraphFactory:
    @staticmethod
    def load_from_file(path: str) -> Graph:
        parser = Parser()
        content = parser.parse(path)
        graph = Graph()

        for hub_data in content["hubs"]:
            meta = hub_data["meta"]
            zone_type = meta.get("zone", "normal")
            zone = Zone(
                name=hub_data["name"],
                pos=(hub_data["coords"]["x"], hub_data["coords"]["y"]),
                type=zone_type,
                max_drones=int(meta.get("max_drones", 1)),
                color=meta.get("color", "none")
            )
            graph.add_zone(zone)

        for conn_data in content["connections"]:
            meta = conn_data["meta"]
            capacity = int(meta.get("max_link_capacity", 1))
            graph.add_edge(
                source=conn_data["from"],
                target=conn_data["to"],
                capacity=capacity
            )
        return graph
