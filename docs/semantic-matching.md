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
    "restroom": "a restroom / bathroom / toilet",
    "info_desk": "an information desk / help desk where staff can answer questions, give directions, and help if you are lost",
    "exit": "the exit leading outside the building",
}
```

Richer descriptions for `food_court` and `info_desk` were added after the
first eval run — see analysis below.

## Eval set + matcher comparison (Step 13)

`navigator/eval.py` — 16 `(query, expected_label)` pairs; runs both
`match_goal` (keyword) and `match_goal_embedding` and reports per-query
results + accuracy.

```bash
python3 -m navigator.eval
```

## Interesting analysis

Full latest run: [`data/test/matcher_eval_results.txt`](../data/test/matcher_eval_results.txt)

### Baseline (original descriptions)

| Matcher | Accuracy |
|---------|----------|
| Keyword | 81.25% (13/16) |
| Embedding | 68.75% (11/16) |

Keyword matching won on this tiny benchmark. Embedding failures included
`I'm thirsty` → restroom, and `info_desk` queries (0/3 correct).

### After richer descriptions

| Matcher | Accuracy | Δ |
|---------|----------|---|
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

### Takeaways

- **Description quality matters more than model choice** on a 5-object map —
  a few targeted synonyms closed much of the gap (68.75% → 75%).
- **Keyword matcher is still ahead** (81.25%) because eval queries overlap
  heavily with hand-written keyword lists.
- **Both matchers struggle on paraphrase** — keyword returns no match;
  embedding often picks a plausible-but-wrong label with low confidence.
- **`info_desk` remains the weak spot for embeddings** (1/3 at best after
  description tweaks; still 0/3 in the latest run). Restroom descriptions
  may be stealing short ambiguous queries.
- **Confidence threshold (0.3)** still flags most embedding misses — wrong
  picks like `can someone give me directions` (0.08) and `I have a question`
  (0.19) score well below threshold, so `explain_choice()` can surface
  uncertainty even when top-1 is wrong.
- **Next levers:** enrich `restroom` / `info_desk` descriptions further, or
  try a hybrid ranker (keyword + embedding) rather than swapping one for the other.
