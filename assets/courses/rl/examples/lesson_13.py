import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(7)
gamma = 0.9
P = np.zeros((3, 2, 3))  # missing probability goes to a zero-value terminal
r = np.array([[3., 0.], [2., 0.], [5., 5.]])
P[0, 1, 1] = 1.; P[1, 1, 2] = 1.
policy = np.zeros(3, dtype=int)
values, previous = [], np.full(3, -np.inf)
for iteration in range(10):
    rows = np.arange(3)
    v = np.linalg.solve(np.eye(3)-gamma*P[rows, policy], r[rows, policy])
    assert np.all(v >= previous-1e-10)
    q = r+gamma*np.einsum('sak,k->sa', P, v)
    improved = policy.copy()
    for s in rows:
        best = int(np.argmax(q[s]))
        if q[s, best] > q[s, policy[s]]+1e-12:
            improved[s] = best  # keep the existing action on a tie
    print('iteration:', iteration, 'policy:', policy, 'value:', v)
    values.append(v.copy()); previous = v
    if np.array_equal(improved, policy):
        break
    policy = improved
for s, name in enumerate(['A', 'B', 'C']):
    plt.plot(np.array(values)[:, s], marker='o', label=name)
plt.xlabel('Policy evaluation round'); plt.ylabel('Value'); plt.legend()
plt.tight_layout(); plt.show()
