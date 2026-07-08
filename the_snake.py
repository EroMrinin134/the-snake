import random
import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
HALF_GRID_SIZE = GRID_SIZE // 2
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

CENTER_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
SQUARES_COUNT = GRID_WIDTH * GRID_HEIGHT

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

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Общий класс игрового объекта."""

    def __init__(self, position=None, body_color=None):
        self.position = position if position else CENTER_POSITION
        self.body_color = body_color if body_color else BOARD_BACKGROUND_COLOR

    def draw(self):
        """Переопределяемый метод для отрисовки игрового объекта."""
        pass


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self):
        super().__init__(None, APPLE_COLOR)

    def randomize_position(self):
        """
        Устанавливает случайную позицию для яблока.
        Яблоко может оказаться внутри другого яблока или змейки.
        """
        self.position = (
            random.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
        )

    def draw(self):
        """Отрисовывает яблоко."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self):
        super().__init__(None, SNAKE_COLOR)
        self.pattern_color = SNAKE_PATTERN_COLOR
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None
        self.pattern_points = [None for _ in range(3)]

    def move(self):
        """Перемещение змейки согласно направлению."""
        self.position = (
            self.position[0] + self.direction[0] * GRID_SIZE,
            self.position[1] + self.direction[1] * GRID_SIZE
        )

        x, y = self.position

        if x < 0:
            x = SCREEN_WIDTH - GRID_SIZE
        elif x >= SCREEN_WIDTH:
            x = 0

        if y < 0:
            y = SCREEN_HEIGHT - GRID_SIZE
        elif y >= SCREEN_HEIGHT:
            y = 0

        self.position = (x, y)

        self.last = self.positions.pop()

        self.positions = [self.position] + self.positions

    def reset(self):
        """Откатывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def draw(self):
        """
        Отрисовывает змейку.
        Погалается на факт, что экран полностью не перерисовывается.
        """
        head_rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        for index, offsets in enumerate(PATTERN_OFFSETS[self.direction]):
            self.pattern_points[index] = (
                self.position[0] + offsets[0],
                self.position[1] + offsets[1]
            )
        pygame.draw.polygon(screen, self.pattern_color, self.pattern_points)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        if self.last is not None and self.last != self.position:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """Выдаёт позицию головы."""
        return self.position

    def update_direction(self):
        """Обновляет направление змейки."""
        if self.next_direction is not None:
            self.direction = self.next_direction
            self.next_direction = None


def handle_keys(snake):
    """Обрабатывает нажатия кнопок и возвращает флаг, закрыто ли окно."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake.direction != DOWN:
                snake.next_direction = UP
            elif event.key == pygame.K_DOWN and snake.direction != UP:
                snake.next_direction = DOWN
            elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                snake.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                snake.next_direction = RIGHT
    return False


def eat_apple(snake, apples):
    """
    Процедура поедания яблока, если змейка его достигла.
    После поядения яблоко перемещается на новое место.
    """
    for apple in apples:
        if snake.position == apple.position:
            snake.positions.append(snake.last)
            snake.last = None

            relocate_apple(apple, apples, snake)

            break


def is_snake_collides(snake):
    """Проверка, касается ли голова змейки её тела."""
    return snake.position in snake.positions[1:]


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

    x_shift = random.choice((-1, 1)) * GRID_SIZE
    y_shift = random.choice((-1, 1)) * GRID_SIZE

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


def reset(apples, snake):
    """Установка начального состояния игры."""
    snake.reset()

    for _ in range(APPLE_COUNT - len(apples)):
        apples.append(Apple())

    for apple in apples:
        relocate_apple(apple, apples, snake)

    screen.fill(BOARD_BACKGROUND_COLOR)


def main():
    """Запускает основной цикл игры."""
    pygame.init()

    apples = [Apple() for _ in range(APPLE_COUNT)]
    snake = Snake()

    for apple in apples:
        relocate_apple(apple, apples, snake)

    for apple in apples:
        apple.draw()
    snake.draw()

    pygame.display.update()

    while True:
        clock.tick(SPEED)

        is_quit_asked = handle_keys(snake)
        if is_quit_asked:
            break

        snake.update_direction()
        snake.move()

        eat_apple(snake, apples)

        if is_snake_collides(snake):
            print(f'Игра окончена. Ваш счёт: {len(snake.positions) - 1}.')
            reset(apples, snake)

        if len(apples) == 0:
            print('Вы победили!')
            reset(apples, snake)

        for apple in apples:
            apple.draw()
        snake.draw()

        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()
