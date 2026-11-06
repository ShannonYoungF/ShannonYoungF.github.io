import numpy as np
rng = np.random.default_rng(52)
def expert(x): return -0.8*np.tanh(1.5*x)
def features(x):
    x = np.asarray(x)
    return np.column_stack([np.ones(x.size), x.ravel(), x.ravel()**2])
xdata = rng.normal(0.5, 0.12, 80)
ydata = expert(xdata)
def fit():
    F = features(xdata)
    return np.linalg.solve(F.T@F+1e-5*np.eye(3), F.T@ydata)
def rollout(w):
    x = 2.2; states = []
    for _ in range(25):
        states.append(x)
        u = np.clip((features([x])@w).item(), -1, 1)
        x = 1.05*x+u
    return np.array(states)
for iteration in range(6):
    w = fit(); visited = rollout(w)
    actions = np.clip(features(visited)@w, -1, 1)
    error = np.mean((actions-expert(visited))**2)
    print("aggregation", iteration, "visited imitation MSE", error,
          "max |x|", np.max(np.abs(visited)))
    xdata = np.r_[xdata, visited]
    ydata = np.r_[ydata, expert(visited)]
print("This is a supervised aggregation demo, not a safety guarantee.")
