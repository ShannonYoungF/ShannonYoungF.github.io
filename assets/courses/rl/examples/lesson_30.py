import numpy as np
rng = np.random.default_rng(7)
logits = np.array([0.0, np.log(3.0)])
weights = np.exp(logits - logits.max())
prob = weights / weights.sum()
reward = np.array([1.0, 3.0])
actions = rng.choice(2, size=20000, p=prob)
print("policy:", prob)
print("exact expected reward:", prob @ reward)
print("sample average:", reward[actions].mean())
p = prob[1]
print("dJ/dtheta:", 2 * p * (1-p))
