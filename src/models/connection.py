from pydantic import BaseModel

from typing import FrozenSet


class Connection(BaseModel):
    zones: FrozenSet[str]
    capacity: int
