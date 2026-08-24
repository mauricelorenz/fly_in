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


def get_objects(
    input_list: List[Tuple[int, str]]
) -> Tuple[List[Drone], List[Hub], List[Connection]]:
    nb_drones = None
    for line_number, line in input_list:
        if line.startswith("nb_drones"):
            nb_drones = int(line.split(":")[1].strip()) # noqa
        elif line.startswith(("start_hub", "hub", "end_hub")):
            pass
    return ([], [], [])


def parse(path: Path) -> Any:
    input_list = get_input_list(path) # noqa
