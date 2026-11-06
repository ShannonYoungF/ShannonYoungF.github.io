import numpy as np
import time
rng = np.random.default_rng(63)
a_nom, b, R = 1.0, 0.5, 0.1
P = 1.0
for _ in range(200):
    P = 1+a_nom*a_nom*P-(a_nom*b*P)**2/(R+b*b*P)
K = b*P*a_nom/(R+b*b*P)
def mpc(x):
    # Deterministic discrete-action shooting: fixed and explicit compute budget.
    actions = np.array([-1., -0.5, 0., 0.5, 1.])
    plans = np.array(np.meshgrid(*([actions]*4))).T.reshape(-1, 4)
    z = np.full(len(plans), x); cost = np.zeros(len(plans))
    for j in range(4):
        cost += z*z+R*plans[:, j]**2
        z = a_nom*z+b*plans[:, j]
    return plans[np.argmin(cost+P*z*z), 0]
for name in ["nominal LQR", "nominal MPC"]:
    costs, latencies = [], []
    for seed in range(10):
        noise = np.random.default_rng(seed).normal(0, .01, 30)
        x = 2.0; total = 0.0
        for w in noise:
            start = time.perf_counter()
            u = float(np.clip(-K*x, -1, 1)) if name.endswith("LQR") else mpc(x)
            latencies.append(time.perf_counter()-start)
            total += x*x+R*u*u
            x = 1.1*x+b*u+w
        costs.append(total)
    print(name, "mean cost", np.mean(costs),
          "mean latency ms", 1000*np.mean(latencies))
print("Both controllers use the nominal model; this script trains no RL policy.")
