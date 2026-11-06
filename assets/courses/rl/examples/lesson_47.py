import numpy as np
for gain in [.5, 2.2]:
    x = 1.0
    trajectory = [x]
    for _ in range(8):
        x = (1-gain)*x
        trajectory.append(x)
    print("gain", gain, "trajectory", np.round(trajectory,4))
x, dt, eps, proposed = .1, .2, .02, -1.
filtered = max(proposed, (eps-x)/dt)
worst_next = x+dt*filtered-eps
print("proposed",proposed,"filtered",filtered,"worst next",worst_next)
assert worst_next >= -1e-12
