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
        for turn in turns[1:]:
            formatted = [
                f"D{d}-{h}" if isinstance(h, str) else f"D{d}-{h[0]}-{h[1]}"
                for d, h in turn.items()
            ]
            print(" ".join(formatted))
