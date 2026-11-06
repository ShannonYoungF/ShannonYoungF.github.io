import numpy as np
old_logp = np.log(np.array([0.4, 0.6]))
new_logp = old_logp.copy()
ratio = np.exp(new_logp-old_logp)
assert np.allclose(ratio, 1), "Identity ratio failed"
def objective(r, advantage, eps=0.2):
    return np.minimum(r*advantage, np.clip(r, 1-eps, 1+eps)*advantage)
assert np.isclose(objective(1.5, 2), 2.4)
assert np.isclose(objective(1.5, -2), -3)
print("ratio identity and clipping sign checks passed")
new_prob = np.array([0.6, 0.4])
old_prob = np.exp(old_logp)
exact_kl = np.sum(old_prob*(old_logp-np.log(new_prob)))
print("exact categorical KL(old||new):", exact_kl)
# Training implementation already supplied in lesson 39.
print("Next: python lesson_39.py --smoke")
print("For a full study, fix a budget and repeat --seed 0,1,2,...")
