import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any
from models import Zone, Drone, Hub, Connection
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
                if hub_list or connection_list:
                    raise ParsingError(
                        ("'nb_drones' must be defined before hubs and "
                         "connections"), line_number
                    )
                drone_list = self._create_drones(content, line_number)
            elif directive in ("start_hub", "hub", "end_hub"):
                if not drone_list:
                    raise ParsingError(
                        f"'nb_drones' must be defined before '{directive}'",
                        line_number
                    )
                if connection_list:
                    raise ParsingError(
                        f"'{directive}' cannot be defined after connections",
                        line_number
                    )
                hub_list.append(
                    self._create_hub(directive, content, line_number)
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
                    self._create_connection(content, line_number)
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
        nb_drones = int(content)
        return [Drone(i + 1) for i in range(nb_drones)]

    def _create_hub(
        self, directive: str, content: str, line_number: int
    ) -> Hub:
        line_list = [directive, content]
        hub_type = line_list[0].strip()
        params = line_list[1].strip().split()[:3]
        optional_dict: Dict[str, Any] = {}
        if "[" in line_list[1]:
            optional_params = (
                line_list[1][line_list[1].index("["):].strip("[]")
            )
            for pair in optional_params.split():
                key, value = pair.split("=", maxsplit=1)
                optional_dict[key] = value
        name = params[0]
        pos_x = int(params[1])
        pos_y = int(params[2])
        is_start = (hub_type == "start_hub")
        is_end = (hub_type == "end_hub")
        if "zone" in optional_dict:
            optional_dict["zone"] = Zone[optional_dict["zone"].upper()]
        if is_start or is_end:
            optional_dict["max_drones"] = sys.maxsize
        elif "max_drones" in optional_dict:
            optional_dict["max_drones"] = int(optional_dict["max_drones"])
        return Hub(name, pos_x, pos_y, is_start, is_end, **optional_dict)

    def _create_connection(self, content: str, line_number: int) -> Connection:
        connection = content.strip()
        optional_dict: Dict[str, Any] = {}
        if "[" in connection:
            optional_params = connection[connection.index("["):].strip("[]")
            for pair in optional_params.split():
                key, value = pair.split("=", maxsplit=1)
                optional_dict[key] = value
            connection = connection[:connection.index("[")].strip()
        hub1, hub2 = connection.strip().split("-")
        if "max_link_capacity" in optional_dict:
            optional_dict["max_link_capacity"] = int(
                optional_dict["max_link_capacity"]
            )
        return Connection(hub1, hub2, **optional_dict)
