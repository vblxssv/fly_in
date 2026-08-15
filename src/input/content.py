from .line import DroneLine, HubLine, ConnectionLine

from pydantic import BaseModel, Field, model_validator
from typing import List, Any


class Content(BaseModel):
    drone_line: DroneLine
    lines: List[HubLine | ConnectionLine]
