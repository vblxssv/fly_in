import pygame
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from src.models.zone import ZoneColor, ZoneType
from src.models.graph import Graph  # поправьте путь под свою структуру проекта


# ---- Цвета -----------------------------------------------------------

ZONE_COLOR_MAP: Dict[ZoneColor, Tuple[int, int, int]] = {
    ZoneColor.RED: (220, 20, 60),
    ZoneColor.GREEN: (34, 139, 34),
    ZoneColor.BLUE: (30, 144, 255),
    ZoneColor.PURPLE: (147, 112, 219),
    ZoneColor.BLACK: (40, 40, 40),
    ZoneColor.BROWN: (139, 69, 19),
    ZoneColor.ORANGE: (255, 140, 0),
    ZoneColor.MAROON: (128, 0, 0),
    ZoneColor.GOLD: (255, 215, 0),
    ZoneColor.DARKRED: (139, 0, 0),
    ZoneColor.VIOLET: (238, 130, 238),
    ZoneColor.CRIMSON: (220, 20, 60),
    ZoneColor.RAINBOW: (255, 0, 255),  # спецкейс, можно раскрасить радугой отдельно
    ZoneColor.NONE: (100, 100, 100),
}

# Обводка в зависимости от типа зоны — чтобы был виден статус, а не только цвет
ZONE_TYPE_BORDER: Dict[ZoneType, Tuple[int, int, int]] = {
    ZoneType.NORMAL: (255, 255, 255),
    ZoneType.BLOCKED: (80, 80, 80),
    ZoneType.RESTRICTED: (255, 0, 0),
    ZoneType.PRIORITY: (255, 215, 0),
}

BG_COLOR = (18, 18, 24)
EDGE_COLOR = (90, 90, 105)
EDGE_LABEL_COLOR = (200, 200, 210)
TEXT_COLOR = (235, 235, 235)
DRONE_COLOR = (255, 200, 0)
DRONE_OUTLINE = (30, 30, 30)

ZONE_RADIUS = 34
DRONE_RADIUS = 7


@dataclass
class DroneMovement:
    """Одно перемещение дрона между двумя зонами."""
    source: str
    target: str
    progress: float = 0.0      # 0.0 -> в source, 1.0 -> в target
    drone_id: Optional[str] = None
    speed: float = 0.01        # прирост progress за кадр (если используется update())

    def advance(self) -> bool:
        """Продвигает прогресс. Возвращает True, если перемещение завершено."""
        self.progress += self.speed
        if self.progress >= 1.0:
            self.progress = 1.0
            return True
        return False


class Renderer:
    def __init__(self, graph: Graph, width: int = 1000, height: int = 800,
                 zone_radius: int = ZONE_RADIUS):
        pygame.init()
        self.graph = graph
        self.width = width
        self.height = height
        self.zone_radius = zone_radius

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Drone Zone Graph")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("Arial", 16)
        self.small_font = pygame.font.SysFont("Arial", 12)

        self.movements: List[DroneMovement] = []

        self._screen_positions: Dict[str, Tuple[int, int]] = {}
        self._compute_screen_positions()

    # ---- Настройка -----------------------------------------------------

    def _compute_screen_positions(self) -> None:
        """
        Пересчитывает Zone.pos (произвольные условные координаты) в пиксельные
        координаты экрана, растягивая их на весь холст с отступами.
        Работает и если pos — маленькие индексы (0,1,2...), и если это уже пиксели.
        """
        if not self.graph.zones:
            return

        margin = self.zone_radius + 80
        xs = [z.pos[0] for z in self.graph.zones.values()]
        ys = [z.pos[1] for z in self.graph.zones.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        span_x = max_x - min_x
        span_y = max_y - min_y

        drawable_w = self.width - 2 * margin
        drawable_h = self.height - 2 * margin

        for name, zone in self.graph.zones.items():
            if span_x == 0:
                sx = self.width // 2
            else:
                sx = margin + int((zone.pos[0] - min_x) / span_x * drawable_w)
            if span_y == 0:
                sy = self.height // 2
            else:
                sy = margin + int((zone.pos[1] - min_y) / span_y * drawable_h)
            self._screen_positions[name] = (sx, sy)

    def get_position(self, zone_name: str) -> Tuple[int, int]:
        return self._screen_positions[zone_name]

    # ---- Управление дронами ---------------------------------------------

    def add_movement(self, movement: DroneMovement) -> None:
        self.movements.append(movement)

    def set_movements(self, movements: List[DroneMovement]) -> None:
        self.movements = movements

    def clear_finished_movements(self) -> None:
        self.movements = [m for m in self.movements if m.progress < 1.0]

    def update_movements(self) -> None:
        """Продвигает все перемещения на один кадр (использует Movement.speed)."""
        for m in self.movements:
            m.advance()

    # ---- Отрисовка -------------------------------------------------------

    def _draw_edges(self) -> None:
        drawn_pairs = set()
        for source, edges in self.graph.adjacency_list.items():
            for edge in edges:
                pair_key = frozenset((source, edge.target))
                if pair_key in drawn_pairs:
                    continue
                drawn_pairs.add(pair_key)

                if source not in self._screen_positions or edge.target not in self._screen_positions:
                    continue

                x1, y1 = self._screen_positions[source]
                x2, y2 = self._screen_positions[edge.target]

                pygame.draw.line(self.screen, EDGE_COLOR, (x1, y1), (x2, y2), 2)

                mx, my = (x1 + x2) // 2, (y1 + y2) // 2
                label = self.small_font.render(str(edge.capacity), True, EDGE_LABEL_COLOR)
                label_rect = label.get_rect(center=(mx, my))
                pygame.draw.rect(self.screen, BG_COLOR, label_rect.inflate(6, 4))
                self.screen.blit(label, label_rect)

    def _draw_zones(self) -> None:
        for name, zone in self.graph.zones.items():
            x, y = self._screen_positions[name]
            fill = ZONE_COLOR_MAP.get(zone.color, ZONE_COLOR_MAP[ZoneColor.NONE])
            border = ZONE_TYPE_BORDER.get(zone.type, (255, 255, 255))

            pygame.draw.circle(self.screen, fill, (x, y), self.zone_radius)
            pygame.draw.circle(self.screen, border, (x, y), self.zone_radius, 3)

            name_label = self.font.render(name, True, TEXT_COLOR)
            name_rect = name_label.get_rect(center=(x, y - self.zone_radius - 14))
            self.screen.blit(name_label, name_rect)

            info_label = self.small_font.render(
                f"{zone.type.value} | max {zone.max_drones}", True, TEXT_COLOR
            )
            info_rect = info_label.get_rect(center=(x, y + self.zone_radius + 12))
            self.screen.blit(info_label, info_rect)

    def _draw_drones(self) -> None:
        for movement in self.movements:
            if movement.source not in self._screen_positions or movement.target not in self._screen_positions:
                continue
            x1, y1 = self._screen_positions[movement.source]
            x2, y2 = self._screen_positions[movement.target]

            t = max(0.0, min(1.0, movement.progress))
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t

            pygame.draw.circle(self.screen, DRONE_COLOR, (int(x), int(y)), DRONE_RADIUS)
            pygame.draw.circle(self.screen, DRONE_OUTLINE, (int(x), int(y)), DRONE_RADIUS, 1)

            if movement.drone_id:
                label = self.small_font.render(movement.drone_id, True, TEXT_COLOR)
                self.screen.blit(label, (int(x) + 8, int(y) - 8))

    def draw(self) -> None:
        self.screen.fill(BG_COLOR)
        self._draw_edges()
        self._draw_zones()
        self._draw_drones()
        pygame.display.flip()

    # ---- Главный цикл ----------------------------------------------------

    def run(self, fps: int = 60, auto_advance: bool = True) -> None:
        """
        Запускает цикл окна. Если auto_advance=True, перемещения дронов
        продвигаются автоматически по своему speed; иначе progress
        нужно менять извне между кадрами (например, из симуляции).
        """
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            if auto_advance:
                self.update_movements()
                self.clear_finished_movements()

            self.draw()
            self.clock.tick(fps)

        pygame.quit()