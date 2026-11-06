"""Double Q-learning in a noisy two-stage MDP. pip install numpy."""
import argparse
import numpy as np


def choose(row, rng, epsilon=0.1):
    if rng.random() < epsilon:
        return int(rng.integers(len(row)))
    return int(rng.choice(np.flatnonzero(row == row.max())))


def learn(double, runs, episodes, actions, seed):
    # A: action 0 -> terminal reward 0; action 1 -> B reward 0.
    # B: each of K actions terminates with reward Normal(-0.1, 1).
    # Therefore the true optimal action at A is action 0.
    fractions, estimates = [], []
    for run in range(runs):
        rng = np.random.default_rng(seed + run)
        qa, qb = np.zeros((2, actions)), np.zeros((2, actions))
        left = []
        for _ in range(episodes):
            action = choose((qa[0] + qb[0])[:2] if double else qa[0, :2], rng)
            left.append(action == 1)
            if double:
                first, second = (qa, qb) if rng.random() < .5 else (qb, qa)
                if action == 0:
                    target = 0.0
                else:
                    best = choose(first[1], rng, epsilon=0)
                    target = second[1, best]
                first[0, action] += .1 * (target - first[0, action])
            else:
                target = 0.0 if action == 0 else qa[1].max()
                qa[0, action] += .1 * (target - qa[0, action])
            if action == 1:
                ba = choose(qa[1] + qb[1] if double else qa[1], rng)
                reward = rng.normal(-.1, 1)
                table = (qa if rng.random() < .5 else qb) if double else qa
                table[1, ba] += .1 * (reward - table[1, ba])
        fractions.append(np.mean(left[-min(100, episodes):]))
        estimates.append((qa[0, 1] + qb[0, 1]) / 2 if double else qa[0, 1])
    return np.mean(fractions), np.mean(estimates)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--trials', type=int, default=50000)
    p.add_argument('--actions', type=int, default=10)
    p.add_argument('--runs', type=int, default=30)
    p.add_argument('--episodes', type=int, default=1000)
    p.add_argument('--seed', type=int, default=23)
    a = p.parse_args()
    rng = np.random.default_rng(a.seed)
    qa = rng.normal(0, 1, (a.trials, a.actions))
    qb = rng.normal(0, 1, (a.trials, a.actions))
    selected = qa.argmax(axis=1)
    print('Independent-noise true action values: 0')
    print('single max mean:', qa.max(axis=1).mean())
    print('A selects/B evaluates mean:', qb[np.arange(a.trials), selected].mean())
    for double in (False, True):
        fraction, estimate = learn(double, a.runs, a.episodes, a.actions, a.seed)
        print('Double Q' if double else 'Q-learning',
              'final-window noisy-branch fraction:', fraction,
              'mean estimated Q(A,noisy):', estimate)
    print('True Q(A,noisy)=-0.1; exploratory action floor is epsilon/2=0.05.')
    print('Finite constant-step estimates fluctuate; learning tables are correlated.')
