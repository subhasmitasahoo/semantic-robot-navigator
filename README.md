## Progress

### Step 1: Grid Map (done)
`navigator/grid_map.py` — `GridMap` class: 2D free/obstacle grid + named
objects placed at (x, y) coordinates. Includes `neighbors()` for
4-connected walkable cells.

### Step 2: Example World (done)
`navigator/world.py` — `build_mall_world()`: 20x12 grid, mall-themed
rooms with doorways, labeled objects (`food_court`, `clothing_store`,
`restroom`, `info_desk`, `exit`).

### Step 3: Visualization (done)
`navigator/visualize.py` — `plot_map()` renders the grid + objects +
optional path/robot marker. `animate_path()` animates the robot
stepping along a path.

### Step 4: A* Path Planning (done)
`navigator/planner.py` — `astar()` finds the shortest path between two
cells using Manhattan-distance heuristic. Returns `None` if no path
exists (e.g. disconnected rooms).

### Step 5-6: Path drawing + animation (done)
Path is drawn on the map and the robot animates along it cell by cell.

### Step 7: Natural-language goal matching (done)
`navigator/semantics.py` — `match_goal()` ranks objects by keyword
overlap with a natural-language query (e.g. "I need caffeine" ->
`food_court`).

### Step 8: End-to-end demo (done)
`navigator/main.py` — `navigate(m, start, query)`: ranks targets,
plans a path to the best *reachable* match, falling back to the next
match if unreachable, then animates the result.

#### Try it
```bash
pip install -r requirements.txt
python3 -m navigator.main
