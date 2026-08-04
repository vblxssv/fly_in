from .zone import Zone
from .edge import Edge

from typing import Dict, List
from pydantic import BaseModel, Field


class Graph(BaseModel):
    zones: Dict[str, Zone] = Field(default_factory=dict)
    adjacency_list: Dict[str, List[Edge]] = Field(default_factory=dict)
    start: str = ""
    end: str = ""

    def add_zone(self, zone: Zone) -> None:
        self.zones[zone.name] = zone
        self.adjacency_list[zone.name] = []

    def add_edge(self, source: str, target: str, capacity: int) -> None:
        if source not in self.zones or target not in self.zones:
            raise ValueError(f"Error: connection {source}-{target} "
                             f"leads to non-existing hub")
        self.adjacency_list[source].append(Edge(target=target,
                                                capacity=capacity))
        self.adjacency_list[target].append(Edge(target=source,
                                                capacity=capacity))

    def get_neighbors(self, zone_name: str) -> List[str]:
        if zone_name not in self.zones.keys():
            raise ValueError(f"There is no zone: {zone_name} in known zones")
        return [edge.target for edge in self.adjacency_list.get(zone_name, [])]

    def get_edge(self, target: str, source: str) -> Edge:
        for edge in self.adjacency_list.get(source, []):
            if edge.target == target:
                return edge
        raise ValueError(f"No edge from {source} to {target}")

    def get_zone(self, zone_name: str) -> Zone:
        if zone_name not in self.zones:
            raise ValueError(f"There is no {zone_name} in graph")
        return self.zones[zone_name]

    def __str__(self) -> str:
        lines = ["Graph Status:"]
        lines.append(f"  Total Zones: {len(self.zones)}")

        lines.append("\n  Zones (Hubs):")
        for name, zone in self.zones.items():
            lines.append(f"    - {name}: Type={zone.type.value}, "
                         f"Color={zone.color.value}, Drones={zone.max_drones}")

        lines.append("\n  Connections:")
        for source, edges in self.adjacency_list.items():
            for edge in edges:
                lines.append(f"    {source} --({edge.capacity})"
                             f"--> {edge.target}")

        return "\n".join(lines)



class Connection(BaseModel):
    zones: frozenset[str]
    capacity: int


class Graph(BaseModel):
    zones: Dict[str, Zone] = Field(default_factory=dict)
    connections: Dict[frozenset[str], Connection] = Field(default_factory=dict)
    adjacency_list: Dict[str, List[str]] = Field(default_factory=dict)