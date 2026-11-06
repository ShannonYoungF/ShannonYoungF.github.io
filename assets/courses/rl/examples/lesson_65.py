import numpy as np
import json
import platform
from pathlib import Path
K, horizon = 1.5, 40
true_a, control_b, noise_std = 1.1, 0.5, 0.03
def episode(k, seed):
    rng = np.random.default_rng(seed)
    x = 2.0; cost = 0.0; violations = 0
    for _ in range(horizon):
        u = np.clip(-K*x+k*np.tanh(x), -1, 1)
        cost += x*x+0.1*u*u
        x = true_a*x+control_b*u+rng.normal(0, noise_std)
        violations += abs(x)>3
    return cost, violations
rng = np.random.default_rng(65)
candidates = np.r_[0.0, rng.uniform(-0.5, 0.5, 30)]
train_seeds, test_seeds = range(5), range(100, 130)
scores = [np.mean([episode(k, s)[0] for s in train_seeds]) for k in candidates]
k_best = float(candidates[np.argmin(scores)])
results = {}
for name, k in [("baseline", 0.0), ("searched residual", k_best)]:
    runs = np.array([episode(k, s) for s in test_seeds])
    results[name] = {"k": k, "mean_cost": float(runs[:, 0].mean()),
                     "cost_std": float(runs[:, 0].std(ddof=1)),
                     "mean_violations": float(runs[:, 1].mean()),
                     "episode_costs": runs[:, 0].tolist(),
                     "episode_violation_counts": runs[:, 1].astype(int).tolist()}
report = {"python": platform.python_version(), "numpy": np.__version__,
          "selection_seed": 65,
          "config": {"K": K, "horizon": horizon, "initial_state": 2.0,
                     "true_a": true_a, "control_b": control_b,
                     "noise_std": noise_std, "violation_threshold": 3.0,
                     "action_bounds": [-1.0, 1.0], "candidate_count": len(candidates)},
          "training_seeds": list(train_seeds),
          "candidate_log": [{"k": float(k), "mean_training_cost": float(score)}
                            for k, score in zip(candidates, scores)],
          "training_env_steps": len(candidates)*len(train_seeds)*horizon,
          "evaluation_env_steps": len(results)*len(test_seeds)*horizon,
          "evaluation_seeds": list(test_seeds), "results": results,
          "scope": "scalar finite-horizon teaching prototype; not PPO or SAC"}
Path("lesson65_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
