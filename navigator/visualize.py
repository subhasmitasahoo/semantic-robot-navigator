"""Simple matplotlib visualization of the grid map."""

import matplotlib.pyplot as plt
import numpy as np

from navigator.grid_map import GridMap
from matplotlib.animation import FuncAnimation


def plot_map(m: GridMap, path=None, robot_pos=None, title="Grid Map"):
    fig, ax = plt.subplots(figsize=(m.width / 2, m.height / 2))

    grid = np.array(m.grid)
    ax.imshow(grid, cmap="Greys", origin="upper", vmin=0, vmax=1)

    # Draw object labels
    for label, (x, y) in m.objects.items():
        ax.plot(x, y, "o", color="tab:blue", markersize=10)
        ax.text(x, y - 0.4, label, ha="center", va="bottom", fontsize=8, color="tab:blue")

    # Draw path (if given)
    if path:
        xs = [p[0] for p in path]
        ys = [p[1] for p in path]
        ax.plot(xs, ys, "-", color="tab:red", linewidth=2)

    # Draw robot (if given)
    if robot_pos:
        ax.plot(robot_pos[0], robot_pos[1], "s", color="tab:green", markersize=12)

    ax.set_title(title)
    ax.set_xticks(range(m.width))
    ax.set_yticks(range(m.height))
    ax.grid(True, color="lightgray", linewidth=0.5)
    plt.tight_layout()
    plt.show()



def animate_path(m: GridMap, path, title="Robot Navigation"):
    fig, ax = plt.subplots(figsize=(m.width / 2, m.height / 2))

    grid = np.array(m.grid)
    ax.imshow(grid, cmap="Greys", origin="upper", vmin=0, vmax=1)

    # Draw object labels (static)
    for label, (x, y) in m.objects.items():
        ax.plot(x, y, "o", color="tab:blue", markersize=10)
        ax.text(x, y - 0.4, label, ha="center", va="bottom", fontsize=8, color="tab:blue")

    # Draw the full path as a faint line
    xs = [p[0] for p in path]
    ys = [p[1] for p in path]
    ax.plot(xs, ys, "-", color="tab:red", linewidth=1, alpha=0.4)

    # Robot marker, starts at the first cell
    robot_dot, = ax.plot(xs[0], ys[0], "s", color="tab:green", markersize=12)

    ax.set_title(title)
    ax.set_xticks(range(m.width))
    ax.set_yticks(range(m.height))
    ax.grid(True, color="lightgray", linewidth=0.5)
    plt.tight_layout()

    def update(frame):
        robot_dot.set_data([xs[frame]], [ys[frame]])
        return robot_dot,

    anim = FuncAnimation(fig, update, frames=len(path), interval=300, repeat=False)
    plt.show()
    return anim


# main
# python3 -m navigator.visualize
if __name__ == "__main__":
    from navigator.world import build_mall_world

    world = build_mall_world()
    plot_map(world, title="Mall World")