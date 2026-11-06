"""Dueling DQN. Download lesson_26.py into this same directory first.
pip install numpy torch gymnasium; python lesson_29.py --smoke
"""
import torch
from torch import nn
from lesson_26 import parser, train

class DuelingNetwork(nn.Module):
    def __init__(self, obs_dim, actions):
        super().__init__()
        self.features = nn.Sequential(nn.Linear(obs_dim, 64), nn.ReLU())
        self.value = nn.Sequential(nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 1))
        self.advantage = nn.Sequential(nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, actions))
    def forward(self, x):
        hidden = self.features(x)
        value, advantage = self.value(hidden), self.advantage(hidden)
        # Average over actions within each state, never over the batch.
        return value + advantage - advantage.mean(dim=1, keepdim=True)

def aggregation_demo():
    value = torch.tensor([[3.0]])
    raw = torch.tensor([[1.0, -1.0, 2.0]])
    q = value + raw - raw.mean(1, keepdim=True)
    shifted = raw + 100
    q_shifted = value + shifted - shifted.mean(1, keepdim=True)
    print('mean-centered Q:', q.numpy())
    print('mean Q equals V:', q.mean().item(), value.item())
    print('constant advantage-shift error:', (q-q_shifted).abs().max().item())
    assert torch.allclose(q, q_shifted, atol=1e-5)

if __name__ == '__main__':
    aggregation_demo()
    # Keep the DQN target unchanged to isolate architecture from Double DQN.
    train(parser(default_seed=29).parse_args(), network_factory=DuelingNetwork)
