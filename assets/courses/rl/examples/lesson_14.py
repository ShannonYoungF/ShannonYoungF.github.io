import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(7)
n, gamma = 5, 0.95
P = np.zeros((n, 2, n)); r = np.zeros((n, 2))
for s in range(n):
    for a, direction in enumerate([-1, 1]):
        intended = max(0, s+direction)
        for next_state, probability in [(intended, 0.9), (s, 0.1)]:
            reward = 1.0 if next_state == n else -0.1
            r[s, a] += probability*reward
            if next_state < n:
                P[s, a, next_state] += probability
assert np.all(P >= 0) and np.all(P.sum(axis=2) <= 1+1e-12)
def backup(v):
    return r+gamma*np.einsum('sak,k->sa', P, v)
v = np.zeros(n); history = [v.copy()]
value_tolerance = 1e-7
for iteration in range(10000):
    new_v = backup(v).max(axis=1)
    v = new_v; history.append(v.copy())
    residual = np.max(np.abs(backup(v).max(axis=1)-v))
    if residual <= (1-gamma)*value_tolerance:
        break
policy = backup(v).argmax(axis=1)
rows = np.arange(n)
v_policy = np.linalg.solve(np.eye(n)-gamma*P[rows, policy], r[rows, policy])
print('Sweeps:', iteration+1, 'policy (0 left, 1 right):', policy)
print('Residual:', residual, 'value error bound:', residual/(1-gamma))
print('Difference from exact extracted-policy value:', np.max(np.abs(v-v_policy)))
plt.plot(np.array(history))
plt.xlabel('Synchronous sweeps'); plt.ylabel('Value of each corridor cell')
plt.tight_layout(); plt.show()
