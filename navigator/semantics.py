"""Maps natural-language goals to target objects/locations using simple
keyword overlap scoring. No ML required for this first version."""

from sentence_transformers import SentenceTransformer, util

from navigator.world import build_mall_world

# label -> set of keywords/phrases associated with it
OBJECT_KEYWORDS = {
    "food_court": {"food", "eat", "hungry", "lunch", "snack", "caffeine", "coffee", "drink"},
    "clothing_store": {"clothes", "shirt", "shopping", "buy", "shoes", "wear"},
    "restroom": {"bathroom", "toilet", "restroom", "washroom", "pee"},
    "info_desk": {"information", "info", "help", "ask", "question", "directions"},
    "exit": {"exit", "leave", "outside", "out", "go home", "door"},
}

OBJECT_DESCRIPTIONS = {
    "food_court": "a food court with restaurants, snacks, coffee, drinks, water, and something to eat or drink when hungry or thirsty",
    "clothing_store": "a clothing store selling shirts, shoes, and clothes",
    "restroom": "a restroom / bathroom / toilet",
    "info_desk": "an information desk / help desk where staff can answer questions, give directions, and help if you are lost",
    "exit": "the exit leading outside the building",
}


def match_goal(query: str, m) -> list[tuple[str, float]]:
    """Return [(label, score), ...] sorted by score descending.

    score = (# matching keywords) / (# keywords for that object)
    Only objects that exist in the map's m.objects are considered.
    """
    query_words = set(query.lower().split())

    scores = []
    for label, keywords in OBJECT_KEYWORDS.items():
        if label not in m.objects:
            continue
        overlap = query_words & keywords
        score = len(overlap) / len(keywords)
        if score > 0:
            scores.append((label, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


_model = None

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def match_goal_embedding(query: str, m) -> list[tuple[str, float]]:
    """Return [(label, score), ...] sorted by cosine similarity descending.

    score = cosine similarity between query embedding and object
    description embedding, in [-1, 1] (typically [0, 1] for short phrases).
    Only objects that exist in the map's m.objects are considered.
    """
    model = _get_model()

    labels = [label for label in OBJECT_DESCRIPTIONS if label in m.objects]
    descriptions = [OBJECT_DESCRIPTIONS[label] for label in labels]

    query_emb = model.encode(query, convert_to_tensor=True)
    desc_embs = model.encode(descriptions, convert_to_tensor=True)

    scores = util.cos_sim(query_emb, desc_embs)[0]  # shape: (num_labels,)

    results = list(zip(labels, scores.tolist()))
    results.sort(key=lambda x: x[1], reverse=True)
    return results


CONFIDENCE_THRESHOLD = 0.3

def explain_choice(query: str, m, matcher=match_goal_embedding):
    """Pick the best-matching object and explain the choice.

    Returns (label, score, confident: bool) or (None, None, False) if
    there are no candidates at all.
    """
    results = matcher(query, m)
    if not results:
        return None, None, False

    label, score = results[0]
    confident = score >= CONFIDENCE_THRESHOLD

    if confident:
        print(f"I think you want '{label}' (matches \"{OBJECT_DESCRIPTIONS[label]}\", "
              f"confidence={score:.2f})")
    else:
        print(f"I'm not very confident, but my best guess is '{label}' "
              f"(matches \"{OBJECT_DESCRIPTIONS[label]}\", confidence={score:.2f} "
              f"— below threshold {CONFIDENCE_THRESHOLD})")

    return label, score, confident


# main
# python3 -m navigator.semantics
if __name__ == "__main__":
#     m = build_mall_world()
#     print("I need caffeine:", match_goal("I need caffeine", m))
#     print("where can I buy shoes:", match_goal("where can I buy shoes", m))
#     print("I need to use the bathroom:", match_goal("I need to use the bathroom", m))

    # Embedding  based.
    m = build_mall_world()
    for q in ["I need caffeine", "I'm thirsty", "somewhere quiet to sit", "I need to use the bathroom"]:
        print(q)
        print("  keyword: ", match_goal(q, m))
        print("  embedding:", match_goal_embedding(q, m))
        print("=======")