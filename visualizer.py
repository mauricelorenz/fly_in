import pygame
from typing import List, Tuple
from models import Drone, Hub, Connection


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
        pygame.display.set_caption("Fly-in")
        self.boundaries = self.get_boundaries()
        self.scale_factor = self.get_scale_factor()
        self.hub_pixels = {
            hub.name: self.to_pixels(hub.pos_x, hub.pos_y)
            for hub in self.objects[1]
        }
        self.font = pygame.font.SysFont(
            None, int(min(self.scale_factor * 0.17, 20))
        )

    def clear_screen(self) -> None:
        self.screen.fill((127, 127, 127))

    def run(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE
                ):
                    running = False
            self.clear_screen()
            self.draw_connections()
            self.draw_hubs()
            pygame.display.flip()
        pygame.quit()

    def get_boundaries(self) -> Tuple[int, int, int, int]:
        x_list = [hub.pos_x for hub in self.objects[1]]
        y_list = [hub.pos_y for hub in self.objects[1]]
        return (min(x_list), max(x_list), min(y_list), max(y_list))

    def get_scale_factor(self) -> float:
        min_x, max_x, min_y, max_y = self.boundaries
        canvas_width = WINDOW_WIDTH - 2 * PADDING
        canvas_height = WINDOW_HEIGHT - 2 * PADDING
        factor_x = canvas_width / ((max_x - min_x) or 1)
        factor_y = canvas_height / ((max_y - min_y) or 1)
        return min(factor_x, factor_y)

    def to_pixels(self, pos_x: int, pos_y: int) -> Tuple[int, int]:
        min_x, _, min_y, _ = self.boundaries
        factor = self.scale_factor
        pixel_x = PADDING + (pos_x - min_x) * factor
        pixel_y = PADDING + (pos_y - min_y) * factor
        return (int(pixel_x), int(pixel_y))

    def draw_hubs(self) -> None:
        for hub in self.objects[1]:
            pixel_x, pixel_y = self.hub_pixels[hub.name]
            if hub.color is None:
                color = DEFAULT_COLOR
            else:
                color = KNOWN_COLORS.get(hub.color, DEFAULT_COLOR)
            size = int(min(self.scale_factor * 0.4, 40))
            pygame.draw.circle(self.screen, color, (pixel_x, pixel_y), size)
            pygame.draw.circle(
                self.screen, "black", (pixel_x, pixel_y),
                size, size // 20 or 1
            )
            text_surface = self.font.render(hub.name, True, "black")
            text_x = pixel_x - text_surface.get_width() // 2
            text_y = pixel_y + size * 1.1
            self.screen.blit(text_surface, (text_x, text_y))

    def draw_connections(self) -> None:
        for connection in self.objects[2]:
            pygame.draw.line(
                self.screen,
                "black",
                self.hub_pixels[connection.hub1],
                self.hub_pixels[connection.hub2]
            )
