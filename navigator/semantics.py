"""Maps natural-language goals to target objects/locations using simple
keyword overlap scoring. No ML required for this first version."""

from navigator.world import build_mall_world

# label -> set of keywords/phrases associated with it
OBJECT_KEYWORDS = {
    "food_court": {"food", "eat", "hungry", "lunch", "snack", "caffeine", "coffee", "drink"},
    "clothing_store": {"clothes", "shirt", "shopping", "buy", "shoes", "wear"},
    "restroom": {"bathroom", "toilet", "restroom", "washroom", "pee"},
    "info_desk": {"information", "info", "help", "ask", "question", "directions"},
    "exit": {"exit", "leave", "outside", "out", "go home", "door"},
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


# main
# python3 -m navigator.semantics
if __name__ == "__main__":
    m = build_mall_world()
    print("I need caffeine:", match_goal("I need caffeine", m))
    print("where can I buy shoes:", match_goal("where can I buy shoes", m))
    print("I need to use the bathroom:", match_goal("I need to use the bathroom", m))
