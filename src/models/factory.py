from .graph import Graph
from .zone import Zone, ZoneRole, ZoneType, ZoneColor
from .connection import Connection
from src.input import Content, ConnectionLine, HubLine


class GraphFactory:
    @staticmethod
    def _build_zone(line: HubLine) -> Zone:
        zonerole = ZoneRole(line.hub_type)
        zonetype = ZoneType(line.meta.get("zone", ZoneType.NORMAL.value))
        zonecolor = ZoneColor(line.meta.get("color", ZoneColor.NONE.value))
        zonecapacity = line.meta.get("max_drones", 1)

        return Zone(name=line.name,
                    pos=(line.x, line.y),
                    type=zonetype,
                    role=zonerole,
                    max_drones=zonecapacity,
                    color=zonecolor)

    @staticmethod
    def _build_connection(line: ConnectionLine) -> Connection:
        capacity = line.meta.get("max_link_capacity", 1)
        return Connection(zones=frozenset([line.from_zone, line.to_zone]),
                          capacity=capacity)

    @staticmethod
    def build(content: Content) -> Graph:
        graph = Graph()
        for line in content.lines:
            if isinstance(line, ConnectionLine):
                try:
                    connection = GraphFactory._build_connection(line)
                    graph.add_connection(connection)
                except ValueError as e:
                    raise ValueError(f"Line {line.line}: {e}")
            elif isinstance(line, HubLine):
                try:
                    zone = GraphFactory._build_zone(line)
                    graph.add_zone(zone)
                except ValueError as e:
                    raise ValueError(f"Line {line.line}: {e}")
        return graph
