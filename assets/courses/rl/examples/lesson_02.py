import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(7)  # no sampling is needed for these fixed paths

def backward_return(rewards, gamma):
    total = 0.0
    for reward in reversed(rewards):
        total = reward + gamma * total
    return total

paths = {'A': [4.0], 'B': [0.0, 0.0, 8.0]}
for gamma in [0.5, 0.9]:
    for name, rewards in paths.items():
        direct = np.dot(gamma ** np.arange(len(rewards)), rewards)
        recursive = backward_return(rewards, gamma)
        assert np.isclose(direct, recursive)
        print(f'gamma={gamma}: route {name}, return={recursive:.4f}')
grid = np.linspace(0, 1, 201)
for name, rewards in paths.items():
    plt.plot(grid, [backward_return(rewards, g) for g in grid], label=name)
plt.axvline(1 / np.sqrt(2), linestyle='--', color='gray', label='tie')
plt.xlabel('Discount gamma'); plt.ylabel('Return'); plt.legend()
plt.tight_layout(); plt.show()
