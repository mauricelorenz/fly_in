import sys
from pathlib import Path
from parser import parse
from visualizer import Visualizer
from simulation import Simulation
from output import Output


def main() -> None:
    if len(sys.argv) >= 2:
        path = Path(sys.argv[1])
    else:
        path = Path("maps/easy/01_linear_path.txt")
    objects = parse(path)
    simulation = Simulation(objects)
    turns = simulation.solve()
    output = Output()
    output.display(turns)
    visualizer = Visualizer(objects)
    visualizer.run(turns)


if __name__ == "__main__":
    main()
