import heapq
from typing import Dict, List, Tuple, Optional, Set

from src.models import Graph
from .reservation_table import ReservationTable


class SpaceTimeAStar:

    @staticmethod
    def add_path(
        drone_id: int,
        graph: Graph,
        table: ReservationTable,
        heuristic: Dict[str, float],
        start: str,
        goal: str
    ) -> None:
        