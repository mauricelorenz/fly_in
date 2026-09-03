import pygame
from typing import List, Tuple
from parser import Drone, Hub, Connection


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

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

    def clear_screen(self) -> None:
        self.screen.fill("white")

    def run(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            self.clear_screen()
            pygame.display.flip()

    def get_boundaries(self) -> Tuple[int, int, int, int]:
        x_list = [i.pos_x for i in self.objects[1]]
        y_list = [i.pos_y for i in self.objects[1]]
        return (min(x_list), max(x_list), min(y_list), max(y_list))

    def scale_point(self, pos_x: int, pos_y: int) -> Tuple[int, int]:
        min_x, max_x, min_y, max_y = self.get_boundaries()
        padding = 50
        canvas_width = WINDOW_WIDTH - 2 * padding
        canvas_height = WINDOW_HEIGHT - 2 * padding
        factor_x = canvas_width / ((max_x - min_x) or 1)
        factor_y = canvas_height / ((max_y - min_y) or 1)
        pixel_x = padding + (pos_x - min_x) * factor_x
        pixel_y = padding + (pos_y - min_y) * factor_y
        return (int(pixel_x), int(pixel_y))
