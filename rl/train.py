"""Train a Q-learning agent to navigate to a goal in GridMap."""

from navigator.visualize import animate_path
from navigator.world import build_mall_world
from rl.env import GridNavEnv, ACTIONS
from rl.q_learning import QLearningAgent

# How many full attempts ("episodes") the agent gets to learn from.
# More episodes = more chances to refine the Q-table, but with
# diminishing returns once it converges.
NUM_EPISODES = 500

# Safety cap on how long a single episode can run. Early on, a mostly
# random agent could wander forever without reaching the goal — this
# forces the episode to end and start a fresh attempt.
MAX_STEPS_PER_EPISODE = 200


def train():
    # Build the world and define start/goal for this training run.
    m = build_mall_world()
    start = (1, 1)
    goal = m.objects["food_court"]  # reachable from (1,1)

    # env: handles "what happens when the agent takes an action".
    # agent: handles "what action to take, and how to learn from results".
    env = GridNavEnv(m, start, goal)
    agent = QLearningAgent(actions=list(ACTIONS.keys()))

    # Track total reward per episode so we can see if learning is working.
    episode_rewards = []

    for episode in range(NUM_EPISODES):
        # Reset the agent to `start` at the beginning of each episode.
        state = env.reset()
        total_reward = 0

        for _ in range(MAX_STEPS_PER_EPISODE):
            # 1. Agent picks an action (epsilon-greedy: explore or exploit).
            action = agent.choose_action(state)

            # 2. Environment applies the action, returns what happened.
            next_state, reward, done, _ = env.step(action)

            # 3. Agent updates its Q-table based on this experience.
            agent.update(state, action, reward, next_state, done)

            # Move to the new state and accumulate reward for this episode.
            state = next_state
            total_reward += reward

            # If the goal was reached, end this episode early.
            if done:
                break

        episode_rewards.append(total_reward)

        # Every 50 episodes, print the average reward over the last 50 —
        # a rough signal of whether the agent is improving over time.
        if (episode + 1) % 50 == 0:
            avg_reward = sum(episode_rewards[-50:]) / 50
            print(f"Episode {episode + 1}: avg reward (last 50) = {avg_reward:.2f}")

    # Return the trained agent (with its learned Q-table) and the env,
    # so the caller can inspect/visualize the learned policy.
    return agent, env


def run_greedy(agent, env, max_steps=50):
    """Run the agent greedily (no exploration) and return the path taken."""
    state = env.reset()
    path = [state]

    for _ in range(max_steps):
        # Pick the best-known action — no randomness.
        q_values = agent.q_table[state]
        action = max(q_values, key=q_values.get)

        state, reward, done, _ = env.step(action)
        path.append(state)

        if done:
            break

    return path


if __name__ == "__main__":
    agent, env = train()

    path = run_greedy(agent, env)
    print("Greedy path:", path)
    print("Length:", len(path) - 1, "steps")

    animate_path(env.map, path, title="Learned policy (Q-learning)")
