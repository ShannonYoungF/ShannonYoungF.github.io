import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(55)
q_values = np.linspace(0, 1, 101)
go_value = 1-3*q_values
for q in [0.1, 0.8]:
    other_go = rng.random(100000) < q
    reward = np.where(other_go, -2.0, 1.0)
    print("other go probability", q,
          "empirical own-go value", reward.mean(), "exact", 1-3*q)
plt.plot(q_values, go_value, label="Q(go)")
plt.axhline(0, color="gray", linestyle="--", label="Q(wait)")
plt.axvline(1/3, color="gray", linestyle=":")
plt.xlabel("other agent go probability")
plt.ylabel("expected one-step reward")
plt.legend(); plt.tight_layout(); plt.savefig("lesson55_game.png")
