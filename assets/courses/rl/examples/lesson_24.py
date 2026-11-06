"""Linear semi-gradient TD prediction with deliberately aliased features."""
import argparse
import numpy as np

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--episodes', type=int, default=4000)
    p.add_argument('--seed', type=int, default=24)
    a = p.parse_args()
    rng = np.random.default_rng(a.seed)
    # Two coefficients represent five state values; terminal features are zero.
    features = np.zeros((7, 2))
    features[1:6, 0] = 1
    features[1:6, 1] = np.linspace(-1, 1, 5)
    w = np.zeros(2)
    for ep in range(a.episodes):
        s = 3
        while s not in (0, 6):
            ns = s + rng.choice([-1, 1])
            r = float(ns == 6)
            delta = r + features[ns] @ w - features[s] @ w
            # Detach the bootstrap target: only differentiate current prediction.
            alpha = 0.03 / (1 + ep / 1000)
            w += alpha * delta * features[s]
            s = ns
    pred, truth = features[1:6] @ w, np.arange(1, 6)/6
    print('weights:', np.round(w, 3))
    print('predictions:', np.round(pred, 3))
    print('RMSE:', np.sqrt(np.mean((pred-truth)**2)))
    alias = np.ones((5, 1))
    best_constant = np.linalg.lstsq(alias, truth, rcond=None)[0]
    print('constant-feature least-squares prediction:', best_constant[0])
    print('Feature choice limits what can be represented, regardless of data volume.')
