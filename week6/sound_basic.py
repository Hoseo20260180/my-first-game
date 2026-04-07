import pygame

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Sound Basics")
clock = pygame.time.Clock()

# ── ① 효과음 로드 ──────────────────────────────
shoot_sound = pygame.mixer.Sound("asset/shoot.wav")

# ── ② 배경음악 로드 ────────────────────────────
pygame.mixer.music.load("asset/bgm.ogg")

# ── ③ 볼륨 조절 ────────────────────────────────
shoot_sound.set_volume(0.5)        # 0.0 ~ 1.0
pygame.mixer.music.set_volume(0.3)

# ── ④ 배경음악 재생 ────────────────────────────
pygame.mixer.music.play(-1,fade_ms=3000)  # -1: 무한 반복

running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    # ── 마우스 클릭으로 효과음 재생 ──
        if event.type == pygame.MOUSEBUTTONDOWN:  # 마우스 클릭 감지
            shoot_sound.stop()  # 재생 중이면 중지
            shoot_sound.play()  # 처음부터 재생

    screen.fill((30, 30, 40))
    pygame.display.flip()

pygame.quit()
