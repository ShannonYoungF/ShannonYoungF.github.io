import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(7)
A = np.array([[1.0]]); B = np.array([[1.0]])
Q = np.array([[1.0]]); R = np.array([[1.0]]); Qf = Q.copy()
H = 2
P = [None]*(H+1); K = [None]*H; P[H] = Qf
for t in reversed(range(H)):
    M = R+B.T@P[t+1]@B
    K[t] = np.linalg.solve(M, B.T@P[t+1]@A)
    P[t] = Q+A.T@P[t+1]@A-A.T@P[t+1]@B@K[t]
    P[t] = (P[t]+P[t].T)/2  # remove floating-point asymmetry
x0 = np.array([2.0]); x = x0.copy()
states, controls, cost = [x.copy()], [], 0.0
for t in range(H):
    u = -K[t]@x
    cost += float(x@Q@x+u@R@u)
    x = A@x+B@u
    states.append(x.copy()); controls.append(u.copy())
cost += float(x@Qf@x)
predicted = float(x0@P[0]@x0)
print('P:', [p.item() for p in P], 'K:', [k.item() for k in K])
print('Rollout cost:', cost, 'Bellman prediction:', predicted)
assert np.isclose(cost, predicted)
fig, axes = plt.subplots(1, 2, figsize=(8, 3))
axes[0].plot(range(H+1), np.array(states)[:, 0], marker='o')
axes[0].set(xlabel='Time step', ylabel='State')
axes[1].step(range(H), np.array(controls)[:, 0], where='post')
axes[1].set(xlabel='Time step', ylabel='Control')
plt.tight_layout(); plt.show()
