from src.models.zone import Zone
from typing import Dict, Tuple, List, Set


class Graph:
    def __init__(self) -> None:
        self.zones: Dict[str, Zone] = {}
        self.adjacency_list: Dict[str, List[Tuple[str, int]]] = {}
        self.start_hub: Zone | None = None
        self.end_hub: Zone | None = None

        self._registered_edges: Set[Tuple[str, str]] = set()

    def add_zone(self, zone: Zone) -> None:
        if zone.name not in self.zones:
            self.zones[zone.name] = zone
            self.adjacency_list[zone.name] = []

    def set_start(self, zone: Zone) -> None:
        self.add_zone(zone)
        self.start_hub = zone

    def set_end(self, zone: Zone) -> None:
        self.add_zone(zone)
        self.end_hub = zone

    def add_connection(self, connection: Tuple[str, str, int]) -> None:
        name1, name2, capacity = connection
        if name1 not in self.zones or name2 not in self.zones:
            raise ValueError(f"Error: both zones '{name1}' and '{name2}' "
                             f"must be added to the graph first.")
        u, v = sorted([name1, name2])
        edge_key: Tuple[str, str] = (u, v)
        if edge_key in self._registered_edges:
            raise ValueError(f"Duplicate connection "
                             f"detected: link between "
                             f"'{name1}' and '{name2}' already exists.")
        self._registered_edges.add(edge_key)
        self.adjacency_list[name1].append((name2, capacity))
        self.adjacency_list[name2].append((name1, capacity))

    def __repr__(self) -> str:
        start_name = self.start_hub.name if self.start_hub else "None"
        end_name = self.end_hub.name if self.end_hub else "None"
        edges_str: List[str] = []
        for u, v in sorted(self._registered_edges):
            capacity = 0
            for neighbor, cap in self.adjacency_list[u]:
                if neighbor == v:
                    capacity = cap
                    break
            edges_str.append(f"    {u} <-> {v} (capacity={capacity})")
        connections_block = "\n".join(edges_str) if edges_str else "    None"
        return (
            f"Graph(\n"
            f"  Start Hub: {start_name}\n"
            f"  End Hub: {end_name}\n"
            f"  Zones ({len(self.zones)}): {list(self.zones.keys())}\n"
            f"  Connections:\n{connections_block}\n"
            f")"
        )
