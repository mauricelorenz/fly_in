"""Custom exceptions for map parsing and pathfinding errors."""


class ParsingError(Exception):
    """Raised when the map file contains invalid or malformed instructions."""

    def __init__(self, message: str, line_number: int | None = None) -> None:
        """Initialize a ParsingError.

        Args:
            message: A human-readable description of the error.
            line_number: The line number in the input file where the error
                occurred, if known.
        """
        self.message = message
        self.line_number = line_number
        show_line = f" in line {self.line_number}" if self.line_number else ""
        super().__init__(f"ParsingError{show_line}: {self.message}")


class PathError(Exception):
    """Raised when no valid path exists between the start and end hubs."""

    def __init__(self, start: str, end: str) -> None:
        """Initialize a PathError.

        Args:
            start: The name of the start hub.
            end: The name of the end hub.
        """
        self.start = start
        self.end = end
        super().__init__(
            f"PathError: No path found from '{self.start}' to '{self.end}'"
        )
