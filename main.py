import sys
from pathlib import Path
from parser import parse
from visualizer import Visualizer


def main() -> None:
    if len(sys.argv) >= 2:
        path = Path(sys.argv[1])
    else:
        path = Path("maps/easy/01_linear_path.txt")
    objects = parse(path)
    window = Visualizer(objects)  # noqa
    window.run()


if __name__ == "__main__":
    main()
