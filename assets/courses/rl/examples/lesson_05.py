import numpy as np
import matplotlib.pyplot as plt

def run(epsilon, seed, horizon=500):
    rng = np.random.default_rng(seed)
    means = np.array([1.0, 2.0])
    q = np.array([2.0, 0.0])  # a misleading initial observation per arm
    count = np.ones(2, dtype=int)
    regret = []
    for t in range(horizon):
        if rng.random() < epsilon:
            action = rng.integers(2)
        else:
            ties = np.flatnonzero(q == q.max())
            action = rng.choice(ties)
        reward = means[action]  # deterministic continuation isolates the trap
        count[action] += 1
        q[action] += (reward-q[action]) / count[action]
        regret.append(means.max()-means[action])
    return np.cumsum(regret)

for epsilon in [0.0, 0.1, 0.5]:
    curves = np.array([run(epsilon, seed) for seed in range(100)])
    avg = curves.mean(axis=0)
    print(f'epsilon={epsilon}: mean final pseudo-regret={avg[-1]:.2f}')
    plt.plot(avg, label=f'epsilon={epsilon}')
plt.xlabel('Additional decisions'); plt.ylabel('Mean cumulative pseudo-regret')
plt.legend(); plt.tight_layout(); plt.show()
