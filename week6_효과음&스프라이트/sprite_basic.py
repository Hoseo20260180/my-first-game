import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Sprite Basics")
clock = pygame.time.Clock()

# ── ① 이미지 로드 ──────────────────────────────
img = pygame.image.load("asset/player.png").convert_alpha()

# ── ② 크기 조절 ────────────────────────────────
img = pygame.transform.scale(img, (96, 96))

# ── ③ Rect로 위치 지정 ─────────────────────────
rect = img.get_rect()
rect.topleft = (0, 0)  # ← 왼쪽 위에서 시작

# ── ④ 회전 ─────────────────────────────────────
img = pygame.transform.rotate(img, 45)
rect = img.get_rect(topleft=rect.topleft)

# ── 이동 속도 설정 ─────────────────────────────
dx = 1   # 오른쪽으로 이동
dy = 1   # 아래로 이동

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # ── 위치 업데이트 (핵심!) ───────────────────
    rect.x += dx
    rect.y += dy

    # ── 화면 밖 → 반대편으로 이동 (wrap) ─────────
    if rect.left > 400:   # 오른쪽 밖으로 나가면
        rect.right = 0    # 왼쪽에서 등장

    if rect.right < 0:    # 왼쪽 밖으로 나가면
        rect.left = 400   # 오른쪽에서 등장

    if rect.top > 300:    # 아래로 나가면
        rect.bottom = 0   # 위에서 등장

    if rect.bottom < 0:   # 위로 나가면
        rect.top = 300    # 아래에서 등장

    screen.fill((30, 30, 40))
    screen.blit(img, rect)
    pygame.display.flip()

pygame.quit()