from pydantic import BaseModel, Field
from dataclasses import dataclass
from typing import Dict


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
