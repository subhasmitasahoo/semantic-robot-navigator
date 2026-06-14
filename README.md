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

### Step 9-10: Dynamic obstacles, re-planning, and waiting (done)
`navigator/main.py` — `navigate()` now steps the robot one cell at a
time, re-running A* from its current position every step. A temporary
obstacle can appear mid-route (simulating a person blocking a doorway)
and disappear after a few steps. If A* returns no path, the robot
waits in place and retries, giving up only after `max_wait` failed
attempts.

### Step 11-12: Embedding-based semantics + confidence (done)
`navigator/semantics.py`:
- `OBJECT_DESCRIPTIONS` — natural-language description per object.
- `match_goal_embedding()` — ranks objects by cosine similarity
  (via `sentence-transformers`, model `all-MiniLM-L6-v2`) between the
  query and each object's description.
- `explain_choice()` — picks the top match, prints a human-readable
  explanation, and flags low-confidence picks (score < `CONFIDENCE_THRESHOLD = 0.3`).

`navigator/main.py` — `navigate()` now uses `explain_choice()` to pick
a target and reports confidence before planning/navigating.

#### Try it
```bash
python3 -m navigator.main
```

### What's next
- **Eval set**: a list of `(query, expected_label)` pairs + a script that measures match accuracy — this is where your eval/ranking background really fits.
Given your background, I'd guess **embeddings + eval set together** would be the most interesting next pair — replace the keyword matcher, then measure how much better (or differently-wrong) it is on a small benchmark. Want to go that direction, or pick something else?