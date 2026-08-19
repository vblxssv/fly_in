from pydantic import BaseModel, Field

from typing import FrozenSet


class Connection(BaseModel):
    zones: FrozenSet[str]
    capacity: int = Field(gt=0)
