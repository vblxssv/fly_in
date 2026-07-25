from .line import Line

from typing import List, Set, Tuple


class Validator:
    @staticmethod
    def _check_zone_line(line: Line, seen_zones: Set[str]) -> None:
        line_number = line.line_number
        if (len(line.arguments) > 4):
            raise ValueError(
                f"Line {line_number}: Too many arguments")
        elif (len(line.arguments) < 4):
            raise ValueError(
                f"Line {line_number}: Too few arguments")
        if '-' in line.arguments[1]:
            raise ValueError(
                f"Line {line_number}: Forbidden '-' in name"
            )
        try:
            int(line.arguments[2])
        except ValueError:
            raise ValueError(
                f"Line {line_number}: x is supposed to be an integer value"
            )
        try:
            int(line.arguments[3])
        except ValueError:
            raise ValueError(
                f"Line {line_number}: y is supposed to be an integer value"
            )
        if line.arguments[1] in seen_zones:
            raise ValueError(
                f"Line {line_number}: Found duplicate zone"
            )
        for key, value in line.meta.items():
            if key == "zone":
                if (value not in
                        ["normal", "blocked", "restricted", "priority"]):
                    raise ValueError(
                        f"Line {line_number}: Unknown zone type: {value}"
                    )
            elif key == "max_drones":
                try:
                    max_drones = int(value)
                except ValueError:
                    raise ValueError(
                        f"Line {line_number}: maximum drones is supposed "
                        "to be an integer value"
                    )
                if max_drones < 1:
                    raise ValueError(
                        f"Line {line_number}: maximum drones is supposed "
                        "to be bigger than 0"
                    )
            elif key != "color":
                raise ValueError(
                    f"Line {line_number}: Unknown meta argument: {key}"
                )

    @staticmethod
    def _check_nb_drones(line: Line) -> None:
        line_number = line.line_number
        if (len(line.arguments) > 2):
            raise ValueError(
                f"Line {line_number}: Too many arguments")
        elif (len(line.arguments) < 2):
            raise ValueError(
                f"Line {line_number}: Too few arguments")
        try:
            drones = int(line.arguments[1])
        except ValueError:
            raise ValueError(
                f"Line {line_number}: number of drones is supposed "
                "to be an integer value"
            )
        if drones < 0:
            raise ValueError(
                f"Line {line_number}: number of drones is supposed "
                "to be positive"
            )
        if line.meta:
            raise ValueError(
                f"Line {line_number}: Found metadata in nb_drones line"
            )

    @staticmethod
    def _check_connection(
        line: Line,
        seen_zones: Set[str],
        seen_connections: Set[Tuple[str, str]],
    ) -> None:
        line_number = line.line_number
        if (len(line.arguments) > 2):
            raise ValueError(
                f"Line {line_number}: Too many arguments")
        elif (len(line.arguments) < 2):
            raise ValueError(
                f"Line {line_number}: Too few arguments")

        connection = line.arguments[1]
        if '-' not in connection:
            raise ValueError(
                f"Line {line_number}: invalid connection format "
                f"'{connection}'. Expected 'from-to'"
            )

        nodes = connection.split('-')
        if len(nodes) != 2 or not nodes[0] or not nodes[1]:
            raise ValueError(
                f"Line {line_number}: invalid connection format "
                f"'{connection}'. Expected 'from-to'"
            )

        from_zone, to_zone = nodes[0], nodes[1]

        if from_zone == to_zone:
            raise ValueError(
                f"Line {line_number}: connection '{connection}' "
                "connects a zone to itself"
            )

        if from_zone not in seen_zones:
            raise ValueError(
                f"Line {line_number}: zone: {from_zone} is not defined"
            )

        if to_zone not in seen_zones:
            raise ValueError(
                f"Line {line_number}: zone: {to_zone} is not defined"
            )

        connection_key = (
            min(from_zone, to_zone),
            max(from_zone, to_zone)
        )
        if connection_key in seen_connections:
            raise ValueError(
                f"Line {line_number}: Found duplicate connection "
                f"'{from_zone}-{to_zone}'"
            )
        seen_connections.add(connection_key)

        for key, value in line.meta.items():
            if key == "max_link_capacity":
                try:
                    capacity = int(value)
                except ValueError:
                    raise ValueError(
                        f"Line {line_number}: max_link_capacity is "
                        "supposed to be an integer value"
                    )
                if capacity < 1:
                    raise ValueError(
                        f"Line {line_number}: max_link_capacity is "
                        "supposed to be a positive integer"
                    )
            else:
                raise ValueError(
                    f"Line {line_number}: Unknown meta argument: {key}"
                )

    @staticmethod
    def validate(lines: List[Line]) -> None:
        start_hub_amount: int = 0
        end_hub_amount: int = 0
        nb_drones_amount: int = 0
        seen_zones: Set[str] = set()
        seen_connections: Set[Tuple[str, str]] = set()

        for line in lines:
            if not len(line.arguments):
                raise ValueError(
                    f"Line {line.line_number}: Amount of arguments cannot be 0"
                )
            type_of_line: str = line.arguments[0]
            if type_of_line != "nb_drones:" and nb_drones_amount == 0:
                raise ValueError(
                    f"Line {line.line_number}: The first "
                    f"instruction must be 'nb_drones:'"
                )
            if type_of_line == "hub:":
                Validator._check_zone_line(line, seen_zones)
                seen_zones.add(line.arguments[1])
            elif type_of_line == "start_hub:":
                Validator._check_zone_line(line, seen_zones)
                seen_zones.add(line.arguments[1])
                start_hub_amount += 1
                if start_hub_amount > 1:
                    raise ValueError(
                        f"Line {line.line_number}: Found second start_hub"
                    )
            elif type_of_line == "end_hub:":
                Validator._check_zone_line(line, seen_zones)
                seen_zones.add(line.arguments[1])
                end_hub_amount += 1
                if end_hub_amount > 1:
                    raise ValueError(
                        f"Line {line.line_number}: Found second end_hub"
                    )
            elif type_of_line == "nb_drones:":
                Validator._check_nb_drones(line)
                nb_drones_amount += 1
                if nb_drones_amount > 1:
                    raise ValueError(
                        f"Line {line.line_number}: Found second nb_drones line"
                    )
            elif type_of_line == "connection:":
                Validator._check_connection(line, seen_zones, seen_connections)
            else:
                raise ValueError(
                    f"Line {line.line_number}: Unknown line type: "
                    f"{type_of_line}"
                )

        if start_hub_amount != 1:
            raise ValueError("Missing start_hub")
        if end_hub_amount != 1:
            raise ValueError("Missing end_hub")
        if nb_drones_amount != 1:
            raise ValueError("Missing nb_drones")
