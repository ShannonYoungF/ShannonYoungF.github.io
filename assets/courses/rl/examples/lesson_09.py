import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(7)
gamma = 0.9
paths = [[2.0, 0.0], [0.0, 10.0]]
q = np.array([sum(gamma**t*r for t, r in enumerate(path)) for path in paths])
policy = np.array([0.7, 0.3])
v = policy @ q
chosen = rng.choice(2, size=20000, p=policy)
returns = q[chosen]  # deterministic path after a sampled first action
print('Action values:', q)
print('Exact state value:', v, 'empirical:', returns.mean())
assert q.min() <= v <= q.max()
plt.plot(np.cumsum(returns)/np.arange(1, len(returns)+1), label='sample mean')
plt.axhline(v, color='gray', linestyle='--', label='exact value')
plt.xlabel('Episodes'); plt.ylabel('Mean return'); plt.legend()
plt.tight_layout(); plt.show()
