import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(49)
n = 250
x, u = rng.uniform(-1, 1, (2, n))
y = 1.1*x + 0.5*u + rng.normal(0, 0.02, n)
X = np.column_stack([x, u])
w = np.linalg.lstsq(X, y, rcond=None)[0]
# Bootstrap ensembles illustrate parameter sensitivity to this dataset.
ensemble = []
for _ in range(20):
    ix = rng.integers(n, size=n)
    ensemble.append(np.linalg.lstsq(X[ix], y[ix], rcond=None)[0])
print("estimated [a,b]:", w)
print("ensemble parameter std:", np.std(ensemble, axis=0))
truth, model = [1.0], [1.0]
for _ in range(25):
    truth.append(1.1*truth[-1])
    model.append(w[0]*model[-1])
print("25-step absolute error:", abs(truth[-1]-model[-1]))
plt.plot(truth, label="true open-loop")
plt.plot(model, "--", label="learned open-loop")
plt.xlabel("step"); plt.ylabel("state"); plt.legend()
plt.tight_layout(); plt.savefig("lesson49_model.png")
