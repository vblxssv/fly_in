from typing import List, Dict, Tuple, Any
from src.models.zone import Zone, ZoneType, ZoneColor
from src.models.graph import Graph


class ZoneFactory:
    @staticmethod
    def create(data: List[str]) -> Zone:
        if len(data) != 5:
            raise ValueError(f"Wrong amount of arguments for "
                             f"zone creation. Expected 5, got: {data}")
        name: str = data[1]
        try:
            x: int = int(data[2])
            y: int = int(data[3])
        except ValueError:
            raise ValueError(f"Invalid coordinates for zone '{name}'. Must be "
                             f"integers. Got x='{data[2]}', y='{data[3]}'")
        metadata: Dict[str, str] = {}
        for token in data[4]:
            key, separator, value = token.partition('=')
            if not separator:
                raise ValueError(f"Wrong metadata format in zone "
                                 f"'{name}': token '{token}' missing '='")
            metadata[key.strip()] = value.strip()
        color_str: str = metadata.get("color", "none")
        try:
            color = ZoneColor(color_str)
        except ValueError:
            raise ValueError(f"Invalid color '{color_str}' for zone '{name}'. "
                             f"Allowed values: {[e.value for e in ZoneColor]}")
        max_drones_str: str = metadata.get("max_drones", "1")
        try:
            max_drones_int: int = int(max_drones_str)
            if max_drones_int <= 0:
                raise ValueError()
        except ValueError:
            raise ValueError(f"Invalid max_drones value '{max_drones_str}' in "
                             f"zone '{name}'. Must be a positive integer.")
        zone_override: str = metadata.get("zone", "normal")
        try:
            zone_type = ZoneType(zone_override)
        except ValueError:
            raise ValueError(f"Invalid zone type '{zone_override}' "
                             f"for zone '{name}'. "
                             f"Allowed values: {[e.value for e in ZoneType]}")

        return Zone(
            name=name,
            pos=(x, y),
            type=zone_type,
            max_drones=max_drones_int,
            color=color
        )


class ConnectionFactory:
    @staticmethod
    def create(data: List[str]) -> Tuple[str, str, int]:
        # ['connection:', 'waypoint1-waypoint2', ['max_drones=5']]
        if len(data) != 3:
            raise ValueError(f"Wrong amount of arguments for "
                             f"connection creation. Expected 3, got: {data}")
        waypoints = data[1].split('-')
        if len(waypoints) != 2:
            raise ValueError(f"Invalid waypoint "
                             f"format: {data[1]}. Expected 'wp1-wp2'")
        name1: str = waypoints[0]
        name2: str = waypoints[1]

        metadata: Dict[str, str] = {}
        for token in data[-1]:
            key, separator, value = token.partition('=')
            if not separator:
                raise ValueError("Wrong metadata format missing '='")
            metadata[key.strip()] = value.strip()
        drones_str: str = metadata.get("max_link_capacity", "1")
        try:
            drones_int: int = int(drones_str)
        except ValueError:
            raise ValueError(f"Invalid max_drones value '{drones_str}'")
        return (name1, name2, drones_int)


class GraphFactory:
    @staticmethod
    def create(data: List[List[Any]]) -> Graph:
        graph = Graph()
        for row in data:
            command = row[0]
            if command == "hub:":
                graph.add_zone(ZoneFactory.create(row))
            elif command == "start_hub:":
                graph.set_start(ZoneFactory.create(row))
            elif command == "end_hub:":
                graph.set_end(ZoneFactory.create(row))

        for row in data:
            command = row[0]
            if command == "connection:":
                graph.add_connection(ConnectionFactory.create(row))
        if not graph.start_hub:
            raise ValueError("Invalid map configuration: "
                             "'start_hub:' is missing.")
        if not graph.end_hub:
            raise ValueError("Invalid map configuration: "
                             "'end_hub:' is missing.")

        return graph
