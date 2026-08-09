from stable_baselines3 import DQN
from stable_baselines3.common.evaluation import evaluate_policy

from spaceinvaders import SpaceInvaders
from space_invaders_env import SpaceInvadersEnv

import numpy as np

game = SpaceInvaders(start_speed=50)
env = SpaceInvadersEnv(game, show_training=False)

model = DQN.load("space_invaders_dqn")

mean_reward, std_reward = evaluate_policy(
    model,
    env,
    n_eval_episodes=100,
    deterministic=True
)

print("AI average reward:", mean_reward)
print("Standard deviation:", std_reward)

rewards = []

for _ in range(100):
    obs, _ = env.reset()
    total_reward = 0
    done = False

    while not done:
        action = env.action_space.sample()

        obs, reward, terminated, truncated, _ = env.step(action)

        total_reward += reward
        done = terminated or truncated

    rewards.append(total_reward)

print("Random average reward:", np.mean(rewards))
print("Random std deviation:", np.std(rewards))