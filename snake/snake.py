import pygame
import random
import sys

pygame.init()

# ------------------ 폰트 ------------------
def get_korean_font(size):
    for name in ["malgungothic", "applegothic", "nanumgothic", "notosanscjk"]:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent() > 0:
            return font
    return pygame.font.SysFont(None, size)

# ------------------ 설정 ------------------
WIDTH, HEIGHT = 1200, 1000
CELL = 20
SPEED = 10

POISON_COUNT = 3
INV_COUNT = 2
SPEED_COUNT = 2
SLOW_COUNT = 2

SAFE_DISTANCE = 6
HOLE_MIN_W, HOLE_MAX_W = 4, 7

INV_DURATION = 5
SPEED_DURATION = 5
SLOW_DURATION = 5

# ------------------ 색상 ------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
DARK = (30, 150, 30)
RED = (220, 50, 50)
GRAY = (40, 40, 40)
GRID = (55, 55, 55)
PURPLE = (160, 60, 200)
YELLOW = (240, 220, 70)
BLUE = (70, 140, 255)
CYAN = (120, 120, 255)

# ------------------ 화면 ------------------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()

font = get_korean_font(36)
font_big = get_korean_font(72)

# ------------------ 구멍 ------------------
hole_img = pygame.image.load("asset/hole.png").convert_alpha()

# ------------------ 안전 생성 ------------------
def new_items(count, snake, occupied):
    items = []
    tries = 0

    while len(items) < count and tries < 2000:
        tries += 1

        pos = (
            random.randrange(0, WIDTH // CELL) * CELL,
            random.randrange(0, HEIGHT // CELL) * CELL,
        )

        if pos in snake:
            continue
        if pos in occupied:
            continue
        if pos in items:
            continue

        items.append(pos)

    return items

def new_food(snake):
    while True:
        pos = (random.randrange(0, WIDTH // CELL) * CELL,
               random.randrange(0, HEIGHT // CELL) * CELL)
        if pos not in snake:
            return pos

def new_hole(snake):
    while True:
        w = random.randint(HOLE_MIN_W, HOLE_MAX_W)
        h = random.randint(2, max(2, w - 1))

        x = random.randrange(0, WIDTH // CELL - w) * CELL
        y = random.randrange(0, HEIGHT // CELL - h) * CELL

        head = snake[0]
        dist = abs(head[0] - x) // CELL + abs(head[1] - y) // CELL

        if dist < SAFE_DISTANCE:
            continue

        overlap = any(
            (x + i * CELL, y + j * CELL) in snake
            for i in range(w)
            for j in range(h)
        )

        if not overlap:
            surf = pygame.transform.scale(hole_img, (w * CELL, h * CELL))
            return (x, y, w, h, surf)

# ------------------ 그리기 ------------------
def draw_grid():
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, GRID, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(screen, GRID, (0, y), (WIDTH, y))

def draw_snake(snake, invincible):
    for i, seg in enumerate(snake):
        color = YELLOW if invincible else (DARK if i == 0 else GREEN)
        pygame.draw.rect(screen, color, (*seg, CELL, CELL))
        pygame.draw.rect(screen, BLACK, (*seg, CELL, CELL), 1)

# ------------------ 게임 오버 ------------------
def game_over_screen(score):
    screen.fill(GRAY)
    screen.blit(font_big.render("GAME OVER", True, RED), (350, 250))
    screen.blit(font.render(f"Score: {score}", True, WHITE), (520, 360))
    screen.blit(font.render("R: Restart   Q: Quit", True, WHITE), (450, 420))
    pygame.display.flip()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    return True
                if e.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

# ------------------ 메인 ------------------
def main():

    snake = [(WIDTH // 2, HEIGHT // 2)]
    direction = (CELL, 0)

    # 🔥 생성 순서 FIX (핵심)
    food = new_food(snake)
    poisons = new_items(POISON_COUNT, snake, [food])
    inv_items = new_items(INV_COUNT, snake, [food] + poisons)
    speed_items = new_items(SPEED_COUNT, snake, [food] + poisons + inv_items)
    slow_items = new_items(SLOW_COUNT, snake, [food] + poisons + inv_items + speed_items)

    invincible = False
    speed_boost = False
    slow_boost = False

    inv_timer = 0
    speed_timer = 0
    slow_timer = 0

    holes = []
    hole_timer = 3

    score = 0

    # ------------------ loop ------------------
    while True:

        # 속도 결정
        if speed_boost:
            speed = SPEED * 2
        elif slow_boost:
            speed = max(2, int(SPEED * 0.5))
        else:
            speed = SPEED

        dt = clock.tick(speed) / 1000

        # ---------------- input ----------------
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP and direction != (0, CELL):
                    direction = (0, -CELL)
                if e.key == pygame.K_DOWN and direction != (0, -CELL):
                    direction = (0, CELL)
                if e.key == pygame.K_LEFT and direction != (CELL, 0):
                    direction = (-CELL, 0)
                if e.key == pygame.K_RIGHT and direction != (-CELL, 0):
                    direction = (CELL, 0)

        # ---------------- move ----------------
        x = snake[0][0] + direction[0]
        y = snake[0][1] + direction[1]

        if invincible:
            x %= WIDTH
            y %= HEIGHT

        head = (x, y)

        # ---------------- hole ----------------
        hole_timer -= dt
        if hole_timer <= 0:
            holes.append(new_hole(snake))
            hole_timer = random.randint(3, 6)

        for hx, hy, hw, hh, _ in holes:
            if hx <= head[0] < hx + hw * CELL and hy <= head[1] < hy + hh * CELL:
                if not invincible:
                    if game_over_screen(score):
                        main()
                    return

        # ---------------- death ----------------
        if (x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT) and not invincible:
            if game_over_screen(score):
                main()
            return

        if head in snake:
            if game_over_screen(score):
                main()
            return

        snake.insert(0, head)

        grow = False

        # ---------------- items ----------------
        if head == food:
            score += 10
            food = new_food(snake)
            grow = True

        elif head in poisons:
            score = max(0, score - 5)
            poisons.remove(head)
            poisons.append(new_items(1, snake, [food] + poisons)[0])
            grow = True

        elif head in inv_items:
            invincible = True
            inv_timer = INV_DURATION
            inv_items.remove(head)
            inv_items.append(new_items(1, snake, [food] + poisons + inv_items)[0])

        elif head in speed_items:
            if slow_boost:
                slow_boost = False
                slow_timer = 0
                speed_boost = False
                speed_timer = 0
            else:
                speed_boost = True
                speed_timer = SPEED_DURATION

            speed_items.remove(head)
            speed_items.append(new_items(1, snake, [food] + poisons + inv_items + speed_items)[0])

        elif head in slow_items:
            if speed_boost:
                speed_boost = False
                speed_timer = 0
                slow_boost = False
                slow_timer = 0
            else:
                slow_boost = True
                slow_timer = SLOW_DURATION

            slow_items.remove(head)
            slow_items.append(new_items(1, snake, [food] + poisons + inv_items + speed_items + slow_items)[0])

        # ---------------- timers ----------------
        if invincible:
            inv_timer -= dt
            if inv_timer <= 0:
                invincible = False

        if speed_boost:
            speed_timer -= dt
            if speed_timer <= 0:
                speed_boost = False

        if slow_boost:
            slow_timer -= dt
            if slow_timer <= 0:
                slow_boost = False

        if not grow:
            snake.pop()

        # ---------------- render ----------------
        screen.fill(GRAY)

        draw_grid()

        pygame.draw.rect(screen, RED, (*food, CELL, CELL))

        for p in poisons:
            pygame.draw.rect(screen, PURPLE, (*p, CELL, CELL))

        for i in inv_items:
            pygame.draw.rect(screen, YELLOW, (*i, CELL, CELL))

        for s in speed_items:
            pygame.draw.rect(screen, BLUE, (*s, CELL, CELL))

        for s in slow_items:
            pygame.draw.rect(screen, CYAN, (*s, CELL, CELL))

        for hx, hy, hw, hh, surf in holes:
            screen.blit(surf, (hx, hy))

        draw_snake(snake, invincible)

        screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))

        pygame.display.flip()


main()