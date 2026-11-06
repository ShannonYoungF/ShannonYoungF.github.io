import numpy as np

def gae(delta, boundary, gamma=0.9, lam=0.8):
    advantage = np.zeros_like(delta, dtype=float)
    trace = 0.0
    for t in range(len(delta)-1, -1, -1):
        trace = delta[t] + gamma*lam*(1-boundary[t])*trace
        advantage[t] = trace
    return advantage

delta = np.array([1.0, 2.0, 3.0])
print("continuous:", gae(delta, np.array([0,0,0])))
print("reset after t=0:", gae(delta, np.array([1,0,0])))
for lam in [0, 0.5, 0.8, 1]:
    print("lambda", lam, gae(delta, np.zeros(3), lam=lam))
