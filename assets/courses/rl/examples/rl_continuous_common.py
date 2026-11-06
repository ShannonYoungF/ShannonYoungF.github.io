"""Minimal DDPG / TD3 / SAC implementations for Pendulum-v1.

Install: python -m pip install numpy torch gymnasium matplotlib
Actor/critic inputs use normalized actions in [-1, 1]. SAC entropy is
expressed in physical action coordinates, including the constant scale Jacobian.
"""
import argparse
import copy
import random
import numpy as np
import torch
from torch import nn
from torch.distributions import Normal
import gymnasium as gym


def mlp(inputs, outputs):
    return nn.Sequential(nn.Linear(inputs, 64), nn.ReLU(), nn.Linear(64, 64),
                         nn.ReLU(), nn.Linear(64, outputs))


class Actor(nn.Module):
    def __init__(self, obs_dim, action_dim, stochastic=False):
        super().__init__()
        self.stochastic = stochastic
        self.action_dim = action_dim
        self.net = mlp(obs_dim, action_dim * (2 if stochastic else 1))

    def forward(self, state, deterministic=False):
        output = self.net(state)
        if not self.stochastic:
            return output.tanh(), None
        mean, log_std = output.chunk(2, dim=-1)
        dist = Normal(mean, log_std.clamp(-5, 2).exp())
        latent = mean if deterministic else dist.rsample()
        action = latent.tanh()
        # Stable exact log(1 - tanh(z)^2), avoiding a saturated-action log(0).
        correction = 2 * (np.log(2.0) - latent - nn.functional.softplus(-2 * latent))
        log_prob = (dist.log_prob(latent) - correction).sum(-1, keepdim=True)
        return action, log_prob


class Critic(nn.Module):
    def __init__(self, obs_dim, action_dim):
        super().__init__()
        self.net = mlp(obs_dim + action_dim, 1)

    def forward(self, state, action):
        return self.net(torch.cat((state, action), dim=-1))


class Replay:
    def __init__(self, obs_dim, action_dim, seed, capacity=100000):
        self.s = np.zeros((capacity, obs_dim), np.float32)
        self.a = np.zeros((capacity, action_dim), np.float32)
        self.r = np.zeros((capacity, 1), np.float32)
        self.ns = np.zeros_like(self.s)
        self.term = np.zeros_like(self.r)
        self.position, self.size, self.capacity = 0, 0, capacity
        self.rng = np.random.default_rng(seed)

    def add(self, state, action, reward, nxt, terminated):
        i = self.position
        self.s[i], self.a[i], self.r[i] = state, action, reward
        self.ns[i], self.term[i] = nxt, float(terminated)
        self.position = (i + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)

    def sample(self, batch):
        indices = self.rng.integers(self.size, size=batch)
        return [torch.as_tensor(x[indices]) for x in (self.s, self.a, self.r, self.ns, self.term)]


def soft_update(target, source, tau=0.005):
    with torch.no_grad():
        for t, p in zip(target.parameters(), source.parameters()):
            t.mul_(1 - tau).add_(p, alpha=tau)


def make_env(name):
    if name == "PointRobot-v0":
        from lesson_48 import PointRobotEnv
        return PointRobotEnv()
    return gym.make(name)


def evaluate(actor, seed, episodes, scale, center, env_name):
    env = make_env(env_name)
    scores = []
    for episode in range(episodes):
        state, _ = env.reset(seed=seed + episode)
        score = 0.0
        while True:
            with torch.no_grad():
                action, _ = actor(torch.tensor(state, dtype=torch.float32), deterministic=True)
            state, reward, term, trunc, _ = env.step(center + scale * action.numpy())
            score += reward
            if term or trunc:
                break
        scores.append(score)
    env.close()
    return scores


def run(mode):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=50000)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--env", choices=["Pendulum-v1", "PointRobot-v0"], default="Pendulum-v1")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    steps = min(args.steps, 256) if args.smoke else args.steps
    if steps < 1:
        parser.error("--steps must be positive")
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.set_num_threads(1)
    rng = np.random.default_rng(args.seed)
    env = make_env(args.env)
    state, _ = env.reset(seed=args.seed)
    obs_dim, action_dim = env.observation_space.shape[0], env.action_space.shape[0]
    scale = (env.action_space.high - env.action_space.low) / 2
    center = (env.action_space.high + env.action_space.low) / 2
    log_scale = float(np.log(scale).sum())
    actor = Actor(obs_dim, action_dim, mode == "sac")
    actor_target = copy.deepcopy(actor)
    q1, q2 = Critic(obs_dim, action_dim), Critic(obs_dim, action_dim)
    t1, t2 = copy.deepcopy(q1), copy.deepcopy(q2)
    critics = list(q1.parameters()) + ([] if mode == "ddpg" else list(q2.parameters()))
    actor_opt = torch.optim.Adam(actor.parameters(), lr=3e-4)
    critic_opt = torch.optim.Adam(critics, lr=3e-4)
    log_alpha = torch.tensor(np.log(0.2), dtype=torch.float32, requires_grad=True)
    alpha_opt = torch.optim.Adam([log_alpha], lr=3e-4)
    target_entropy = -action_dim + log_scale  # entropy target in physical coordinates
    replay = Replay(obs_dim, action_dim, args.seed)
    warmup = min(1000, max(1, steps // 4))
    batch, gamma = 64, 0.99
    updates, episode_return, returns = 0, 0.0, []
    for step in range(steps):
        if step < warmup:
            action = rng.uniform(-1, 1, action_dim).astype(np.float32)
        else:
            with torch.no_grad():
                action, _ = actor(torch.tensor(state, dtype=torch.float32))
            action = action.numpy()
            if mode != "sac":
                action = np.clip(action + rng.normal(0, 0.1, action_dim), -1, 1).astype(np.float32)
        nxt, reward, term, trunc, _ = env.step(center + scale * action)
        replay.add(state, action, reward, nxt, term)
        state = nxt
        episode_return += reward
        if term or trunc:
            returns.append(episode_return)
            episode_return = 0.0
            state, _ = env.reset()
        if step < warmup or replay.size < batch:
            continue
        s, a, r, ns, terminated = replay.sample(batch)
        alpha = log_alpha.exp().detach()
        with torch.no_grad():
            if mode == "sac":
                na, next_log_prob = actor(ns)
                next_log_prob = next_log_prob - log_scale
                bootstrap = torch.minimum(t1(ns, na), t2(ns, na)) - alpha * next_log_prob
            else:
                na, _ = actor_target(ns)
                if mode == "td3":
                    noise = (torch.randn_like(na) * 0.2).clamp(-0.5, 0.5)
                    na = (na + noise).clamp(-1, 1)
                    bootstrap = torch.minimum(t1(ns, na), t2(ns, na))
                else:
                    bootstrap = t1(ns, na)
            target = r + gamma * (1 - terminated) * bootstrap
        loss = (q1(s, a) - target).square().mean()
        if mode != "ddpg":
            loss = loss + (q2(s, a) - target).square().mean()
        critic_opt.zero_grad()
        loss.backward()
        critic_opt.step()
        updates += 1
        if mode != "td3" or updates % 2 == 0:
            for parameter in critics:
                parameter.requires_grad_(False)
            pa, log_prob = actor(s)
            if mode == "sac":
                log_prob = log_prob - log_scale
                actor_loss = (alpha * log_prob - torch.minimum(q1(s, pa), q2(s, pa))).mean()
            else:
                actor_loss = -q1(s, pa).mean()
            actor_opt.zero_grad()
            actor_loss.backward()
            actor_opt.step()
            for parameter in critics:
                parameter.requires_grad_(True)
            if mode == "sac":
                alpha_loss = -(log_alpha * (log_prob.detach() + target_entropy)).mean()
                alpha_opt.zero_grad()
                alpha_loss.backward()
                alpha_opt.step()
            soft_update(actor_target, actor)
            soft_update(t1, q1)
            if mode != "ddpg":
                soft_update(t2, q2)
    env.close()
    scores = evaluate(actor, args.seed + 10000, 1 if args.smoke else 5, scale, center, args.env)
    print(f"{mode}: steps={steps}, critic_updates={updates}, alpha={float(log_alpha.exp().detach()):.4f}")
    print("Independent deterministic evaluation:", scores, "mean=", float(np.mean(scores)))
    print("A smoke run checks execution; compare learning using multiple training seeds.")
    if args.plot:
        import matplotlib.pyplot as plt
        plt.plot(returns)
        plt.xlabel("Completed training episode")
        plt.ylabel("Undiscounted episode reward")
        plt.title(f"{mode}, seed {args.seed}")
        plt.show()
