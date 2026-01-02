import random
from enum import Enum
from typing import List, Tuple

Position = Tuple[int, int]

GRID_ROWS = 20
GRID_COLUMNS = 20

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class ObjectType(Enum):
    EMPTY = 0
    APPLE = 1
    BOMB = 2
    SNAKE = 3


class SnakeGame:

    def __init__(self, width: int = None, height: int = None, bomb_spawn_probability: float = 0.08, max_bombs: int = 20):
        self.width = width if width is not None else GRID_COLUMNS
        self.height = height if height is not None else GRID_ROWS
        self.bomb_spawn_probability = bomb_spawn_probability
        self.max_bombs = max_bombs
        self.reset()

    def reset(self):
        mid_x = self.width // 2
        mid_y = self.height // 2
        
        self.snake: List[Position] = [
            (mid_x, mid_y),
            (mid_x - 1, mid_y),
            (mid_x - 2, mid_y)
        ]
        
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.score = 0
        self.game_over = False
        self.game_over_reason = None
        self.apple = None
        self.bombs: List[Position] = []
        
        self._place_apple()

    def _get_empty_cells(self) -> List[Position]:
        occupied = set(self.snake)
        if self.apple:
            occupied.add(self.apple)
        occupied.update(self.bombs)
        
        return [(x, y) for x in range(self.width) for y in range(self.height) if (x, y) not in occupied]

    def _place_apple(self):
        empty = self._get_empty_cells()
        if empty:
            self.apple = random.choice(empty)
        else:
            self.apple = None

    
    def _try_spawn_bomb(self):
        if len(self.bombs) < self.max_bombs and random.random() < self.bomb_spawn_probability:
            empty = self._get_empty_cells()
            if empty:
                self.bombs.append(random.choice(empty))

    def set_direction(self, new_dir: Tuple[int, int]):
        if (new_dir[0] == -self.direction[0] and new_dir[1] == -self.direction[1]):
            return
        self.next_direction = new_dir

    def update(self):
        """Oyun durumunu bir adım güncelle."""
        if self.game_over:
            return

        # Buffered yön girdisini uygula
        self.direction = self.next_direction

        # Yeni baş pozisyonunu hesapla
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        if not (0 <= new_head[0] < self.width and 0 <= new_head[1] < self.height):
            self.game_over = True
            self.game_over_reason = "Hit the wall!"
            return

        if new_head in self.snake:
            self.game_over = True
            self.game_over_reason = "Hit yourself!"
            return

        if new_head in self.bombs:
            self.game_over = True
            self.game_over_reason = "Hit the bomb!"
            return

        self.snake.insert(0, new_head)

        if self.apple and new_head == self.apple:
            self.score += 1
            self._place_apple()
        else:
            self.snake.pop()
        
        self._try_spawn_bomb()

    def get_state(self) -> dict:
        return {
            "snake": list(self.snake),
            "apple": self.apple,
            "bombs": list(self.bombs),
            "score": self.score,
            "game_over": self.game_over,
            "game_over_reason": self.game_over_reason,
            "width": self.width,
            "height": self.height,
        }

    def is_game_over(self) -> bool:
        return self.game_over

    def get_score(self) -> int:
        return self.score
