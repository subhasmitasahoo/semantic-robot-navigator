"""A* path planning over a GridMap."""

import heapq

from navigator.grid_map import GridMap


def heuristic(a, b):
    """Manhattan distance — good fit for 4-connected grid movement."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(m: GridMap, start, goal):
    """Return a list of (x, y) cells from start to goal, or None if no path."""

    # Priority queue of (f_score, cell), ordered by lowest f_score first.
    open_set = [(0, start)]

    # came_from[cell] = previous cell on the best path found so far.
    came_from = {}

    # g_score[cell] = cheapest known cost from start to cell.
    g_score = {start: 0}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            return _reconstruct_path(came_from, current)

        for neighbor in m.neighbors(*current):
            tentative_g = g_score[current] + 1

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))
                came_from[neighbor] = current

    return None  # no path found


def _reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


# main
# python3 -m navigator.planner
# main
# python3 -m navigator.planner
if __name__ == "__main__":
    from navigator.world import build_mall_world
    from navigator.visualize import animate_path

    m = build_mall_world()
    start = (1, 1)
    goal = m.objects["restroom"]

    path = astar(m, start, goal)
    print("start:", start, "goal:", goal)
    print("path:", path)
    print("length:", len(path) if path else None)

    if path:
        animate_path(m, path, title="Robot heading to restroom")