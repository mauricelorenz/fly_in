from enum import Enum
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Any


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


class Drone:
    def __init__(self, drone_id: int) -> None:
        self.drone_id = drone_id


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


def get_input_list(path: Path) -> List[Tuple[int, str]]:
    result = []
    with open(path) as f:
        for number, line in enumerate(f, 1):
            if not line.startswith("#") and line.strip():
                result.append((number, line.strip()))
    return result


def parse(path: Path) -> Any:
    input_list = get_input_list(path) # noqa
