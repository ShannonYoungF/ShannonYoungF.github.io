import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(7)
truth = np.array([1.0, 1.5, 2.0])
q, count = np.zeros(3), np.zeros(3, dtype=int)
history = [[] for _ in truth]
trace = []
for t in range(900):
    a = t % 3  # fixed balanced collection, not a decision algorithm
    reward = rng.normal(truth[a], 1.0)
    count[a] += 1
    q[a] += (reward-q[a]) / count[a]
    history[a].append(reward)
    trace.append(q.copy())
for a in range(3):
    assert np.isclose(q[a], np.mean(history[a]))
    print(f'Arm {a}: n={count[a]}, estimate={q[a]:.3f}, truth={truth[a]:.3f}')
trace = np.array(trace)
for a in range(3):
    plt.plot(trace[:, a], label=f'arm {a}')
    plt.axhline(truth[a], linestyle=':', alpha=0.4)
plt.xlabel('Total visits'); plt.ylabel('Incremental mean'); plt.legend()
plt.tight_layout(); plt.show()
