import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(7)
# Each outcome contains (next state, reward, probability).
outcomes = [('goal', 5.0, 0.8), ('corridor', -1.0, 0.2)]
prob = np.array([row[2] for row in outcomes])
assert np.all(prob >= 0) and np.isclose(prob.sum(), 1.0)
expected = sum(reward*p for _, reward, p in outcomes)
indices = rng.choice(len(outcomes), size=10000, p=prob)
rewards = np.array([outcomes[i][1] for i in indices])
success = np.mean(indices == 0)
print('Kernel expected reward:', expected)
print('Empirical mean reward:', rewards.mean())
print('One-step goal probability, empirical:', success)
plt.bar(['theory', 'sample'], [expected, rewards.mean()])
plt.ylabel('One-step mean reward'); plt.tight_layout(); plt.show()
