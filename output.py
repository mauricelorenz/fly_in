from typing import Any, Dict, List


class Output:
    def __init__(self) -> None:
        pass

    def display(self, turns: List[Dict[int, Any]]) -> None:
        for i, turn in enumerate(turns[1:], 1):
            print(f"Turn {i}: ", end="")
            for drone_id, hub in turn.items():
                if isinstance(hub, str):
                    print(f"D{drone_id}-{hub} ", end="")
                else:
                    hub1, hub2 = hub
                    print(f"D{drone_id}-{hub1}-{hub2} ", end="")
            print()
