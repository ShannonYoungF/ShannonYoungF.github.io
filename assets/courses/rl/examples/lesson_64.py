import json
import math
from pathlib import Path
plan = {
    "hypothesis": "Bounded residual SAC improves adaptation under specified mismatch",
    "mechanism": "A useful feedback baseline reduces what must be relearned",
    "training_budget_env_steps": 100000,
    "training_seeds": list(range(5)),
    "primary_metric": "held-out integrated tracking error",
    "safety_metric": "constraint violation rate, reported separately",
    "baselines": ["fixed controller", "SAC from scratch", "residual SAC"],
    "ablations": ["remove residual bound", "replace useful baseline"],
    "test_conditions": ["held-out mismatch values", "held-out disturbances"],
    "falsification": "no meaningful improvement or unacceptable safety degradation"
}
sigma, half_width = 8.0, 4.0
print("rough independent units needed:", math.ceil((1.96*sigma/half_width)**2))
Path("lesson64_research_plan.json").write_text(
    json.dumps(plan, indent=2), encoding="utf-8")
print("The five-seed example plan is exploratory, not the calculated precision target.")
