from stable_baselines3 import DQN

from stable_baselines3.common.callbacks import CheckpointCallback

checkpoint_callback = CheckpointCallback(
    save_freq=100_000,
    save_path="./checkpoints/",
    name_prefix="space_invaders"
)

from spaceinvaders import SpaceInvaders
from space_invaders_env import SpaceInvadersEnv

game = SpaceInvaders(start_speed=10)
env = SpaceInvadersEnv(game, show_training=False)

model = DQN(
    "MlpPolicy",
    env,
    verbose=1
)

#model.learn(total_timesteps=1_000)
model.learn(
    #total_timesteps=10_000,
    total_timesteps=100_000,
    #total_timesteps=200_000,
    #total_timesteps=500_000,
    #total_timesteps=1_000_000,
    log_interval=1,
    callback=checkpoint_callback)
model.save("space_invaders_dqn")

print("Training test finished") 