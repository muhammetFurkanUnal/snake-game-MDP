import pygame
import random
import pickle
import os
import numpy as np
from collections import defaultdict
from game import SnakeGame, UP, DOWN, LEFT, RIGHT, GRID_ROWS, GRID_COLUMNS
from render import draw_game, WINDOW_WIDTH, WINDOW_HEIGHT

FPS = 30
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.99
EPSILON_START = 1.0
EPSILON_DECAY = 0.995
EPSILON_MIN = 0.01
Q_TABLE_FILE = "combined_Q_table.pkl"


def get_state(game: SnakeGame):
    head = game.snake[0]
    
    point_l = (head[0] - 1, head[1])
    point_r = (head[0] + 1, head[1])
    point_u = (head[0], head[1] - 1)
    point_d = (head[0], head[1] + 1)

    dir_l = game.direction == LEFT
    dir_r = game.direction == RIGHT
    dir_u = game.direction == UP
    dir_d = game.direction == DOWN

    def is_danger(point):
        x, y = point
        if not (0 <= x < game.width and 0 <= y < game.height):
            return True
        if point in game.snake:
            return True
        if point in game.bombs:
            return True
        return False
    # --------------------------

    state = [
        (dir_r and is_danger(point_r)) or 
        (dir_l and is_danger(point_l)) or 
        (dir_u and is_danger(point_u)) or 
        (dir_d and is_danger(point_d)),

        (dir_u and is_danger(point_r)) or 
        (dir_d and is_danger(point_l)) or 
        (dir_l and is_danger(point_u)) or 
        (dir_r and is_danger(point_d)),

        (dir_d and is_danger(point_r)) or 
        (dir_u and is_danger(point_l)) or 
        (dir_r and is_danger(point_u)) or 
        (dir_l and is_danger(point_d)),

        dir_l,
        dir_r,
        dir_u,
        dir_d,

        (game.apple[0] < head[0]) if game.apple else False, 
        (game.apple[0] > head[0]) if game.apple else False,
        (game.apple[1] < head[1]) if game.apple else False,  
        (game.apple[1] > head[1]) if game.apple else False  
    ]

    return tuple(map(int, state))


def load_q_table():
    """Load Q-table from file if it exists."""
    if os.path.exists(Q_TABLE_FILE):
        try:
            with open(Q_TABLE_FILE, 'rb') as f:
                return pickle.load(f)
        except (EOFError, pickle.UnpicklingError):
            os.remove(Q_TABLE_FILE)
    return {}


def save_q_table(q_table):
    """Save Q-table to file."""
    with open(Q_TABLE_FILE, 'wb') as f:
        pickle.dump(q_table, f)


def get_action(state, q_table, epsilon):
    """Epsilon-greedy action selection."""
    if random.random() < epsilon:
        return random.randint(0, 3)
    else:
        q_values = q_table.get(state, [0.0, 0.0, 0.0, 0.0])
        return q_values.index(max(q_values))


def action_to_direction(action):
    """Convert action index to direction."""
    actions = [UP, DOWN, LEFT, RIGHT]
    return actions[action]


def train_q_learning(num_episodes: int = 100, show_render: bool = False):
    """Train Q-learning agent."""
    pygame.init()
    
    if show_render:
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        clock = pygame.time.Clock()
    
    q_table = load_q_table()
    epsilon = EPSILON_START
    total_rewards = []
    
    for episode in range(num_episodes):
        game = SnakeGame()
        state = get_state(game)
        episode_reward = 0
        
        while not game.is_game_over():
            if show_render:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
            
            action = get_action(state, q_table, epsilon)
            direction = action_to_direction(action)
            
            old_score = game.get_score()
            game.set_direction(direction)
            game.update()
            new_score = game.get_score()
            
            reward = 0
            if new_score > old_score:
                reward = 10
            elif game.is_game_over():
                reward = -10
            else:
                reward = -0.1
            
            next_state = get_state(game)
            
            old_q = q_table.get(state, [0.0, 0.0, 0.0, 0.0])[action]
            next_q_max = max(q_table.get(next_state, [0.0, 0.0, 0.0, 0.0]))
            new_q = old_q + LEARNING_RATE * (reward + DISCOUNT_FACTOR * next_q_max - old_q)
            
            if state not in q_table:
                q_table[state] = [0.0, 0.0, 0.0, 0.0]
            q_table[state][action] = new_q
            
            episode_reward += reward
            state = next_state
            
            if show_render:
                draw_game(screen, game)
                clock.tick(FPS)
        
        total_rewards.append(episode_reward)
        epsilon = max(EPSILON_MIN, epsilon * EPSILON_DECAY)
        
        if (episode + 1) % 10 == 0:
            avg_reward = sum(total_rewards[-10:]) / 10
            
    
    if show_render:
        pygame.quit()
    
    save_q_table(q_table)
    return q_table


def play_q_learning(num_games: int = 1, show_render: bool = True):
    """Play the snake game using trained Q-learning agent."""
    pygame.init()
    
    q_table = load_q_table()
    
    if show_render:
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game - Q-Learning Agent")
        clock = pygame.time.Clock()
    
    games_played = 0
    total_score = 0
    
    while games_played < num_games:
        game = SnakeGame()
        state = get_state(game)
        
        while not game.is_game_over():
            if show_render:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
            
            q_values = q_table.get(state, [0.0, 0.0, 0.0, 0.0])
            action = q_values.index(max(q_values))
            direction = action_to_direction(action)
            
            game.set_direction(direction)
            game.update()
            state = get_state(game)
            
            if show_render:
                draw_game(screen, game)
                clock.tick(FPS)
        
        score = game.get_score()
        total_score += score
        games_played += 1
        
        
        if show_render:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            draw_game(screen, game)
            pygame.time.wait(1000)
    
    if show_render:
        pygame.quit()
    
    avg_score = total_score / num_games if num_games > 0 else 0


if __name__ == "__main__":
    train_q_learning(num_episodes=300, show_render=False)
    play_q_learning(num_games=3, show_render=True)
