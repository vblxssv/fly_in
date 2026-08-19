from pydantic import BaseModel, Field

from typing import FrozenSet


class Connection(BaseModel):
    """Represent an undirected, capacity-limited connection between zones."""

    zones: FrozenSet[str]
    capacity: int = Field(gt=0)
