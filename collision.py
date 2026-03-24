import pygame
import sys
import math

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Collision Demo")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)

# 색상
gray = (150, 150, 150)
red = (255, 0, 0)
blue = (0, 150, 255)
green = (0, 255, 0)
black = (0, 0, 0)

# 이동 오브젝트
player = pygame.Rect(100, 100, 100, 100)
speed = 5

# 회전 오브젝트
rect_size = (150, 150)
center_surface = pygame.Surface(rect_size, pygame.SRCALPHA)
center_surface.fill(gray)

center_pos = (400, 300)
angle = 0

# =======================
# 유틸 함수
# =======================

def normalize(v):
    length = math.hypot(v[0], v[1])
    return (v[0] / length, v[1] / length)

def project(points, axis):
    dots = [p[0]*axis[0] + p[1]*axis[1] for p in points]
    return min(dots), max(dots)

def overlap(a, b):
    return a[0] <= b[1] and b[0] <= a[1]

def get_obb_points(center, size, angle):
    cx, cy = center
    w, h = size[0] / 2, size[1] / 2

    rad = math.radians(angle)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)

    points = [(-w,-h), (w,-h), (w,h), (-w,h)]

    result = []
    for px, py in points:
        rx = px * cos_a - py * sin_a
        ry = px * sin_a + py * cos_a
        result.append((cx + rx, cy + ry))

    return result

def sat_collision(points1, points2):
    axes = []

    for points in [points1, points2]:
        for i in range(4):
            pA = points[i]
            pB = points[(i + 1) % 4]

            edge = (pB[0] - pA[0], pB[1] - pA[1])
            axis = (-edge[1], edge[0])
            axis = normalize(axis)

            axes.append(axis)

    for axis in axes:
        proj1 = project(points1, axis)
        proj2 = project(points2, axis)

        if not overlap(proj1, proj2):
            return False

    return True

# =======================
# 메인 루프
# =======================

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # 이동
    if keys[pygame.K_LEFT]:
        player.x -= speed
    if keys[pygame.K_RIGHT]:
        player.x += speed
    if keys[pygame.K_UP]:
        player.y -= speed
    if keys[pygame.K_DOWN]:
        player.y += speed

    # 회전 속도 (Z 키)
    rotation_speed = 5 if keys[pygame.K_z] else 1
    angle += rotation_speed

    # 회전 적용
    rotated_surface = pygame.transform.rotate(center_surface, angle)
    rotated_rect = rotated_surface.get_rect(center=center_pos)

    # =======================
    # 충돌 계산
    # =======================

    # Circle
    c1 = player.center
    c2 = center_pos
    r1 = player.width // 2
    r2 = rect_size[0] // 2

    dx = c1[0] - c2[0]
    dy = c1[1] - c2[1]
    circle_collision = (dx*dx + dy*dy) <= (r1 + r2) ** 2

    # AABB
    aabb_collision = player.colliderect(rotated_rect)

    # OBB (SAT)
    player_points = get_obb_points(player.center, (player.width, player.height), 0)
    center_points = get_obb_points(center_pos, rect_size, angle)
    obb_collision = sat_collision(player_points, center_points)

    # =======================
    # 배경 (OBB 기준)
    # =======================
    screen.fill(blue if obb_collision else black)

    # =======================
    # 오브젝트 그리기
    # =======================

    # 플레이어
    pygame.draw.rect(screen, gray, player)
    pygame.draw.rect(screen, red, player, 2)

    # 회전 오브젝트
    screen.blit(rotated_surface, rotated_rect)

    # AABB (회전된 bounding)
    pygame.draw.rect(screen, red, rotated_rect, 2)

    # Circle
    pygame.draw.circle(screen, blue, c1, r1, 2)
    pygame.draw.circle(screen, blue, c2, r2, 2)

    # OBB
    points = get_obb_points(center_pos, rect_size, angle)
    pygame.draw.polygon(screen, green, points, 2)

    # =======================
    # 텍스트 출력
    # =======================

    circle_text = font.render(
        f"Circle: {'HIT' if circle_collision else 'MISS'}", True, (255,255,255)
    )
    aabb_text = font.render(
        f"AABB: {'HIT' if aabb_collision else 'MISS'}", True, (255,255,255)
    )
    obb_text = font.render(
        f"OBB: {'HIT' if obb_collision else 'MISS'}", True, (255,255,255)
    )

    screen.blit(circle_text, (10, 10))
    screen.blit(aabb_text, (10, 40))
    screen.blit(obb_text, (10, 70))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()