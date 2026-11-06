"""Off-policy Q-learning in a cliff grid. Install: pip install numpy."""
import argparse
import numpy as np
START, GOAL = 36, 47

def step(s, a):
    r, c = divmod(s, 12)
    dr, dc = [(-1, 0), (0, 1), (1, 0), (0, -1)][a]
    ns = int(np.clip(r + dr, 0, 3) * 12 + np.clip(c + dc, 0, 11))
    if 37 <= ns <= 46:
        return START, -100.0, False
    return ns, -1.0, ns == GOAL

def action(q, s, eps, rng):
    if rng.random() < eps:
        return int(rng.integers(4))
    return int(rng.choice(np.flatnonzero(q[s] == q[s].max())))

def run(episodes, seed):
    rng = np.random.default_rng(seed)
    q, rewards, falls = np.zeros((48, 4)), [], 0
    for _ in range(episodes):
        s, total = START, 0.0
        for t in range(1000):
            a = action(q, s, 0.1, rng)
            ns, r, done = step(s, a)
            target = r if done else r + q[ns].max()
            q[s, a] += 0.5 * (target - q[s, a])
            falls += int(r == -100)
            total += r
            s = ns
            if done:
                break
        rewards.append(total)
    s, path = START, [START]
    for _ in range(100):
        s, _, done = step(s, action(q, s, 0.0, rng))
        path.append(s)
        if done:
            break
    print('mean final training return:', np.mean(rewards[-100:]))
    print('all training cliff falls:', falls)
    print('greedy route:', [divmod(s, 12) for s in path])
    print('greedy success:', path[-1] == GOAL)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--episodes', type=int, default=1500)
    p.add_argument('--seed', type=int, default=20)
    a = p.parse_args()
    run(a.episodes, a.seed)
