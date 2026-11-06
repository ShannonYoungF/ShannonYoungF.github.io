import json
from pathlib import Path
# Deterministic reading worksheet: no random process is involved.
record = {
    "paper": "Fill in title, year, version, URL",
    "question": "Which concrete failure motivates the method?",
    "claim": {"setting": "", "baseline": "", "metric": "", "scope": ""},
    "theory": {"assumptions": [], "result": "", "unproved_bridge": ""},
    "implementation": {"target_equation": "", "code_location": "",
                       "gradient_stops": "", "data_distribution": ""},
    "evidence": {"environment": "", "budget": "", "training_seeds": [],
                 "evaluation_episodes": "", "ablations": []},
    "limitations": [],
    "next_test": ""
}
Path("lesson59_reading.json").write_text(
    json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
gamma, epsilon = 0.9, 0.02
print("conditional asymptotic bound:", epsilon/(1-gamma))
print("Do not substitute average squared TD loss for a uniform backup bound.")
