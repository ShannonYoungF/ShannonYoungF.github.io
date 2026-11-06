"""Minimal discrete-policy trainers for lessons 31, 34, 35 and 39.

Install: python -m pip install numpy torch gymnasium matplotlib
Run an importing lesson script with --smoke or --steps 20000 --plot.
All networks and updates are written here; no RL framework is used.
"""
import argparse
import random
import numpy as np
import torch
from torch import nn
from torch.distributions import Categorical
import gymnasium as gym


class ActorCritic(nn.Module):
    def __init__(self, obs_dim, actions):
        super().__init__()
        self.body = nn.Sequential(nn.Linear(obs_dim, 64), nn.Tanh(),
                                  nn.Linear(64, 64), nn.Tanh())
        self.actor = nn.Linear(64, actions)
        self.value = nn.Linear(64, 1)

    def forward(self, obs):
        features = self.body(obs)
        return Categorical(logits=self.actor(features)), self.value(features).squeeze(-1)


def evaluate(net, seed, episodes):
    env = gym.make("CartPole-v1")
    scores = []
    for episode in range(episodes):
        obs, _ = env.reset(seed=seed + episode)
        score = 0.0
        while True:
            with torch.no_grad():
                dist, _ = net(torch.as_tensor(obs, dtype=torch.float32))
                action = int(dist.probs.argmax())
            obs, reward, terminated, truncated, _ = env.step(action)
            score += reward
            if terminated or truncated:
                break
        scores.append(score)
    env.close()
    return scores


def run(mode):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    budget = min(args.steps, 256) if args.smoke else args.steps
    if budget < 1:
        parser.error("--steps must be positive")
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.set_num_threads(1)
    count = 4 if mode == "a2c" else 1
    envs = [gym.make("CartPole-v1") for _ in range(count)]
    obs = np.stack([env.reset(seed=args.seed + i)[0] for i, env in enumerate(envs)])
    net = ActorCritic(obs.shape[-1], envs[0].action_space.n)
    opt = torch.optim.Adam(net.parameters(), lr=3e-4)
    gamma, lam = 0.99, (0.95 if mode == "ppo" else 1.0 if mode == "a2c" else 0.0)
    steps, train_returns = 0, []
    totals = np.zeros(count)

    while steps < budget:
        if mode == "reinforce":
            # The benchmark's 500-step limit is treated as the finite episode objective.
            trajectory, rewards = [], []
            while True:
                state = torch.tensor(obs[0], dtype=torch.float32)
                dist, _ = net(state)
                action = dist.sample()
                nxt, reward, term, trunc, _ = envs[0].step(int(action))
                trajectory.append((state, action.detach()))
                rewards.append(reward)
                steps += 1
                obs[0] = nxt
                if term or trunc:
                    obs[0], _ = envs[0].reset()
                    break
            returns, value = [], 0.0
            for reward in reversed(rewards):
                value = reward + gamma * value
                returns.append(value)
            returns = torch.tensor(returns[::-1], dtype=torch.float32)
            states = torch.stack([pair[0] for pair in trajectory])
            actions = torch.stack([pair[1] for pair in trajectory])
            dist, _ = net(states)
            # gamma**t is needed for the discounted start-state objective used here.
            weights = gamma ** torch.arange(len(rewards), dtype=torch.float32)
            loss = -(weights * dist.log_prob(actions) * returns).sum()
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(net.parameters(), 1.0)
            opt.step()
            train_returns.append(sum(rewards))
            continue

        observations, actions, old_logs = [], [], []
        values, rewards, next_values, terminals, boundaries = [], [], [], [], []
        horizon = min(128 if mode == "ppo" else 16, max(1, (budget - steps) // count))
        for _ in range(horizon):
            state = torch.tensor(obs, dtype=torch.float32)
            with torch.no_grad():
                dist, value = net(state)
                action = dist.sample()
                old_log = dist.log_prob(action)
            raw_next, rs, ts, bs = [], [], [], []
            for i, env in enumerate(envs):
                nxt, reward, term, trunc, _ = env.step(int(action[i]))
                raw_next.append(nxt.copy())
                rs.append(reward)
                ts.append(float(term))
                bs.append(float(term or trunc))
                totals[i] += reward
                obs[i] = nxt
                if term or trunc:
                    train_returns.append(float(totals[i]))
                    totals[i] = 0
                    obs[i], _ = env.reset()
            with torch.no_grad():
                _, nv = net(torch.tensor(np.stack(raw_next), dtype=torch.float32))
            observations.append(state)
            actions.append(action)
            old_logs.append(old_log)
            values.append(value)
            rewards.append(torch.tensor(rs))
            next_values.append(nv)
            terminals.append(torch.tensor(ts))
            boundaries.append(torch.tensor(bs))
            steps += count

        value = torch.stack(values)
        advantage = torch.zeros_like(value)
        trace = torch.zeros(count)
        for t in reversed(range(horizon)):
            delta = rewards[t] + gamma * (1 - terminals[t]) * next_values[t] - value[t]
            # Bootstrap time truncations; never carry a trace across a reset.
            trace = delta + gamma * lam * (1 - boundaries[t]) * trace
            advantage[t] = trace
        target = (advantage + value).flatten().detach()
        adv = advantage.flatten().detach()
        states = torch.stack(observations).reshape(-1, obs.shape[-1])
        acts = torch.stack(actions).flatten()
        old = torch.stack(old_logs).flatten().detach()
        if mode == "ppo" and len(adv) > 1:
            adv = (adv - adv.mean()) / (adv.std(unbiased=False) + 1e-8)
        epochs = 4 if mode == "ppo" else 1
        for _ in range(epochs):
            permutation = torch.randperm(len(adv))
            for batch in permutation.split(64 if mode == "ppo" else len(adv)):
                dist, predicted = net(states[batch])
                log_prob = dist.log_prob(acts[batch])
                if mode == "ppo":
                    ratio = (log_prob - old[batch]).exp()
                    actor = -torch.minimum(ratio * adv[batch],
                                           ratio.clamp(0.8, 1.2) * adv[batch]).mean()
                else:
                    actor = -(log_prob * adv[batch]).mean()
                critic = 0.5 * (predicted - target[batch]).square().mean()
                loss = actor + critic - 0.01 * dist.entropy().mean()
                opt.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(net.parameters(), 0.5)
                opt.step()
    for env in envs:
        env.close()
    scores = evaluate(net, args.seed + 10000, 1 if args.smoke else 5)
    print(f"{mode}: training_steps={steps}, completed_episodes={len(train_returns)}")
    print("Independent deterministic evaluation:", scores, "mean=", float(np.mean(scores)))
    print("A smoke run checks execution; it does not establish learning performance.")
    if args.plot:
        import matplotlib.pyplot as plt
        plt.plot(train_returns, alpha=0.65)
        plt.xlabel("Completed training episode")
        plt.ylabel("Undiscounted episode reward")
        plt.title(f"{mode}, training seed {args.seed}")
        plt.show()
