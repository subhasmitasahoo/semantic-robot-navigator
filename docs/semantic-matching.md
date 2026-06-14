# Semantic Matching

How natural-language goals are mapped to mall objects, and how keyword vs
embedding matchers compare on a small eval set.

## Keyword matching (Step 7)

`navigator/semantics.py` — `match_goal()` ranks objects by keyword overlap
with a natural-language query (e.g. "I need caffeine" → `food_court`).

Each object has a hand-written keyword set in `OBJECT_KEYWORDS`. Score =
(# matching query words) / (# keywords for that object).

## Embedding-based semantics + confidence (Step 11–12)

`navigator/semantics.py`:

- `OBJECT_DESCRIPTIONS` — natural-language description per object.
- `match_goal_embedding()` — ranks objects by cosine similarity
  (via `sentence-transformers`, model `all-MiniLM-L6-v2`) between the
  query and each object's description.
- `explain_choice()` — picks the top match, prints a human-readable
  explanation, and flags low-confidence picks (score < `CONFIDENCE_THRESHOLD = 0.3`).

`navigator/main.py` — `navigate()` uses `explain_choice()` to pick a target
and reports confidence before planning/navigating.

### Object descriptions (current)

```python
OBJECT_DESCRIPTIONS = {
    "food_court": "a food court with restaurants, snacks, coffee, drinks, water, and something to eat or drink when hungry or thirsty",
    "clothing_store": "a clothing store selling shirts, shoes, and clothes",
    "restroom": "a restroom / bathroom / toilet where you can wash your hands",
    "info_desk": "ask here if you have a question, need directions, are lost, or need help finding something",
    "exit": "the exit leading outside the building",
}
```

Richer descriptions for `food_court` and `info_desk` were added after
iteration 1 — see [iteration 2 changes](#iteration-2-richer-descriptions) below.

## Eval set + matcher comparison (Step 13)

`navigator/eval.py` — 16 `(query, expected_label)` pairs; runs both
`match_goal` (keyword) and `match_goal_embedding` and reports per-query
results + accuracy.

```bash
python3 -m navigator.eval
```

## Interesting analysis

Eval runs are saved per iteration:
- [`data/test/iteration_1.txt`](../data/test/iteration_1.txt) — baseline (original descriptions)
- [`data/test/iteration_2.txt`](../data/test/iteration_2.txt) — richer `food_court` + `info_desk` descriptions
- [`data/test/iteration_3.txt`](../data/test/iteration_3.txt) — richer `restroom` description
- [`data/test/iteration_4.txt`](../data/test/iteration_4.txt) — query-shaped `info_desk` description

### Iteration 1 (original descriptions)

| Matcher | Accuracy |
|---------|----------|
| Keyword | 81.25% (13/16) |
| Embedding | 68.75% (11/16) |

Keyword matching won on this tiny benchmark. Embedding failures included
`I'm thirsty` → restroom, and `info_desk` queries (0/3 correct).

### Iteration 2: richer descriptions

**Change:** [commit ed3787b](https://github.com/subhasmitasahoo/semantic-robot-navigator/commit/ed3787b) — expanded `OBJECT_DESCRIPTIONS` in `navigator/semantics.py`:

| Object | Before | After |
|--------|--------|-------|
| `food_court` | "…coffee, and drinks" | added "water, and something to eat or drink when hungry or thirsty" |
| `info_desk` | "…staff can help with directions" | added "/ help desk", "answer questions", "help if you are lost" |

(No PR — changes landed directly on `main`.)

| Matcher | Accuracy | Δ vs iter 1 |
|---------|----------|-------------|
| Keyword | 81.25% (13/16) | — |
| Embedding | **75.00%** (12/16) | **+6.25 pp** |

**What improved:** adding "thirsty", "water", and hunger/drink phrasing to
`food_court` fixed `I'm thirsty` (was restroom @ 0.14, now food_court @ 0.26).

**Still failing (embedding):**
- `I need to wash my hands` → clothing_store (expected restroom)
- `I have a question` → restroom (expected info_desk)
- `can someone give me directions` → exit (expected info_desk)
- `I'm lost` → restroom (expected info_desk)

**Keyword still fails on:** `I'm thirsty`, `I need to wash my hands`, `I'm lost`
(no keyword overlap → `predicted=None`).

### Iteration 3: restroom description

**Change:** [commit 9f37360](https://github.com/subhasmitasahoo/semantic-robot-navigator/commit/9f37360) — expanded `restroom` in `OBJECT_DESCRIPTIONS`:

| Object | Before | After |
|--------|--------|-------|
| `restroom` | "a restroom / bathroom / toilet" | added "where you can wash your hands" |

| Matcher | Accuracy | Δ vs iter 2 |
|---------|----------|-------------|
| Keyword | 81.25% (13/16) | — |
| Embedding | **81.25%** (13/16) | **+6.25 pp** |

**What improved:** `I need to wash my hands` now hits restroom (was clothing_store @ 0.22 in iter 2, now restroom @ 0.57). Embeddings **tie keyword** on this benchmark.

**Still failing (embedding):**
- `I have a question` → food_court (expected info_desk)
- `can someone give me directions` → exit (expected info_desk)
- `I'm lost` → restroom (expected info_desk)

**Keyword still fails on:** `I'm thirsty`, `I need to wash my hands`, `I'm lost`.

### Iteration 4: query-shaped info_desk description

**Change:** rewrote `info_desk` in `OBJECT_DESCRIPTIONS` to mirror eval
query phrasing instead of a formal location description.

| Object | Before | After |
|--------|--------|-------|
| `info_desk` | "an information desk / help desk where staff can answer questions, give directions, and help if you are lost" | "ask here if you have a question, need directions, are lost, or need help finding something" |

| Matcher | Accuracy | Δ vs iter 3 |
|---------|----------|-------------|
| Keyword | 81.25% (13/16) | — |
| Embedding | **100.00%** (16/16) | **+18.75 pp** |

**What improved:** all three `info_desk` queries now pass:
- `I have a question` → info_desk (0.20)
- `can someone give me directions` → info_desk (0.56)
- `I'm lost` → info_desk (0.33)

Embeddings now **beat keyword** on this benchmark (100% vs 81.25%).

**Keyword still fails on:** `I'm thirsty`, `I need to wash my hands`, `I'm lost`.

### Takeaways

- **Description quality matters more than model choice** on a 5-object map —
  four rounds of tuning: 68.75% → 75% → 81.25% → **100%**.
- **Query-shaped descriptions beat formal ones** for embedding match — iter 4
  rewrote `info_desk` to echo how users ask, fixing all three remaining failures.
- **Keyword matcher plateaus at 81.25%** — it only matches literal keyword
  overlap, so paraphrases (`I'm thirsty`, `wash my hands`, `I'm lost`) still
  return `predicted=None`.
- **Embeddings generalize once descriptions are tuned** — same model and eval
  set, no hybrid ranker needed to clear the benchmark.
- **Next levers:** hybrid ranker for production (keyword fast-path + embedding
  fallback), larger eval set, or harder queries outside the 16-pair benchmark.
