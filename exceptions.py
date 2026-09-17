class ParsingError(Exception):
    def __init__(self, message: str, line_number: int | None = None) -> None:
        self.message = message
        self.line_number = line_number
        show_line = f" in line {self.line_number}" if self.line_number else ""
        super().__init__(f"ParsingError{show_line}: {self.message}")


class PathError(Exception):
    def __init__(self, start: str, end: str) -> None:
        self.start = start
        self.end = end
        super().__init__(
            f"PathError: No path found from '{self.start}' to '{self.end}'"
        )
