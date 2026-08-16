from .line import DroneLine, HubLine, ConnectionLine

from pydantic import BaseModel, model_validator
from typing import List


class Content(BaseModel):
    drone_line: DroneLine
    lines: List[HubLine | ConnectionLine]

    @model_validator(mode="before")
    @classmethod
    def validate_required_fields(cls, data):
        if data.get("drone_line") is None:
            raise ValueError("Missing nb_drones instruction")
        return data

    @model_validator(mode="after")
    def validate_content(self):
        line_numbers = [
            self.drone_line.line,
            *(line.line for line in self.lines),
        ]

        if self.drone_line.line != min(line_numbers):
            raise ValueError(
                f"Line {self.drone_line.line}: "
                "nb_drones must be the first instruction"
            )

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

        return self

    def __str__(self) -> str:
        result = f"Drone line: {self.drone_line}\n"

        for line in self.lines:
            result += f"{line}\n"

        return result

    @property
    def nb_drones(self) -> int:
        return self.drone_line.amount
