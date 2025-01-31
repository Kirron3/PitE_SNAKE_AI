# Snake Game AI Project

This project implements a classic Snake game with an AI player that learns to play using Q-learning, a reinforcement learning technique. The project is structured into three main components: the game engine, the AI agent, and a logging system.

## Project Structure

```
snake_project/
│
├── game.py         # Snake game implementation
├── ai.py           # Q-learning AI implementation
├── snake_logger.py # Logging and visualization system
└── logs/           # Directory containing training logs and plots
```

## Components

### Game Engine (game.py)
The game engine implements the classic Snake game with modern features:
- Snake class managing the snake's body and movement
- Fruit class handling collectible items
- Game class orchestrating the game logic and rendering
- Configurable game parameters (speed, size, visibility)
- Different colored fruits with equal point values
- Progressive difficulty increase as the score rises

Key Features:
- Customizable window size (default: 800x600)
- Adjustable game speed
- Support for both visible and hidden gameplay (for AI training)
- Collision detection with walls and self

### AI Agent (ai.py)
The AI implementation uses Q-learning to teach the snake how to play:

#### Key Components:
- SnakeAI class managing the learning process
- State representation including:
  - Danger detection in three directions
  - Relative fruit position
  - Current movement direction
- Actions: straight, left turn, right turn

#### Learning Parameters:
- Learning rate: 0.1
- Discount factor: 0.95
- Initial exploration rate (epsilon): 1.0
- Epsilon decay: 0.998
- Minimum epsilon: 0.01

#### Training Process:
1. State observation
2. Action selection (exploration vs exploitation)
3. Reward calculation based on:
   - Fruit collection (+10)
   - Game over (-10)
   - Steps without fruit (penalty after 100 steps)
4. Q-table update
5. Model persistence (saved as 'snake_ai.pkl')

### Logging System (snake_logger.py)
Comprehensive logging and visualization system:

#### Features:
- Training progress tracking
- Performance metrics logging
- Statistical analysis
- Automated plot generation
- Data persistence

#### Logged Metrics:
- Game scores
- Q-table size evolution
- Average performance
- Training duration
- Best scores achieved

#### Visualization:
- Training progress plots
- Score evolution graphs
- Q-table growth visualization
- Support for large datasets (automatic data sampling)

## Usage

### Running the Game
```python
from game import Game

game = Game(visible=True)
game.run()
```

### Training the AI
```python
from ai import SnakeAI

ai = SnakeAI()
ai.train(num_games=500)  # Adjust number of games as needed
```

### Watching the AI Play
```python
ai.play(speed=0.1)  # Adjust speed to control visualization
```

## Training Process
1. The AI starts with no knowledge (empty Q-table)
2. During training, it learns by:
   - Exploring random actions (early stages)
   - Exploiting learned patterns (later stages)
   - Balancing exploration/exploitation through epsilon decay
3. Training progress is automatically logged and visualized
4. A trained model is saved for later use

## Performance Monitoring
The logging system provides:
- Real-time training statistics
- Progress visualization
- Performance metrics
- Training summary reports

All data is saved in the `logs` directory with timestamped files for easy tracking and comparison between training sessions.

## Controls
- Arrow keys for manual play
- ESC to quit AI demonstration
- R to restart after game over

## Technical Requirements
- Python 3.x
- pygame
- numpy
- matplotlib (for visualization)
