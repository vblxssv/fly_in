from pydantic import BaseModel
from typing import Dict, Tuple, Set


class ReservationTable(BaseModel):
    slots: Dict[Tuple[str, int], Set[int]]

