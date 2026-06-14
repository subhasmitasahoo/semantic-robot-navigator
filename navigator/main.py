"""End-to-end demo: natural language goal -> ranked targets -> path -> animation."""

from navigator.world import build_mall_world
from navigator.semantics import match_goal
from navigator.semantics import explain_choice
from navigator.planner import astar
from navigator.visualize import animate_path


def navigate(m, start, query, blocked_cell=None, block_after_steps=2,
             unblock_after_steps=3, max_wait=10):
    """blocked_cell: a cell that becomes a dynamic obstacle after
    `block_after_steps` steps, and is removed after `unblock_after_steps`
    steps of being blocked (simulating someone walking through and leaving).
    max_wait: give up if the robot waits this many steps with no path."""

    # ===== Keyword-based matching (START)=====
    # matches = match_goal(query, m)
    # print(f"Goal: '{query}'")
    # print("Ranked matches:", matches)

    # if not matches:
    #     print("No matching object found for this goal.")
    #     return

    # target = None
    # for label, score in matches:
    #     if astar(m, start, m.objects[label]):
    #         target = m.objects[label]
    #         print(f"-> Chose '{label}' (score={score:.2f})")
    #         break

    # if target is None:
    #     print("No reachable object matches this goal.")
    #     return
    # ===== Keyword-based matching (END)=====

    # ===== Embedding-based matching (START)=====
    label, score, confident = explain_choice(query, m)
    if label is None:
        print("No matching object found for this goal.")
        return

    target = m.objects[label]
    if astar(m, start, target) is None:
        print(f"'{label}' is unreachable from {start}.")
        return
    # ===== Embedding-based matching (END)=====

    current = start
    full_journey = [current]
    step = 0
    obstacle_placed = False
    blocked_since = None  # step count when obstacle appeared
    wait_count = 0

    while current != target:
        # Obstacle appears
        if blocked_cell and not obstacle_placed and step == block_after_steps:
            print(f"Step {step}: Obstacle appeared at {blocked_cell}!")
            m.dynamic_obstacles.add(blocked_cell)
            obstacle_placed = True
            blocked_since = step

        # Obstacle disappears after unblock_after_steps steps of existing
        if obstacle_placed and blocked_cell in m.dynamic_obstacles:
            if step - blocked_since >= unblock_after_steps:
                print(f"Step {step}: Obstacle at {blocked_cell} cleared!")
                m.dynamic_obstacles.discard(blocked_cell)

        path = astar(m, current, target)

        if path is None:
            wait_count += 1
            print(f"Step {step}: no path, waiting ({wait_count}/{max_wait})...")
            if wait_count >= max_wait:
                print(f"Gave up at {current} — waited too long.")
                break
            step += 1
            full_journey.append(current)  # robot stays in place
            continue

        wait_count = 0
        next_cell = path[1] if len(path) > 1 else path[0]
        current = next_cell
        full_journey.append(current)
        step += 1

    if current == target:
        print(f"Arrived at {current} in {len(full_journey) - 1} steps (incl. waits)")

    animate_path(m, full_journey, title=f"Goal: '{query}' (with replanning + waiting)")


# python3 -m navigator.main
# if __name__ == "__main__":
#     m = build_mall_world()
#     start = (1, 1)

#     navigate(m, start, "I need to use the bathroom",
#              blocked_cell=(3, 4), block_after_steps=2,
#              unblock_after_steps=3, max_wait=10)

if __name__ == "__main__":

    for q in ["I need to use the bathroom", "I'm thirsty", "I need caffeine"]:
        m = build_mall_world()
        start = (1, 1)
        print("="*40)
        navigate(m, start, q, blocked_cell=(3, 4), block_after_steps=2,
                 unblock_after_steps=3, max_wait=10)