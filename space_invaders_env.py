import gymnasium as gym
from gymnasium import spaces
import numpy as np

from spaceinvaders import SpaceInvaders

from gymnasium.utils.env_checker import check_env

class SpaceInvadersEnv(gym.Env):
    def __init__(self, game, show_training=False):
        super().__init__()

        self.game = game   

        self.render_every = 10
        self.step_count = 0
        self.show_training = show_training

        # Valid actions: 0, 1, 2, 3, 4, 5
        self.action_space = spaces.Discrete(6)

        # State contains three normalized numbers
        # self.observation_space = spaces.Box(
        #     #low=np.zeros(7, dtype=np.float32),
        #     #high=np.ones(7, dtype=np.float32),
        #     low=np.array([0, -1, 0, -1, 0, -1, -1, 0, 0], dtype=np.float32),
        #     high=np.ones(9, dtype=np.float32),
        #     dtype=np.float32
        # )

        self.observation_space = spaces.Box(
            low=np.array(
                [0, -1, -1, -1, 0, 0] + [0] * 16,
                dtype=np.float32
            ),
            high=np.array(
                [1, 1, 1, 1, 1, 1] + [1] * 16,
                dtype=np.float32
            ),
            dtype=np.float32
        )

    def step(self, action):
        state, reward, done = self.game.advance(int(action))

        self.step_count += 1

        if (
            self.show_training
            and self.step_count % self.game.speed_multiplier == 0
        ):
            self.game.render_frame()
            self.game.clock.tick(60)

        terminated = done
        truncated = False
        info = {}

        return state, float(reward), terminated, truncated, info

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.step_count = 0

        state = self.game.reset_game()
        info = {}

        return state, info

        # super().reset(seed=seed)

        # if seed is not None:
        #     random.seed(seed)

        # state = self.game.reset_game()
        # return np.asarray(state, dtype=np.float32), {}

if __name__ == "__main__":
    # game = SpaceInvaders()
    # env = SpaceInvadersEnv(game)

    # state, info = env.reset()

    # print(state)
    # print("type:", type(state))
    # print("shape:", state.shape)
    # print("dtype:", state.dtype)
    # print("valid:", env.observation_space.contains(state))

    # print("space:", env.observation_space)
    # print("space shape:", env.observation_space.shape)
    # print("space dtype:", env.observation_space.dtype)
    # print("low:", env.observation_space.low)
    # print("high:", env.observation_space.high)

    # state, _ = env.reset()
    # print(env.observation_space.contains(state))

    game = SpaceInvaders()
    env = SpaceInvadersEnv(game)

    check_env(env, skip_render_check=True)
    print("Environment check passed")

    