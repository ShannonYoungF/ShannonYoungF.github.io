import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(7)
gamma = 0.9
plans = {'take_now': [2.0], 'move_then_take': [0.0, 5.0]}
values = {name: sum(gamma**t*r for t, r in enumerate(path))
          for name, path in plans.items()}
v_b = 5.0
q_a = np.array([2.0, 0.0+gamma*v_b])
v_a = np.max(q_a)
print('Enumerated plan returns:', values)
print('Optimal B value:', v_b, 'A action values:', q_a)
print('Optimal A action:', list(plans)[int(np.argmax(q_a))], 'value:', v_a)
assert np.isclose(v_a, max(values.values()))
plt.bar(list(values), list(values.values()))
plt.ylabel('Discounted return'); plt.tight_layout(); plt.show()
