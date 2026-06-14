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

**What this means:** the "world" is just a grid of squares. Each square
is either empty (the robot can stand there) or a wall (it can't). Some
empty squares also have a label, like `coffee_machine` or `exit`, so we
know where things are. `x` = column (left/right), `y` = row (top/bottom,
counting down from the top). `neighbors()` looks at the square above,
below, left, and right of a given square, and returns only the ones that
are walkable — this is the basic building block everything else uses to
move around.

### Step 2: Example World (done)
`navigator/world.py` — `build_mall_world()`: 20x12 grid, mall-themed
rooms with doorways, labeled objects (`food_court`, `clothing_store`,
`restroom`, `info_desk`, `exit`).

**What this means:** a concrete example map — a small mall floor split
into a few rooms by walls, with gaps in the walls acting as doorways
between rooms. A handful of useful places (`food_court`, `restroom`,
etc.) are placed inside it. This is the map every later step runs on.

### Step 3: Visualization (done)
`navigator/visualize.py` — `plot_map()` renders the grid + objects +
optional path/robot marker. `animate_path()` animates the robot
stepping along a path.

**What this means:** turns the grid of numbers into a picture you can
actually look at — black squares for walls, white for open floor, blue
dots with labels for places like `restroom`. `animate_path()` additionally
draws a green square that visibly moves step by step along a route, so
you can watch the robot "walk".

### Step 4: A* Path Planning (done)
`navigator/planner.py` — `astar()` finds the shortest path between two
cells using Manhattan-distance heuristic. Returns `None` if no path
exists (e.g. disconnected rooms).

**What this means:** given a start square and a goal square, `astar()`
works out the shortest route between them, going only through walkable
squares. It's smart about *which* routes to try first — it estimates
"how far away is the goal in a straight line" and prioritizes routes
that seem to be heading the right direction, so it doesn't waste time
exploring obviously-wrong directions. If the goal is in a part of the
map that's completely walled off with no doorway, it correctly reports
"no path exists" instead of guessing.

### Step 5-6: Path drawing + animation (done)
Path is drawn on the map and the robot animates along it cell by cell.

**What this means:** combining Steps 3 and 4 — once `astar()` works out
a route, we draw it as a red line on the map and animate the green robot
square walking along it, square by square.

### Step 7: Natural-language goal matching (done)
`navigator/semantics.py` — keyword-based `match_goal()`. See
[Semantic Matching](docs/semantic-matching.md) for full details.

**What this means:** this is the first step toward understanding plain
English. Each place on the map (e.g. `food_court`) has a list of words
people might say when they want it (e.g. "coffee", "hungry", "snack").
`match_goal()` takes what the user typed, splits it into words, and
checks how many of those words overlap with each place's word list —
the place with the most overlap "wins". Simple, but only works if the
user happens to use one of the exact listed words.

### Step 8: End-to-end demo (done)
`navigator/main.py` — `navigate(m, start, query)`: ranks targets,
plans a path to the best *reachable* match, falling back to the next
match if unreachable, then animates the result.

**What this means:** the first version that ties everything together —
type a sentence, the system picks the best-matching place, checks A* can
actually get there, plans the route, and animates the robot walking to
it. If the top choice turns out to be unreachable, it tries the
next-best match instead of just giving up.

### Step 9-10: Dynamic obstacles, re-planning, and waiting (done)
`navigator/main.py` — `navigate()` now steps the robot one cell at a
time, re-running A* from its current position every step. A temporary
obstacle can appear mid-route (simulating a person blocking a doorway)
and disappear after a few steps. If A* returns no path, the robot
waits in place and retries, giving up only after `max_wait` failed
attempts.

**What this means:** real environments change while you're moving
through them — someone might step into a doorway you were about to use.
Instead of planning one route at the start and blindly following it, the
robot now re-plans *every single step*, using the map as it currently is.
If a new obstacle blocks the only way through, A* will (correctly) say
"no path" — so the robot waits a few steps (maybe the obstacle moves
away) before giving up entirely.

### Step 11-13: Embeddings, confidence, and eval (done)
Embedding-based matching (`match_goal_embedding`), confidence reporting
(`explain_choice`), and a 16-query benchmark (`navigator/eval.py`).
Richer object descriptions improved embedding accuracy from 68.75% → 100% (see [iterations](docs/semantic-matching.md#interesting-analysis)).

**What this means:** this replaces the "exact word match" approach from
Step 7 with something that understands *meaning*. Each place gets a
short description (e.g. "a restroom / bathroom / toilet"), and a
pretrained language model turns both the user's sentence and each
description into a list of numbers ("embeddings") that capture meaning.
Sentences that mean similar things end up with similar numbers, so
"where's the toilet" can match `restroom` even though the word "toilet"
never appears in its description. `explain_choice()` also reports a
confidence score, and tells you honestly when it's "not very confident".
The 16-question benchmark (`eval.py`) is how we measured and improved
this — checking, for a fixed set of test sentences, whether the system
picks the *expected* place, and iterating on the descriptions until it
reached 100%.

→ **[Semantic Matching — full write-up + analysis](docs/semantic-matching.md)**

### Step 15: Visualization polish (done)
`navigator/visualize.py` — `animate_path()` now accepts a `subtitle`,
rendered below the map. `navigator/main.py` builds this subtitle from
`explain_choice()`'s output: chosen target, its description, and the
confidence score (flagged as "confident" or "low-confidence guess").

**What this means:** the animation now shows *why* the robot is going
where it's going — a caption under the map saying which place it picked,
what that place is, and how confident the system was about that choice.

#### Try it
```bash
python3 -m navigator.main
python3 -m navigator.eval
```

## Next stage: Reinforcement Learning

Instead of telling the robot the rules (like A* does), here we let the
robot learn by trial and error: try an action, see what happens, get a
reward, and slowly get better over many attempts.

### RL Step 1: Environment (done)
`rl/env.py` — `GridNavEnv` wraps `GridMap` so an agent can interact
with it in a simple, standard way:
- `reset()` — puts the robot back at the start.
- `step(action)` — moves the robot (action = 0/1/2/3 for up/down/left/right)
  and returns `(new_position, reward, done, info)`.
- Rewards: `+10` for reaching the goal, `-1` for every normal step
  (including bumping into a wall and staying still). Small negative
  rewards per step encourage the robot to find short paths — every
  step "costs" something.

### RL Step 2: Q-learning agent (done)
`rl/q_learning.py` — `QLearningAgent` keeps a table of
"how good is it to take this action from this position?" called the
Q-table. Two key ideas:
- **Explore vs exploit**: most of the time the agent picks its
  current best-known action, but sometimes (`epsilon` chance) it picks
  a random action instead, so it keeps discovering new routes instead
  of getting stuck on an early, mediocre one.
- **Learning update**: after each step, the agent nudges its Q-table
  entry toward "reward I just got, plus the best value I expect from
  here onward". Repeated many times, these numbers settle into good
  estimates of "how good is this move, really".

### RL Step 3: Training loop + greedy run (done)
`rl/train.py`:
- `train()` runs many episodes (attempts). Each episode: reset, then
  repeatedly choose an action, take it, and learn from the result,
  until the robot reaches the goal or runs out of steps. Prints the
  average reward every 50 episodes so you can watch it improve.
- `run_greedy()` runs the trained agent with no randomness — always
  picking its best-known action — and returns the path it takes.
- The result is animated using the same `animate_path()` from the A*
  track.

#### Try it
```bash
python3 -m rl.train
```

#### What we found
- Goal = `food_court` (2 steps away): the agent learned the optimal
  2-step path almost immediately — too easy to be interesting.
- Goal = `restroom` (9 steps away, same target used in the A* demo):
  - Early on, the average reward per episode was very negative
    (around -32) — the robot was mostly bumping into walls and
    wandering.
  - Within ~100 episodes, it found a good route, and it eventually
    settled on the **optimal 9-step path** — the same length as A*'s
    path (a different route, but equally short).

#### Important limitation found
This agent only learned a path to **one specific goal** (`restroom`).
The "state" it learns from is just its `(x, y)` position — it has no
idea *what* the goal is. If you change the goal without retraining,
the learned table is useless for the new goal.

This is the opposite tradeoff from A*: A* re-plans instantly for any
new goal but does a fresh search every time; Q-learning takes a while
to learn but then "just knows" the answer — for the one goal it was
trained on.

### What's next (ideas, not yet built)
- **Compare RL vs A*** side by side on path length / success rate for
  several goals (`rl/evaluate.py`).
- **Multi-goal RL**: include the goal in the state, so one trained
  agent can handle any goal — closer to how A* behaves.
- **Partial observability**: the robot only "sees" nearby cells, not
  the whole map — closer to a real robot with limited sensors.
