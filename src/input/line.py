from pydantic import BaseModel, Field
from dataclasses import dataclass
from typing import List, Dict


class Line(BaseModel):
    line_number: int
    arguments: List[str]
    meta: Dict[str, str]

    def __str__(self) -> str:
        res: str = ''
        res += f"Line {self.line_number}\n"
        res += f"Arguments: {self.arguments}\n"
        res += f"Meta: {self.meta}\n"
        return res


class DroneLine(BaseModel):
    line: int
    amount: int = Field(gt=0)


@dataclass
class HubLine:
    line: int
    hub_type: str  # start, end, hub
    name: str
    x: str
    y: str
    meta: Dict[str, str]


@dataclass
class ConnectionLine:
    line: int
    from_zone: str
    to_zone: str
    meta: Dict[str, str]
