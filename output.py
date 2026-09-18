"""Text-based output for displaying simulation results."""

from typing import Any, Dict, List


class Output:
    """Formats and prints simulation turns to standard output."""

    def __init__(self) -> None:
        """Initialize the output handler."""

    def display(self, turns: List[Dict[int, Any]]) -> None:
        """Print each turn showing which drone reached a hub or is in transit.

        Args:
            turns: A list of turn dictionaries mapping drone IDs to hub names
                or in-transit connection tuples.
        """
        for i, turn in enumerate(turns[1:], 1):
            print(f"Turn {i}: ", end="")
            for drone_id, hub in turn.items():
                if isinstance(hub, str):
                    print(f"D{drone_id}-{hub} ", end="")
                else:
                    hub1, hub2 = hub
                    print(f"D{drone_id}-{hub1}-{hub2} ", end="")
            print()
