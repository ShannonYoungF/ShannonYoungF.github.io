import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(62)
# Synthetic training-level data only; replace with independent real runs.
baseline = np.array([90, 100, 80, 110, 95], dtype=float)
candidate = np.array([103, 97, 91, 120, 99], dtype=float)
difference = candidate-baseline
samples = rng.choice(difference, size=(10000, len(difference)), replace=True)
boot = samples.mean(axis=1)
low, high = np.quantile(boot, [0.025, 0.975])
print("SYNTHETIC demonstration: mean improvement", difference.mean())
print("training-unit bootstrap interval:", low, high)
print("n independent units:", len(difference))
plt.hist(boot, bins=35)
plt.axvline(0, color="black", linestyle="--")
plt.xlabel("bootstrap mean improvement"); plt.ylabel("resamples")
plt.tight_layout(); plt.savefig("lesson62_bootstrap.png")
