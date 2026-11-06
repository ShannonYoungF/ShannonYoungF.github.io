# Same explicit core as DDPG, now with all three TD3 mechanisms.
# python lesson_43.py --smoke
# python lesson_43.py --steps 50000 --seed 7 --plot
from rl_continuous_common import run
if __name__ == "__main__":
    run("td3")
