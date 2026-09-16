import os
import sys
from pathlib import Path
from parser import Parser
from simulation import Simulation
from output import Output
from exceptions import PathError, ParsingError
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
from visualizer import Visualizer  # noqa: E402


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <map file> [--gui]", file=sys.stderr)
        sys.exit(1)
    gui = len(sys.argv) >= 3 and sys.argv[2] == "--gui"
    try:
        parser = Parser(Path(sys.argv[1]))
        objects = parser.parse()
        simulation = Simulation(objects)
        turns = simulation.solve()
    except (PathError, ParsingError) as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    output = Output()
    output.display(turns)
    if gui:
        visualizer = Visualizer(objects)
        visualizer.run(turns)


if __name__ == "__main__":
    main()
