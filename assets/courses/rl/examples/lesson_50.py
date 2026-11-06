import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(50)
def mpc(x, model_b, horizon=8, candidates=1000):
    U = rng.uniform(-1, 1, (candidates, horizon))
    z = np.full(candidates, x)
    cost = np.zeros(candidates)
    for k in range(horizon):
        cost += z*z + 0.1*U[:, k]**2
        z = z + model_b*U[:, k]
    cost += 3*z*z
    return U[np.argmin(cost), 0]
def rollout(model_b):
    x = 3.0; path = [x]; total = 0.0
    for _ in range(25):
        u = mpc(x, model_b)
        total += x*x + 0.1*u*u
        x = x + u  # real b=1; only the first planned action is applied
        path.append(x)
    return path, total
for b in [1.0, 0.5]:
    path, cost = rollout(b)
    print("model b=", b, "real stage cost=", round(cost, 3))
    plt.plot(path, label=f"model b={b}")
plt.xlabel("control step"); plt.ylabel("position error")
plt.legend(); plt.tight_layout(); plt.savefig("lesson50_mpc.png")
