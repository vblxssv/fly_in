from .reservation_table import ReservationTable
from src.models import Graph

import heapq


class SpaceTimeAStar:
    @staticmethod
    def add_path(drone_id: int, graph: Graph, table: ReservationTable) -> None:
        """Has to mutate table"""
        