"""Minimal complete DQN. pip install numpy torch gymnasium matplotlib
Run: python lesson_26.py --steps 20000; quick plumbing check: --smoke
"""
import argparse
import copy
import random
from collections import deque
import numpy as np
import torch
from torch import nn
import gymnasium as gym

class QNetwork(nn.Module):
    def __init__(self, obs_dim, actions):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(obs_dim, 64), nn.ReLU(),
                                 nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, actions))
    def forward(self, x):
        return self.net(x)

def parser(default_seed=26):
    p = argparse.ArgumentParser()
    p.add_argument('--steps', type=int, default=20000)
    p.add_argument('--seed', type=int, default=default_seed)
    p.add_argument('--smoke', action='store_true')
    p.add_argument('--plot', action='store_true')
    return p

@torch.no_grad()
def evaluate(net, seed, episodes=5):
    # Independent environment and seeds; never add these transitions to replay.
    env, totals = gym.make('CartPole-v1'), []
    for ep in range(episodes):
        state, _ = env.reset(seed=seed + ep)
        total = 0.0
        while True:
            x = torch.as_tensor(state, dtype=torch.float32).unsqueeze(0)
            action = int(net(x).argmax(dim=1).item())
            state, reward, terminated, truncated, _ = env.step(action)
            total += reward
            if terminated or truncated:
                break
        totals.append(total)
    env.close()
    return float(np.mean(totals)), float(np.std(totals))

def train(args, network_factory=QNetwork, double=False):
    if args.smoke:
        args.steps = min(args.steps, 512)
    if args.steps < 1:
        raise ValueError('--steps must be positive')
    random.seed(args.seed); np.random.seed(args.seed); torch.manual_seed(args.seed)
    torch.set_num_threads(1)
    rng = np.random.default_rng(args.seed)
    env = gym.make('CartPole-v1')
    env.action_space.seed(args.seed)
    obs_dim, actions = env.observation_space.shape[0], env.action_space.n
    online = network_factory(obs_dim, actions)
    target = copy.deepcopy(online).eval()
    target.requires_grad_(False)
    opt = torch.optim.Adam(online.parameters(), lr=5e-4)
    replay = deque(maxlen=20000)
    state, _ = env.reset(seed=args.seed)
    gamma, batch = 0.99, 32 if args.smoke else 64
    warmup = 64 if args.smoke else 500
    interval = 256 if args.smoke else 2000
    ep_return, train_returns, evaluations, losses = 0.0, [], [], []
    try:
        for step in range(1, args.steps + 1):
            eps = max(0.05, 1 - 0.95 * step / max(1, args.steps * .6))
            if rng.random() < eps:
                action = int(rng.integers(actions))
            else:
                with torch.no_grad():
                    action = int(online(torch.as_tensor(state).float()[None]).argmax(1).item())
            next_state, reward, terminated, truncated, _ = env.step(action)
            # Keep the real next observation. External TimeLimit still bootstraps.
            replay.append((state.copy(), action, reward, next_state.copy(), terminated))
            state, ep_return = next_state, ep_return + reward
            if terminated or truncated:
                train_returns.append(ep_return)
                state, _ = env.reset()
                ep_return = 0.0
            if step >= warmup and len(replay) >= batch and step % 4 == 0:
                indices = rng.choice(len(replay), batch, replace=False)
                samples = [replay[int(i)] for i in indices]
                s, ac, r, ns, terminal = zip(*samples)
                s, ns = torch.as_tensor(np.stack(s)), torch.as_tensor(np.stack(ns))
                ac = torch.as_tensor(ac, dtype=torch.int64).unsqueeze(1)
                r, terminal = torch.as_tensor(r).float(), torch.as_tensor(terminal).float()
                prediction = online(s).gather(1, ac).squeeze(1)
                with torch.no_grad():
                    if double:
                        # Online selects; target evaluates that selected action.
                        best = online(ns).argmax(1, keepdim=True)
                        bootstrap = target(ns).gather(1, best).squeeze(1)
                    else:
                        bootstrap = target(ns).max(1).values
                    y = r + gamma * (1 - terminal) * bootstrap
                loss = nn.functional.smooth_l1_loss(prediction, y)
                opt.zero_grad(); loss.backward()
                nn.utils.clip_grad_norm_(online.parameters(), 10.0)
                opt.step(); losses.append(float(loss.item()))
            if step % 500 == 0:
                target.load_state_dict(online.state_dict())
            if step % interval == 0 or step == args.steps:
                mean, std = evaluate(online, args.seed + 10000, 2 if args.smoke else 5)
                evaluations.append((step, mean, std))
                print(f'step={step} eval_mean={mean:.1f} eval_std={std:.1f} '
                      f'epsilon={eps:.3f} replay={len(replay)} updates={len(losses)}')
    finally:
        env.close()
    print('final 20 training returns:', np.round(train_returns[-20:], 1))
    print('final 20 mean Huber loss:', np.mean(losses[-20:]) if losses else 'no updates')
    if args.smoke:
        print('SMOKE checks execution only; this budget cannot establish learning quality.')
    if args.plot:
        import matplotlib.pyplot as plt
        x, y, sd = np.array(evaluations).T
        plt.plot(x, y, marker='o', label='Independent greedy evaluation')
        plt.fill_between(x, y-sd, y+sd, alpha=.2, label='Episode standard deviation')
        plt.xlabel('Training environment steps'); plt.ylabel('Return'); plt.legend(); plt.show()
    return online, evaluations

if __name__ == '__main__':
    train(parser().parse_args())
