from .zone import Zone, ZoneRole
from .connection import Connection

from typing import Dict, List, FrozenSet
from pydantic import BaseModel, Field


class Graph(BaseModel):
    """Store zones, connections, and adjacency data for the drone network."""

    zones: Dict[str, Zone] = Field(default_factory=dict)
    connections: Dict[FrozenSet[str], Connection] = Field(
        default_factory=dict[FrozenSet[str], Connection]
    )
    adjacency_list: Dict[str, List[str]] = Field(default_factory=dict)

    def add_zone(self, zone: Zone) -> None:
        """Add a zone and initialize its adjacency list."""
        self.zones[zone.name] = zone
        self.adjacency_list[zone.name] = []

    def add_connection(self, connection: Connection) -> None:
        """Add an undirected connection to the graph."""
        self.connections[connection.zones] = connection
        a, b = connection.zones
        self.adjacency_list[a].append(b)
        self.adjacency_list[b].append(a)

    def get_neighbors(self, zone_name: str) -> List[str]:
        """Return the names of zones adjacent to ``zone_name``."""
        return self.adjacency_list.get(zone_name, [])

    def get_zone(self, zone_name: str) -> Zone:
        """Return the zone identified by ``zone_name``."""
        return self.zones[zone_name]

    def get_connection(self, A: str, B: str) -> Connection:
        """Return the connection between the two named zones."""
        return self.connections[frozenset({A, B})]

    def get_start(self) -> str:
        """Return the name of the start zone."""
        for name, zone in self.zones.items():
            if zone.role == ZoneRole.START:
                return name
        raise ValueError("There is no start zone")

    def get_end(self) -> str:
        """Return the name of the end zone."""
        for name, zone in self.zones.items():
            if zone.role == ZoneRole.END:
                return name
        raise ValueError("There is no end zone")

    def __str__(self) -> str:
        """Return a readable summary of zones and connections."""
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
