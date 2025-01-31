import pygame
import random
import sys
from enum import Enum
from typing import List, Tuple, Optional

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

# Snake class representing the snake in the game
class Snake:
    def __init__(self, start_pos: Tuple[int, int], block_size: int):
        self.body = [start_pos]  # Initializing the snake's body with a starting position
        self.direction = Direction.RIGHT  # Default movement direction is right
        self.block_size = block_size  # Size of each snake block
        self.growth_pending = False  # Flag to track if the snake should grow
        self.color = (50, 168, 82)  # Snake body color (green shade)
        self.head_color = (34, 139, 34)  # Snake head color (darker green)

    def move(self) -> None:
        current_head = self.body[0]  # Getting the current head position
        dx, dy = self.direction.value  # Extracting direction offsets
        new_head = (
            current_head[0] + dx * self.block_size,
            current_head[1] + dy * self.block_size
        )  # Calculating new head position based on direction
        self.body.insert(0, new_head)  # Adding new head to the body
        
        if not self.growth_pending:
            self.body.pop()  # Removing last segment if the snake is not growing
        else:
            self.growth_pending = False  # Reset growth flag

    def grow(self) -> None:
        self.growth_pending = True  # Setting growth flag to True

    def check_collision(self, width: int, height: int) -> bool:
        head = self.body[0]  # Getting the head position
        # Checking if the head collides with the game boundaries
        if (head[0] < 0 or head[0] >= width or 
            head[1] < 0 or head[1] >= height):
            return True
        
        # Checking if the head collides with the snake's body
        if head in self.body[1:]:
            return True
            
        return False
    

# Fruit class representing the food item in the game
class Fruit:
    def __init__(self, width: int, height: int, block_size: int):
        self.block_size = block_size  # Size of the fruit block
        self.width = width  # Game area width
        self.height = height  # Game area height
        self.position = (0, 0)  # Initializing position
        self.colors = [
            (255, 0, 0),    # Red
            (255, 165, 0),  # Orange
            (255, 215, 0),  # Gold
            (148, 0, 211)   # Purple
        ]  # List of fruit colors
        self.color = random.choice(self.colors)  # Randomly choosing fruit color
        self.points = 1  # Each fruit is worth 1 point
        self.respawn()  # Setting an initial position for the fruit

    def respawn(self) -> None:
        # Setting boundaries to avoid fruit spawning too close to walls
        min_x = self.block_size * 2
        max_x = self.width - (self.block_size * 2)
        min_y = self.block_size * 2
        max_y = self.height - (self.block_size * 2)
        
        # Generating random fruit position within safe boundaries
        x = random.randrange(min_x, max_x, self.block_size)
        y = random.randrange(min_y, max_y, self.block_size)
        
        self.position = (x, y)  # Updating fruit position
        self.color = random.choice(self.colors)  # Assigning a new random color


# Game class managing game logic and rendering
class Game:
    def __init__(self, width: int = 800, height: int = 600, visible: bool = True):
        pygame.init()  # Initializing pygame
        self.width = width  # Setting game width
        self.height = height  # Setting game height
        self.block_size = 20  # Size of each grid block
        self.visible = visible  # Flag for rendering visibility
        
        if visible:
            self.screen = pygame.display.set_mode((width, height))  # Creating a window
            pygame.display.set_caption("Snake Game")  # Setting game title
        else:
            self.screen = pygame.display.set_mode((width, height), pygame.HIDDEN)  # Invisible mode for training
        
        spawn_pos = (width // 2, height // 2)  # Setting initial snake position
        self.snake = Snake(spawn_pos, self.block_size)  # Creating snake instance
        self.fruit = Fruit(width, height, self.block_size)  # Creating fruit instance
        
        self.score = 0  # Initializing score
        self.game_over = False  # Game state flag
        self.clock = pygame.time.Clock()  # Creating game clock
        self.speed = 10  # Initial game speed

    def handle_input(self) -> bool:
        for event in pygame.event.get():  # Checking user input events
            if event.type == pygame.QUIT:
                return False  # Exit game if quit event is detected
            
            if event.type == pygame.KEYDOWN:  # Checking key press events
                if event.key == pygame.K_UP and self.snake.direction != Direction.DOWN:
                    self.snake.direction = Direction.UP
                elif event.key == pygame.K_DOWN and self.snake.direction != Direction.UP:
                    self.snake.direction = Direction.DOWN
                elif event.key == pygame.K_LEFT and self.snake.direction != Direction.RIGHT:
                    self.snake.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT and self.snake.direction != Direction.LEFT:
                    self.snake.direction = Direction.RIGHT
        return True

    def update(self) -> None:
        if self.game_over:
            return

        self.snake.move()
        
        # Check collisions
        if self.snake.check_collision(self.width, self.height):
            self.game_over = True
            return
            
        # Check fruit collection
        if self.snake.body[0] == self.fruit.position:
            self.snake.grow()
            self.score += self.fruit.points
            self.speed = min(20, 10 + (self.score // 10))  # Progressive speed increase
            self.fruit.respawn()
            
            # Avoid fruit spawning on snake
            while self.fruit.position in self.snake.body:
                self.fruit.respawn()

    def draw(self) -> None:
        if not self.visible:
            return
            
        self.screen.fill((0, 0, 0))  # Black background
        
        # Draw snake
        for i, segment in enumerate(self.snake.body):
            color = self.snake.head_color if i == 0 else self.snake.color
            pygame.draw.rect(self.screen, color, 
                           (segment[0], segment[1], self.block_size, self.block_size))
            
        # Draw fruit
        pygame.draw.rect(self.screen, self.fruit.color,
                        (self.fruit.position[0], self.fruit.position[1],
                         self.block_size, self.block_size))
        
        # Display score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # Display game over
        if self.game_over:
            game_over_text = font.render('Game Over!', True, (255, 0, 0))
            text_rect = game_over_text.get_rect(center=(self.width/2, self.height/2))
            self.screen.blit(game_over_text, text_rect)
            
            restart_text = font.render('Press R to restart', True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(self.width/2, self.height/2 + 40))
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()

    def reset(self) -> None:
        spawn_pos = (self.width // 2, self.height // 2)
        self.snake = Snake(spawn_pos, self.block_size)
        self.fruit.respawn()
        self.score = 0
        self.game_over = False
        self.speed = 10

    def run(self) -> None:
        running = True
        while running:
            running = self.handle_input()
            
            if self.game_over:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_r]:
                    self.reset()
            
            self.update()
            self.draw()
            self.clock.tick(self.speed)

def main():
    game = Game(visible=True)
    game.run()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 