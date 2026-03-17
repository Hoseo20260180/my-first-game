import pygame
import sys

pygame.init()

screen = pygame.display.set_mode((1200, 800))
pygame.display.set_caption("FPS Example")

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 30)  # FPS 출력용 글꼴

#원의 좌표
x = 600
y = 400
speed = 5
# 반지름
radius= 75 

running = True

while running: #실행 중이라면.
    for event in pygame.event.get():
        if event.type == pygame.QUIT: #창 닫기.
            running = False #반복문 종료.

    #키 입력 인식.
    keys = pygame.key.get_pressed()

    #방향키를 누르면 해당 방향에 따른 X,Y 좌표값이 증감함.
    if keys[pygame.K_LEFT]:
        x -= speed
    if keys[pygame.K_RIGHT]:
        x += speed
    if keys[pygame.K_UP]:
        y -= speed
    if keys[pygame.K_DOWN]:
        y += speed

    #원이 테두리를 넘지 못함.
    if x < radius:
        x = radius
    if x > 1200 - radius:
        x = 1200 - radius
    if y < radius:
        y = radius
    if y > 800 - radius:
        y = 800 - radius

    screen.fill((50,50,50))# RGB 배경색. # 기본은 검정.

    pygame.draw.circle(screen, (255,0,0), (x, y), radius)
    #pygame.draw.circle(screen, 색깔, (X좌표, Y좌표), 원크기)

    # FPS 계산
    fps = clock.get_fps()
    fps_text = font.render(f"FPS: {fps:.2f}", True, BLACK)
    # FPS를 화면에 출력함.
    screen.blit(fps_text, (10, 10))

    pygame.display.flip()# 화면 업데이트 기능. 없다면 화면이 갱신되지 않음.
    clock.tick(60) # FPS: Frame per Second. 초당 프레임수

pygame.quit()
sys.exit()