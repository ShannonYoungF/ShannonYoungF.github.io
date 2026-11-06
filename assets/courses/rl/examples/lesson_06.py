import numpy as np
import matplotlib.pyplot as plt
MEANS = np.array([0.3, 0.5, 0.7])
HORIZON = 2000

def run(method, seed):
    rng = np.random.default_rng(seed)
    count = np.zeros(3, dtype=int); q = np.zeros(3)
    losses = []
    for t in range(1, HORIZON+1):
        if t <= 3:
            a = t-1
        elif method == 'ucb':
            a = int(np.argmax(q + np.sqrt(2*np.log(t)/count)))
        elif rng.random() < 0.1:
            a = rng.integers(3)
        else:
            a = rng.choice(np.flatnonzero(q == q.max()))
        reward = float(rng.random() < MEANS[a])
        count[a] += 1; q[a] += (reward-q[a])/count[a]
        losses.append(MEANS.max()-MEANS[a])
    return np.cumsum(losses), count

for method in ['ucb', 'epsilon']:
    results = [run(method, seed) for seed in range(40)]
    curves = np.array([r[0] for r in results])
    counts = np.array([r[1] for r in results])
    print(method, 'mean visits:', counts.mean(axis=0),
          'mean final pseudo-regret:', curves[:, -1].mean())
    plt.plot(curves.mean(axis=0), label=method)
plt.xlabel('Decisions'); plt.ylabel('Mean cumulative pseudo-regret')
plt.legend(); plt.tight_layout(); plt.show()
