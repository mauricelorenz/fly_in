"""Pygame-based GUI for visualizing the fly-in drone simulation."""

from typing import Any, Dict, List, Tuple

import pygame

from models import COLORS, Connection, Drone, Hub, Zone

WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 800
PADDING = 100


class Visualizer:
    """Renders the simulation state on screen using Pygame."""

    def __init__(
        self, objects: Tuple[List[Drone], List[Hub], List[Connection]]
    ) -> None:
        """Initialize the Pygame window and compute layout scaling.

        Args:
            objects: A tuple of (drones, hubs, connections) parsed from the map
                file.
        """
        self.drones, self.hubs, self.connections = objects
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Fly-in")
        self.boundaries = self._get_boundaries()
        self.scale_factor = self._get_scale_factor()
        self.hub_pixels = {
            h.name: self._to_pixels(h.pos_x, h.pos_y)
            for h in self.hubs
        }
        self.hub_font = pygame.font.SysFont(
            None, int(min(min(self.scale_factor) * 0.2, 20))
        )
        self.drone_font = pygame.font.SysFont(
            None, int(min(min(self.scale_factor) * 0.7, 20))
        )
        self.current_turn = 0
        self.start_name = next(h.name for h in self.hubs if h.is_start)

    def run(self, turns: List[Dict[int, Any]]) -> None:
        """Run the main event loop, advancing turns on spacebar press.

        Args:
            turns: A list of turn dictionaries mapping drone IDs to their
                positions.
        """
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
                    and self.current_turn < len(turns) - 1
                ):
                    self.current_turn += 1
            self._clear_screen()
            self._draw_connections()
            self._draw_hubs()
            self._draw_drones(full_positions[self.current_turn])
            pygame.display.flip()
        pygame.quit()

    def _resolve_full_positions(
        self, turns: List[Dict[int, Any]]
    ) -> List[Dict[int, Any]]:
        """Fill drone positions per turn, carrying forward last location.

        Args:
            turns: The raw turn data where only changes are recorded.

        Returns:
            A list of turn dictionaries with complete drone positions at each
            turn.
        """
        full_positions = []
        last_known = {d.drone_id: self.start_name for d in self.drones}
        for turn in turns:
            last_known.update(turn)
            full_positions.append(dict(last_known))
        return full_positions

    def _clear_screen(self) -> None:
        """Fill the screen with the background color."""
        self.screen.fill((180, 180, 190))

    def _draw_hubs(self) -> None:
        """Draw each hub as a colored circle with its name and stats."""
        for hub in self.hubs:
            pixel_x, pixel_y = self.hub_pixels[hub.name]
            if hub.color is None:
                color = COLORS["default"]
            else:
                color = COLORS.get(hub.color, COLORS["default"])
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

    def _draw_connections(self) -> None:
        """Draw a line for every connection between hubs."""
        for connection in self.connections:
            pygame.draw.line(
                self.screen,
                "black",
                self.hub_pixels[connection.hub1],
                self.hub_pixels[connection.hub2]
            )

    def _draw_drones(self, current_pos: Dict[int, Any]) -> None:
        """Draw drones at their current positions, grouping overlapping ones.

        Args:
            current_pos: A mapping from drone ID to its current hub name or
                connection tuple.
        """
        size = int(min(min(self.scale_factor) * 0.3, 30))
        drones_by_pos: Dict[Any, List[int]] = {}
        for drone_id, pos in current_pos.items():
            if pos not in drones_by_pos:
                drones_by_pos[pos] = []
            drones_by_pos[pos].append(drone_id)
        for pos, value in drones_by_pos.items():
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
            drones_amount = len(value)
            if drones_amount == 1:
                text = f"D{value[0]}"
            else:
                text = f"{drones_amount}x"
            text_surface = self.drone_font.render(text, True, "black")
            pixel_x, pixel_y = drone_pixel
            text_x = pixel_x - text_surface.get_width() // 2
            text_y = pixel_y - text_surface.get_height() // 2
            self.screen.blit(text_surface, (text_x, text_y))

    def _get_boundaries(self) -> Tuple[int, int, int, int]:
        """Compute the bounding box of all hub coordinates.

        Returns:
            A tuple of (min_x, max_x, min_y, max_y).
        """
        x_list = [h.pos_x for h in self.hubs]
        y_list = [h.pos_y for h in self.hubs]
        return (min(x_list), max(x_list), min(y_list), max(y_list))

    def _get_scale_factor(self) -> Tuple[float, float]:
        """Compute the scale factors for mapping coordinates to screen pixels.

        Returns:
            A tuple of (scale_x, scale_y).
        """
        min_x, max_x, min_y, max_y = self.boundaries
        canvas_width = WINDOW_WIDTH - 2 * PADDING
        canvas_height = WINDOW_HEIGHT - 2 * PADDING
        factor_x = canvas_width / ((max_x - min_x) or 1)
        factor_y = canvas_height / ((max_y - min_y) or 1)
        return (factor_x, factor_y)

    def _to_pixels(self, pos_x: int, pos_y: int) -> Tuple[int, int]:
        """Convert map coordinates to screen pixel positions.

        Args:
            pos_x: The x coordinate on the map.
            pos_y: The y coordinate on the map.

        Returns:
            A tuple of (pixel_x, pixel_y) on the screen.
        """
        min_x, _, min_y, _ = self.boundaries
        factor_x, factor_y = self.scale_factor
        pixel_x = PADDING + (pos_x - min_x) * factor_x
        dynamic_height = min(factor_y, (factor_y + factor_x) // 2)
        pixel_y = PADDING + (pos_y - min_y) * dynamic_height
        return (int(pixel_x), int(pixel_y))
