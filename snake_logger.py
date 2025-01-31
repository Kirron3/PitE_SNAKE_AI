import logging
import json
import time
from datetime import datetime
import os
from typing import Dict, List, Any

class SnakeLogger:
    def __init__(self, log_dir: str = "logs"):
        # Create logs directory if it doesn't exist
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

        # Create log files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.training_file = f"{log_dir}/training_{timestamp}.log"
        self.stats_file = f"{log_dir}/stats_{timestamp}.json"

        # Initialize training statistics
        self.training_stats = {
            "start_time": time.time(),
            "total_games": 0,
            "best_score": 0,
            "scores_history": [],
            "average_scores": [],
            "q_table_sizes": []
        }

        # Setup logging configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.training_file),
                logging.StreamHandler()  # Also print to console
            ]
        )
        self.logger = logging.getLogger("SnakeAI")

    def log_training_start(self, num_games: int):
        """Log the start of a training session"""
        msg = f"Starting new training session with {num_games} games"
        self.logger.info(msg)
        self.training_stats["total_games"] = num_games

    def log_game_result(self, game_number: int, score: int, q_table_size: int, epsilon: float):
        """Log the result of a single game"""
        self.training_stats["scores_history"].append(score)
        self.training_stats["q_table_sizes"].append(q_table_size)
        
        if score > self.training_stats["best_score"]:
            self.training_stats["best_score"] = score
            self.logger.info(f"New best score achieved: {score} (Game {game_number})")

        # Calculate and store average score every 10 games
        if game_number % 10 == 0:
            recent_scores = self.training_stats["scores_history"][-10:]
            avg_score = sum(recent_scores) / len(recent_scores)
            self.training_stats["average_scores"].append(avg_score)
            
            self.logger.info(
                f"Game {game_number} completed:\n"
                f"  Score: {score}\n"
                f"  Recent Average: {avg_score:.2f}\n"
                f"  Q-table size: {q_table_size}\n"
                f"  Epsilon: {epsilon:.3f}"
            )

    def log_training_end(self):
        """Log the end of training and save final statistics"""
        duration = time.time() - self.training_stats["start_time"]
        final_avg = sum(self.training_stats["scores_history"]) / len(self.training_stats["scores_history"])
        
        summary = (
            f"\nTraining Summary:\n"
            f"Total duration: {duration:.1f} seconds\n"
            f"Games played: {self.training_stats['total_games']}\n"
            f"Best score: {self.training_stats['best_score']}\n"
            f"Average score: {final_avg:.2f}\n"
            f"Final Q-table size: {self.training_stats['q_table_sizes'][-1]}"
        )
        
        self.logger.info(summary)
        
        # Save complete statistics to JSON file
        with open(self.stats_file, 'w') as f:
            json.dump(self.training_stats, f, indent=4)

    def log_play_game(self, score: int, moves: int):
        """Log the result of a played game"""
        self.logger.info(
            f"Game finished:\n"
            f"  Final score: {score}\n"
            f"  Total moves: {moves}"
        )

    def get_training_summary(self) -> Dict[str, Any]:
        """Get a summary of the training statistics"""
        return {
            "best_score": self.training_stats["best_score"],
            "average_score": sum(self.training_stats["scores_history"]) / max(len(self.training_stats["scores_history"]), 1),
            "total_games": len(self.training_stats["scores_history"]),
            "final_q_table_size": self.training_stats["q_table_sizes"][-1] if self.training_stats["q_table_sizes"] else 0
        }

    def plot_training_progress(self):
        """Generate training progress plots (if matplotlib is available)"""
        try:
            import matplotlib
            # Use Agg backend to avoid Tkinter issues
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            
            # Create plots with reduced data points for better performance
            scores = self.training_stats["scores_history"]
            q_table_sizes = self.training_stats["q_table_sizes"]
            
            # Reduce number of points if too many games
            if len(scores) > 1000:
                step = len(scores) // 1000
                scores = scores[::step]
                q_table_sizes = q_table_sizes[::step]
            
            # Create a figure with subplots
            plt.figure(figsize=(10, 8))
            
            # Plot scores
            plt.subplot(2, 1, 1)
            plt.plot(scores, label='Game Scores', alpha=0.3)
            plt.plot(range(0, len(self.training_stats["average_scores"]) * 10, 10),
                    self.training_stats["average_scores"],
                    label='Average (10 games)', linewidth=2)
            plt.title('Training Scores Progress')
            plt.xlabel('Game Number')
            plt.ylabel('Score')
            plt.legend()
            plt.grid(True)
            
            # Plot Q-table size
            plt.subplot(2, 1, 2)
            plt.plot(q_table_sizes, label='Q-table Size')
            plt.title('Q-table Growth')
            plt.xlabel('Game Number')
            plt.ylabel('Number of States')
            plt.legend()
            plt.grid(True)
            
            # Save the plot
            plot_file = os.path.join(self.log_dir, 'training_progress.png')
            plt.tight_layout()
            plt.savefig(plot_file)
            plt.close()
            
            self.logger.info(f"Training progress plot saved to {plot_file}")
            
        except ImportError:
            self.logger.warning("Matplotlib not installed. Unable to generate plots.")
        except Exception as e:
            self.logger.warning(f"Error generating plots: {str(e)}")

def main():
    """Example usage of the logger"""
    logger = SnakeLogger()
    
    # Simulate some training
    logger.log_training_start(num_games=100)
    
    for i in range(100):
        # Simulate a game
        fake_score = i % 10 + 5  # Just for demonstration
        fake_q_table_size = 1000 + i * 10
        fake_epsilon = max(0.01, 1.0 - (i / 100))
        
        logger.log_game_result(i+1, fake_score, fake_q_table_size, fake_epsilon)
    
    logger.log_training_end()
    logger.plot_training_progress()

if __name__ == "__main__":
    main()


    
'''
##### Q table graph analysis #####
A rapid rise at the beginning, a sign that the AI ​​is exploring well.
A gradual slowdown, a sign that the AI ​​is specializing.
A plateau after several games, a sign that the AI ​​has learned everything it needs to.
'''