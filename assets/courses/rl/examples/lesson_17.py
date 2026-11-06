"""TD(0) prediction on a random walk. Install: pip install numpy."""
import argparse
import numpy as np

def run(episodes=2000, seed=17, alpha=0.05):
    rng = np.random.default_rng(seed)
    v = np.zeros(7)
    truth = np.arange(1, 6) / 6
    errors = []
    for _ in range(episodes):
        s = 3
        while s not in (0, 6):
            ns = s + rng.choice([-1, 1])
            reward = float(ns == 6)
            terminated = ns in (0, 6)
            target = reward + (0 if terminated else v[ns])
            v[s] += alpha * (target - v[s])
            s = ns
        errors.append(np.sqrt(np.mean((v[1:6] - truth)**2)))
    print('values:', np.round(v[1:6], 3))
    print('last episode RMSE:', errors[-1])
    print('mean RMSE in final 100 episodes:', np.mean(errors[-100:]))
    return errors

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--episodes', type=int, default=2000)
    p.add_argument('--seed', type=int, default=17)
    p.add_argument('--alpha', type=float, default=0.05)
    p.add_argument('--plot', action='store_true')
    a = p.parse_args()
    errors = run(a.episodes, a.seed, a.alpha)
    if a.plot:
        import matplotlib.pyplot as plt
        plt.plot(errors); plt.xlabel('Episode'); plt.ylabel('Value RMSE'); plt.show()
