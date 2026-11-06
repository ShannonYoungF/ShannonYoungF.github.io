"""On-policy SARSA in a cliff grid. Install: pip install numpy."""
import argparse
import numpy as np

START, GOAL = 36, 47
DELTAS = [(-1, 0), (0, 1), (1, 0), (0, -1)]

def step(s, a):
    row, col = divmod(s, 12)
    dr, dc = DELTAS[a]
    row, col = np.clip(row + dr, 0, 3), np.clip(col + dc, 0, 11)
    ns = int(row * 12 + col)
    if 37 <= ns <= 46:
        return START, -100.0, False
    return ns, -1.0, ns == GOAL

def choose(q, s, eps, rng):
    if rng.random() < eps:
        return int(rng.integers(4))
    return int(rng.choice(np.flatnonzero(q[s] == q[s].max())))

def run(episodes=1500, seed=19):
    rng = np.random.default_rng(seed)
    q, rewards = np.zeros((48, 4)), []
    for _ in range(episodes):
        s, total = START, 0.0
        a = choose(q, s, 0.1, rng)
        for t in range(1000):
            ns, r, terminated = step(s, a)
            na = choose(q, ns, 0.1, rng)
            target = r if terminated else r + q[ns, na]
            q[s, a] += 0.5 * (target - q[s, a])
            total += r
            s, a = ns, na
            if terminated:
                break
        # The 1000-step cutoff ends collection, not the underlying task.
        rewards.append(total)
    s, path = START, [START]
    for _ in range(100):
        s, _, done = step(s, choose(q, s, 0.0, rng))
        path.append(s)
        if done:
            break
    print('mean final training return:', np.mean(rewards[-100:]))
    print('greedy route:', [divmod(s, 12) for s in path])
    print('greedy success:', path[-1] == GOAL)
    return rewards

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--episodes', type=int, default=1500)
    p.add_argument('--seed', type=int, default=19)
    a = p.parse_args()
    run(a.episodes, a.seed)
