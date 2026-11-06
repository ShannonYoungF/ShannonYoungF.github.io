import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(7)
p_left, n = 0.7, 10000
# Each trial restarts in the same state; 0 means left, 1 means right.
actions = rng.choice(2, size=n, p=[p_left, 1-p_left])
rewards = np.array([2.0, 5.0])[actions]
counts = np.arange(1, n+1)
frequency = np.cumsum(actions == 0) / counts
running_reward = np.cumsum(rewards) / counts
expected = p_left*2 + (1-p_left)*5
print('Designed left probability:', p_left)
print('Observed left frequency:', frequency[-1])
print('Expected / observed reward:', expected, running_reward[-1])
fig, axes = plt.subplots(1, 2, figsize=(9, 3))
axes[0].plot(counts, frequency); axes[0].axhline(p_left, color='gray')
axes[0].set(xlabel='Trials', ylabel='Left frequency')
axes[1].plot(counts, running_reward); axes[1].axhline(expected, color='gray')
axes[1].set(xlabel='Trials', ylabel='Mean reward')
plt.tight_layout(); plt.show()
