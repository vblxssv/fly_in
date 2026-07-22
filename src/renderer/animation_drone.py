from dataclasses import dataclass
from typing import Tuple


@dataclass
class AnimDrone:
    drone_id: int
    start_pos: Tuple[float, float]
    target_pos: Tuple[float, float]
    total_turns: int = 1
    turns_done: int = 0
    turn_progress: float = 0.0

    def advance_turn(self) -> None:
        self.turns_done = min(self.turns_done + 1, self.total_turns)
        self.turn_progress = 0.0

    def advance_time(self, delta_time: float, turn_duration: float) -> None:
        if self.turns_done >= self.total_turns:
            return
        self.turn_progress = min(
            1.0, self.turn_progress + delta_time / turn_duration
        )

    @property
    def progress(self) -> float:
        overall = (self.turns_done + self.turn_progress) / self.total_turns
        return min(1.0, overall)

    @property
    def current_pos(self) -> Tuple[float, float]:
        p = self.progress
        x = self.start_pos[0] + (self.target_pos[0] - self.start_pos[0]) * p
        y = self.start_pos[1] + (self.target_pos[1] - self.start_pos[1]) * p
        return x, y
