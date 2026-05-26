import pygame
import sys
import random

pygame.init()

# ------------------ 설정 ------------------
WIDTH, HEIGHT = 1000, 700
MAP_WIDTH, MAP_HEIGHT = 3000, 3000
CELL = 25

FPS = 60
SPEED = 220
ENEMY_SPEED = 120
ENEMY_COUNT = 2

PROJECTILE_SPEED = 400
PROJECTILE_SIZE = 18
PROJECTILE_DAMAGE = 5
PROJECTILE_COOLDOWN = 2000

WHITE = (255, 255, 255)
GREEN = (50, 200, 50)
GRAY = (40, 40, 40)
SWORD = (220, 220, 220)
RED = (200, 50, 50)
YELLOW = (255, 220, 0)
BLUE = (80, 180, 255)
PURPLE = (180, 80, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zelda Field Final")

clock = pygame.time.Clock()

# ------------------ 카메라 ------------------
camera_x = 0
camera_y = 0
DEADZONE_W = 300
DEADZONE_H = 200

# ------------------ 플레이어 ------------------
player_x = MAP_WIDTH // 2
player_y = MAP_HEIGHT // 2
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

hit_enemies = set()

# ------------------ 검기 ------------------
projectiles = []
projectile_cooldown_timer = 0

# ------------------ 적 ------------------
enemies = []

for _ in range(ENEMY_COUNT):
    enemies.append({
        "type": "normal",
        "x": random.randrange(0, MAP_WIDTH - CELL),
        "y": random.randrange(0, MAP_HEIGHT - CELL),
        "hp": 3,
        "max_hp": 3,
        "hit": 0
    })

enemies.append({
    "type": "elite",
    "x": random.randrange(0, MAP_WIDTH - CELL),
    "y": random.randrange(0, MAP_HEIGHT - CELL),
    "hp": 6,
    "max_hp": 6,
    "hit": 0,
    "state": "chase",
    "charge_timer": 0,
    "dash_timer": 0,
    "dx": 0,
    "dy": 0
})

# ------------------ 상태 ------------------
game_clear = False

# 히트스톱
hitstop_timer = 0
HITSTOP_TIME = 80

# ------------------ 함수 ------------------
def draw_grid():
    for x in range(0, MAP_WIDTH, CELL):
        pygame.draw.line(screen, (60, 60, 60),
            (x - camera_x, 0 - camera_y),
            (x - camera_x, MAP_HEIGHT - camera_y))
    for y in range(0, MAP_HEIGHT, CELL):
        pygame.draw.line(screen, (60, 60, 60),
            (0 - camera_x, y - camera_y),
            (MAP_WIDTH - camera_x, y - camera_y))

def clamp(val, minv, maxv):
    return max(minv, min(val, maxv))

# ------------------ 메인 루프 ------------------
while True:
    dt = clock.tick(FPS) / 1000

    # 히트스톱
    if hitstop_timer > 0:
        hitstop_timer -= dt * 1000
        dt = 0

    # 이벤트
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if e.type == pygame.KEYDOWN and not game_clear:
            if e.key == pygame.K_SPACE:
                if attack_timer <= 0 and cooldown_timer <= 0:
                    attack_timer = attack_duration
                    attack_dir = direction
                    cooldown_timer = cooldown
                    hit_enemies.clear()

                    if player_hp == MAX_HP and projectile_cooldown_timer <= 0:
                        spawn_x = player_x + attack_dir[0] * CELL + (CELL - PROJECTILE_SIZE) / 2
                        spawn_y = player_y + attack_dir[1] * CELL + (CELL - PROJECTILE_SIZE) / 2

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

    if not game_clear:
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

    player_x = clamp(player_x, 0, MAP_WIDTH - CELL)
    player_y = clamp(player_y, 0, MAP_HEIGHT - CELL)

    player_rect = pygame.Rect(int(player_x), int(player_y), CELL, CELL)

    # 🎯 소프트 카메라
    player_screen_x = player_x - camera_x
    player_screen_y = player_y - camera_y

    left = WIDTH // 2 - DEADZONE_W // 2
    right = WIDTH // 2 + DEADZONE_W // 2
    top = HEIGHT // 2 - DEADZONE_H // 2
    bottom = HEIGHT // 2 + DEADZONE_H // 2

    if player_screen_x < left:
        camera_x -= (left - player_screen_x)
    elif player_screen_x > right:
        camera_x += (player_screen_x - right)

    if player_screen_y < top:
        camera_y -= (top - player_screen_y)
    elif player_screen_y > bottom:
        camera_y += (player_screen_y - bottom)

    camera_x = clamp(camera_x, 0, MAP_WIDTH - WIDTH)
    camera_y = clamp(camera_y, 0, MAP_HEIGHT - HEIGHT)

    # ------------------ 적 AI ------------------
    for enemy in enemies:
        diff_x = player_x - enemy["x"]
        diff_y = player_y - enemy["y"]
        dist = (diff_x**2 + diff_y**2) ** 0.5

        if enemy["type"] == "normal":
            if dist != 0:
                enemy["x"] += (diff_x / dist) * ENEMY_SPEED * dt
                enemy["y"] += (diff_y / dist) * ENEMY_SPEED * dt

        elif enemy["type"] == "elite":
            if enemy["state"] == "chase":
                if dist != 0:
                    enemy["x"] += (diff_x / dist) * ENEMY_SPEED * dt
                    enemy["y"] += (diff_y / dist) * ENEMY_SPEED * dt

                enemy["charge_timer"] += dt * 1000
                if enemy["charge_timer"] > 1500:
                    enemy["state"] = "charge"
                    enemy["charge_timer"] = 400
                    if dist != 0:
                        enemy["dx"] = diff_x / dist
                        enemy["dy"] = diff_y / dist

            elif enemy["state"] == "charge":
                enemy["charge_timer"] -= dt * 1000
                if enemy["charge_timer"] <= 0:
                    enemy["state"] = "dash"
                    enemy["dash_timer"] = 300

            elif enemy["state"] == "dash":
                enemy["x"] += enemy["dx"] * 400 * dt
                enemy["y"] += enemy["dy"] * 400 * dt
                enemy["dash_timer"] -= dt * 1000

                if enemy["dash_timer"] <= 0:
                    enemy["state"] = "chase"

        enemy["x"] = clamp(enemy["x"], 0, MAP_WIDTH - CELL)
        enemy["y"] = clamp(enemy["y"], 0, MAP_HEIGHT - CELL)

    # ------------------ 검기 ------------------
    for proj in projectiles:
        proj["x"] += proj["dx"] * PROJECTILE_SPEED * dt
        proj["y"] += proj["dy"] * PROJECTILE_SPEED * dt

    projectiles = [p for p in projectiles if 0 <= p["x"] <= MAP_WIDTH and 0 <= p["y"] <= MAP_HEIGHT]

    # ------------------ 타이머 ------------------
    attack_timer -= dt * 1000 if attack_timer > 0 else 0
    cooldown_timer -= dt * 1000 if cooldown_timer > 0 else 0
    invincible_timer -= dt * 1000 if invincible_timer > 0 else 0
    projectile_cooldown_timer -= dt * 1000 if projectile_cooldown_timer > 0 else 0

    # ------------------ 공격 ------------------
    attack_rect = None
    if attack_timer > 0:
        ax = int(player_x + attack_dir[0] * CELL)
        ay = int(player_y + attack_dir[1] * CELL)

        if attack_dir[1] != 0:
            attack_rect = pygame.Rect(ax + CELL // 4, ay, CELL // 2, CELL)
        else:
            attack_rect = pygame.Rect(ax, ay + CELL // 4, CELL, CELL // 2)

    # ------------------ 충돌 ------------------
    for enemy in enemies:
        enemy_rect = pygame.Rect(int(enemy["x"]), int(enemy["y"]), CELL, CELL)

        if attack_rect and attack_rect.colliderect(enemy_rect):
            if id(enemy) not in hit_enemies:
                enemy["hp"] -= 1
                enemy["hit"] = 100
                hit_enemies.add(id(enemy))
                hitstop_timer = HITSTOP_TIME

        for proj in projectiles[:]:
            proj_rect = pygame.Rect(int(proj["x"]), int(proj["y"]), PROJECTILE_SIZE, PROJECTILE_SIZE)
            if proj_rect.colliderect(enemy_rect):
                enemy["hp"] -= PROJECTILE_DAMAGE
                enemy["hit"] = 100
                projectiles.remove(proj)
                hitstop_timer = HITSTOP_TIME

        if player_rect.colliderect(enemy_rect):
            if invincible_timer <= 0:
                damage = 2 if enemy["type"] == "elite" and enemy.get("state") == "dash" else 1
                player_hp -= damage
                invincible_timer = invincible_time
                hitstop_timer = HITSTOP_TIME

    enemies = [e for e in enemies if e["hp"] > 0]

    if not enemies and not game_clear:
        game_clear = True

    # ------------------ 그리기 ------------------
    screen.fill(GRAY)
    draw_grid()

    for enemy in enemies:
        color = PURPLE if enemy["type"] == "elite" and enemy["state"] == "dash" else (
            BLUE if enemy["type"] == "elite" else (YELLOW if enemy["hit"] > 0 else RED))

        pygame.draw.rect(screen, color,
            (int(enemy["x"] - camera_x), int(enemy["y"] - camera_y), CELL, CELL))

        if enemy["hit"] > 0:
            enemy["hit"] -= dt * 1000

        hp_ratio = enemy["hp"] / enemy["max_hp"]
        pygame.draw.rect(screen, (60, 60, 60),
            (int(enemy["x"] - camera_x), int(enemy["y"] - camera_y - 8), CELL, 5))
        pygame.draw.rect(screen, GREEN,
            (int(enemy["x"] - camera_x), int(enemy["y"] - camera_y - 8), int(CELL * hp_ratio), 5))

    for proj in projectiles:
        pygame.draw.rect(screen, BLUE,
            (int(proj["x"] - camera_x), int(proj["y"] - camera_y), PROJECTILE_SIZE, PROJECTILE_SIZE))

    if attack_rect:
        pygame.draw.rect(screen, SWORD,
            (attack_rect.x - camera_x, attack_rect.y - camera_y,
             attack_rect.width, attack_rect.height))

    color = GREEN
    if invincible_timer > 0 and int(invincible_timer / 100) % 2 == 0:
        color = WHITE

    pygame.draw.rect(screen, color,
        (int(player_x - camera_x), int(player_y - camera_y), CELL, CELL))

    for i in range(player_hp):
        pygame.draw.rect(screen, RED, (10 + i * 30, 30, 20, 20))

    if game_clear:
        font = pygame.font.SysFont(None, 80)
        text = font.render("ALL CLEAR!", True, WHITE)
        screen.blit(text, (WIDTH // 2 - 180, HEIGHT // 2 - 40))

    pygame.display.flip()

    if player_hp <= 0:
        pygame.quit()
        sys.exit()