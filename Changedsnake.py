import pygame
import sys
import random

pygame.init()

# ------------------ 기본 설정 ------------------
WIDTH, HEIGHT = 1000, 700

# 방 크기를 화면 크기와 같게 줄임
# 카메라 기능은 그대로 유지됨
ROOM_WIDTH, ROOM_HEIGHT = 1000, 700

CELL = 25
FPS = 60

SPEED = 220
ENEMY_SPEED = 120
STRONG_SPEED = 110

# ------------------ 플레이어 공격 ------------------
SWORD_DAMAGE = 2
SWORD_RANGE = CELL

PROJECTILE_DAMAGE = 1
PROJECTILE_SPEED = 400
PROJECTILE_SIZE = 18
PROJECTILE_COOLDOWN = 2000
MIN_PROJECTILE_COOLDOWN = 600

# ------------------ 적 투사체 ------------------
ENEMY_PROJECTILE_SPEED = 260
ENEMY_PROJECTILE_SIZE = 14
SHOOTER_ATTACK_TIME = 1600
REFLECTED_PROJECTILE_DAMAGE = 2

# ------------------ 방패 ------------------
SHIELD_HEIGHT = 14
SHIELD_COLOR = (180, 180, 255)

MAX_SHIELD_DURABILITY = 3
shield_durability = MAX_SHIELD_DURABILITY
SHIELD_RECOVER_TIME = 1800
shield_recover_timer = 0
SHIELD_MOVE_SPEED_RATE = 0.55

# ------------------ 아이템 ------------------
ITEM_DROP_CHANCE = 0.3

# ------------------ 게임오버 ------------------
GAME_OVER_EFFECT_TIME = 1200
game_over_timer = 0

# ------------------ 색상 ------------------
WHITE = (255, 255, 255)
GREEN = (50, 200, 50)
GRAY = (40, 40, 40)
DARK = (25, 25, 25)
SWORD = (220, 220, 220)
RED = (200, 50, 50)
YELLOW = (255, 220, 0)
BLUE = (80, 180, 255)
PURPLE = (180, 80, 255)
ORANGE = (255, 150, 40)
CYAN = (120, 255, 255)
DOOR_COLOR = (130, 80, 40)
OPEN_DOOR_COLOR = (80, 200, 120)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Room Battle RPG")
clock = pygame.time.Clock()

font_big = pygame.font.SysFont(None, 90)
font_mid = pygame.font.SysFont(None, 45)
font_small = pygame.font.SysFont(None, 30)

# ------------------ 게임 상태 ------------------
game_state = "start"

# ------------------ 카메라 ------------------
camera_x = 0
camera_y = 0
DEADZONE_W = 300
DEADZONE_H = 200

# ------------------ 플레이어 ------------------
player_x = 100
player_y = ROOM_HEIGHT // 2
direction = (1, 0)

player_hp = 5
MAX_HP = 5
invincible_timer = 0
invincible_time = 1000

# ------------------ 공격 상태 ------------------
attack_timer = 0
attack_duration = 120
attack_dir = (1, 0)
cooldown_timer = 0
cooldown = 250
hit_enemies = set()

# ------------------ 오브젝트 ------------------
projectiles = []
enemy_projectiles = []
enemies = []
items = []

projectile_cooldown_timer = 0

# ------------------ 히트스톱 ------------------
hitstop_timer = 0
HITSTOP_TIME = 80

# ------------------ 방 데이터 ------------------
current_room_index = 0
room_cleared = False

rooms = [
    {
        "name": "Room 1 - Tutorial",
        "enemies": [
            ("normal", 380, 260),
            ("normal", 520, 390),
            ("normal", 680, 280),
        ],
        "reward_items": []
    },
    {
        "name": "Room 2 - Dash Enemy",
        "enemies": [
            ("normal", 360, 250),
            ("normal", 500, 430),
            ("strong_dash", 700, 330),
        ],
        "reward_items": []
    },
    {
        "name": "Room 3 - Shooter Enemy",
        "enemies": [
            ("normal", 350, 250),
            ("normal", 500, 430),
            ("strong_shooter", 700, 330),
        ],
        "reward_items": []
    },
    {
        "name": "Room 4 - Mixed Battle",
        "enemies": [
            ("normal", 330, 230),
            ("normal", 430, 450),
            ("strong_dash", 650, 270),
            ("strong_shooter", 760, 430),
        ],
        "reward_items": []
    },
    {
        "name": "Room 5 - Reward Room",
        "enemies": [],
        "reward_items": [
            ("heal", 420, 330),
            ("sword_up", 520, 330),
            ("projectile_up", 620, 330),
        ]
    },
    {
        "name": "Room 6 - Final Room",
        "enemies": [
            ("normal", 330, 220),
            ("normal", 380, 480),
            ("normal", 520, 350),
            ("strong_dash", 660, 260),
            ("strong_shooter", 760, 440),
        ],
        "reward_items": []
    },
]


def clamp(val, minv, maxv):
    return max(minv, min(val, maxv))


def draw_grid():
    for x in range(0, ROOM_WIDTH, CELL):
        pygame.draw.line(
            screen,
            (60, 60, 60),
            (x - camera_x, -camera_y),
            (x - camera_x, ROOM_HEIGHT - camera_y)
        )

    for y in range(0, ROOM_HEIGHT, CELL):
        pygame.draw.line(
            screen,
            (60, 60, 60),
            (-camera_x, y - camera_y),
            (ROOM_WIDTH - camera_x, y - camera_y)
        )


def make_enemy(enemy_type, x, y):
    if enemy_type == "normal":
        return {
            "type": "normal",
            "x": x,
            "y": y,
            "hp": 2,
            "max_hp": 2,
            "hit": 0
        }

    if enemy_type == "strong_dash":
        return {
            "type": "strong_dash",
            "x": x,
            "y": y,
            "hp": 5,
            "max_hp": 5,
            "hit": 0,
            "state": "chase",
            "charge_timer": 0,
            "dash_timer": 0,
            "dx": 0,
            "dy": 0
        }

    if enemy_type == "strong_shooter":
        return {
            "type": "strong_shooter",
            "x": x,
            "y": y,
            "hp": 5,
            "max_hp": 5,
            "hit": 0,
            "shoot_timer": 0
        }


def load_room(index):
    global enemies, items, projectiles, enemy_projectiles
    global player_x, player_y, direction
    global camera_x, camera_y
    global room_cleared
    global attack_timer, cooldown_timer, projectile_cooldown_timer
    global hit_enemies

    room = rooms[index]

    enemies = []
    items = []
    projectiles = []
    enemy_projectiles = []

    for enemy_type, x, y in room["enemies"]:
        enemies.append(make_enemy(enemy_type, x, y))

    for item_type, x, y in room["reward_items"]:
        items.append({
            "type": item_type,
            "x": x,
            "y": y
        })

    room_cleared = len(enemies) == 0

    player_x = 100
    player_y = ROOM_HEIGHT // 2
    direction = (1, 0)

    camera_x = 0
    camera_y = clamp(player_y - HEIGHT // 2, 0, max(0, ROOM_HEIGHT - HEIGHT))

    attack_timer = 0
    cooldown_timer = 0
    projectile_cooldown_timer = 0
    hit_enemies.clear()


def reset_game():
    global player_hp, invincible_timer
    global SWORD_DAMAGE, PROJECTILE_DAMAGE, PROJECTILE_COOLDOWN, SWORD_RANGE
    global shield_durability, shield_recover_timer
    global current_room_index, game_over_timer
    global hitstop_timer

    player_hp = MAX_HP
    invincible_timer = 0

    SWORD_DAMAGE = 2
    PROJECTILE_DAMAGE = 1
    PROJECTILE_COOLDOWN = 2000
    SWORD_RANGE = CELL

    shield_durability = MAX_SHIELD_DURABILITY
    shield_recover_timer = 0

    current_room_index = 0
    game_over_timer = 0
    hitstop_timer = 0

    load_room(current_room_index)


def drop_item(x, y):
    item_type = random.choice([
        "heal",
        "sword_up",
        "projectile_up",
        "cooldown_down",
        "range_up"
    ])

    items.append({
        "type": item_type,
        "x": x,
        "y": y
    })


def get_door_rect():
    return pygame.Rect(ROOM_WIDTH - 60, ROOM_HEIGHT // 2 - 60, 45, 120)


def draw_start_screen():
    screen.fill(DARK)

    title = font_big.render("ROOM BATTLE", True, WHITE)
    info = font_small.render("Click START or press ENTER", True, WHITE)

    button_rect = pygame.Rect(WIDTH // 2 - 130, HEIGHT // 2 + 40, 260, 80)

    pygame.draw.rect(screen, BLUE, button_rect, border_radius=12)
    pygame.draw.rect(screen, WHITE, button_rect, 3, border_radius=12)

    button_text = font_mid.render("START", True, WHITE)

    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 150))
    screen.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT // 2 - 60))
    screen.blit(button_text, (WIDTH // 2 - button_text.get_width() // 2, HEIGHT // 2 + 60))

    pygame.display.flip()
    return button_rect


def draw_game_over_screen():
    screen.fill((15, 15, 15))

    title = font_big.render("GAME OVER", True, RED)
    info = font_small.render("Press ENTER to Restart", True, WHITE)
    quit_info = font_small.render("Press ESC to Quit", True, WHITE)

    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 120))
    screen.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT // 2))
    screen.blit(quit_info, (WIDTH // 2 - quit_info.get_width() // 2, HEIGHT // 2 + 40))

    pygame.display.flip()


def draw_game_clear_screen():
    screen.fill((10, 25, 15))

    title = font_big.render("GAME CLEAR!", True, GREEN)
    info = font_small.render("Press ENTER to Play Again", True, WHITE)
    quit_info = font_small.render("Press ESC to Quit", True, WHITE)

    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 120))
    screen.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT // 2))
    screen.blit(quit_info, (WIDTH // 2 - quit_info.get_width() // 2, HEIGHT // 2 + 40))

    pygame.display.flip()


def draw_world():
    screen.fill(GRAY)
    draw_grid()

    door_rect = get_door_rect()
    door_color = OPEN_DOOR_COLOR if room_cleared else DOOR_COLOR

    pygame.draw.rect(
        screen,
        door_color,
        (
            door_rect.x - camera_x,
            door_rect.y - camera_y,
            door_rect.width,
            door_rect.height
        )
    )

    door_text = font_small.render("NEXT", True, WHITE)
    screen.blit(
        door_text,
        (
            door_rect.x - camera_x - 5,
            door_rect.y - camera_y + 45
        )
    )


while True:
    dt = clock.tick(FPS) / 1000

    if hitstop_timer > 0:
        hitstop_timer -= dt * 1000
        dt = 0

    # ------------------ 시작 화면 ------------------
    if game_state == "start":
        button_rect = draw_start_screen()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(e.pos):
                    reset_game()
                    game_state = "play"

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    reset_game()
                    game_state = "play"

        continue

    # ------------------ 게임오버 화면 ------------------
    if game_state == "game_over":
        draw_game_over_screen()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    reset_game()
                    game_state = "play"

                elif e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        continue

    # ------------------ 게임 클리어 화면 ------------------
    if game_state == "game_clear":
        draw_game_clear_screen()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    reset_game()
                    game_state = "play"

                elif e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        continue

    # ------------------ 게임오버 연출 ------------------
    if game_state == "game_over_effect":
        game_over_timer -= dt * 1000

        screen.fill((20, 0, 0))
        draw_grid()

        for enemy in enemies:
            if enemy["type"] == "strong_dash":
                color = BLUE
            elif enemy["type"] == "strong_shooter":
                color = CYAN
            else:
                color = RED

            pygame.draw.rect(
                screen,
                color,
                (
                    int(enemy["x"] - camera_x),
                    int(enemy["y"] - camera_y),
                    CELL,
                    CELL
                )
            )

        fade_ratio = game_over_timer / GAME_OVER_EFFECT_TIME
        fade_ratio = max(0, min(1, fade_ratio))

        player_color = (
            int(50 * fade_ratio),
            int(200 * fade_ratio),
            int(50 * fade_ratio)
        )

        pygame.draw.rect(
            screen,
            player_color,
            (
                int(player_x - camera_x),
                int(player_y - camera_y),
                CELL,
                CELL
            )
        )

        over_text = font_mid.render("You Died...", True, WHITE)
        screen.blit(
            over_text,
            (
                WIDTH // 2 - over_text.get_width() // 2,
                HEIGHT // 2 - 30
            )
        )

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if game_over_timer <= 0:
            game_state = "game_over"

        continue

    # ------------------ 이벤트 ------------------
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # 좌클릭 검 공격
        if e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1:
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

    # ------------------ 입력 ------------------
    keys = pygame.key.get_pressed()
    mouse_buttons = pygame.mouse.get_pressed()

    shield_using = mouse_buttons[2] and shield_durability > 0

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

    current_speed = SPEED

    if shield_using:
        current_speed = SPEED * SHIELD_MOVE_SPEED_RATE

    player_x += dx * current_speed * dt
    player_y += dy * current_speed * dt

    player_x = clamp(player_x, 0, ROOM_WIDTH - CELL)
    player_y = clamp(player_y, 0, ROOM_HEIGHT - CELL)

    player_rect = pygame.Rect(int(player_x), int(player_y), CELL, CELL)

    # ------------------ 카메라 ------------------
    player_screen_x = player_x - camera_x
    player_screen_y = player_y - camera_y

    left = WIDTH // 2 - DEADZONE_W // 2
    right = WIDTH // 2 + DEADZONE_W // 2
    top = HEIGHT // 2 - DEADZONE_H // 2
    bottom = HEIGHT // 2 + DEADZONE_H // 2

    if player_screen_x < left:
        camera_x -= left - player_screen_x
    elif player_screen_x > right:
        camera_x += player_screen_x - right

    if player_screen_y < top:
        camera_y -= top - player_screen_y
    elif player_screen_y > bottom:
        camera_y += player_screen_y - bottom

    camera_x = clamp(camera_x, 0, max(0, ROOM_WIDTH - WIDTH))
    camera_y = clamp(camera_y, 0, max(0, ROOM_HEIGHT - HEIGHT))

    # ------------------ 방 클리어 / 문 이동 ------------------
    if len(enemies) == 0:
        room_cleared = True

    door_rect = get_door_rect()

    if room_cleared and player_rect.colliderect(door_rect):
        current_room_index += 1

        if current_room_index >= len(rooms):
            game_state = "game_clear"
            continue
        else:
            load_room(current_room_index)
            continue

    # ------------------ 적 AI ------------------
    for enemy in enemies:
        diff_x = player_x - enemy["x"]
        diff_y = player_y - enemy["y"]
        dist = (diff_x ** 2 + diff_y ** 2) ** 0.5

        if enemy["type"] == "normal":
            if dist != 0:
                enemy["x"] += (diff_x / dist) * ENEMY_SPEED * dt
                enemy["y"] += (diff_y / dist) * ENEMY_SPEED * dt

        elif enemy["type"] == "strong_dash":
            if enemy["state"] == "chase":
                if dist != 0:
                    enemy["x"] += (diff_x / dist) * STRONG_SPEED * dt
                    enemy["y"] += (diff_y / dist) * STRONG_SPEED * dt

                enemy["charge_timer"] += dt * 1000

                if enemy["charge_timer"] > 1600:
                    enemy["state"] = "charge"
                    enemy["charge_timer"] = 450

                    if dist != 0:
                        enemy["dx"] = diff_x / dist
                        enemy["dy"] = diff_y / dist

            elif enemy["state"] == "charge":
                enemy["charge_timer"] -= dt * 1000

                if enemy["charge_timer"] <= 0:
                    enemy["state"] = "dash"
                    enemy["dash_timer"] = 320

            elif enemy["state"] == "dash":
                enemy["x"] += enemy["dx"] * 430 * dt
                enemy["y"] += enemy["dy"] * 430 * dt
                enemy["dash_timer"] -= dt * 1000

                if enemy["dash_timer"] <= 0:
                    enemy["state"] = "chase"
                    enemy["charge_timer"] = 0

        elif enemy["type"] == "strong_shooter":
            if dist != 0:
                enemy["x"] += (diff_x / dist) * (STRONG_SPEED * 0.75) * dt
                enemy["y"] += (diff_y / dist) * (STRONG_SPEED * 0.75) * dt

            enemy["shoot_timer"] += dt * 1000

            if enemy["shoot_timer"] >= SHOOTER_ATTACK_TIME:
                enemy["shoot_timer"] = 0

                if dist != 0:
                    enemy_projectiles.append({
                        "x": enemy["x"] + CELL // 2 - ENEMY_PROJECTILE_SIZE // 2,
                        "y": enemy["y"] + CELL // 2 - ENEMY_PROJECTILE_SIZE // 2,
                        "dx": diff_x / dist,
                        "dy": diff_y / dist,
                        "reflected": False
                    })

        enemy["x"] = clamp(enemy["x"], 0, ROOM_WIDTH - CELL)
        enemy["y"] = clamp(enemy["y"], 0, ROOM_HEIGHT - CELL)

    # ------------------ 플레이어 검기 이동 ------------------
    for proj in projectiles:
        proj["x"] += proj["dx"] * PROJECTILE_SPEED * dt
        proj["y"] += proj["dy"] * PROJECTILE_SPEED * dt

    projectiles = [
        p for p in projectiles
        if 0 <= p["x"] <= ROOM_WIDTH and 0 <= p["y"] <= ROOM_HEIGHT
    ]

    # ------------------ 적 투사체 이동 ------------------
    for ep in enemy_projectiles:
        ep["x"] += ep["dx"] * ENEMY_PROJECTILE_SPEED * dt
        ep["y"] += ep["dy"] * ENEMY_PROJECTILE_SPEED * dt

    enemy_projectiles = [
        ep for ep in enemy_projectiles
        if 0 <= ep["x"] <= ROOM_WIDTH and 0 <= ep["y"] <= ROOM_HEIGHT
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

    if shield_durability < MAX_SHIELD_DURABILITY:
        shield_recover_timer += dt * 1000

        if shield_recover_timer >= SHIELD_RECOVER_TIME:
            shield_durability += 1
            shield_recover_timer = 0
    else:
        shield_recover_timer = 0

    # ------------------ 공격 판정 ------------------
    attack_rect = None

    if attack_timer > 0:
        if attack_dir[1] != 0:
            attack_rect = pygame.Rect(
                int(player_x + CELL // 4),
                int(player_y + attack_dir[1] * SWORD_RANGE),
                CELL // 2,
                SWORD_RANGE
            )
        else:
            attack_rect = pygame.Rect(
                int(player_x + attack_dir[0] * SWORD_RANGE),
                int(player_y + CELL // 4),
                SWORD_RANGE,
                CELL // 2
            )

    # ------------------ 방패 판정 ------------------
    shield_rect = None

    if shield_using:
        if direction[1] != 0:
            shield_rect = pygame.Rect(
                int(player_x - 5),
                int(player_y + direction[1] * CELL),
                CELL + 10,
                SHIELD_HEIGHT
            )

            if direction[1] < 0:
                shield_rect.y = int(player_y - SHIELD_HEIGHT)

        else:
            shield_rect = pygame.Rect(
                int(player_x + direction[0] * CELL),
                int(player_y - 5),
                SHIELD_HEIGHT,
                CELL + 10
            )

            if direction[0] < 0:
                shield_rect.x = int(player_x - SHIELD_HEIGHT)

    # 방패로 적 투사체 반사
    for ep in enemy_projectiles:
        ep_rect = pygame.Rect(
            int(ep["x"]),
            int(ep["y"]),
            ENEMY_PROJECTILE_SIZE,
            ENEMY_PROJECTILE_SIZE
        )

        if shield_rect and ep_rect.colliderect(shield_rect) and not ep["reflected"]:
            ep["dx"] *= -1
            ep["dy"] *= -1
            ep["reflected"] = True

            shield_durability -= 1
            shield_recover_timer = 0

            if shield_durability <= 0:
                shield_durability = 0
                shield_rect = None

    # ------------------ 충돌 ------------------
    dead_enemies = []

    for enemy in enemies:
        enemy_rect = pygame.Rect(int(enemy["x"]), int(enemy["y"]), CELL, CELL)

        # 검 공격
        if attack_rect and attack_rect.colliderect(enemy_rect):
            if id(enemy) not in hit_enemies:
                enemy["hp"] -= SWORD_DAMAGE
                enemy["hit"] = 100
                hit_enemies.add(id(enemy))
                hitstop_timer = HITSTOP_TIME

        # 플레이어 검기
        for proj in projectiles[:]:
            proj_rect = pygame.Rect(
                int(proj["x"]),
                int(proj["y"]),
                PROJECTILE_SIZE,
                PROJECTILE_SIZE
            )

            if proj_rect.colliderect(enemy_rect):
                enemy["hp"] -= PROJECTILE_DAMAGE
                enemy["hit"] = 100
                projectiles.remove(proj)
                hitstop_timer = HITSTOP_TIME

        # 반사된 적 투사체가 적에게 명중
        for ep in enemy_projectiles[:]:
            if not ep["reflected"]:
                continue

            ep_rect = pygame.Rect(
                int(ep["x"]),
                int(ep["y"]),
                ENEMY_PROJECTILE_SIZE,
                ENEMY_PROJECTILE_SIZE
            )

            if ep_rect.colliderect(enemy_rect):
                if enemy["type"] == "strong_shooter":
                    enemy["hp"] = 0
                else:
                    enemy["hp"] -= REFLECTED_PROJECTILE_DAMAGE

                enemy["hit"] = 100

                if ep in enemy_projectiles:
                    enemy_projectiles.remove(ep)

                hitstop_timer = HITSTOP_TIME

        # 적과 플레이어 몸 충돌
        if player_rect.colliderect(enemy_rect):
            if invincible_timer <= 0:
                damage = 2 if enemy["type"] == "strong_dash" and enemy.get("state") == "dash" else 1
                player_hp -= damage
                invincible_timer = invincible_time
                hitstop_timer = HITSTOP_TIME

        if enemy["hp"] <= 0:
            dead_enemies.append(enemy)

    # 적 투사체가 플레이어에게 명중
    for ep in enemy_projectiles[:]:
        if ep["reflected"]:
            continue

        ep_rect = pygame.Rect(
            int(ep["x"]),
            int(ep["y"]),
            ENEMY_PROJECTILE_SIZE,
            ENEMY_PROJECTILE_SIZE
        )

        if player_rect.colliderect(ep_rect):
            enemy_projectiles.remove(ep)

            if invincible_timer <= 0:
                player_hp -= 1
                invincible_timer = invincible_time
                hitstop_timer = HITSTOP_TIME

    # 적 사망 처리
    for enemy in dead_enemies:
        if enemy["type"] in ["strong_dash", "strong_shooter"]:
            if random.random() < ITEM_DROP_CHANCE:
                drop_item(enemy["x"], enemy["y"])

        if enemy in enemies:
            enemies.remove(enemy)

    # 아이템 획득
    for item in items[:]:
        item_rect = pygame.Rect(int(item["x"]), int(item["y"]), CELL, CELL)

        if player_rect.colliderect(item_rect):
            if item["type"] == "heal":
                player_hp = min(MAX_HP, player_hp + 1)

            elif item["type"] == "sword_up":
                SWORD_DAMAGE += 1

            elif item["type"] == "projectile_up":
                PROJECTILE_DAMAGE += 1

            elif item["type"] == "cooldown_down":
                PROJECTILE_COOLDOWN = max(
                    MIN_PROJECTILE_COOLDOWN,
                    PROJECTILE_COOLDOWN - 250
                )

            elif item["type"] == "range_up":
                SWORD_RANGE += 8

            items.remove(item)

    # 게임오버 진입
    if player_hp <= 0:
        player_hp = 0
        game_state = "game_over_effect"
        game_over_timer = GAME_OVER_EFFECT_TIME
        continue

    # ------------------ 그리기 ------------------
    draw_world()

    # 아이템
    for item in items:
        if item["type"] == "heal":
            color = GREEN
            mark = "+"
        elif item["type"] == "sword_up":
            color = YELLOW
            mark = "S"
        elif item["type"] == "projectile_up":
            color = BLUE
            mark = "P"
        elif item["type"] == "cooldown_down":
            color = ORANGE
            mark = "C"
        else:
            color = PURPLE
            mark = "R"

        pygame.draw.rect(
            screen,
            color,
            (
                int(item["x"] - camera_x),
                int(item["y"] - camera_y),
                CELL,
                CELL
            )
        )

        text = font_small.render(mark, True, WHITE)
        screen.blit(
            text,
            (
                int(item["x"] - camera_x + 6),
                int(item["y"] - camera_y + 1)
            )
        )

    # 적
    for enemy in enemies:
        if enemy["type"] == "strong_dash":
            if enemy["state"] == "dash":
                color = PURPLE
            elif enemy["state"] == "charge":
                color = ORANGE
            else:
                color = BLUE
        elif enemy["type"] == "strong_shooter":
            color = CYAN
        else:
            color = YELLOW if enemy["hit"] > 0 else RED

        pygame.draw.rect(
            screen,
            color,
            (
                int(enemy["x"] - camera_x),
                int(enemy["y"] - camera_y),
                CELL,
                CELL
            )
        )

        if enemy["hit"] > 0:
            enemy["hit"] -= dt * 1000

        hp_ratio = enemy["hp"] / enemy["max_hp"]

        pygame.draw.rect(
            screen,
            (60, 60, 60),
            (
                int(enemy["x"] - camera_x),
                int(enemy["y"] - camera_y - 8),
                CELL,
                5
            )
        )

        pygame.draw.rect(
            screen,
            GREEN,
            (
                int(enemy["x"] - camera_x),
                int(enemy["y"] - camera_y - 8),
                int(CELL * hp_ratio),
                5
            )
        )

    # 플레이어 검기
    for proj in projectiles:
        pygame.draw.rect(
            screen,
            BLUE,
            (
                int(proj["x"] - camera_x),
                int(proj["y"] - camera_y),
                PROJECTILE_SIZE,
                PROJECTILE_SIZE
            )
        )

    # 적 투사체
    for ep in enemy_projectiles:
        color = YELLOW if ep["reflected"] else PURPLE

        pygame.draw.rect(
            screen,
            color,
            (
                int(ep["x"] - camera_x),
                int(ep["y"] - camera_y),
                ENEMY_PROJECTILE_SIZE,
                ENEMY_PROJECTILE_SIZE
            )
        )

    # 검 공격 범위
    if attack_rect:
        pygame.draw.rect(
            screen,
            SWORD,
            (
                attack_rect.x - camera_x,
                attack_rect.y - camera_y,
                attack_rect.width,
                attack_rect.height
            )
        )

    # 방패
    if shield_rect:
        pygame.draw.rect(
            screen,
            SHIELD_COLOR,
            (
                shield_rect.x - camera_x,
                shield_rect.y - camera_y,
                shield_rect.width,
                shield_rect.height
            )
        )

    # 플레이어
    player_color = GREEN

    if invincible_timer > 0 and int(invincible_timer / 100) % 2 == 0:
        player_color = WHITE

    pygame.draw.rect(
        screen,
        player_color,
        (
            int(player_x - camera_x),
            int(player_y - camera_y),
            CELL,
            CELL
        )
    )

    # ------------------ UI ------------------
    room_text = font_small.render(
        f"{rooms[current_room_index]['name']}  ({current_room_index + 1}/{len(rooms)})",
        True,
        WHITE
    )
    screen.blit(room_text, (10, 10))

    for i in range(player_hp):
        pygame.draw.rect(screen, RED, (10 + i * 30, 40, 20, 20))

    enemy_text = font_small.render(f"ENEMIES: {len(enemies)}", True, WHITE)
    screen.blit(enemy_text, (10, 70))

    sword_text = font_small.render(f"SWORD ATK: {SWORD_DAMAGE}", True, WHITE)
    screen.blit(sword_text, (10, 100))

    sword_range_text = font_small.render(f"SWORD RANGE: {SWORD_RANGE}", True, WHITE)
    screen.blit(sword_range_text, (10, 130))

    projectile_text = font_small.render(f"PROJECTILE ATK: {PROJECTILE_DAMAGE}", True, WHITE)
    screen.blit(projectile_text, (10, 160))

    cooldown_text = font_small.render(
        f"PROJECTILE COOLDOWN: {PROJECTILE_COOLDOWN / 1000:.2f}s",
        True,
        WHITE
    )
    screen.blit(cooldown_text, (10, 190))

    if room_cleared:
        clear_text = font_small.render("ROOM CLEAR! Go to the door.", True, GREEN)
        screen.blit(clear_text, (10, 220))
    else:
        lock_text = font_small.render("Defeat all enemies to open the door.", True, WHITE)
        screen.blit(lock_text, (10, 220))

    item_info = font_small.render(
        "+ Heal / S Sword / P Projectile / C Cooldown / R Range",
        True,
        WHITE
    )
    screen.blit(item_info, (10, 250))

    control_info = font_small.render(
        "WASD Move / Left Click Attack / Right Click Shield",
        True,
        WHITE
    )
    screen.blit(control_info, (10, 280))

    shield_text = font_small.render(
        f"SHIELD: {shield_durability}/{MAX_SHIELD_DURABILITY}",
        True,
        WHITE
    )
    screen.blit(shield_text, (10, 310))

    pygame.draw.rect(screen, (60, 60, 60), (10, 340, 130, 12))

    if shield_durability >= MAX_SHIELD_DURABILITY:
        pygame.draw.rect(screen, SHIELD_COLOR, (10, 340, 130, 12))
    else:
        recover_ratio = shield_recover_timer / SHIELD_RECOVER_TIME
        recover_ratio = min(1, recover_ratio)

        pygame.draw.rect(
            screen,
            SHIELD_COLOR,
            (
                10,
                340,
                int(130 * recover_ratio),
                12
            )
        )

    pygame.display.flip()