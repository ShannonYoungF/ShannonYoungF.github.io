import numpy as np
reference = np.array([0.5, 0.5])
reward = np.array([0.0, 1.0])
for beta in [0.1, 1.0, 10.0]:
    logits = np.log(reference)+reward/beta
    p = np.exp(logits-logits.max()); p /= p.sum()
    kl = np.sum(p*np.log(p/reference))
    objective = p@reward-beta*kl
    print("beta", beta, "policy", p, "KL", kl, "objective", objective)
proxy = np.array([0.0, 3.0]); true_utility = np.array([1.0, -1.0])
p = np.exp(proxy-proxy.max()); p /= p.sum()
print("proxy score", p@proxy, "true utility", p@true_utility)
print("Discrete analytic example; no language or robot model is trained.")
