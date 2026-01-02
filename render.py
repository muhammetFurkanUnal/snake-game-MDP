import pygame
from game import SnakeGame, GRID_ROWS, GRID_COLUMNS

CELL_SIZE = 15
WINDOW_WIDTH = GRID_COLUMNS * CELL_SIZE
WINDOW_HEIGHT = GRID_ROWS * CELL_SIZE

COLOR_BACKGROUND = (0, 0, 0)
COLOR_SNAKE_HEAD = (0, 255, 0)
COLOR_SNAKE_BODY = (0, 150, 0)
COLOR_APPLE = (255, 0, 0)
COLOR_BOMB = (255, 255, 0)
COLOR_GRID = (30, 30, 30)
COLOR_TEXT = (200, 200, 200)
COLOR_ERROR = (255, 100, 100)


def draw_game(screen: pygame.Surface, game: SnakeGame):
    state = game.get_state()
    
    screen.fill(COLOR_BACKGROUND)
    
    if state["apple"]:
        ax, ay = state["apple"]
        pygame.draw.rect(screen, COLOR_APPLE, (ax * CELL_SIZE, ay * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    
    for bx, by in state["bombs"]:
        pygame.draw.rect(screen, COLOR_BOMB, (bx * CELL_SIZE, by * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    
    for i, (sx, sy) in enumerate(state["snake"]):
        color = COLOR_SNAKE_HEAD if i == 0 else COLOR_SNAKE_BODY
        pygame.draw.rect(screen, color, (sx * CELL_SIZE, sy * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    
    for gx in range(state["width"] + 1):
        pygame.draw.line(screen, COLOR_GRID, (gx * CELL_SIZE, 0), (gx * CELL_SIZE, WINDOW_HEIGHT), 1)
    for gy in range(state["height"] + 1):
        pygame.draw.line(screen, COLOR_GRID, (0, gy * CELL_SIZE), (WINDOW_WIDTH, gy * CELL_SIZE), 1)
    
    font = pygame.font.SysFont("arial", 20, bold=True)
    score_text = font.render(f"Score: {game.get_score()}", True, COLOR_TEXT)
    screen.blit(score_text, (10, 10))
    
    if game.is_game_over():
        font_large = pygame.font.SysFont("arial", 32, bold=True)
        reason = state["game_over_reason"] or "Game Over"
        reason_text = font_large.render(reason, True, COLOR_ERROR)
        restart_text = font.render("Press R to restart or Q to quit", True, COLOR_TEXT)
        
        screen.blit(reason_text, (WINDOW_WIDTH // 2 - reason_text.get_width() // 2, WINDOW_HEIGHT // 2 - 40))
        screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, WINDOW_HEIGHT // 2 + 20))
    
    pygame.display.flip()
