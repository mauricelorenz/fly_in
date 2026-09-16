import pygame
from typing import List, Tuple, Dict, Any
from models import Drone, Hub, Connection, Zone


WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 800
PADDING = 100

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
        self.drones, self.hubs, self.connections = objects
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Fly-in")
        self.boundaries = self.get_boundaries()
        self.scale_factor = self.get_scale_factor()
        self.hub_pixels = {
            hub.name: self.to_pixels(hub.pos_x, hub.pos_y)
            for hub in self.hubs
        }
        self.hub_font = pygame.font.SysFont(
            None, int(min(min(self.scale_factor) * 0.2, 20))
        )
        self.drone_font = pygame.font.SysFont(
            None, int(min(min(self.scale_factor) * 0.7, 20))
        )
        self.current_turn = 0
        self.start_name = next(h.name for h in self.hubs if h.is_start)

    def clear_screen(self) -> None:
        self.screen.fill((180, 180, 190))

    def run(self, turns: List[Dict[int, Any]]) -> None:
        full_positions = self._resolve_full_positions(turns)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE
                ):
                    running = False
                elif (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_SPACE
                ):
                    if self.current_turn < len(turns) - 1:
                        self.current_turn += 1
            self.clear_screen()
            self.draw_connections()
            self.draw_hubs()
            self.draw_drones(full_positions[self.current_turn])
            pygame.display.flip()
        pygame.quit()

    def get_boundaries(self) -> Tuple[int, int, int, int]:
        x_list = [hub.pos_x for hub in self.hubs]
        y_list = [hub.pos_y for hub in self.hubs]
        return (min(x_list), max(x_list), min(y_list), max(y_list))

    def get_scale_factor(self) -> Tuple[float, float]:
        min_x, max_x, min_y, max_y = self.boundaries
        canvas_width = WINDOW_WIDTH - 2 * PADDING
        canvas_height = WINDOW_HEIGHT - 2 * PADDING
        factor_x = canvas_width / ((max_x - min_x) or 1)
        factor_y = canvas_height / ((max_y - min_y) or 1)
        return (factor_x, factor_y)

    def to_pixels(self, pos_x: int, pos_y: int) -> Tuple[int, int]:
        min_x, _, min_y, _ = self.boundaries
        factor_x, factor_y = self.scale_factor
        pixel_x = PADDING + (pos_x - min_x) * factor_x
        dynamic_height = min(factor_y, (factor_y + factor_x) // 2)
        pixel_y = PADDING + (pos_y - min_y) * dynamic_height
        return (int(pixel_x), int(pixel_y))

    def draw_hubs(self) -> None:
        for hub in self.hubs:
            pixel_x, pixel_y = self.hub_pixels[hub.name]
            if hub.color is None:
                color = DEFAULT_COLOR
            else:
                color = KNOWN_COLORS.get(hub.color, DEFAULT_COLOR)
            size = int(min(min(self.scale_factor) * 0.4, 40))
            pygame.draw.circle(self.screen, color, (pixel_x, pixel_y), size)
            pygame.draw.circle(
                self.screen, "black", (pixel_x, pixel_y),
                size, size // 20 or 1
            )
            name_surface = self.hub_font.render(hub.name, True, "black")
            text_x = pixel_x - name_surface.get_width() // 2
            text_y = pixel_y + size * 1.1
            self.screen.blit(name_surface, (text_x, text_y))
            stats = (f"[{'R' if hub.zone == Zone.RESTRICTED else ''}"
                     f"{'P' if hub.zone == Zone.PRIORITY else ''}"
                     f"{hub.max_drones}]")
            show_stats = stats if not any((hub.is_start, hub.is_end)) else ""
            stats_surface = self.hub_font.render(show_stats, True, "black")
            text_x = pixel_x - stats_surface.get_width() // 2
            text_y = pixel_y + size * 1.05 + name_surface.get_height() * 1.2
            self.screen.blit(stats_surface, (text_x, text_y))

    def draw_connections(self) -> None:
        for connection in self.connections:
            pygame.draw.line(
                self.screen,
                "black",
                self.hub_pixels[connection.hub1],
                self.hub_pixels[connection.hub2]
            )

    def draw_drones(self, current_pos: Dict[int, Any]) -> None:
        size = int(min(min(self.scale_factor) * 0.3, 30))
        drones_by_pos: Dict[Any, List[int]] = {}
        for drone_id, pos in current_pos.items():
            if pos not in drones_by_pos:
                drones_by_pos[pos] = []
            drones_by_pos[pos].append(drone_id)
        for pos in drones_by_pos:
            if isinstance(pos, str):
                drone_pixel = self.hub_pixels[pos]
            else:
                hub1, hub2 = pos
                hub1_pixel = self.hub_pixels[hub1]
                hub2_pixel = self.hub_pixels[hub2]
                drone_pixel = (
                    int((hub1_pixel[0] + hub2_pixel[0]) // 2),
                    int((hub1_pixel[1] + hub2_pixel[1]) // 2)
                )
            pygame.draw.circle(self.screen, (127, 127, 127), drone_pixel, size)
            pygame.draw.circle(
                self.screen, "black", drone_pixel, size, size // 20 or 1
            )
            drones_amount = len(drones_by_pos[pos])
            if drones_amount == 1:
                text = f"D{drones_by_pos[pos][0]}"
            else:
                text = f"{drones_amount}x"
            text_surface = self.drone_font.render(text, True, "black")
            pixel_x, pixel_y = drone_pixel
            text_x = pixel_x - text_surface.get_width() // 2
            text_y = pixel_y - text_surface.get_height() // 2
            self.screen.blit(text_surface, (text_x, text_y))

    def _resolve_full_positions(
        self, turns: List[Dict[int, Any]]
    ) -> List[Dict[int, Any]]:
        full_positions = []
        last_known = {d.drone_id: self.start_name for d in self.drones}
        for turn in turns:
            last_known.update(turn)
            full_positions.append(dict(last_known))
        return full_positions
