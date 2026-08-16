from .line import DroneLine, HubLine, ConnectionLine

from pydantic import BaseModel, model_validator
from typing import List, Any, Self


class Content(BaseModel):
    drone_line: DroneLine
    lines: List[HubLine | ConnectionLine]

    @model_validator(mode="before")
    @classmethod
    def validate_required_fields(cls, data: Any) -> Any:
        if data.get("drone_line") is None:
            raise ValueError("Missing nb_drones instruction")

        return data

    @model_validator(mode="after")
    def validate_content(self) -> Self:
        self._validate_first_instruction()
        self._validate_special_hubs()
        self._validate_duplicate_zones()
        self._validate_duplicate_connections()
        self._validate_connection_zones()

        return self

    def _validate_connection_zones(self) -> None:
        zones: set[str] = set()

        for line in self.lines:
            if isinstance(line, HubLine):
                zones.add(line.name)
                continue

            if isinstance(line, ConnectionLine):
                if line.from_zone not in zones:
                    raise ValueError(
                        f"Line {line.line}: "
                        f"unknown zone '{line.from_zone}'"
                    )

                if line.to_zone not in zones:
                    raise ValueError(
                        f"Line {line.line}: "
                        f"unknown zone '{line.to_zone}'"
                    )

    def _validate_first_instruction(self) -> None:
        line_numbers = [
            self.drone_line.line,
            *(line.line for line in self.lines),
        ]

        if self.drone_line.line != min(line_numbers):
            raise ValueError(
                f"Line {self.drone_line.line}: "
                "nb_drones must be the first instruction"
            )

    def _validate_special_hubs(self) -> None:
        start_hub = None
        end_hub = None

        for line in self.lines:
            if not isinstance(line, HubLine):
                continue

            if line.hub_type == "start_hub":
                if start_hub is not None:
                    raise ValueError(
                        f"Line {line.line}: found start_hub duplicate"
                    )
                start_hub = line

            elif line.hub_type == "end_hub":
                if end_hub is not None:
                    raise ValueError(
                        f"Line {line.line}: found end_hub duplicate"
                    )
                end_hub = line

        if start_hub is None:
            raise ValueError("Missing start_hub")

        if end_hub is None:
            raise ValueError("Missing end_hub")

    def _validate_duplicate_zones(self) -> None:
        zones: set[str] = set()

        for line in self.lines:
            if not isinstance(line, HubLine):
                continue

            if line.name in zones:
                raise ValueError(
                    f"Line {line.line}: found zone duplicate '{line.name}'"
                )

            zones.add(line.name)

    def _validate_duplicate_connections(self) -> None:
        connections: set[frozenset[str]] = set()

        for line in self.lines:
            if not isinstance(line, ConnectionLine):
                continue

            connection = frozenset({
                line.from_zone,
                line.to_zone,
            })

            if connection in connections:
                raise ValueError(
                    f"Line {line.line}: found connection duplicate "
                    f"'{line.from_zone}-{line.to_zone}'"
                )

            connections.add(connection)

    def __str__(self) -> str:
        result = f"Drone line: {self.drone_line}\n"

        for line in self.lines:
            result += f"{line}\n"

        return result

    @property
    def nb_drones(self) -> int:
        return self.drone_line.amount
