*This project has been created as part of the 42 curriculum by mlorenz.*

# Fly-in

## Description

Fly-in is a drone routing simulation system that efficiently navigates a fleet of drones from a start hub to an end hub through a graph of interconnected hubs. The system parses custom map files, computes collision-free paths using optimized pathfinding, and visualizes the simulation both in the terminal and through an interactive Pygame-based GUI.

The project models a real-world-inspired drone logistics scenario where drones must respect zone types (normal, restricted, priority, blocked), hub capacity limits (`max_drones`), and connection capacity limits (`max_link_capacity`). The goal is to deliver all drones from the start to the end hub in the fewest possible simulation turns.

### Features

- **Custom map parser** supporting zone types, colors, capacity constraints, and connection metadata
- **Greedy pathfinding with Dijkstra-style priority queue** that accounts for zone costs, capacity, and turn-based scheduling
- **Terminal output** showing step-by-step drone movements per turn
- **Interactive Pygame GUI** displaying the network, drone positions, and turn-by-turn progression
- **Strict type safety** via mypy and flake8 linting
- **Object-oriented architecture** with dataclasses and enums

## Instructions

### Prerequisites

- Python 3.10 or later
- `pip` (or any package manager)

### Installation

```bash
make install
```

This creates a virtual environment in `.venv/` and installs all dependencies from `requirements.txt`.

### Running the Simulation

**With Pygame GUI (default):**

```bash
make run
```

**Terminal output only:**

```bash
make run GUI=
```

**Running a specific map:**

```bash
make run MAP=maps/medium/02_circular_loop.txt
```

You can also run directly with Python:

```bash
python3 main.py <map_file> [--gui]
```

Press **Space** to advance turns in the GUI. Press **Escape** to close.

### Available Maps

| Difficulty | Map | Drones | Description |
|------------|-----|--------|-------------|
| Easy | `01_linear_path.txt` | 2 | Simple linear progression |
| Easy | `02_simple_fork.txt` | 3 | Basic path splitting |
| Easy | `03_basic_capacity.txt` | 4 | Capacity constraints |
| Medium | `01_dead_end_trap.txt` | 5 | Dead end traps |
| Medium | `02_circular_loop.txt` | 6 | Circular paths with restricted zones |
| Medium | `03_priority_puzzle.txt` | 4 | Priority zone optimization |
| Hard | `01_maze_nightmare.txt` | 8 | Complex maze with traps and loops |
| Hard | `02_capacity_hell.txt` | 12 | Extreme capacity constraints |
| Hard | `03_ultimate_challenge.txt` | 15 | All challenges combined |
| Challenger | `01_the_impossible_dream.txt` | 25 | Quasi-unsolvable |

### Linting

```bash
make lint        # Standard lint (flake8 + mypy)
make lint-strict # Strict lint (--strict mode)
```

### Debugging

```bash
make debug
```

### Cleaning

```bash
make clean
```

## Architecture

```
main.py          # Entry point: parses CLI args, runs simulation, displays output
parser.py        # Parses map files into Drone, Hub, and Connection objects
models.py        # Dataclasses (Drone, Hub, Connection), Zone enum, and COLORS dict
simulation.py    # Pathfinding solver with priority queue and capacity tracking
output.py        # Formats and prints turn-by-turn results to terminal
visualizer.py    # Pygame-based interactive GUI
exceptions.py    # Custom exceptions for parsing and pathfinding errors
```

## Resources

- [Dijkstra's Shortest Path Algorithm](https://www.freecodecamp.org/news/dijkstras-shortest-path-algorithm-visual-introduction/) — reference for the priority-queue-based shortest-path approach used in the solver
- [Pygame Documentation](https://www.pygame.org/docs/) — library used for the interactive GUI
- [Python typing Module](https://docs.python.org/3/library/typing.html) — type hints used throughout the codebase
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/) — docstring style guide followed in this project
- [Flake8 Documentation](https://flake8.pycqa.org/) — linter used for code style enforcement
- [mypy Documentation](https://mypy-lang.org/) — static type checker used for type safety

**AI usage:** AI assistants were used for brainstorming the pathfinding approach, debugging edge cases, adding docstrings, and drafting this README. The core algorithm implementation and integration were done manually.

## Algorithm and Implementation Strategy

### Pathfinding

The solver uses a **modified Dijkstra algorithm** with a priority queue that optimizes for two dimensions:

1. **Turn cost** (primary key): The number of simulation turns required to traverse a path, accounting for zone-type movement costs:
   - `normal`: 1 turn
   - `restricted`: 2 turns
   - `priority`: 1 turn

   Hubs with zone `blocked` are impassable and are skipped entirely during pathfinding.

2. **Penalty score** (secondary key): A tiebreaker that favors paths through priority zones, discouraging unnecessary traversal of restricted or normal zones when priority alternatives exist.

The algorithm runs **greedily** — one drone at a time, in sequence. Each drone's path is computed while respecting the occupancy reservations left by all previously routed drones. This means the first drone gets the globally optimal path, and subsequent drones adapt around the existing schedule.

### Capacity and Conflict Resolution

- **Hub occupancy** is tracked per turn in `occupied_hubs` (keyed by `(hub_name, turn)`).
- **Connection occupancy** is tracked per turn in `occupied_connections` (keyed by `(sorted_hub1, sorted_hub2, turn)`).
- Before routing a drone, the algorithm checks `_is_hub_free()` and `_is_connection_free()` at every candidate step, skipping routes that would violate capacity.
- **Waiting** is modeled explicitly: a drone can stay in its current hub if capacity allows, with the wait turn added to the priority queue as a candidate state.

### Restricted Zone Handling

Restricted zones cost 2 turns. During traversal, the drone occupies the connection for the full 2-turn duration and cannot be rerouted mid-transit. The `_build_turns()` method handles this by emitting an in-transit marker (`(hub1, hub2)`) at `turn + 1` for restricted movements.

### Turn Construction

After all paths are computed, `_build_turns()` converts the per-drone path lists into a unified turn-by-turn structure: a list of dictionaries, each mapping drone IDs to their position (hub name or in-transit tuple) for that turn. This structure drives both terminal output and the GUI.

## Visual Representation

### Terminal Output

The `Output` class prints one line per simulation turn. Each line lists all drone movements in the format `D<ID>-<hub>` (arrived) or `D<ID>-<hub1>-<hub2>` (in transit). Only drones that move on a given turn are shown; delivered drones are omitted from subsequent turns.

### Pygame GUI

The `Visualizer` class provides an interactive graphical interface:

- **Hubs** are rendered as colored circles, with colors matching the map metadata. Hub names and zone stats (restricted/priority, max capacity) are displayed below each hub.
- **Connections** are drawn as lines between hubs.
- **Drones** are shown as gray circles at their current positions. When multiple drones occupy the same position, they are grouped with a count label (e.g., `3x`).
- **In-transit drones** (traversing restricted zones over 2 turns) are positioned at the midpoint of their connection.
- The simulation advances one turn at a time via **Spacebar** press.
- Window dimensions adapt to the map boundaries using a computed scale factor with padding.
