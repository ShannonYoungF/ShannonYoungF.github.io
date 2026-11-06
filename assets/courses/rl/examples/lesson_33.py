import numpy as np
rng = np.random.default_rng(7)
a = rng.integers(0, 2, 20000)
r = np.array([1.0, 3.0])[a]
score = a - 0.5
for baseline in [0.0, 2.0, 100.0]:
    g = (r-baseline)*score
    print("b=", baseline, "mean=", g.mean(), "var=", g.var())
wrong = (r-r)*score  # action-dependent baseline: biased
print("wrong action-dependent baseline:", wrong.mean())
