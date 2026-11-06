import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(7)
p_success, gamma = 0.8, 0.9
exact = (p_success*5-(1-p_success))/(1-(1-p_success)*gamma)
returns, capped = [], 0
for episode in range(20000):
    total, discount = 0.0, 1.0
    for step in range(1000):  # numerical guard, not task termination
        success = rng.random() < p_success
        reward = 5.0 if success else -1.0
        total += discount*reward
        if success:
            break
        discount *= gamma
    else:
        capped += 1
    returns.append(total)
returns = np.array(returns)
print('Bellman solution:', exact)
print('Simulated mean:', returns.mean(), 'capped episodes:', capped)
print('Sample mean standard error:', returns.std(ddof=1)/np.sqrt(len(returns)))
plt.plot(np.cumsum(returns)/np.arange(1, len(returns)+1), label='mean return')
plt.axhline(exact, color='gray', linestyle='--', label='Bellman solution')
plt.xlabel('Independent episodes'); plt.ylabel('Estimated value'); plt.legend()
plt.tight_layout(); plt.show()
