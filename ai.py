import numpy as np
import pygame
import random
from game import Game, Direction
import pickle
from time import sleep
import time
import os
from snake_logger import SnakeLogger

class SnakeAI:
    def __init__(self):
         # Q-learning parameters
        self.learning_rate = 0.05  # Controls how much new information overrides old knowledge (higher = faster learning, but less stable)
        self.discount_factor = 0.95  # Determines how much future rewards are taken into account (higher = considers long-term gains more)
        self.epsilon = 1.0  # Exploration rate, determines how often the AI explores random actions instead of choosing the best known action
        self.epsilon_decay = 0.998  # Controls how quickly the AI reduces exploration over time (higher = slower decay, more exploration)
        self.epsilon_min = 0.01  # Minimum exploration rate to prevent complete exploitation and allow some continued exploration
        
        # Q-table to store state-action values
        self.q_table = {}  # Dictionary storing state-action mappings and their expected rewards
        
        # Logger for recording training progress
        self.logger = SnakeLogger()
    
    #   """Convert game state to a tuple for Q-table
    def get_state(self, game):
        snake_head = game.snake.body[0]
        fruit_pos = game.fruit.position
        
        # Get relative direction of fruit
        rel_x = fruit_pos[0] - snake_head[0]
        rel_y = fruit_pos[1] - snake_head[1]
        
        # Check immediate dangers
        danger_straight = False
        danger_left = False
        danger_right = False
        
        # Current direction
        current_dir = game.snake.direction
        
        # Simple danger check based on current direction
        if current_dir == Direction.UP:
            danger_straight = (snake_head[1] - game.block_size < 0)
            danger_left = (snake_head[0] - game.block_size < 0)
            danger_right = (snake_head[0] + game.block_size >= game.width)
        elif current_dir == Direction.DOWN:
            danger_straight = (snake_head[1] + game.block_size >= game.height)
            danger_left = (snake_head[0] + game.block_size >= game.width)
            danger_right = (snake_head[0] - game.block_size < 0)
        elif current_dir == Direction.LEFT:
            danger_straight = (snake_head[0] - game.block_size < 0)
            danger_left = (snake_head[1] + game.block_size >= game.height)
            danger_right = (snake_head[1] - game.block_size < 0)
        elif current_dir == Direction.RIGHT:
            danger_straight = (snake_head[0] + game.block_size >= game.width)
            danger_left = (snake_head[1] - game.block_size < 0)
            danger_right = (snake_head[1] + game.block_size >= game.height)
            
        # Also check if any of these positions contain snake body
        for segment in game.snake.body[1:]:
            if current_dir == Direction.UP:
                if (snake_head[0], snake_head[1] - game.block_size) == segment:
                    danger_straight = True
                if (snake_head[0] - game.block_size, snake_head[1]) == segment:
                    danger_left = True
                if (snake_head[0] + game.block_size, snake_head[1]) == segment:
                    danger_right = True
            elif current_dir == Direction.DOWN:
                if (snake_head[0], snake_head[1] + game.block_size) == segment:
                    danger_straight = True
                if (snake_head[0] + game.block_size, snake_head[1]) == segment:
                    danger_left = True
                if (snake_head[0] - game.block_size, snake_head[1]) == segment:
                    danger_right = True
            elif current_dir == Direction.LEFT:
                if (snake_head[0] - game.block_size, snake_head[1]) == segment:
                    danger_straight = True
                if (snake_head[0], snake_head[1] + game.block_size) == segment:
                    danger_left = True
                if (snake_head[0], snake_head[1] - game.block_size) == segment:
                    danger_right = True
            elif current_dir == Direction.RIGHT:
                if (snake_head[0] + game.block_size, snake_head[1]) == segment:
                    danger_straight = True
                if (snake_head[0], snake_head[1] - game.block_size) == segment:
                    danger_left = True
                if (snake_head[0], snake_head[1] + game.block_size) == segment:
                    danger_right = True
        

        ### RETURN CURRENT STATE AFTER ANALYSIS
        return (
            # Dangers
            danger_straight,
            danger_left,
            danger_right,
            # Fruit direction
            rel_x > 0,  # fruit is to the right
            rel_x < 0,  # fruit is to the left
            rel_y > 0,  # fruit is below
            rel_y < 0,  # fruit is above
            # Current direction
            current_dir == Direction.UP,
            current_dir == Direction.DOWN,
            current_dir == Direction.LEFT,
            current_dir == Direction.RIGHT
        )

    # Choose action based on epsilon-greedy policy
    def get_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, 2)  # 0: straight, 1: left, 2: right
            
        if state not in self.q_table:
            self.q_table[state] = [0, 0, 0]
            
        return np.argmax(self.q_table[state])


            
    # Apply chosen action to the game
    def apply_action(self, game, action):
        current_direction = game.snake.direction
        
        if action == 1:  # Turn left
            if current_direction == Direction.UP:
                game.snake.direction = Direction.LEFT
            elif current_direction == Direction.LEFT:
                game.snake.direction = Direction.DOWN
            elif current_direction == Direction.DOWN:
                game.snake.direction = Direction.RIGHT
            else:
                game.snake.direction = Direction.UP
        elif action == 2:  # Turn right
            if current_direction == Direction.UP:
                game.snake.direction = Direction.RIGHT
            elif current_direction == Direction.RIGHT:
                game.snake.direction = Direction.DOWN
            elif current_direction == Direction.DOWN:
                game.snake.direction = Direction.LEFT
            else:
                game.snake.direction = Direction.UP

    #Train the AI
    def train(self, num_games=5000):
        
        print("\nStarting training...\n")
        self.logger.log_training_start(num_games)
        
        for game_num in range(num_games):
            game = Game(visible=False)
            score = 0
            steps_without_fruit = 0
            moves_made = 0
            
            while not game.game_over:
                # Get current state
                old_state = self.get_state(game)
                old_score = game.score
                
                # Choose and perform an action
                action = self.get_action(old_state)
                self.apply_action(game, action)
                game.update()
                moves_made += 1
                
                # Get new state
                new_state = self.get_state(game)
                new_score = game.score
                
                # Calculate reward
                reward = 0
                if game.game_over:
                    reward = -10
                elif new_score > old_score:
                    reward = 10
                    steps_without_fruit = 0
                else:
                    steps_without_fruit += 1
                    if steps_without_fruit > 100:
                        game.game_over = True
                        reward = -10
                
                # Update Q-table
                if old_state not in self.q_table:
                    self.q_table[old_state] = [0, 0, 0]
                if new_state not in self.q_table:
                    self.q_table[new_state] = [0, 0, 0]
                    
                #### UPDATE Q_TABLE with Bellman Formula
                old_q = self.q_table[old_state][action]
                next_max = np.max(self.q_table[new_state])
                new_q = old_q + self.learning_rate * (reward + self.discount_factor * next_max - old_q)
                self.q_table[old_state][action] = new_q
            
            # Log game results
            self.logger.log_game_result(game_num + 1, game.score, len(self.q_table), self.epsilon)
            
            # Decay epsilon
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay

        # Log end of training and create plots
        self.logger.log_training_end()
        self.logger.plot_training_progress()
        
        # Save the trained AI
        with open('snake_ai.pkl', 'wb') as f:
            pickle.dump(self.q_table, f)

    #Let the trained AI play a game
    def play(self, speed=0.1):
        
        game = Game(visible=True)
        print("\nStarting game demonstration...")
        print("Press ESC to quit the demonstration")
        
        running = True
        moves_made = 0
        
        while not game.game_over and running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    print("\nDemonstration stopped by user")
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        print("\nDemonstration stopped by user (ESC)")
                        break
            
            if not running:
                break
                
            state = self.get_state(game)
            action = self.get_action(state)
            self.apply_action(game, action)
            game.update()
            game.draw()
            moves_made += 1
            sleep(speed)
            
        if game.game_over and running:
            self.logger.log_play_game(game.score, moves_made)
            # Keep the window open a bit after game over
            timeout = time.time() + 2  # 2 seconds timeout
            while time.time() < timeout:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        break
                pygame.display.flip()
        
        pygame.quit()

def main():
    try:
        ai = SnakeAI()
        
        # Training phase
        print("Training new AI...")
        ai.train(num_games=200)
        
        # Playing phase
        print("\nWatching trained AI play...")
        ai.play()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()