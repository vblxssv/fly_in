from pydantic import BaseModel, Field
from dataclasses import dataclass
from typing import Dict


class DroneLine(BaseModel):
    """Represent a parsed ``nb_drones`` map instruction."""

    line: int
    amount: int = Field(gt=0)


@dataclass
class HubLine:
    """Represent a parsed start, end, or regular hub instruction."""

    line: int
    hub_type: str  # start, end, hub
    name: str
    x: str
    y: str
    meta: Dict[str, str]


@dataclass
class ConnectionLine:
    """Represent a parsed connection instruction between two hubs."""

    line: int
    from_zone: str
    to_zone: str
    meta: Dict[str, str]
