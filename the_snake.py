"""Игра «Изгиб Питона» — классическая змейка на Pygame."""

from __future__ import annotations

from random import choice
from typing import Optional, Tuple
import pygame
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

BOARD_BACKGROUND_COLOR = (0, 0, 0)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

START_LENGTH = 1
START_DIRECTION = RIGHT
SPEED = 20
WINDOW_TITLE = 'Изгиб Питона'
CENTER_POSITION = (GRID_WIDTH // 2, GRID_HEIGHT // 2)

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()
pygame.display.set_caption(WINDOW_TITLE)

ALL_CELLS = {
    (x, y)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
}


class GameObject:
    """Базовый класс игровых объектов."""

    def __init__(
        self,
        position: Tuple[int, int] = CENTER_POSITION,
        body_color: Tuple[int, int, int] = BOARD_BACKGROUND_COLOR,
    ) -> None:
        """Инициализировать игровой объект.

        Args:
            position: Позиция объекта на игровом поле.
            body_color: Цвет объекта в формате RGB.
        """
        self.position = position
        self.body_color = body_color

    @staticmethod
    def _get_cell_rect(position: Tuple[int, int]) -> pygame.Rect:
        """Преобразовать координаты клетки в прямоугольник Pygame.

        Args:
            position: Координаты клетки на игровом поле.

        Returns:
            Прямоугольник для отрисовки клетки.
        """
        return pygame.Rect(
            position[0] * GRID_SIZE,
            position[1] * GRID_SIZE,
            GRID_SIZE,
            GRID_SIZE,
        )

    def draw_cell(
        self,
        surface: pygame.Surface,
        position: Tuple[int, int],
        color: Tuple[int, int, int],
    ) -> None:
        """Отрисовать одну клетку игрового поля.

        Args:
            surface: Поверхность Pygame для рисования.
            position: Координаты клетки.
            color: Цвет клетки.
        """
        pygame.draw.rect(surface, color, self._get_cell_rect(position))

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовать объект на поверхности.

        Args:
            surface: Поверхность Pygame для рисования.
        """
        pass


class Apple(GameObject):
    """Класс яблока."""

    def __init__(
        self,
        occupied_positions: Optional[set[Tuple[int, int]]] = None,
    ) -> None:
        """Создать яблоко в случайной свободной клетке.

        Args:
            occupied_positions: Клетки, занятые змейкой.
        """
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position(occupied_positions)

    def randomize_position(
        self,
        occupied_positions: Optional[set[Tuple[int, int]]] = None,
    ) -> None:
        """Установить яблоко в случайную свободную клетку.

        Args:
            occupied_positions: Клетки, занятые змейкой.
        """
        occupied = occupied_positions or set()
        free_cells = tuple(ALL_CELLS - occupied)
        self.position = choice(free_cells) if free_cells else CENTER_POSITION

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовать яблоко.

        Args:
            surface: Поверхность Pygame для рисования.
        """
        self.draw_cell(surface, self.position, self.body_color)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self) -> None:
        """Инициализировать змейку."""
        super().__init__(position=CENTER_POSITION, body_color=SNAKE_COLOR)
        self.length = START_LENGTH
        self.positions = [self.position]
        self.direction = START_DIRECTION
        self.next_direction: Optional[Tuple[int, int]] = None

    def update_direction(self) -> None:
        """Обновить направление движения змейки."""
        if self.next_direction is not None:
            opposite_direction = (
                -self.direction[0],
                -self.direction[1],
            )
            if self.next_direction != opposite_direction:
                self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Переместить змейку на одну клетку."""
        new_head = tuple(
            (position + delta) % size
            for position, delta, size in zip(
                self.get_head_position(),
                self.direction,
                (GRID_WIDTH, GRID_HEIGHT),
            )
        )

        self.positions.insert(0, new_head)
        self.position = new_head

        if len(self.positions) > self.length:
            self.positions.pop()

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовать змейку.

        Args:
            surface: Поверхность Pygame для рисования.
        """
        for segment in self.positions:
            self.draw_cell(surface, segment, self.body_color)

    def get_head_position(self) -> Tuple[int, int]:
        """Вернуть позицию головы змейки.

        Returns:
            Координаты головы змейки.
        """
        return self.positions[0]

    def reset(self) -> None:
        """Сбросить змейку после самоукуса, оставив только голову."""
        head = self.get_head_position()
        self.position = head
        self.length = START_LENGTH
        self.positions = [head]
        self.direction = START_DIRECTION
        self.next_direction = None


def handle_keys(game_object: Snake) -> None:
    """Обработать события клавиатуры и закрытие окна.

    Args:
        game_object: Экземпляр змейки.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
            if event.key == pygame.K_UP:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT:
                game_object.next_direction = RIGHT


def draw(surface: pygame.Surface, snake: Snake, apple: Apple) -> None:
    """Отрисовать кадр игры.

    Args:
        surface: Игровая поверхность.
        snake: Экземпляр змейки.
        apple: Экземпляр яблока.
    """
    surface.fill(BOARD_BACKGROUND_COLOR)
    apple.draw(surface)
    snake.draw(surface)


def main() -> None:
    """Запустить игру."""
    snake = Snake()
    apple = Apple(occupied_positions=set(snake.positions))

    while True:
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(occupied_positions=set(snake.positions))

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(occupied_positions=set(snake.positions))

        draw(screen, snake, apple)
        pygame.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()