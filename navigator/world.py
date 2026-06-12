"""Defines the example world: a small shopping mall floor."""

import matplotlib.pyplot as plt

from navigator.grid_map import GridMap

def build_mall_world() -> GridMap:
    """A 20x12 grid representing one floor of a small mall."""
    w, h = 20, 12

    m = GridMap.empty(w, h)

    # outer walls
    for x in range(w):
        m.set_obstacle(x, 0)
        m.set_obstacle(x, h - 1)
    for y in range(h):
        m.set_obstacle(0, y)
        m.set_obstacle(w - 1, y)

    # add some obstacles
    m.set_obstacle(5, 5)
    m.set_obstacle(7, 5)
    m.set_obstacle(9, 5)

    # Vertical wall splitting left wing from right wing, doorway at y=5
    for y in range(1, h - 1):
        if y != 5:
            m.set_obstacle(6, y)

    # Horizontal wall splitting top wing from bottom wing, doorways at x=3 and x=13
    for x in range(1, w - 1):
        if x not in (3, 13):
            m.set_obstacle(x, 4)

    # Place a few labeled objects
    m.place_object("food_court", 3, 1)
    m.place_object("clothing_store", 16, 1)
    m.place_object("restroom", 3, 8)
    m.place_object("info_desk", 9, 6)
    m.place_object("exit", 17, 10)

    return m

# main
# python3 -m navigator.world
if __name__ == "__main__":
    m = build_mall_world()
    print(m.grid)
    print(m.objects)
    print(m.is_free(1, 1))
    print(m.is_free(1, 2))
    print(m.is_free(2, 1))
    print(m.is_free(2, 2))

    # print the world
    plt.imshow(m.grid, cmap='gray')
    plt.show()