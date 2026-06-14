"""End-to-end demo: natural language goal -> ranked targets -> path -> animation."""

from navigator.world import build_mall_world
from navigator.semantics import match_goal
from navigator.planner import astar
from navigator.visualize import animate_path


def navigate(m, start, query):
    matches = match_goal(query, m)
    print(f"Goal: '{query}'")
    print("Ranked matches:", matches)

    if not matches:
        print("No matching object found for this goal.")
        return

    # Try each match in ranked order until we find one with a valid path
    for label, score in matches:
        target = m.objects[label]
        path = astar(m, start, target)
        if path:
            print(f"-> Chose '{label}' (score={score:.2f}), path length={len(path)}")
            animate_path(m, path, title=f"Goal: '{query}' -> {label}")
            return
        else:
            print(f"-> '{label}' (score={score:.2f}) is unreachable, trying next...")

    print("No reachable object matches this goal.")


# python3 -m navigator.main
if __name__ == "__main__":
    m = build_mall_world()
    start = (1, 1)

    navigate(m, start, "I need caffeine")