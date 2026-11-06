import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(7)  # deterministic example
DT = 0.5

def step(state, acceleration):
    x, v = state
    return np.array([x+v*DT, v+acceleration*DT])

for velocity in [0.0, 2.0]:
    state = np.array([0.5, velocity]); positions = [state[0]]
    for _ in range(4):
        state = step(state, 0.0); positions.append(state[0])
    print('initial velocity:', velocity, 'next position:', positions[1])
    plt.plot(np.arange(5)*DT, positions, marker='o', label=f'v={velocity}')
x_previous, x_current, u_previous = 0.0, 0.5, 2.0
v_reconstructed = (x_current-x_previous)/DT + u_previous*DT
print('Current velocity reconstructed from history:', v_reconstructed)
plt.axhline(1.0, linestyle='--', color='gray', label='wall position')
plt.xlabel('Time (s)'); plt.ylabel('Position (m)'); plt.legend()
plt.tight_layout(); plt.show()
