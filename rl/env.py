"""Gym-style environment wrapper around GridMap for RL experiments."""

from navigator.grid_map import GridMap
from navigator.world import build_mall_world

# Action -> (dx, dy). Remember y increases downward.
ACTIONS = {
    0: (0, -1),  # up
    1: (0, 1),   # down
    2: (-1, 0),  # left
    3: (1, 0),   # right
}

STEP_REWARD = -1
GOAL_REWARD = 10
WALL_PENALTY = -1  # bumping into a wall costs the same as a normal step


class GridNavEnv:
    def __init__(self, grid_map: GridMap, start, goal):
        self.map = grid_map
        self.start = start
        self.goal = goal
        self.agent_pos = start

    def reset(self):
        self.agent_pos = self.start
        return self.agent_pos

    def step(self, action):
        dx, dy = ACTIONS[action]
        x, y = self.agent_pos
        nx, ny = x + dx, y + dy

        if self.map.is_free(nx, ny):
            self.agent_pos = (nx, ny)
        # else: bump into wall, agent stays in place

        done = self.agent_pos == self.goal
        if done:
            reward = GOAL_REWARD
        elif not self.map.is_free(nx, ny):
            reward = WALL_PENALTY
        else:
            reward = STEP_REWARD

        return self.agent_pos, reward, done, {}


# python3 -m rl.env
if __name__ == "__main__":
    m = build_mall_world()
    env = GridNavEnv(m, start=(1, 1), goal=m.objects["restroom"])

    state = env.reset()
    print("start state:", state)

    # Try moving down a few times
    for _ in range(3):
        state, reward, done, info = env.step(1)  # action 1 = down
        print(state, reward, done)