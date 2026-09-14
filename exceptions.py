class ParsingError(Exception):
    def __init__(self, line_number: int, message: str) -> None:
        self.line_number = line_number
        self.message = message
        super().__init__(f"Error in line {self.line_number}: {self.message}")


class PathError(Exception):
    def __init__(self, start: str, end: str) -> None:
        self.start = start
        self.end = end
        super().__init__(
            f"Error: No path found from {self.start} to {self.end}"
        )
