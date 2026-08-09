from stable_baselines3 import DQN
from spaceinvaders import SpaceInvaders
from space_invaders_env import SpaceInvadersEnv

game = SpaceInvaders(start_speed=1)
env = SpaceInvadersEnv(game, show_training=True)

model = DQN.load("space_invaders_dqn")

obs, _ = env.reset()

action_counts = [0] * 6

while True:
    action, _ = model.predict(obs, deterministic=True)
    action_counts[int(action)] += 1

    obs, reward, terminated, truncated, _ = env.step(action)
    
    if terminated or truncated:
        obs, _ = env.reset()
        print("Actions:", action_counts)
        action_counts = [0] * 6