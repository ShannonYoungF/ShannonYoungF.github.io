"""Reward audit: prescribed policies, not a learning algorithm."""
import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(7)  # deterministic dynamics here
HORIZON, GAMMA = 6, 0.9

def rollout(policy):
    state, rewards = 'far', []
    for _ in range(HORIZON):
        if state == 'far':
            state, reward = 'near', 1.0
        elif policy == 'enter':
            state, reward = 'charged', 0.0
        else:
            state, reward = 'far', 0.0
        rewards.append(reward)
        if state == 'charged':
            break
    discounted = sum(GAMMA ** t * r for t, r in enumerate(rewards))
    return sum(rewards), discounted, int(state == 'charged')

names = ['enter', 'loop']
results = np.array([rollout(name) for name in names])
for name, result in zip(names, results):
    print(name, 'total, discounted, success =', result)
fig, axes = plt.subplots(1, 2, figsize=(8, 3))
axes[0].bar(names, results[:, 0]); axes[0].set_title('Reward total')
axes[1].bar(names, results[:, 2]); axes[1].set_title('Task success')
axes[1].set_ylim(0, 1.2)
plt.tight_layout(); plt.show()
