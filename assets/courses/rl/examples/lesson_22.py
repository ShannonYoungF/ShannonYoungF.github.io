"""Frozen-value forward/backward trace identity; then online TD(lambda)."""
import argparse
import numpy as np

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--episodes', type=int, default=1000)
    p.add_argument('--lam', type=float, default=0.8)
    p.add_argument('--seed', type=int, default=22)
    a = p.parse_args()
    gamma, lam = 0.9, a.lam
    states, rewards = [1, 2, 1, 3], [0.0, 0.0, 1.0]
    v0 = np.array([0, .2, .4, 0.0])
    delta = np.array([rewards[t] + gamma * v0[states[t+1]] - v0[states[t]]
                      for t in range(3)])
    forward, backward, e = np.zeros(4), np.zeros(4), np.zeros(4)
    for t in range(3):
        forward[states[t]] += sum((gamma*lam)**(k-t)*delta[k] for k in range(t, 3))
        e *= gamma * lam
        e[states[t]] += 1
        backward += delta[t] * e
    print('frozen forward sum:', forward)
    print('frozen backward sum:', backward)
    print('identity error:', np.max(np.abs(forward-backward)))
    assert np.allclose(forward, backward)
    rng, v = np.random.default_rng(a.seed), np.zeros(7)
    for _ in range(a.episodes):
        s, e = 3, np.zeros(7)
        while s not in (0, 6):
            ns = s + rng.choice([-1, 1])
            done = ns in (0, 6)
            d = float(ns == 6) + (0 if done else v[ns]) - v[s]
            e *= lam  # gamma=1 for this separate episodic random walk
            e[s] += 1
            v += 0.03 * d * e
            s = ns
    print('online accumulating TD(lambda):', np.round(v[1:6], 3))
    print('Online changing values do not obey the frozen-value identity exactly.')
