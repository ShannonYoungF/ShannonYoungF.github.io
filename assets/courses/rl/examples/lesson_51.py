import numpy as np
rng = np.random.default_rng(51)
n = 1000
state = rng.normal(size=(n, 2))  # position, velocity
background = rng.normal(0, 10, (n, 1))
obs = np.hstack([state, background])
mean = obs.mean(0)
_, _, vt = np.linalg.svd(obs-mean, full_matrices=False)
for rank in [1, 2, 3]:
    W = vt[:rank].T
    z = (obs-mean) @ W
    reconstruction = z @ W.T + mean
    # Check whether a linear readout recovers control-relevant variables.
    X = np.column_stack([z, np.ones(n)])
    coef = np.linalg.lstsq(X[:700], state[:700], rcond=None)[0]
    pred = X[700:] @ coef
    print("latent rank", rank,
          "reconstruction MSE", np.mean((reconstruction-obs)**2),
          "held-out state MSE", np.mean((pred-state[700:])**2))
print("Large background variance can dominate a small PCA representation.")
