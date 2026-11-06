"""First-visit Monte Carlo prediction. Install: pip install numpy."""
import argparse
import numpy as np

def run(episodes=3000, seed=16):
    rng = np.random.default_rng(seed)
    values, counts = np.zeros(7), np.zeros(7, dtype=int)
    for _ in range(episodes):
        state, trajectory = 3, []
        while state not in (0, 6):
            next_state = state + rng.choice([-1, 1])
            trajectory.append((state, float(next_state == 6)))
            state = next_state
        # First collect all returns, then update only a state's first visit.
        returns, g = np.zeros(len(trajectory)), 0.0
        for t in reversed(range(len(trajectory))):
            g = trajectory[t][1] + g
            returns[t] = g
        seen = set()
        for (s, _), g in zip(trajectory, returns):
            if s not in seen:
                seen.add(s)
                counts[s] += 1
                values[s] += (g - values[s]) / counts[s]
    truth = np.arange(1, 6) / 6
    print('first-visit values:', np.round(values[1:6], 3))
    print('analytical values :', np.round(truth, 3))
    print('RMSE:', np.sqrt(np.mean((values[1:6] - truth)**2)))
    print('state visit counts:', counts[1:6])
    return values

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--episodes', type=int, default=3000)
    p.add_argument('--seed', type=int, default=16)
    a = p.parse_args()
    run(a.episodes, a.seed)
