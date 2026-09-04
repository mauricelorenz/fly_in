import pygame
from typing import List, Tuple
from parser import Drone, Hub, Connection


WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 1200
PADDING = 50

KNOWN_COLORS = {
    "black": (0, 0, 0),
    "blue": (0, 0, 255),
    "brown": (165, 42, 42),
    "crimson": (220, 20, 60),
    "cyan": (0, 255, 255),
    "darkred": (139, 0, 0),
    "gold": (255, 215, 0),
    "green": (0, 128, 0),
    "lime": (0, 255, 0),
    "magenta": (255, 0, 255),
    "maroon": (128, 0, 0),
    "orange": (255, 165, 0),
    "purple": (128, 0, 128),
    "rainbow": (255, 255, 255),
    "red": (255, 0, 0),
    "violet": (238, 130, 238),
    "yellow": (255, 255, 0),
}

DEFAULT_COLOR = (200, 200, 200)


class Visualizer:
    def __init__(
        self, objects: Tuple[List[Drone], List[Hub], List[Connection]]
    ) -> None:
        self.objects = objects
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.boundaries = self.get_boundaries()
        self.scale_factor = self.get_scale_factor()
        self.hub_lookup = {hub.name: hub for hub in self.objects[1]}

    def clear_screen(self) -> None:
        self.screen.fill((127, 127, 127))

    def run(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            self.clear_screen()
            self.draw_connections()
            self.draw_hubs()
            pygame.display.flip()

    def get_boundaries(self) -> Tuple[int, int, int, int]:
        x_list = [i.pos_x for i in self.objects[1]]
        y_list = [i.pos_y for i in self.objects[1]]
        return (min(x_list), max(x_list), min(y_list), max(y_list))

    def get_scale_factor(self) -> float:
        min_x, max_x, min_y, max_y = self.boundaries
        canvas_width = WINDOW_WIDTH - 2 * PADDING
        canvas_height = WINDOW_HEIGHT - 2 * PADDING
        factor_x = canvas_width / ((max_x - min_x) or 1)
        factor_y = canvas_height / ((max_y - min_y) or 1)
        return min(factor_x, factor_y)

    def scale_point(self, pos_x: int, pos_y: int) -> Tuple[int, int]:
        min_x, _, min_y, _ = self.boundaries
        factor = self.scale_factor
        pixel_x = PADDING + (pos_x - min_x) * factor
        pixel_y = PADDING + (pos_y - min_y) * factor
        return (int(pixel_x), int(pixel_y))

    def draw_hubs(self) -> None:
        for i in self.objects[1]:
            pixel_xy = self.scale_point(i.pos_x, i.pos_y)
            if i.color is None:
                color = DEFAULT_COLOR
            else:
                color = KNOWN_COLORS.get(i.color, DEFAULT_COLOR)
            size = int(min(self.scale_factor * 0.4, 40))
            pygame.draw.circle(self.screen, color, pixel_xy, size)
            pygame.draw.circle(
                self.screen, "black", pixel_xy,
                size, size // 20 or 1
            )

    def draw_connections(self) -> None:
        for i in self.objects[2]:
            hub1 = self.hub_lookup[i.hub1]
            pixel_hub1 = self.scale_point(hub1.pos_x, hub1.pos_y)
            hub2 = self.hub_lookup[i.hub2]
            pixel_hub2 = self.scale_point(hub2.pos_x, hub2.pos_y)
            pygame.draw.line(self.screen, "black", pixel_hub1, pixel_hub2)
