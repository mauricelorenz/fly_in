"""Data models for drones, hubs, connections, zones, and colors."""

from dataclasses import dataclass
from enum import Enum

COLORS = {
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
    "default": (200, 200, 200)
}


class Zone(Enum):
    """Zone types that affect how drones traverse hubs."""

    NORMAL = 1
    BLOCKED = 2
    RESTRICTED = 3
    PRIORITY = 4


@dataclass
class Drone:
    """A drone that must travel from the start hub to the end hub."""

    drone_id: int


@dataclass
class Hub:
    """A location on the map where drones can be positioned or pass through."""

    name: str
    pos_x: int
    pos_y: int
    is_start: bool
    is_end: bool
    zone: Zone = Zone.NORMAL
    color: str | None = None
    max_drones: int = 1


@dataclass
class Connection:
    """An edge linking two hubs with a limited traversal capacity."""

    hub1: str
    hub2: str
    max_link_capacity: int = 1
