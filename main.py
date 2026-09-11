import sys
from pathlib import Path
from parser import parse
from visualizer import Visualizer
from simulation import Simulation


def main() -> None:
    if len(sys.argv) >= 2:
        path = Path(sys.argv[1])
    else:
        path = Path("maps/easy/01_linear_path.txt")
    objects = parse(path)
    simulation = Simulation(objects)  # noqa
    visualizer = Visualizer(objects)
    test_turns = [
        {1: "start", 2: "start"},
        {1: "waypoint1", 2: "start"},
        {1: "waypoint2", 2: "waypoint1"},
        {1: "goal", 2: "waypoint2"},
        {1: "goal", 2: "goal"}
    ]
    visualizer.run(test_turns)


if __name__ == "__main__":
    main()
