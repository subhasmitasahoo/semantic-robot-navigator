# Semantic Robot Navigator

A simulated 2D indoor robot that follows natural-language goals like
"I need caffeine" or "I'm lost" by combining classic robotics (mapping,
A* planning, navigation, re-planning around dynamic obstacles) with a
semantic layer (embedding-based intent matching, confidence, eval).

## Setup

```bash
pip install -r requirements.txt
```

Run modules from the project root:

```bash
python3 -m navigator.visualize   # view the map
python3 -m navigator.main        # end-to-end demo: goal -> plan -> navigate
python3 -m navigator.eval        # semantic matcher benchmark
```

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
`navigator/semantics.py` — keyword-based `match_goal()`. See
[Semantic Matching](docs/semantic-matching.md) for full details.

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

### Step 11-13: Embeddings, confidence, and eval (done)
Embedding-based matching (`match_goal_embedding`), confidence reporting
(`explain_choice`), and a 16-query benchmark (`navigator/eval.py`).
Richer object descriptions improved embedding accuracy from 68.75% → 100% (see [iterations](docs/semantic-matching.md#interesting-analysis)).

→ **[Semantic Matching — full write-up + analysis](docs/semantic-matching.md)**

### Step 15: Visualization polish (done)
`navigator/visualize.py` — `animate_path()` now accepts a `subtitle`,
rendered below the map. `navigator/main.py` builds this subtitle from
`explain_choice()`'s output: chosen target, its description, and the
confidence score (flagged as "confident" or "low-confidence guess").

#### Try it
```bash
python3 -m navigator.main
python3 -m navigator.eval
```
