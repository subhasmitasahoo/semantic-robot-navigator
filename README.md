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

### Step 13: Eval set + matcher comparison (done)
`navigator/eval.py` — 16 `(query, expected_label)` pairs; runs both
`match_goal` (keyword) and `match_goal_embedding` and reports per-query
results + accuracy.

#### Try it
```bash
python3 -m navigator.main
python3 -m navigator.eval
```

### Interesting analysis
Full run saved in [`data/test/matcher_eval_results.txt`](data/test/matcher_eval_results.txt).

On this 16-query benchmark, **keyword matching beat embeddings** (81.25% vs 68.75%) — counterintuitive at first, but the failures tell a clear story:

| Matcher | Accuracy | Strengths | Weak spots |
|---------|----------|-----------|------------|
| Keyword | 81.25% | Exact word hits (`caffeine`, `toilet`, `shopping`) | Paraphrases with no keyword overlap (`I'm thirsty`, `wash my hands`, `I'm lost`) → no match |
| Embedding | 68.75% | Strong on clear intent (`where can I get food` 0.50, `where's the toilet` 0.73) | Short/vague queries drift to wrong labels (`I'm thirsty` → restroom, `I'm lost` → restroom); `info_desk` is especially weak (0/3) |

Takeaways:
- **Hand-tuned keywords win on a tiny mall map** because the eval queries overlap heavily with the keyword lists we wrote — embeddings generalize in theory but lose here without richer object descriptions.
- **Both matchers fail on paraphrase** — keyword returns `None`, embedding often picks a plausible-but-wrong label with low confidence.
- **Confidence threshold (0.3) would flag most embedding misses** — several wrong picks score below 0.3, so `explain_choice()` can surface uncertainty even when top-1 is wrong.
- **Next lever**: richer `OBJECT_DESCRIPTIONS` (synonyms, use-cases) or a hybrid ranker (keyword + embedding) rather than swapping one for the other.