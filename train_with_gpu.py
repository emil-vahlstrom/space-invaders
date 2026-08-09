from stable_baselines3 import DQN
from spaceinvaders import SpaceInvaders
from space_invaders_env import SpaceInvadersEnv

game = SpaceInvaders(start_speed=10)
env = SpaceInvadersEnv(game, show_training=False)

model = DQN(
    "MlpPolicy",
    env,
    verbose=1,
    device="cuda" # or device cpu
)

import torch

print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))