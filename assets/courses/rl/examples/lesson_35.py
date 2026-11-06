# Four separate environments, synchronously collected and updated.
# python lesson_35.py --smoke
# python lesson_35.py --steps 20000 --seed 7 --plot
from rl_policy_common import run
if __name__ == "__main__":
    run("a2c")
