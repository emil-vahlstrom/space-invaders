# Space Invaders RL

This project is a reinforcement-learning experiment built on top of the original
[Space Invaders](https://github.com/leerob/space-invaders) Pygame project by Lee Robinson.

The original game was forked and refactored so that it can be controlled both by a human player and by a reinforcement-learning agent.

## What I changed

The game was modified to support:

- A fixed-step game simulation independent of rendering speed
- Adjustable simulation speed
- A discrete action interface for human and AI control
- A custom Gymnasium environment
- Reinforcement learning using Stable-Baselines3 DQN
- Headless training without rendering
- Model evaluation against a random-action baseline
- Checkpointing and deterministic AI playback

## AI actions

The agent has six possible actions:

1. Stay
2. Move left
3. Move right
4. Shoot
5. Move left + shoot
6. Move right + shoot

## Observation space

The neural network receives a compact representation of the current game state rather than the raw screen image.

The current observation contains 25 values:

- Player horizontal position
- Relative X/Y position of the current target enemy
- Enemy formation direction
- Whether the player can currently shoot
- Fraction of enemies remaining
- Predicted danger when moving left
- Predicted danger when staying still
- Predicted danger when moving right
- 16 horizontal bullet-danger lanes covering the screen

The danger information is calculated from enemy bullet positions and predicted movement, allowing the agent to learn basic bullet avoidance.

## Reward system

The reward function is intentionally kept relatively simple.

The agent receives:

- `+1` for destroying an enemy
- `+5` for clearing a round
- `-10` for losing a life
- `-10` for game over
- A very small time penalty to discourage wasting time
- Small shaping rewards for moving toward the current target
- Small shaping rewards or penalties for moving away from or toward bullet danger

Earlier versions used much stronger reward shaping. This often caused the agent to exploit the reward function instead of actually learning to play the game.

## Reinforcement learning

The project uses:

- **Pygame** — game simulation and rendering
- **Gymnasium** — RL environment interface
- **Stable-Baselines3** — DQN implementation
- **PyTorch** — neural network backend
- **NumPy** — observation representation

The agent uses a DQN with an MLP policy and six discrete actions.

## Results

The trained agent learned to:

- Track and approach enemy targets
- Shoot enemies
- Avoid many incoming bullets
- Clear complete waves
- Play substantially better than a random-action agent

Example evaluation over 100 episodes:

```text
AI average reward:      349.47
AI standard deviation:   29.52

Random average reward:   -6.24
Random std deviation:    12.57