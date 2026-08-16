from .line import DroneLine, HubLine, ConnectionLine
from .content import Content

from typing import List, Dict, Tuple


class Parser:
    @staticmethod
    def _split_meta(line_number: int, line: str) -> Tuple[str, str | None]:
        brackets: Tuple[int, int] = (line.count("["), line.count("]"))

        if brackets[0] > 1 or brackets[1] > 1:  # [[]]
            raise ValueError(f"Line {line_number}: Too many square brackets")
        if brackets[0] == 1 and brackets[1] == 0:  # [
            raise ValueError(f"Line {line_number}:"
                             f"There is no close square bracket")
        if brackets[0] == 0 and brackets[1] == 1:  # ]
            raise ValueError(f"Line {line_number}:"
                             f"There is no open square bracket")
        if brackets[0] == 1 and brackets[1] == 1:
            if not line.rstrip().endswith("]"):
                raise ValueError(
                    f"Line {line_number}: Meta"
                    f" section must be the last element"
                )
        if brackets[0] == 0 and brackets[1] == 0:  # There is no meta
            return (line, None)
        start = line.index("[")
        return (
            line[:start].strip(),
            line[start:].strip()
        )

    @staticmethod
    def _parse_meta(line_number: int, line: str | None) -> Dict[str, str]:
        meta_dic: Dict[str, str] = {}
        if not line:
            return meta_dic
        for pair in line[1: -1].split():
            if pair.count("=") != 1:
                raise ValueError(
                    f"Line {line_number}: amount of '=' is not 1")
            key, value = pair.split("=", 1)
            if key in meta_dic:
                raise ValueError(
                    f"Line {line_number}: duplicate meta argument: {key}"
                )
            meta_dic[key] = value
        return meta_dic

    @staticmethod
    def _parse_hub_line(line: int,
                        arguments: List[str], meta: Dict[str, str]) -> HubLine:
        hub_type = arguments[0][:-1]

        if hub_type in ("start_hub", "end_hub"):
            allowed_meta = {"color"}
        else:
            allowed_meta = {"zone", "max_drones", "color"}
        unknown = meta.keys() - allowed_meta
        if unknown:
            raise ValueError(
                f"Line {line}: unknown hub meta: {next(iter(unknown))}"
            )
        if len(arguments) != 4:
            raise ValueError(f"Line {line}: must be 4 arguments")

        return HubLine(line=line, hub_type=arguments[0][:-1],
                       name=arguments[1],
                       x=arguments[2],
                       y=arguments[3],
                       meta=meta)

    @staticmethod
    def _parse_connection_line(line: int,
                               arguments: List[str],
                               meta: Dict[str, str]) -> ConnectionLine:
        allowed_meta = {"max_link_capacity"}
        unknown = meta.keys() - allowed_meta
        if unknown:
            raise ValueError(
                f"Line {line}: unknown connection meta: {next(iter(unknown))}"
            )
        try:
            connection, = arguments[1:]
            from_zone, to_zone = connection.split("-")
        except ValueError:
            raise ValueError(
                f"Line {line}: connection expects 1 argument "
                "in format 'from-to'"
            )
        return ConnectionLine(
            line=line,
            from_zone=from_zone,
            to_zone=to_zone,
            meta=meta,
        )

    @staticmethod
    def _parse_drone_line(line: int,
                          arguments: List[str],
                          meta: Dict[str, str]) -> DroneLine:
        if meta:
            raise ValueError(f"Line {line}: nb_drones does not support meta")
        if len(arguments) != 2:
            raise ValueError(f"Line {line}: must be 2 arguments")
        return DroneLine(line=line, amount=int(arguments[1]))

    @staticmethod
    def parse(path: str) -> Content:
        drone_line = None
        lines: List[HubLine | ConnectionLine] = []
        first_instruction = True

        with open(path, "r", encoding="utf-8") as file:
            for line_number, raw_line in enumerate(file, start=1):
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = Parser._split_meta(line_number, line)

                arguments = parts[0].split()
                meta_dict: Dict[str, str] = Parser._parse_meta(
                    line_number, parts[1])
                line_type = arguments[0]

                if first_instruction:
                    if line_type != "nb_drones:":
                        raise ValueError(
                            f"Line {line_number}: "
                            "first instruction must be 'nb_drones:'"
                        )
                    first_instruction = False

                if line_type == "nb_drones:":
                    if drone_line is not None:
                        raise ValueError(
                            f"Line {line_number}: "
                            "duplicate nb_drones instruction"
                        )
                    try:
                        drone_line = (Parser._parse_drone_line(
                            line_number, arguments, meta_dict))
                    except ValueError as e:
                        raise ValueError(f"Line {line_number}: {e}")
                elif line_type in ("hub:", "start_hub:", "end_hub:"):
                    lines.append(Parser._parse_hub_line(
                                 line_number, arguments, meta_dict))
                elif line_type == "connection:":
                    lines.append(Parser._parse_connection_line(
                                 line_number, arguments, meta_dict))
                else:
                    raise ValueError(f"Line {line_number}: "
                                     f"Unknown line type {line_type}")
        if drone_line is None:
            raise ValueError("Missing nb_drones instruction")
        return Content(drone_line=drone_line, lines=lines)
