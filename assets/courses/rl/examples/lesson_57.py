import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(57)
a = 1.05; k = 2.0
def simulate(b, delay=0):
    x = 1.0; history = [x]; queue = [0.0]*delay
    for _ in range(25):
        proposed = -k*x
        if delay:
            applied = queue.pop(0); queue.append(proposed)
        else: applied = proposed
        x = a*x+b*applied
        history.append(x)
    return np.array(history)
for b, delay in [(0.5, 0), (1.2, 0), (0.5, 1)]:
    path = simulate(b, delay)
    print("b, delay", b, delay, "max |x|", abs(path).max())
    plt.plot(path, label=f"b={b}, delay={delay}")
test_b = rng.uniform(0.4, 0.6, 100)
print("in-range stable fraction:", np.mean(np.abs(a-test_b*k)<1))
plt.xlabel("step"); plt.ylabel("state")
plt.legend(); plt.tight_layout(); plt.savefig("lesson57_gap.png")
