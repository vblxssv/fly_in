from .line import Line

from pydantic import BaseModel, Field, model_validator
from typing import List, Any


class Content(BaseModel):
    nb_drones: int = Field(gt=0)
    lines: List[Line]

    @model_validator(mode="before")
    @classmethod
    def parse_content(cls, data: Any) -> Any:
        if isinstance(data, list):
            lines = data
        elif isinstance(data, dict) and "lines" in data:
            lines = data["lines"]
        else:
            return data

        if not lines:
            raise ValueError("Content cannot be empty")

        first = lines[0]

        if first.type != "nb_drones:":
            raise ValueError(
                f"Line {first.line_number}: "
                "first line must be 'nb_drones:'"
            )

        try:
            amount, = first.arguments[1:]
        except ValueError:
            raise ValueError(
                f"Line {first.line_number}: "
                "nb_drones expects 1 argument"
            )

        return {
            "nb_drones": amount,
            "lines": lines,
        }
