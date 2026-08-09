from stable_baselines3 import DQN
from stable_baselines3.common.evaluation import evaluate_policy


model = DQN.load("space_invaders_dqn_v1")
print(model.observation_space)
print(model.action_space)
print(model.learning_rate)
print(model.gamma)