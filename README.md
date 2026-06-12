# Semantic Robot Navigator

A simulated 2D indoor robot that follows natural-language goals like
"go to the nearest place where I can make coffee" by combining classic
robotics (mapping, planning, navigation) with a semantic layer
(query understanding, ranking, confidence).

## Setup

```bash
pip install -r requirements.txt
```

Run modules from the project root:

```bash
python -m navigator.visualize
python -m navigator.world
```

## Progress

### Step 1: Grid Map (done)

`navigator/grid_map.py` — `GridMap` class representing a 2D grid of
free (0) / obstacle (1) cells, plus a dict of named objects
(`food_court`, `exit`, ...) placed at specific (x, y) coordinates.

### Step 2: Example World (done)

`navigator/world.py` — `build_mall_world()` builds a 20×12 grid
representing one floor of a small mall: outer walls, two interior
walls with doorway gaps, and labeled objects (`food_court`,
`clothing_store`, `restroom`, `info_desk`, `exit`).

### Step 3: Visualization (done)

`navigator/visualize.py` — renders the grid with matplotlib:
obstacles in black, free space in white, objects as blue dots with
labels. Also supports drawing a path and robot position (for later
steps).

## Coordinate convention

- **x** = column (increases left → right)
- **y** = row (increases top → bottom; `imshow` with `origin="upper"` puts row 0 at the top)
- Functions take `(x, y)` order; internally the grid is stored as `grid[y][x]` (row-major)

## Next steps

1. **A\* path planning** (`navigator/planner.py`) — find a path between two points on the grid
2. Draw the planned path on the map using `plot_map(path=...)`
3. Animate the robot moving along the path
4. Natural-language goal → target object (keyword/embedding matching), then plan a path to it
