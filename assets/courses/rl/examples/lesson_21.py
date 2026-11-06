"""Ordinary and weighted importance sampling on complete short trajectories."""
import argparse
import numpy as np

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--samples', type=int, default=10000)
    p.add_argument('--horizon', type=int, default=3)
    p.add_argument('--seed', type=int, default=21)
    a = p.parse_args()
    rng = np.random.default_rng(a.seed)
    # a=1 earns 1. Behavior chooses it with 0.2, target with 0.8.
    behavior, target = 0.2, 0.8
    actions = rng.binomial(1, behavior, size=(a.samples, a.horizon))
    ratios = np.where(actions == 1, target / behavior,
                      (1 - target) / (1 - behavior))
    weights = ratios.prod(axis=1)
    returns = actions.sum(axis=1)
    ordinary = np.mean(weights * returns)
    weighted = np.dot(weights, returns) / weights.sum()
    ess = weights.sum()**2 / np.dot(weights, weights)
    print('analytic target value:', a.horizon * target)
    print('raw behavior mean:', returns.mean())
    print('ordinary IS:', ordinary, 'weighted IS:', weighted)
    print('mean weight:', weights.mean(), 'effective sample size:', ess)
    print('largest weight:', weights.max())
