import numpy as np
gamma = 0.9
options = {"A": ([1.0, 2.0], 4.0), "B": ([1.0], 5.0)}
for name, (rewards, next_value) in options.items():
    tau = len(rewards)
    R = sum(gamma**k*r for k, r in enumerate(rewards))
    target = R + gamma**tau*next_value
    print(name, "duration", tau, "R_option", R, "target", target)
rng = np.random.default_rng(54)
durations = rng.choice([1, 4], size=100000, p=[0.5, 0.5])
estimate = np.mean(gamma**durations*5)
exact = 0.5*(gamma+gamma**4)*5
print("sampled continuation", estimate, "exact", exact)
print("using mean duration instead:", gamma**np.mean(durations)*5)
