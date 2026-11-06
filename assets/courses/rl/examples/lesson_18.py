"""n-step target bias and variance with a deliberately imperfect bootstrap."""
import argparse
import numpy as np

def sample_targets(n, draws, rng):
    # States 0 and 6 are absorbing; v_true(i)=i/6 under a fair random walk.
    estimate = np.arange(7, dtype=float) / 6 + 0.2
    out = np.empty(draws)
    for j in range(draws):
        s, g, terminal = 3, 0.0, False
        for _ in range(n):
            s += rng.choice([-1, 1])
            if s in (0, 6):
                g = float(s == 6)
                terminal = True
                break
        out[j] = g if terminal else g + estimate[s]
    return out

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--draws', type=int, default=10000)
    p.add_argument('--seed', type=int, default=18)
    a = p.parse_args()
    rng = np.random.default_rng(a.seed)
    for n in (1, 2, 4, 8, 32, 256):
        targets = sample_targets(n, a.draws, rng)
        bias = targets.mean() - 0.5
        var = targets.var()
        mse = np.mean((targets - 0.5)**2)
        print(f'n={n:3d} bias={bias:+.4f} variance={var:.4f} MSE={mse:.4f}')
    print('MSE = squared bias + variance for this fixed target distribution.')
