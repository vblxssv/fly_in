*This project has been created as part of the 42 curriculum by vborysov.*

# Fly-in

## Description

Fly-in is a Python simulation that routes a fleet of drones from a start hub
to an end hub through a graph of connected zones. The goal is to deliver every
drone in as few simulation turns as possible while respecting zone capacities,
connection capacities, blocked zones, and two-turn restricted-zone movements.

The project includes a parser for the supplied map format, a time-aware routing
engine, textual turn-by-turn output, and an Arcade graphical visualization.

## Requirements

- Python 3.10 or newer
- Dependencies listed in `requirements.txt`
- GNU Make (for the provided Makefile commands)

## Instructions

### Installation

Create the virtual environment and install dependencies:

```bash
make install
```

### Usage

Run the simulation with the default map and file logger:

```bash
make run
```

Choose a map and print turns to the console:

```bash
make run MAP=maps/easy/01_linear_path.txt LOGGER=console
```

Run the application under Python's debugger:

```bash
make debug MAP=maps/easy/01_linear_path.txt LOGGER=console
```

Run static checks:

```bash
make lint
```

Remove the virtual environment and generated caches:

```bash
make clean
```

The command-line interface also accepts these options directly:

```bash
.venv/bin/python3 main.py --map maps/easy/01_linear_path.txt --logger console
```

- `--map` is the path to an input map file.
- `--logger` is either `console` or `file`. File output is written to
  `output.txt`.

## Input format

A map begins with the number of drones, followed by hub and connection
definitions:

```text
nb_drones: 2
start_hub: start 0 0 [color=green]
end_hub: goal 2 0 [color=red]
hub: middle 1 0 [max_drones=1]
connection: start-middle
connection: middle-goal
```

Zone metadata supports `zone`, `max_drones`, and `color`. Connection metadata
supports `max_link_capacity`. The supported zone types are `normal`,
`restricted`, `priority`, and `blocked`.

## Algorithm and implementation strategy

The application models the map as an undirected graph. Before planning paths,
it runs reverse Dijkstra from the end hub to compute an admissible cost estimate
for every zone. These distances are used as the heuristic for the route search.

Routes are planned with Cooperative A*: drones are handled one at a time, and
each drone uses a space-time A* search from the start to the end. After a route
is found, its zone and connection occupancy is saved in a reservation table.
Every following search consults these reservations, which lets it select another
route or add a wait action instead of creating a collision or exceeding a
capacity limit.

Each A* state contains a destination zone, a time step, and whether the drone
is in a zone or on a connection. This represents restricted zones as a
two-turn movement: entering the connection consumes the first turn, and the
drone reaches the destination on the next one. Blocked zones are never added
to a route, and priority zones have a lower routing cost.

The reservation table enforces `max_drones` and `max_link_capacity`. Start and
end hubs are intentionally exempt from zone occupancy limits, as required by
the subject.

## Visual representation

The Arcade renderer displays the graph, zone colors, connections, and animated
drone positions. Its HUD shows the current turn, the number of moving drones,
average turns per drone, and playback speed. Use Space to pause, R to restart,
Up/Down to change speed, and Escape to close the window.

The logger also provides a compact textual representation: each output line is
one simulation turn, and each item has the form `D<ID>-<destination>`.

## Resources

- [Python documentation](https://docs.python.org/3/)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [Arcade documentation](https://api.arcade.academy/)
- [A* search algorithm](https://en.wikipedia.org/wiki/A*_search_algorithm)
- [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)

## AI usage

AI was used strictly as an **assistive tool for learning, explanation, and documentation**, while all implementation and final design decisions were made by the author of the project.