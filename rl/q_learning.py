"""Tabular Q-learning agent.

Q-learning learns a table Q[state][action] = expected total future
reward (discounted) of taking `action` from `state`, and then acting
optimally afterward. Over many episodes of trial and error, this table
converges toward the true values, and "always pick the action with the
highest Q-value" becomes a good policy.
"""

import random
from collections import defaultdict


class QLearningAgent:
    def __init__(self, actions, alpha=0.1, gamma=0.95, epsilon=0.1):
        # List of possible actions, e.g. [0, 1, 2, 3] for up/down/left/right.
        self.actions = actions

        # alpha (learning rate, 0-1): how much each new experience
        # overwrites the old estimate. Higher = learns faster but noisier.
        self.alpha = alpha

        # gamma (discount factor, 0-1): how much we value future rewards
        # vs immediate ones. Close to 1 = "care a lot about long-term
        # outcome"; close to 0 = "only care about the immediate reward".
        self.gamma = gamma

        # epsilon (exploration rate, 0-1): probability of taking a random
        # action instead of the best-known one. Needed so the agent keeps
        # discovering new states/actions instead of getting stuck on
        # whatever looked best early on.
        self.epsilon = epsilon

        # The Q-table itself. q_table[state] is a dict {action: value}.
        # defaultdict means: the first time we look up a state we've never
        # seen, it auto-creates an entry with all action-values set to 0.0
        # — i.e. "no information yet, assume neutral".
        self.q_table = defaultdict(lambda: {a: 0.0 for a in self.actions})

    def choose_action(self, state):
        """Epsilon-greedy action selection."""

        # With probability epsilon, ignore everything we've learned and
        # pick a uniformly random action. This is "exploration" — without
        # it, the agent could get stuck always repeating an early,
        # mediocre choice and never discover better paths.
        if random.random() < self.epsilon:
            return random.choice(self.actions)

        # Otherwise, "exploit": look up this state's row in the Q-table
        # ({action: value} for all actions) and pick the action with the
        # highest estimated value — i.e. the best move we currently believe
        # we know.
        q_values = self.q_table[state]
        return max(q_values, key=q_values.get)

    def update(self, state, action, reward, next_state, done):
        """Apply one Q-learning update after observing a transition.

        (state, action) -> reward -> next_state (and whether next_state
        is terminal/done).
        """

        # Current estimate of Q(state, action) before this update.
        current_q = self.q_table[state][action]

        if done:
            # If this action ended the episode (reached the goal), there's
            # no "future" beyond this — the target is just the reward
            # received right now.
            target = reward
        else:
            # Otherwise, the target is: reward received now, PLUS the
            # discounted value of the *best* action available from
            # next_state (assuming we act optimally from then on).
            # This is the "Bellman equation" — it lets information about
            # rewards propagate backwards through the state space over
            # many updates/episodes.
            target = reward + self.gamma * max(self.q_table[next_state].values())

        # Move current_q toward target by a fraction `alpha` of the gap
        # between them. alpha=1 would jump straight to target (noisy);
        # alpha=0 would never update at all. 0.1 is a gentle nudge.
        self.q_table[state][action] += self.alpha * (target - current_q)


# python3 -m rl.q_learning
if __name__ == "__main__":
    agent = QLearningAgent(actions=[0, 1, 2, 3])

    state = (1, 1)
    action = agent.choose_action(state)
    print("chosen action:", action)

    agent.update(state, action, reward=-1, next_state=(1, 2), done=False)
    print("Q-table for state (1,1):", agent.q_table[state])