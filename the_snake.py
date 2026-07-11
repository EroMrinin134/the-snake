import random as rnd
import sys

import pygame as pg

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
HALF_GRID_SIZE = GRID_SIZE // 2
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

CENTER_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
SQUARES_COUNT = GRID_WIDTH * GRID_HEIGHT
SAFE_SNAKE_LENGTH = 4

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
SNAKE_PATTERN_COLOR = (255, 255, 255)

APPLE_COUNT = 3
SPEED = 20

PATTERN_OFFSETS = {
    UP: [
        (HALF_GRID_SIZE, HALF_GRID_SIZE),
        (0, 0),
        (GRID_SIZE - 1, 0),
    ],
    DOWN: [
        (HALF_GRID_SIZE, HALF_GRID_SIZE),
        (0, GRID_SIZE - 1),
        (GRID_SIZE - 1, GRID_SIZE - 1),
    ],
    LEFT: [
        (HALF_GRID_SIZE, HALF_GRID_SIZE),
        (0, 0),
        (0, GRID_SIZE - 1),
    ],
    RIGHT: [
        (HALF_GRID_SIZE, HALF_GRID_SIZE),
        (GRID_SIZE - 1, 0),
        (GRID_SIZE - 1, GRID_SIZE - 1),
    ],
}

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock = pg.time.Clock()


class GameObject:
    """Общий класс игрового объекта."""

    def __init__(self, position=CENTER_POSITION, body_color=BORDER_COLOR):
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Переопределяемый метод для отрисовки игрового объекта."""
        class_name = type(self).__name__
        message = f'Класс {class_name} должен переопределять метод draw().'
        raise NotImplementedError(message)


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self, position=CENTER_POSITION, body_color=APPLE_COLOR):
        super().__init__(position, body_color)

    def randomize_position(self):
        """
        Устанавливает случайную позицию для яблока.

        Яблоко может оказаться внутри другого яблока или змейки.
        """
        self.position = (
            rnd.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            rnd.randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
        )

    def draw(self):
        """Отрисовывает яблоко."""
        rect = pg.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self, position=CENTER_POSITION, body_color=SNAKE_COLOR,
                 pattern_color=SNAKE_PATTERN_COLOR):
        super().__init__(position, body_color)
        self.pattern_color = pattern_color
        self.reset()

    def move(self):
        """Перемещение змейки согласно направлению."""
        x, y = self.get_head_position()
        x = (x + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH
        y = (y + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT

        self.positions.insert(0, (x, y))
        self.last = self.positions.pop()

    def reset(self):
        """Откатывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.last = None
        self.pattern_points = [None for _ in range(3)]

    def draw(self):
        """
        Отрисовывает змейку.

        Погалается на факт, что экран полностью не перерисовывается.
        """
        head = self.get_head_position()
        head_rect = pg.Rect(head, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, head_rect)
        for index, offsets in enumerate(PATTERN_OFFSETS[self.direction]):
            self.pattern_points[index] = (
                head[0] + offsets[0],
                head[1] + offsets[1]
            )
        pg.draw.polygon(screen, self.pattern_color, self.pattern_points)
        pg.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        if self.last is not None and self.last != head:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """Выдаёт позицию головы."""
        return self.positions[0]

    def update_direction(self, direction):
        """Обновляет направление змейки."""
        self.direction = direction


def handle_keys(snake):
    """Обрабатывает нажатия кнопок и возвращает флаг, закрыто ли окно."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            return True
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and snake.direction != DOWN:
                snake.update_direction(UP)
            elif event.key == pg.K_DOWN and snake.direction != UP:
                snake.update_direction(DOWN)
            elif event.key == pg.K_LEFT and snake.direction != RIGHT:
                snake.update_direction(LEFT)
            elif event.key == pg.K_RIGHT and snake.direction != LEFT:
                snake.update_direction(RIGHT)
    return False


def eat_apple(snake, apples):
    """
    Процедура поедания яблока, если змейка его достигла.

    После поядения яблоко перемещается на новое место.
    """
    head = snake.get_head_position()
    for apple in apples:
        if head == apple.position:
            snake.positions.append(snake.last)
            snake.length += 1
            snake.last = None

            relocate_apple(apple, apples, snake)

            break


def is_snake_collides(snake):
    """Проверка, касается ли голова змейки её тела."""
    if snake.length <= SAFE_SNAKE_LENGTH:
        return False
    return snake.get_head_position() in snake.positions[SAFE_SNAKE_LENGTH:]


def is_apple_collides(apple, apples, snake):
    """Проверка, не находтся ли яблоко в друго яблоке или змейки."""
    for current_apple in apples:
        if apple is current_apple:
            continue
        if apple.position == current_apple.position:
            return True
    return apple.position in snake.positions


def relocate_apple(apple, apples, snake):
    """
    Перемещает яблоко на случайное свободное место.
    Если места для яблока нет, то оно удаляется из игры.
    """
    if len(snake.positions) + len(apples) > SQUARES_COUNT:
        apples.remove(apple)
        return

    apple.randomize_position()

    x_shift = rnd.choice((-1, 1)) * GRID_SIZE
    y_shift = rnd.choice((-1, 1)) * GRID_SIZE

    while is_apple_collides(apple, apples, snake):
        x, y = apple.position

        x += x_shift

        if x < 0:
            x = SCREEN_WIDTH - GRID_SIZE
            y += y_shift
        elif x >= SCREEN_WIDTH:
            x = 0
            y += y_shift

        if y < 0:
            y = SCREEN_HEIGHT - GRID_SIZE
        elif y >= SCREEN_HEIGHT:
            y = 0

        apple.position = (x, y)

    apple.draw()


def reset(apples, snake):
    """Установка начального состояния игры."""
    screen.fill(BOARD_BACKGROUND_COLOR)

    snake.reset()

    for _ in range(APPLE_COUNT - len(apples)):
        apples.append(Apple())

    for apple in apples:
        relocate_apple(apple, apples, snake)


def main():
    """Запускает основной цикл игры."""
    pg.init()

    apples = [Apple() for _ in range(APPLE_COUNT)]
    snake = Snake()

    for apple in apples:
        relocate_apple(apple, apples, snake)

    for apple in apples:
        apple.draw()
    snake.draw()

    pg.display.update()

    while True:
        clock.tick(SPEED)

        is_quit_asked = handle_keys(snake)
        if is_quit_asked:
            break

        snake.move()

        eat_apple(snake, apples)

        if is_snake_collides(snake):
            sys.stdout.write(f'Игра окончена. Ваш счёт: {snake.length - 1}.\n')
            reset(apples, snake)

        if len(apples) == 0:
            sys.stdout.write('Вы победили!\n')
            reset(apples, snake)

        snake.draw()

        pg.display.update()

    pg.quit()


if __name__ == '__main__':
    main()
