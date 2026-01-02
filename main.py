import sys
import pygame
from game import SnakeGame, UP, DOWN, LEFT, RIGHT, GRID_ROWS, GRID_COLUMNS
from render import draw_game, WINDOW_WIDTH, WINDOW_HEIGHT

FPS = 10


def main():
    pygame.init()
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    clock = pygame.time.Clock()
    game = SnakeGame(bomb_spawn_probability=0.9)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    game.set_direction(UP)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    game.set_direction(DOWN)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    game.set_direction(LEFT)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    game.set_direction(RIGHT)
                elif event.key == pygame.K_r:
                    game.reset()
                elif event.key == pygame.K_q:
                    running = False
        
        game.update()
        draw_game(screen, game)
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
