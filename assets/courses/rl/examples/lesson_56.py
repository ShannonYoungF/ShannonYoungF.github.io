import numpy as np
u_rl = 0.5; x = 0.8
for assumed_disturbance_bound in [0.0, 0.1]:
    upper = min(1.0, 1-x-assumed_disturbance_bound)
    if upper < -1.0:
        raise RuntimeError("No feasible action under the assumptions")
    u = np.clip(u_rl, -1.0, upper)
    actual_next = x+u+0.1
    print("assumed bound", assumed_disturbance_bound,
          "filtered action", u, "actual next", actual_next)
lam = 0.0
for cost_estimate in [2.0, 1.5, 0.8, 0.6]:
    lam = max(0.0, lam+0.2*(cost_estimate-1.0))
    print("cost", cost_estimate, "multiplier", lam)
print("Multiplier updates alone do not guarantee safe trajectories.")
