import numpy as np
p = 0.5
gamma = 0.5
q = np.array([1.0, gamma * 4.0])
prob = np.array([1-p, p])
score = np.array([-p, 1-p])
exact = np.sum(prob * q * score)
def objective(theta):
    right = 1 / (1 + np.exp(-theta))
    return (1-right) + right * gamma * 4
h = 1e-5
finite_difference = (objective(h)-objective(-h))/(2*h)
print("PG theorem:", exact)
print("finite difference:", finite_difference)
assert np.isclose(exact, finite_difference)
