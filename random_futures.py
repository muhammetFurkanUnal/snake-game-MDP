import random
import copy
import pygame
from game import SnakeGame, UP, DOWN, LEFT, RIGHT, GRID_ROWS, GRID_COLUMNS
from render import draw_game, WINDOW_WIDTH, WINDOW_HEIGHT

FPS = 20

def manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def simulate_future(game: SnakeGame, direction: tuple, steps: int) -> dict:
    game_copy = copy.deepcopy(game)
    game_copy.set_direction(direction)
    game_copy.update()
    
    if game_copy.is_game_over():
        return {
            'survived': False,
            'final_distance_to_apple': float('inf'),
            'score_gained': 0
        }
    
    for _ in range(steps - 1):
        if game_copy.is_game_over():
            break
        
        random_dir = random.choice([UP, DOWN, LEFT, RIGHT])
        game_copy.set_direction(random_dir)
        game_copy.update()
    
    state = game_copy.get_state()
    apple = state["apple"]
    
    distance_to_apple = float('inf')
    if apple:
        head = state["snake"][0]
        distance_to_apple = manhattan_distance(head, apple)
    
    return {
        'survived': not game_copy.is_game_over(),
        'final_distance_to_apple': distance_to_apple,
        'score_gained': game_copy.get_score() - game.get_score()
    }

def get_best_direction(game: SnakeGame, num_futures: int = 5, lookahead_steps: int = 10) -> tuple:
    directions = [UP, DOWN, LEFT, RIGHT]
    current_direction = game.direction
    
    results = {}
    
    for direction in directions:
        if direction[0] == -current_direction[0] and direction[1] == -current_direction[1]:
            continue
        
        survived_count = 0
        total_distance = 0
        valid_distance_count = 0
        total_score = 0
        
        for _ in range(num_futures):
            future = simulate_future(game, direction, lookahead_steps)
            
            if future['survived']:
                survived_count += 1
                total_distance += future['final_distance_to_apple']
                valid_distance_count += 1
            
            total_score += future['score_gained']
        
        if valid_distance_count > 0:
            avg_distance = total_distance / valid_distance_count
        else:
            avg_distance = float('inf')
            
        avg_score = total_score / num_futures
        
        results[direction] = {
            'survived_count': survived_count,
            'avg_distance': avg_distance,
            'avg_score': avg_score
        }
    
    if not results:
        return current_direction
    
    best_direction = max(results.keys(), key=lambda d: (
        results[d]['avg_score'] * 5000 + 
        results[d]['survived_count'] * 200 - 
        results[d]['avg_distance']
    ))
    
    return best_direction

def play_futures_bot(num_games: int = 1, num_futures: int = 5, lookahead_steps: int = 10, show_render: bool = True):
    pygame.init()
    
    if show_render:
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        clock = pygame.time.Clock()
    
    games_played = 0
    total_score = 0
    
    while games_played < num_games:
        game = SnakeGame()
        
        while not game.is_game_over():
            if show_render:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
            
            best_direction = get_best_direction(game, num_futures=num_futures, lookahead_steps=lookahead_steps)
            game.set_direction(best_direction)
            game.update()
            
            if show_render:
                draw_game(screen, game)
                clock.tick(FPS)
        
        score = game.get_score()
        total_score += score
        games_played += 1
        
        if show_render:
            pygame.time.wait(500)
    
    if show_render:
        pygame.quit()

if __name__ == "__main__":
    play_futures_bot(num_games=3, num_futures=10, lookahead_steps=6, show_render=True)