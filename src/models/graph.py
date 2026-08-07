from .zone import Zone, ZoneType
from .connection import Connection

from typing import Dict, List, FrozenSet
from pydantic import BaseModel, Field


class Graph(BaseModel):
    zones: Dict[str, Zone] = Field(default_factory=dict)
    connections: Dict[FrozenSet[str], Connection] = Field(
        default_factory=dict[FrozenSet[str], Connection]
    )
    adjacency_list: Dict[str, List[str]] = Field(default_factory=dict)

    def add_zone(self, zone: Zone) -> None:
        self.zones[zone.name] = zone
        self.adjacency_list[zone.name] = []

    def add_connection(self, connection: Connection) -> None:
        self.connections[connection.zones] = connection
        a, b = connection.zones
        self.adjacency_list[a].append(b)
        self.adjacency_list[b].append(a)

    def get_neighbors(self, zone_name: str) -> List[str]:
        return self.adjacency_list.get(zone_name, [])

    def get_zone(self, zone_name: str) -> Zone:
        return self.zones[zone_name]

    def get_connection(self, A: str, B: str) -> Connection:
        return self.connections[frozenset({A, B})]

    def get_start(self) -> str:
        for name, zone in self.zones.items():
            if zone.type == ZoneType.START:
                return name
        raise ValueError("There is no start zone")

    def get_end(self) -> str:
        for name, zone in self.zones.items():
            if zone.type == ZoneType.END:
                return name
        raise ValueError("There is no end zone")

    def __str__(self) -> str:
        lines = ["Graph:"]

        lines.append("\nZones:")
        for zone_name, zone in sorted(self.zones.items()):
            lines.append(
                f"  - {zone_name} "
                f"(type={zone.type.value}, max_drones={zone.max_drones})"
            )

        lines.append("\nConnections:")
        for connection in self.connections.values():
            a, b = sorted(connection.zones)
            lines.append(
                f"  - {a} <-> {b} (capacity={connection.capacity})"
            )

        lines.append("\nAdjacency list:")
        for zone_name in sorted(self.adjacency_list):
            neighbors = ", ".join(sorted(self.adjacency_list[zone_name]))
            lines.append(f"  {zone_name}: [{neighbors}]")

        return "\n".join(lines)
