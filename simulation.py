from typing import List, Tuple, Dict
from models import Drone, Hub, Connection


class Simulation:
    def __init__(
        self, objects: Tuple[List[Drone], List[Hub], List[Connection]]
    ) -> None:
        self.drones, self.hubs, self.connections = objects
        self.hub_lookup = {h.name: h for h in self.hubs}
        self.adjacency = self._get_adjacency(self.hubs, self.connections)

    def _get_adjacency(
        self, hubs: List[Hub], connections: List[Connection]
    ) -> Dict[str, List[Connection]]:
        adjacency: Dict[str, List[Connection]] = {h.name: [] for h in hubs}
        for c in connections:
            adjacency[c.hub1].append(c)
            adjacency[c.hub2].append(c)
        return adjacency
