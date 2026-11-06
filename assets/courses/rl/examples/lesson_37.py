import numpy as np
old = np.array([0.8, 0.2])
new = np.array([0.7, 0.3])
reward = np.array([1., 3.])
ratio = new / old
print("direct:", new @ reward)
print("importance weighted:", old @ (ratio * reward))
print("two right actions trajectory ratio:", ratio[1]**2)
rng = np.random.default_rng(7)
a = rng.choice(2, size=10000, p=old)
print("sample estimate:", np.mean(ratio[a] * reward[a]))
# Fixed-state equality says nothing by itself about changed state occupancy.
