from .zone import Zone
from .edge import Edge

from typing import Dict, List
from pydantic import BaseModel, Field


class Graph(BaseModel):
    zones: Dict[str, Zone] = Field(default_factory=dict)
    adjacency_list: Dict[str, List["Edge"]] = Field(default_factory=dict)
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

    def get_edge(self, target: str, source: str) -> "Edge":
        for edge in self.adjacency_list.get(source, []):
            if edge.target == target:
                return edge
        raise ValueError(f"No edge from {source} to {target}")

    def __repr__(self) -> str:
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
