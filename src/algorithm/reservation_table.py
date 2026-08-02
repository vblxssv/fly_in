from pydantic import BaseModel
from typing import Dict, Tuple, Set, List


class ReservationTable(BaseModel):
    slots: Dict[Tuple[str, int], Set[int]] = {}

    def is_zone_free(self, zone: str, time: int, capacity: int) -> bool:
        occupied_count = len(self.slots.get((zone, time), set()))
        return occupied_count < capacity

    def is_edge_free(self, from_zone: str, to_zone: str, start_time: int,
                     travel_time: int, edge_capacity: int) -> bool:
        edge_key_name = f"{from_zone}->{to_zone}"
        for t in range(start_time, start_time + travel_time):
            occupied_count = len(self.slots.get((edge_key_name, t), set()))
            if occupied_count >= edge_capacity:
                return False
        return True

    def reserve_path(self, drone_id: int,
                     path: List[Tuple[str, int, int]]) -> None:
        for i in range(len(path)):
            zone, time = path[i][0], path[i][1]

            if (zone, time) not in self.slots:
                self.slots[(zone, time)] = set()
            self.slots[(zone, time)].add(drone_id)

            if i + 1 < len(path):
                next_zone, next_time = path[i+1][0], path[i+1][1]
                if zone != next_zone:
                    edge_key = f"{zone}->{next_zone}"
                    for t in range(time, next_time):
                        if (edge_key, t) not in self.slots:
                            self.slots[(edge_key, t)] = set()
                        self.slots[(edge_key, t)].add(drone_id)
