import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any
from models import COLORS, Zone, Drone, Hub, Connection
from exceptions import ParsingError


class Parser:
    def __init__(self, path: Path) -> None:
        self.path = path

    def parse(self) -> Tuple[List[Drone], List[Hub], List[Connection]]:
        input_list = self._get_input_list()
        return self._get_objects(input_list)

    def _get_input_list(self) -> List[Tuple[int, str]]:
        result = []
        try:
            with open(self.path) as f:
                for number, line in enumerate(f, 1):
                    if not line.startswith("#") and line.strip():
                        result.append((number, line.strip()))
            if not result:
                raise ParsingError("File is empty or contains no instructions")
            return result
        except FileNotFoundError:
            raise ParsingError(f"File '{self.path}' not found")
        except PermissionError:
            raise ParsingError(f"Permission for file '{self.path}' denied")
        except IsADirectoryError:
            raise ParsingError(f"'{self.path}' is a directory")
        except UnicodeDecodeError:
            raise ParsingError(
                f"File '{self.path}' is not a valid UTF-8 text file"
            )

    def _get_objects(
        self, input_list: List[Tuple[int, str]]
    ) -> Tuple[List[Drone], List[Hub], List[Connection]]:
        drone_list: List[Drone] = []
        hub_list: List[Hub] = []
        connection_list: List[Connection] = []
        for line_number, line in input_list:
            directive, content = self._split_line(line_number, line)
            if directive == "nb_drones":
                if drone_list:
                    raise ParsingError(
                        "'nb_drones' already defined", line_number
                    )
                drone_list = self._create_drones(content, line_number)
            elif directive in ("start_hub", "hub", "end_hub"):
                if not drone_list:
                    raise ParsingError(
                        f"'nb_drones' must be defined before '{directive}'",
                        line_number
                    )
                hub_list.append(
                    self._create_hub(directive, content, line_number, hub_list)
                )
            elif directive == "connection":
                if not drone_list:
                    raise ParsingError(
                        "'nb_drones' must be defined before connections",
                        line_number
                    )
                if not hub_list:
                    raise ParsingError(
                        "'connection' cannot be defined before hubs",
                        line_number
                    )
                connection_list.append(
                    self._create_connection(
                        content, line_number, hub_list, connection_list
                    )
                )
            else:
                raise ParsingError(
                    f"Unknown directive '{directive}'", line_number
                )
        if not any(h.is_start for h in hub_list):
            raise ParsingError("Missing mandatory 'start_hub'")
        if not any(h.is_end for h in hub_list):
            raise ParsingError("Missing mandatory 'end_hub'")
        return (drone_list, hub_list, connection_list)

    def _split_line(self, line_number: int, line: str) -> Tuple[str, str]:
        try:
            directive, content = map(str.strip, line.split(":", maxsplit=1))
            if not directive or not content:
                raise ParsingError(
                    "Directive or content cannot be empty", line_number
                )
            return (directive, content)
        except ValueError:
            raise ParsingError("Missing separator ':'", line_number)

    def _create_drones(self, content: str, line_number: int) -> List[Drone]:
        try:
            nb_drones = int(content)
            if nb_drones <= 0:
                raise ValueError
        except ValueError:
            raise ParsingError(
                (f"Invalid number of drones '{content}'. "
                 "Expected positive integer"), line_number
            )
        return [Drone(i + 1) for i in range(nb_drones)]

    def _create_hub(
        self, directive: str, content: str,
        line_number: int, hub_list: List[Hub]
    ) -> Hub:
        params = content.split()[:3]
        if len(params) < 3:
            raise ParsingError("Missing positional argument", line_number)
        optional_dict: Dict[str, Any] = {}
        if "[" in content:
            if (content.count("[") != 1 or content.count("]") != 1
                    or not content.endswith("]")):
                raise ParsingError(
                    "Invalid bracket formatting for optional arguments",
                    line_number
                )
            optional_params = (
                content[content.index("["):].strip("[]")
            )
            for pair in optional_params.split():
                try:
                    key, value = pair.split("=", maxsplit=1)
                except ValueError:
                    raise ParsingError(
                        (f"Malformed optional argument '{pair}'. "
                         "Expected 'key=value'"), line_number
                    )
                if key not in ("zone", "color", "max_drones"):
                    raise ParsingError(f"Invalid key '{key}'", line_number)
                optional_dict[key] = value
        name = params[0]
        if "-" in name:
            raise ParsingError("'-' cannot be part of hub name", line_number)
        for hub in hub_list:
            if name == hub.name:
                raise ParsingError(
                    f"Hub name '{name}' used twice", line_number
                )
        try:
            pos_x = int(params[1])
            pos_y = int(params[2])
        except ValueError:
            raise ParsingError(
                ("Invalid coordinates. Expected '<int x> <int y>', got "
                    f"'{params[1]} {params[2]}'"), line_number
                )
        if any(pos_x == h.pos_x and pos_y == h.pos_y for h in hub_list):
            raise ParsingError(
                f"A hub with coordinates '{pos_x} {pos_y}' already exists",
                line_number
            )
        is_start = (directive == "start_hub")
        is_end = (directive == "end_hub")
        try:
            if "zone" in optional_dict:
                optional_dict["zone"] = Zone[optional_dict["zone"].upper()]
        except KeyError:
            raise ParsingError(
                f"Invalid zone type '{optional_dict['zone']}'", line_number
            )
        if is_start or is_end:
            optional_dict["max_drones"] = sys.maxsize
        elif "max_drones" in optional_dict:
            try:
                optional_dict["max_drones"] = int(optional_dict["max_drones"])
                if optional_dict["max_drones"] <= 0:
                    raise ValueError
            except ValueError:
                raise ParsingError(
                    ("Invalid value for max_drones "
                     f"'{optional_dict['max_drones']}'. "
                     "Expected positive integer"), line_number
                )
        color = optional_dict.get("color", None)
        if color and color not in COLORS:
            optional_dict["color"] = "default"
            print(f"Warning in line {line_number}: Unknown color '{color}'. "
                  f"Falling back to default", file=sys.stderr)
        return Hub(name, pos_x, pos_y, is_start, is_end, **optional_dict)

    def _create_connection(
        self, content: str, line_number: int,
        hub_list: List[Hub], connection_list: List[Connection]
    ) -> Connection:
        optional_dict: Dict[str, Any] = {}
        if "[" in content:
            if (content.count("[") != 1 or content.count("]") != 1
                    or not content.endswith("]")):
                raise ParsingError(
                    "Invalid bracket formatting for optional arguments",
                    line_number
                )
            optional_params = (
                content[content.index("["):].strip("[]")
            )
            for pair in optional_params.split():
                try:
                    key, value = pair.split("=", maxsplit=1)
                except ValueError:
                    raise ParsingError(
                        (f"Malformed optional argument '{pair}'. "
                         "Expected 'key=value'"), line_number
                    )
                if key != "max_link_capacity":
                    raise ParsingError(f"Invalid key '{key}'", line_number)
                optional_dict[key] = value
        try:
            hubs = content.split()[0]
            hub1, hub2 = hubs.split("-")
            if not hub1 or not hub2:
                raise ValueError
        except ValueError:
            raise ParsingError(
                ("Invalid connection format. Expected '<hub1>-<hub2>', got "
                    f"'{hubs}'"), line_number
                )
        if not any(h.name == hub1 for h in hub_list):
            raise ParsingError(f"Hub '{hub1}' does not exist", line_number)
        if not any(h.name == hub2 for h in hub_list):
            raise ParsingError(f"Hub '{hub2}' does not exist", line_number)
        if hub1 == hub2:
            raise ParsingError(
                f"Connection cannot link '{hub1}' to itself", line_number
            )
        if any((hub1 == c.hub1 and hub2 == c.hub2)
               or (hub1 == c.hub2 and hub2 == c.hub1)
               for c in connection_list):
            raise ParsingError(
                f"Connection between '{hub1}' and '{hub2}' already exists",
                line_number
            )
        if "max_link_capacity" in optional_dict:
            try:
                optional_dict["max_link_capacity"] = int(
                    optional_dict["max_link_capacity"]
                )
                if optional_dict["max_link_capacity"] <= 0:
                    raise ValueError
            except ValueError:
                raise ParsingError(
                    ("Invalid value for max_link_capacity "
                     f"'{optional_dict['max_link_capacity']}'. "
                     "Expected positive integer"), line_number
                )
        return Connection(hub1, hub2, **optional_dict)
