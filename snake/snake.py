import pygame
import random
import sys

pygame.init()


def get_korean_font(size):
    candidates = ["malgungothic", "applegothic", "nanumgothic", "notosanscjk"]
    for name in candidates:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent() > 0:
            return font
    return pygame.font.SysFont(None, size)

WIDTH, HEIGHT = 1200, 1000
CELL = 20
FPS = 10
SPEED = 10 # 시작 속도값
#아이템 갯수 최댓값
POISON_COUNT = 3
INV_COUNT = 2
SPEED_COUNT = 2

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
DARK = (30, 150, 30)
RED = (220, 50, 50)
GRAY = (40, 40, 40)
PURPLE = (160, 60, 200)
YELLOW = (240, 220, 70)
BLUE = (70, 140, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()
font = get_korean_font(36)
font_big = get_korean_font(72)

# --- 사운드 자리 ---
# eat_sound = pygame.mixer.Sound("eat.wav")
# die_sound = pygame.mixer.Sound("die.wav")


def new_food(snake): #열매 생성 
    while True:
        pos = (
            random.randrange(0, WIDTH // CELL) * CELL,
            random.randrange(0, HEIGHT // CELL) * CELL,
        )
        if pos not in snake:
            return pos
        
def new_poison(snake, food): #독 열매 생성
    while True:
        pos = (
            random.randrange(0, WIDTH // CELL) * CELL,
            random.randrange(0, HEIGHT // CELL) * CELL,
        )
        if pos not in snake and pos != food:
            return pos

def new_invincible(snake, food, poison): #무적 아이템 생성
    while True:
        pos = (
            random.randrange(0, WIDTH // CELL) * CELL,
            random.randrange(0, HEIGHT // CELL) * CELL,
        )
        if pos not in snake and pos != food and pos != poison:
            return pos
        
def new_speed_item(snake, food, poison, inv_item):
    while True:
        pos = (
            random.randrange(0, WIDTH // CELL) * CELL,
            random.randrange(0, HEIGHT // CELL) * CELL,
        )
        if pos not in snake and pos not in (food, poison, inv_item):
            return pos

def new_item_positions(count, snake, occupied):
    items = []
    while len(items) < count:
        pos = (
            random.randrange(0, WIDTH // CELL) * CELL,
            random.randrange(0, HEIGHT // CELL) * CELL,
        )
        if pos not in snake and pos not in occupied and pos not in items:
            items.append(pos)
    return items

def draw_grid():
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, (20, 20, 20), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(screen, (20, 20, 20), (0, y), (WIDTH, y))


def draw_snake(snake,invincible):
    for i, seg in enumerate(snake):
        color = YELLOW if invincible else (DARK if i == 0 else GREEN)
        pygame.draw.rect(screen, color, (*seg, CELL, CELL))
        pygame.draw.rect(screen, BLACK, (*seg, CELL, CELL), 1)


def draw_hud(score):
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))

def game_over_screen(score):
    screen.fill(GRAY)
    screen.blit(font_big.render("GAME OVER", True, RED), (220, 220))
    screen.blit(font.render(f"Score: {score}", True, WHITE), (350, 310))
    screen.blit(font.render("R: Restart   Q: Quit", True, WHITE), (270, 360))
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

def main():

    snake = [(WIDTH // 2, HEIGHT // 2)]
    direction = (CELL, 0)
    food = new_food(snake)
    poisons = new_item_positions(POISON_COUNT, snake, [food])
    #무적
    inv_items = new_item_positions(INV_COUNT, snake, [food] + poisons)
    invincible = False
    inv_timer = 0
    INV_DURATION = 5  # 초
    #게임 가속
    speed_items = new_item_positions(SPEED_COUNT, snake, [food] + poisons + inv_items)
    speed_boost = False
    speed_timer = 0
    SPEED_DURATION = 5  # 초
    SPEED_MULTIPLIER = 1.8
    base_speed = SPEED

    score = 0
    speed = SPEED
    while True:
        current_speed = int(base_speed * SPEED_MULTIPLIER) if speed_boost else base_speed
        dt = clock.tick(current_speed) / 1000  # 초 단위
        if speed_boost:
            speed_timer -= dt
            if speed_timer <= 0:
                speed_boost = False
        if invincible:
            inv_timer -= dt
            if inv_timer <= 0:
                invincible = False

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

        new_x = snake[0][0] + direction[0]
        new_y = snake[0][1] + direction[1]

# 🟡 무적이면 벽 통과 (반대편 이동)
        if invincible:
            new_x %= WIDTH
            new_y %= HEIGHT

        head = (new_x, new_y)

        hit_wall = (
            head[0] < 0
            or head[0] >= WIDTH
            or head[1] < 0
            or head[1] >= HEIGHT
        )

        hit_self = head in snake

        if (hit_wall and not invincible) or hit_self:
            # die_sound.play()
            if game_over_screen(score):
                main()
            return

        if invincible:
            screen.blit(font.render("INVINCIBLE!", True, YELLOW), (600, 10))

        if speed_boost:
            screen.blit(font.render("SPEED UP!", True, BLUE), (580, 40))
        
        
        snake.insert(0, head)

        grow = False  # 🔥 기본: 안 자람

        # 🍎 일반 열매
        if head == food:
            score += 10
            food = new_food(snake)
            grow = True
        # 🟣 독 열매
        elif head in poisons:
            score -= 5
            poisons.remove(head)
            poisons.append(new_item_positions(1, snake, [food] + poisons)[0])
            grow = True
        # 🟡 무적 아이템
        elif head in inv_items:
            invincible = True
            inv_timer = INV_DURATION
            inv_items.remove(head)
            inv_items.append(new_item_positions(1, snake, [food] + poisons + inv_items)[0])
        # 🔵 속도 디버프
        elif head in speed_items:
            speed_boost = True
            speed_timer = SPEED_DURATION
            speed_items.remove(head)
            speed_items.append(new_item_positions(1, snake, [food] + poisons + inv_items + speed_items)[0])
        # ❗ 여기 하나로 통제
        if not grow:
            snake.pop()

        screen.fill(GRAY)
        draw_grid()
        #화면상에 아이템 생성
        pygame.draw.rect(screen, RED, (*food, CELL, CELL))
        for p in poisons:
            pygame.draw.rect(screen, PURPLE, (*p, CELL, CELL))
        for i in inv_items:
            pygame.draw.rect(screen, YELLOW, (*i, CELL, CELL))
        for s in speed_items:
            pygame.draw.rect(screen, BLUE, (*s, CELL, CELL))

        draw_snake(snake,invincible)
        draw_hud(score)
        pygame.display.flip()


main()