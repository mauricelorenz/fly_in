from pathlib import Path
from typing import List, Tuple, Dict, Any
from models import Zone, Drone, Hub, Connection


class Parser:
    def __init__(self, path: Path) -> None:
        self.path = path

    def parse(self) -> Tuple[List[Drone], List[Hub], List[Connection]]:
        input_list = self.get_input_list()
        return self.get_objects(input_list)

    def get_input_list(self) -> List[Tuple[int, str]]:
        result = []
        with open(self.path) as f:
            for number, line in enumerate(f, 1):
                if not line.startswith("#") and line.strip():
                    result.append((number, line.strip()))
        return result

    def get_objects(
        self, input_list: List[Tuple[int, str]]
    ) -> Tuple[List[Drone], List[Hub], List[Connection]]:
        hub_list = []
        connection_list = []
        for line_number, line in input_list:
            if line.startswith("nb_drones"):
                nb_drones = int(line.split(":")[1].strip())
                drone_list = [Drone(i + 1) for i in range(nb_drones)]
            elif line.startswith(("start_hub", "hub", "end_hub")):
                hub_list.append(self.create_hub(line))
            elif line.startswith("connection"):
                connection_list.append(self.create_connection(line))
        return (drone_list, hub_list, connection_list)

    def create_hub(self, line: str) -> Hub:
        line_list = line.split(":")
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
        if "max_drones" in optional_dict:
            optional_dict["max_drones"] = int(optional_dict["max_drones"])
        return Hub(name, pos_x, pos_y, is_start, is_end, **optional_dict)

    def create_connection(self, line: str) -> Connection:
        connection = line.split(":")[1].strip()
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
