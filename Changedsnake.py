import pygame
import sys
import random

pygame.init()

# ------------------ 설정 ------------------
WIDTH, HEIGHT = 1000, 700
CELL = 25

FPS = 60
SPEED = 220
ENEMY_SPEED = 120
ENEMY_COUNT = 3

PROJECTILE_SPEED = 400
PROJECTILE_SIZE = 18
PROJECTILE_DAMAGE = 5
PROJECTILE_COOLDOWN = 2000  # ms

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
GRAY = (40, 40, 40)
SWORD = (220, 220, 220)
RED = (200, 50, 50)
YELLOW = (255, 220, 0)
BLUE = (80, 180, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zelda Final")

clock = pygame.time.Clock()

# ------------------ 플레이어 ------------------
player_x = WIDTH // 2
player_y = HEIGHT // 2
direction = (0, -1)

player_hp = 5
MAX_HP = 5

invincible_timer = 0
invincible_time = 1000

# ------------------ 공격 ------------------
attack_timer = 0
attack_duration = 120
attack_dir = (0, -1)

cooldown_timer = 0
cooldown = 250

# ------------------ 검기 ------------------
projectiles = []
projectile_cooldown_timer = 0

# ------------------ 적 ------------------
enemies = []
for _ in range(ENEMY_COUNT):
    enemies.append({
        "x": random.randrange(0, WIDTH - CELL),
        "y": random.randrange(0, HEIGHT - CELL),
        "hp": 3,
        "hit": 0
    })

# ------------------ 함수 ------------------
def draw_grid():
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, (60, 60, 60), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(screen, (60, 60, 60), (0, y), (WIDTH, y))

def clamp(val, minv, maxv):
    return max(minv, min(val, maxv))

# ------------------ 메인 루프 ------------------
while True:
    dt = clock.tick(FPS) / 1000

    # 이벤트
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE:
                if attack_timer <= 0 and cooldown_timer <= 0:
                    attack_timer = attack_duration
                    attack_dir = direction
                    cooldown_timer = cooldown

                    # 🔥 검기 생성 위치 수정
                    if player_hp == MAX_HP and projectile_cooldown_timer <= 0:
                        spawn_x = player_x + attack_dir[0] * CELL
                        spawn_y = player_y + attack_dir[1] * CELL

                        spawn_x += CELL // 2 - PROJECTILE_SIZE // 2
                        spawn_y += CELL // 2 - PROJECTILE_SIZE // 2

                        projectiles.append({
                            "x": spawn_x,
                            "y": spawn_y,
                            "dx": attack_dir[0],
                            "dy": attack_dir[1]
                        })

                        projectile_cooldown_timer = PROJECTILE_COOLDOWN

    # 입력
    keys = pygame.key.get_pressed()
    dx, dy = 0, 0

    if keys[pygame.K_w]:
        dx, dy = 0, -1
    elif keys[pygame.K_s]:
        dx, dy = 0, 1
    elif keys[pygame.K_a]:
        dx, dy = -1, 0
    elif keys[pygame.K_d]:
        dx, dy = 1, 0

    if dx != 0 or dy != 0:
        direction = (dx, dy)

    player_x += dx * SPEED * dt
    player_y += dy * SPEED * dt

    player_x = clamp(player_x, 0, WIDTH - CELL)
    player_y = clamp(player_y, 0, HEIGHT - CELL)

    player_rect = pygame.Rect(player_x, player_y, CELL, CELL)

    # ------------------ 적 AI ------------------
    for enemy in enemies:
        diff_x = player_x - enemy["x"]
        diff_y = player_y - enemy["y"]

        if abs(diff_x) > abs(diff_y):
            move_x = 1 if diff_x > 0 else -1
            move_y = 0
        else:
            move_x = 0
            move_y = 1 if diff_y > 0 else -1

        enemy["x"] += move_x * ENEMY_SPEED * dt
        enemy["y"] += move_y * ENEMY_SPEED * dt

    # ------------------ 🔥 적끼리 충돌 방지 ------------------
    for i in range(len(enemies)):
        for j in range(i + 1, len(enemies)):
            e1 = enemies[i]
            e2 = enemies[j]

            dx = e1["x"] - e2["x"]
            dy = e1["y"] - e2["y"]

            dist_sq = dx * dx + dy * dy
            min_dist = CELL

            if dist_sq < min_dist * min_dist and dist_sq != 0:
                dist = dist_sq ** 0.5

                overlap = (min_dist - dist) / 2
                nx = dx / dist
                ny = dy / dist

                e1["x"] += nx * overlap
                e1["y"] += ny * overlap
                e2["x"] -= nx * overlap
                e2["y"] -= ny * overlap

    # ------------------ 검기 이동 ------------------
    for proj in projectiles:
        proj["x"] += proj["dx"] * PROJECTILE_SPEED * dt
        proj["y"] += proj["dy"] * PROJECTILE_SPEED * dt

    projectiles = [
        p for p in projectiles
        if 0 <= p["x"] <= WIDTH and 0 <= p["y"] <= HEIGHT
    ]

    # ------------------ 타이머 ------------------
    if attack_timer > 0:
        attack_timer -= dt * 1000

    if cooldown_timer > 0:
        cooldown_timer -= dt * 1000

    if invincible_timer > 0:
        invincible_timer -= dt * 1000

    if projectile_cooldown_timer > 0:
        projectile_cooldown_timer -= dt * 1000

    # ------------------ 공격 범위 ------------------
    attack_rect = None
    if attack_timer > 0:
        ax = player_x + attack_dir[0] * CELL
        ay = player_y + attack_dir[1] * CELL

        if attack_dir[1] != 0:
            attack_rect = pygame.Rect(ax + CELL // 4, ay, CELL // 2, CELL)
        else:
            attack_rect = pygame.Rect(ax, ay + CELL // 4, CELL, CELL // 2)

    # ------------------ 충돌 ------------------
    for enemy in enemies[:]:
        enemy_rect = pygame.Rect(enemy["x"], enemy["y"], CELL, CELL)

        # 근접 공격
        if attack_rect and attack_rect.colliderect(enemy_rect):
            enemy["hp"] -= 1
            enemy["hit"] = 100
            enemy["x"] += attack_dir[0] * 40
            enemy["y"] += attack_dir[1] * 40

        # 검기 공격
        for proj in projectiles[:]:
            proj_rect = pygame.Rect(proj["x"], proj["y"], PROJECTILE_SIZE, PROJECTILE_SIZE)
            if proj_rect.colliderect(enemy_rect):
                enemy["hp"] -= PROJECTILE_DAMAGE
                enemy["hit"] = 100
                enemy["x"] += proj["dx"] * 80
                enemy["y"] += proj["dy"] * 80
                projectiles.remove(proj)

        # 플레이어 피격
        if player_rect.colliderect(enemy_rect):
            if invincible_timer <= 0:
                player_hp -= 1
                invincible_timer = invincible_time

        if enemy["hp"] <= 0:
            enemies.remove(enemy)

    # ------------------ 그리기 ------------------
    screen.fill(GRAY)
    draw_grid()

    # 적
    for enemy in enemies:
        color = YELLOW if enemy["hit"] > 0 else RED
        pygame.draw.rect(screen, color, (enemy["x"], enemy["y"], CELL, CELL))

        if enemy["hit"] > 0:
            enemy["hit"] -= dt * 1000

    # 검기
    for proj in projectiles:
        pygame.draw.rect(screen, BLUE,
                         (int(proj["x"]), int(proj["y"]), PROJECTILE_SIZE, PROJECTILE_SIZE))

    # 공격
    if attack_rect:
        pygame.draw.rect(screen, SWORD, attack_rect)

    # 플레이어
    color = WHITE if invincible_timer > 0 and int(invincible_timer / 100) % 2 == 0 else GREEN
    pygame.draw.rect(screen, color, (player_x, player_y, CELL, CELL))

    # 체력
    for i in range(player_hp):
        pygame.draw.rect(screen, RED, (10 + i * 30, 30, 20, 20))

    # ALL CLEAR
    if len(enemies) == 0:
        font = pygame.font.SysFont(None, 80)
        text = font.render("ALL CLEAR!", True, WHITE)
        screen.blit(text, (WIDTH // 2 - 180, HEIGHT // 2 - 40))

    pygame.display.flip()

    # 게임 오버
    if player_hp <= 0:
        print("GAME OVER")
        pygame.quit()
        sys.exit()