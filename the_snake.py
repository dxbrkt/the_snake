"""Игра «Изгиб Питона» — классическая змейка на Pygame."""

from __future__ import annotations
from random import choice
from typing import ClassVar, Dict, Optional, Tuple

import pygame


SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

START_LENGTH = 1
START_DIRECTION = RIGHT
FPS = 20
WINDOW_TITLE = 'Изгиб Питона'
CENTER_POSITION = (GRID_WIDTH // 2, GRID_HEIGHT // 2)

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
        body_color: Tuple[int, int, int] = BLACK,
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
        super().__init__(body_color=RED)
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

    DIRECTION_MAP: ClassVar[
        Dict[Tuple[int, int, int], Tuple[int, int]]
    ] = {
        (pygame.K_UP, *UP): UP,
        (pygame.K_UP, *DOWN): DOWN,
        (pygame.K_UP, *LEFT): UP,
        (pygame.K_UP, *RIGHT): UP,
        (pygame.K_DOWN, *UP): UP,
        (pygame.K_DOWN, *DOWN): DOWN,
        (pygame.K_DOWN, *LEFT): DOWN,
        (pygame.K_DOWN, *RIGHT): DOWN,
        (pygame.K_LEFT, *UP): LEFT,
        (pygame.K_LEFT, *DOWN): LEFT,
        (pygame.K_LEFT, *LEFT): LEFT,
        (pygame.K_LEFT, *RIGHT): RIGHT,
        (pygame.K_RIGHT, *UP): RIGHT,
        (pygame.K_RIGHT, *DOWN): RIGHT,
        (pygame.K_RIGHT, *LEFT): LEFT,
        (pygame.K_RIGHT, *RIGHT): RIGHT,
    }

    def __init__(self) -> None:
        """Инициализировать змейку."""
        super().__init__(position=CENTER_POSITION, body_color=GREEN)
        self.length = START_LENGTH
        self.positions = [self.position]
        self.direction = START_DIRECTION
        self.next_direction: Optional[Tuple[int, int]] = None
        self.record_length = START_LENGTH

    def _set_initial_state(self, head_position: Tuple[int, int]) -> None:
        """Установить начальное состояние змейки.

        Args:
            head_position: Позиция головы змейки.
        """
        self.position = head_position
        self.length = START_LENGTH
        self.positions = [head_position]
        self.direction = START_DIRECTION
        self.next_direction = None

    def set_next_direction(self, key: int) -> None:
        """Сохранить следующее направление движения по нажатой клавише.

        Args:
            key: Код клавиши Pygame.
        """
        self.next_direction = self.DIRECTION_MAP.get(
            (key, *self.direction),
            self.direction,
        )

    def update_direction(self) -> None:
        """Обновить направление движения змейки."""
        if self.next_direction is not None:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> Optional[Tuple[int, int]]:
        """Переместить змейку на одну клетку.

        Returns:
            Координаты стёртой клетки хвоста, если хвост был сдвинут.
            Иначе возвращает None.
        """
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

        tail = None
        if len(self.positions) > self.length:
            tail = self.positions.pop()

        return tail

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

    def get_positions_set(self) -> set[Tuple[int, int]]:
        """Вернуть множество клеток, занятых змейкой.

        Returns:
            Множество координат сегментов змейки.
        """
        return set(self.positions)

    def grow(self) -> None:
        """Увеличить длину змейки на один сегмент."""
        self.length += 1
        self.record_length = max(self.record_length, self.length)

    def has_self_collision(self) -> bool:
        """Проверить, столкнулась ли змейка сама с собой.

        Returns:
            True, если произошло столкновение, иначе False.
        """
        if self.length <= 2:
            return False
        return self.get_head_position() in self.positions[1:]

    def reset(self) -> None:
        """Сбросить змейку после самоукуса, оставив только голову."""
        self._set_initial_state(self.get_head_position())


def update_caption(snake: Snake) -> None:
    """Обновить заголовок окна.

    Args:
        snake: Экземпляр змейки.
    """
    title = (
        f'{WINDOW_TITLE} | Длина: {snake.length} | '
        f'Рекорд: {snake.record_length}'
    )
    pygame.display.set_caption(title)


def handle_keys(snake: Snake) -> None:
    """Обработать события клавиатуры и закрытие окна.

    Args:
        snake: Экземпляр змейки.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
            snake.set_next_direction(event.key)


def draw(
    surface: pygame.Surface,
    snake: Snake,
    apple: Apple,
) -> None:
    """Отрисовать кадр игры.

    Args:
        surface: Игровая поверхность.
        snake: Экземпляр змейки.
        apple: Экземпляр яблока.
    """
    surface.fill(BLACK)
    apple.draw(surface)
    snake.draw(surface)


def main() -> None:
    """Запустить игру."""
    pygame.init()

    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()

    snake = Snake()
    apple = Apple(occupied_positions=snake.get_positions_set())
    update_caption(snake)

    while True:
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.grow()
            apple.randomize_position(
                occupied_positions=snake.get_positions_set()
            )
            update_caption(snake)

        if snake.has_self_collision():
            snake.reset()
            apple.randomize_position(
                occupied_positions=snake.get_positions_set()
            )
            update_caption(snake)

        draw(screen, snake, apple)
        pygame.display.update()
        clock.tick(FPS)


if __name__ == '__main__':
    main()