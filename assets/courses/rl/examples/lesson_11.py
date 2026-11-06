import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(7)
gamma = 0.9
P = np.array([[0.5, 0.5], [0.0, 0.5]])
r = np.array([0.0, 1.0])
# Missing row probability goes to an omitted zero-value terminal state.
assert np.all(P >= 0) and np.all(P.sum(axis=1) <= 1)
exact = np.linalg.solve(np.eye(2)-gamma*P, r)
v = np.zeros(2); errors = []
for iteration in range(60):
    errors.append(np.max(np.abs(v-exact)))
    v = r+gamma*P@v  # synchronous: the whole RHS uses the old vector
print('Linear solve:', exact)
print('Iterative evaluation:', v)
print('Maximum final error:', np.max(np.abs(v-exact)))
plt.semilogy(errors, label='actual error')
plt.semilogy(errors[0]*gamma**np.arange(60), '--', label='contraction bound')
plt.xlabel('Iteration'); plt.ylabel('Maximum absolute error'); plt.legend()
plt.tight_layout(); plt.show()
