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
        return (0, 0)
