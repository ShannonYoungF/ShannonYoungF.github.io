"""A standalone planar double-integrator Gymnasium environment.

python lesson_48.py --smoke
python lesson_48.py --plot
python lesson_45.py --env PointRobot-v0 --steps 50000 --plot
"""
import argparse
import numpy as np
import gymnasium as gym
from gymnasium import spaces


class PointRobotEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self, dt=0.05, noise=0.0, horizon=200):
        super().__init__()
        self.dt, self.noise, self.horizon = dt, noise, horizon
        self.action_space = spaces.Box(-1, 1, shape=(2,), dtype=np.float32)
        self.observation_space = spaces.Box(-np.inf, np.inf, shape=(4,), dtype=np.float32)
        self.obstacle = np.array([0.65, 0.0])
        self.radius = 0.25
        self.state = np.zeros(4, dtype=np.float32)
        self.elapsed = 0

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        position = np.asarray((options or {}).get("position", self.np_random.uniform(-2, 2, 2)))
        # Reject initial positions already inside the obstacle or goal region.
        while np.linalg.norm(position-self.obstacle) <= self.radius or np.linalg.norm(position) < .2:
            position = self.np_random.uniform(-2, 2, 2)
        self.state = np.concatenate([position, np.zeros(2)]).astype(np.float32)
        self.elapsed = 0
        return self.state.copy(), {"success": False, "collision": False}

    def step(self, action):
        acceleration = np.clip(np.asarray(action, dtype=np.float32), -1, 1)
        acceleration = acceleration + self.np_random.normal(0, self.noise, 2)
        previous = self.state[:2].astype(float).copy()
        position = previous + self.state[2:]*self.dt + .5*acceleration*self.dt**2
        velocity = self.state[2:] + acceleration*self.dt
        self.state = np.concatenate([position, velocity]).astype(np.float32)
        self.elapsed += 1
        segment = position-previous
        fraction = np.clip(np.dot(self.obstacle-previous, segment)/(segment@segment+1e-12), 0, 1)
        collision = bool(np.linalg.norm(previous+fraction*segment-self.obstacle) <= self.radius)
        success = bool(np.linalg.norm(position)<.1 and np.linalg.norm(velocity)<.2)
        outside = bool(np.linalg.norm(position)>5)
        terminated = success or collision or outside
        truncated = self.elapsed >= self.horizon and not terminated
        energy = self.dt*float(acceleration@acceleration)
        reward = -self.dt*(float(position@position)+.05*float(acceleration@acceleration))
        reward += 20*success - 20*(collision or outside)
        info = {"success": success, "collision": collision, "outside": outside,
                "control_energy": energy, "distance": float(np.linalg.norm(position))}
        return self.state.copy(), float(reward), terminated, truncated, info


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    env = PointRobotEnv()
    obs, _ = env.reset(seed=7, options={"position": [-1.6, 1.2]})
    trajectory, score, energy = [obs[:2].copy()], 0.0, 0.0
    for _ in range(16 if args.smoke else env.horizon):
        action = np.clip(-1.2*obs[:2]-1.0*obs[2:], -1, 1)  # PD baseline
        obs, reward, term, trunc, info = env.step(action)
        trajectory.append(obs[:2].copy())
        score += reward
        energy += info["control_energy"]
        if term or trunc:
            break
    print("PD baseline:", info, "return=",score,"energy=",energy)
    if args.plot:
        import matplotlib.pyplot as plt
        xy = np.asarray(trajectory)
        fig, ax = plt.subplots()
        ax.plot(xy[:,0], xy[:,1], label="PD trajectory")
        ax.add_patch(plt.Circle(env.obstacle, env.radius, alpha=.4, color="tab:red"))
        ax.scatter([0],[0],marker="*",s=120,label="goal")
        ax.set(xlabel="x (m)",ylabel="y (m)",aspect="equal")
        ax.legend(); plt.show()
    env.close()
