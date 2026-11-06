"""Fit a nonlinear value surface with a tiny neural network; no RL framework."""
import argparse
import numpy as np
import torch
from torch import nn

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--updates', type=int, default=1000)
    p.add_argument('--seed', type=int, default=25)
    a = p.parse_args()
    torch.manual_seed(a.seed)
    rng = np.random.default_rng(a.seed)
    torch.set_num_threads(1)
    # A fixed supervised target isolates approximation before bootstrapping.
    x = torch.from_numpy(rng.uniform(-1, 1, (128, 1)).astype('float32'))
    y = torch.cos(3 * x) + 0.2 * x
    model = nn.Sequential(nn.Linear(1, 32), nn.Tanh(), nn.Linear(32, 1))
    opt = torch.optim.Adam(model.parameters(), lr=0.01)
    initial = nn.functional.mse_loss(model(x), y).item()
    for _ in range(a.updates):
        loss = nn.functional.mse_loss(model(x), y)
        opt.zero_grad(); loss.backward(); opt.step()
    test_x = torch.linspace(-1, 1, 201).reshape(-1, 1)
    with torch.no_grad():
        test_y = torch.cos(3 * test_x) + 0.2 * test_x
        test_mse = nn.functional.mse_loss(model(test_x), test_y).item()
    print('initial training MSE:', initial)
    print('final training MSE:', loss.item(), 'grid test MSE:', test_mse)
    for name, param in model.named_parameters():
        print(name, tuple(param.shape), 'gradient norm:', param.grad.norm().item())
    print('Small supervised error alone is not evidence of a correct RL policy.')
