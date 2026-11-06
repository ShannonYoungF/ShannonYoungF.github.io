# Download rl_policy_common.py into this directory.
# python lesson_34.py --smoke
# python lesson_34.py --steps 20000 --seed 7 --plot
from rl_policy_common import run
if __name__ == "__main__":
    run("ac")  # lambda=0: one-step TD advantage
