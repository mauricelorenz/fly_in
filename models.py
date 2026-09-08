from enum import Enum
from dataclasses import dataclass


class ParsingError(Exception):
    def __init__(self, line_number: int, message: str) -> None:
        self.line_number = line_number
        self.message = message
        super().__init__(f"Error in line {self.line_number}: {self.message}")


class Zone(Enum):
    NORMAL = 1
    BLOCKED = 2
    RESTRICTED = 3
    PRIORITY = 4


@dataclass
class Drone:
    drone_id: int


@dataclass
class Hub:
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
    hub1: str
    hub2: str
    max_link_capacity: int = 1
