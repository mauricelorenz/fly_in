import heapq
from typing import List, Tuple, Dict, Any
from models import Drone, Hub, Connection, Zone


class Simulation:
    def __init__(
        self, objects: Tuple[List[Drone], List[Hub], List[Connection]]
    ) -> None:
        self.drones, self.hubs, self.connections = objects
        self.hub_lookup = {h.name: h for h in self.hubs}
        self.adjacency = self._build_adjacency(self.hubs, self.connections)
        self.occupied_hubs: Dict[Tuple[str, int], int] = {}
        self.occupied_connections: Dict[Tuple[str, str, int], int] = {}
        self.start_name = next(h.name for h in self.hubs if h.is_start)
        self.end_name = next(h.name for h in self.hubs if h.is_end)

    def _build_adjacency(
        self, hubs: List[Hub], connections: List[Connection]
    ) -> Dict[str, List[Connection]]:
        adjacency: Dict[str, List[Connection]] = {h.name: [] for h in hubs}
        for c in connections:
            adjacency[c.hub1].append(c)
            adjacency[c.hub2].append(c)
        return adjacency

    def _is_hub_free(self, hub: Hub, turn: int) -> bool:
        hub_count = self.occupied_hubs.get((hub.name, turn), 0)
        return hub_count < hub.max_drones

    def _is_connection_free(
        self, connection: Connection, start_turn: int, cost: int
    ) -> bool:
        for t in range(start_turn, start_turn + cost):
            sorted_hub1, sorted_hub2 = sorted(
                (connection.hub1, connection.hub2)
            )
            key = (sorted_hub1, sorted_hub2, t)
            connection_count = self.occupied_connections.get(key, 0)
            if connection_count >= connection.max_link_capacity:
                return False
        return True

    def _find_single_path(self, start: str, end: str) -> List[Tuple[str, int]]:
        queue = [(0, 0, start)]
        came_from = {}
        visited = set()
        while queue:
            turn, penalty, hub = heapq.heappop(queue)
            if hub == end:
                break
            if (hub, turn) in visited:
                continue
            visited.add((hub, turn))
            for connection in self.adjacency[hub]:
                neighbor_name = (
                    connection.hub2 if connection.hub1 == hub
                    else connection.hub1
                )
                neighbor_hub = self.hub_lookup[neighbor_name]
                if neighbor_hub.zone == Zone.BLOCKED:
                    continue
                cost = 2 if neighbor_hub.zone == Zone.RESTRICTED else 1
                new_turn = turn + cost
                new_penalty = penalty + (
                    0 if neighbor_hub.zone == Zone.PRIORITY else 1
                )
                if not self._is_hub_free(neighbor_hub, new_turn):
                    continue
                if not self._is_connection_free(connection, turn, cost):
                    continue
                heapq.heappush(queue, (new_turn, new_penalty, neighbor_name))
                came_from[(neighbor_name, new_turn)] = (hub, turn)
            wait_turn = turn + 1
            if self._is_hub_free(self.hub_lookup[hub], wait_turn):
                heapq.heappush(queue, (wait_turn, penalty, hub))
                came_from[(hub, wait_turn)] = (hub, turn)
        path = []
        current = (hub, turn)
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.append(current)
        path.reverse()
        return path

    def _reserve_path(self, path: List[Tuple[str, int]]) -> None:
        for hub_name, turn in path:
            hub_key = (hub_name, turn)
            self.occupied_hubs[hub_key] = (
                self.occupied_hubs.get(hub_key, 0) + 1
            )
        for i in range(len(path) - 1):
            hub1, turn1 = path[i]
            hub2, turn2 = path[i + 1]
            for t in range(turn1, turn2):
                sorted_hub1, sorted_hub2 = sorted((hub1, hub2))
                connection_key = (sorted_hub1, sorted_hub2, t)
                self.occupied_connections[connection_key] = (
                    self.occupied_connections.get(connection_key, 0) + 1
                )

    def _build_turns(
        self, drone_paths: Dict[int, List[Tuple[str, int]]]
    ) -> List[Dict[int, Any]]:
        turns_amount = 0
        for drone_id in drone_paths:
            for turn in drone_paths[drone_id]:
                if turn[1] > turns_amount:
                    turns_amount = turn[1]
        turns: List[Dict[int, Any]] = [{} for i in range(turns_amount + 1)]
        for drone_id, path in drone_paths.items():
            for i in range(len(path) - 1):
                hub1, turn1 = path[i]
                hub2, turn2 = path[i + 1]
                if hub1 != hub2:
                    turns[turn2][drone_id] = hub2
                    if turn2 - turn1 == 2:
                        turns[turn1 + 1][drone_id] = (hub1, hub2)
        return turns

    def solve(self) -> List[Dict[int, Any]]:
        drone_paths = {}
        for drone in self.drones:
            path = self._find_single_path(self.start_name, self.end_name)
            self._reserve_path(path)
            drone_paths[drone.drone_id] = path
        return self._build_turns(drone_paths)
