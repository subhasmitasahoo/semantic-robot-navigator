"""Evaluate semantic matchers against a small benchmark of queries."""

from navigator.world import build_mall_world
from navigator.semantics import match_goal, match_goal_embedding

EVAL_SET = [
    ("I need caffeine", "food_court"),
    ("where can I get food", "food_court"),
    ("I'm hungry", "food_court"),
    ("I'm thirsty", "food_court"),
    ("where can I buy a shirt", "clothing_store"),
    ("I need new shoes", "clothing_store"),
    ("I want to go shopping", "clothing_store"),
    ("I need to use the bathroom", "restroom"),
    ("where's the toilet", "restroom"),
    ("I need to wash my hands", "restroom"),
    ("I have a question", "info_desk"),
    ("can someone give me directions", "info_desk"),
    ("I'm lost", "info_desk"),
    ("I want to leave", "exit"),
    ("how do I get outside", "exit"),
    ("where's the way out", "exit"),
]


def evaluate(matcher, m, name):
    correct = 0
    print(f"\n--- {name} ---")
    for query, expected in EVAL_SET:
        results = matcher(query, m)
        predicted = results[0][0] if results else None
        score = results[0][1] if results else 0.0
        ok = predicted == expected
        correct += ok
        status = "OK " if ok else "FAIL"
        print(f"[{status}] '{query}' -> predicted={predicted} (score={score:.2f}), expected={expected}")

    accuracy = correct / len(EVAL_SET)
    print(f"\n{name} accuracy: {correct}/{len(EVAL_SET)} = {accuracy:.2%}")
    return accuracy


# python3 -m navigator.eval
if __name__ == "__main__":
    m = build_mall_world()

    keyword_acc = evaluate(match_goal, m, "Keyword matcher")
    embedding_acc = evaluate(match_goal_embedding, m, "Embedding matcher")

    print("\n=== Summary ===")
    print(f"Keyword:   {keyword_acc:.2%}")
    print(f"Embedding: {embedding_acc:.2%}")