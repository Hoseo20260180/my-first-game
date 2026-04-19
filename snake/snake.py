import pygame
import random
import sys

pygame.init()

# ------------------ 설정 ------------------
CELL = 30
GRID_WIDTH = 40
GRID_HEIGHT = 33

WIDTH = CELL * GRID_WIDTH
HEIGHT = CELL * GRID_HEIGHT

BASE_SPEED = 10
WIN_LENGTH = 25

POISON_COUNT = 3
SPEED_COUNT = 2
SLOW_COUNT = 2

# ------------------ 화면 ------------------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()

# ------------------ 이미지 (투명 처리) ------------------
apple_img = pygame.image.load("asset/apple.png").convert_alpha()
apple_img = pygame.transform.scale(apple_img, (CELL, CELL))

poison_img = pygame.image.load("asset/poison_apple.png").convert_alpha()
poison_img = pygame.transform.scale(poison_img, (CELL, CELL))

fast_img = pygame.image.load("asset/fast_time.png").convert_alpha()
fast_img = pygame.transform.scale(fast_img, (CELL, CELL))

slow_img = pygame.image.load("asset/snail_time.png").convert_alpha()
slow_img = pygame.transform.scale(slow_img, (CELL, CELL))

hole_img = pygame.image.load("asset/Hole.png").convert_alpha()

# ------------------ 색상 ------------------
WHITE = (255,255,255)
BLACK = (0,0,0)
GREEN = (50,200,50)
DARK = (30,150,30)
RED = (220,50,50)
GRAY = (40,40,40)
GRID = (70,70,70)
YELLOW = (240,220,70)

# ------------------ 폰트 ------------------
def font(size):
    for n in ["malgungothic","applegothic","nanumgothic","notosanscjk"]:
        f = pygame.font.SysFont(n,size)
        if f.get_ascent()>0:
            return f
    return pygame.font.SysFont(None,size)

F = font(30)
FB = font(64)

# ------------------ 유틸 ------------------
def rand_pos():
    return (
        random.randint(0,GRID_WIDTH-1)*CELL,
        random.randint(0,GRID_HEIGHT-1)*CELL
    )

def near_player(pos,snake):
    h=snake[0]
    for dx in range(-2,3):
        for dy in range(-2,3):
            if pos==(h[0]+dx*CELL,h[1]+dy*CELL):
                return True
    return False

def occupied(snake,food,poisons,speed_items,slow_items):
    occ=set()
    occ.add(food)
    occ.update(poisons)
    occ.update(speed_items)
    occ.update(slow_items)
    occ.update(snake)
    return occ

def new_items(n,snake,occ):
    arr=[]
    while len(arr)<n:
        p=rand_pos()
        if p not in snake and p not in occ:
            arr.append(p)
    return arr

# ------------------ 구멍 ------------------
def create_hole(snake,food,poisons,speed_items,slow_items):
    occ=occupied(snake,food,poisons,speed_items,slow_items)

    while True:
        h=random.randint(2,4)*CELL
        w=random.randint(max(3,h//CELL+1),7)*CELL

        x=random.randint(1,GRID_WIDTH-w//CELL-1)*CELL
        y=random.randint(2,GRID_HEIGHT-3)*CELL

        hole=pygame.Rect(x,y,w,h)

        if near_player((x,y),snake):
            continue

        if any(hole.collidepoint(p) for p in occ):
            continue

        return hole

# ------------------ UI ------------------
def draw_speed(speed):
    x,y=10,50
    w,h=200,15

    r=(speed-5)/(20-5)
    r=max(0,min(1,r))

    pygame.draw.rect(screen,(60,60,60),(x,y,w,h))
    pygame.draw.rect(screen,(0,200,0),(x,y,w*r,h))
    pygame.draw.rect(screen,WHITE,(x,y,w,h),2)

    screen.blit(F.render(f"Speed:{speed}",True,WHITE),(x,y-25))

def center_text(text,font,color,rect):
    img=font.render(text,True,color)
    screen.blit(img,
                (rect.centerx-img.get_width()//2,
                 rect.centery-img.get_height()//2))

# ------------------ 그리기 ------------------
def grid():
    for x in range(0,WIDTH,CELL):
        pygame.draw.line(screen,GRID,(x,0),(x,HEIGHT))
    for y in range(0,HEIGHT,CELL):
        pygame.draw.line(screen,GRID,(0,y),(WIDTH,y))

def draw_snake(snake):
    for i,s in enumerate(snake):
        c=DARK if i==0 else GREEN
        pygame.draw.rect(screen,c,(*s,CELL,CELL))
        pygame.draw.rect(screen,BLACK,(*s,CELL,CELL),1)

# ------------------ START ------------------
def start_screen():
    start_btn=pygame.Rect(WIDTH//2-150,HEIGHT//2,300,80)
    info_btn=pygame.Rect(WIDTH//2-150,HEIGHT//2+120,300,80)

    while True:
        screen.fill(GRAY)

        screen.blit(FB.render("SNAKE GAME",True,WHITE),
                    (WIDTH//2-200,200))

        mouse=pygame.mouse.get_pos()

        pygame.draw.rect(screen,
                         GREEN if start_btn.collidepoint(mouse) else (80,220,80),
                         start_btn)

        pygame.draw.rect(screen,
                         WHITE if info_btn.collidepoint(mouse) else (200,200,200),
                         info_btn)

        center_text("START",F,BLACK,start_btn)
        center_text("INFO",F,BLACK,info_btn)

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type==pygame.MOUSEBUTTONDOWN:
                if start_btn.collidepoint(e.pos):
                    return
                if info_btn.collidepoint(e.pos):
                    info_screen()
            if e.type==pygame.QUIT:
                pygame.quit();sys.exit()

# ------------------ INFO (아이템 설명 포함) ------------------
def info_screen():
    while True:
        screen.fill(GRAY)

        screen.blit(FB.render("INFO",True,WHITE),(WIDTH//2-80,80))

        y=180

        screen.blit(apple_img,(WIDTH//2-220,y))
        screen.blit(F.render("+10점 / 길이 증가",True,WHITE),(WIDTH//2-140,y+5))
        y+=70

        screen.blit(poison_img,(WIDTH//2-220,y))
        screen.blit(F.render("-5점 / 길이 증가",True,WHITE),(WIDTH//2-140,y+5))
        y+=70

        screen.blit(fast_img,(WIDTH//2-220,y))
        screen.blit(F.render("속도 증가",True,WHITE),(WIDTH//2-140,y+5))
        y+=70

        screen.blit(slow_img,(WIDTH//2-220,y))
        screen.blit(F.render("속도 감소",True,WHITE),(WIDTH//2-140,y+5))
        y+=70

        screen.blit(pygame.transform.scale(hole_img,(40,40)),(WIDTH//2-220,y))
        screen.blit(F.render("구멍 = GAME OVER",True,WHITE),(WIDTH//2-140,y+5))
        y+=80

        screen.blit(F.render("뱀 길이 25칸= 승리",True,YELLOW),(WIDTH//2-180,y))
        screen.blit(F.render("ESC로 돌아가기",True,WHITE),(WIDTH//2-140,HEIGHT-80))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE:
                return
            if e.type==pygame.QUIT:
                pygame.quit();sys.exit()

# ------------------ GAME OVER ------------------
def game_over_screen(score):
    while True:
        screen.fill(GRAY)

        screen.blit(FB.render("GAME OVER",True,RED),
                    (WIDTH//2-200,200))

        screen.blit(F.render(f"Score: {score}",True,WHITE),
                    (WIDTH//2-100,350))

        screen.blit(F.render("CLICK TO RESTART",True,WHITE),
                    (WIDTH//2-150,450))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type==pygame.MOUSEBUTTONDOWN:
                return
            if e.type==pygame.QUIT:
                pygame.quit();sys.exit()

# ------------------ WIN ------------------
def win_screen(score):
    while True:
        screen.fill(GRAY)

        screen.blit(FB.render("YOU WIN!",True,YELLOW),
                    (WIDTH//2-160,200))

        screen.blit(F.render(f"Score: {score}",True,WHITE),
                    (WIDTH//2-100,350))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type==pygame.MOUSEBUTTONDOWN:
                return

# ------------------ GAME ------------------
def main():
    snake=[(GRID_WIDTH//2*CELL,GRID_HEIGHT//2*CELL)]
    d=(CELL,0)

    speed=BASE_SPEED
    score=0

    food=rand_pos()
    poisons=new_items(POISON_COUNT,snake,[food])
    speed_items=new_items(SPEED_COUNT,snake,[food])
    slow_items=new_items(SLOW_COUNT,snake,[food])

    hole=create_hole(snake,food,poisons,speed_items,slow_items)
    hole_timer=15

    while True:
        dt=clock.tick(speed)/1000
        hole_timer-=dt

        if hole_timer<=0:
            hole=create_hole(snake,food,poisons,speed_items,slow_items)
            hole_timer=15

        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit();sys.exit()
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_UP and d!=(0,CELL):d=(0,-CELL)
                if e.key==pygame.K_DOWN and d!=(0,-CELL):d=(0,CELL)
                if e.key==pygame.K_LEFT and d!=(CELL,0):d=(-CELL,0)
                if e.key==pygame.K_RIGHT and d!=(-CELL,0):d=(CELL,0)

        head=(snake[0][0]+d[0],snake[0][1]+d[1])

        # 충돌
        if head[0]<0 or head[0]>=WIDTH or head[1]<0 or head[1]>=HEIGHT:
            game_over_screen(score);return

        if hole.collidepoint(head):
            game_over_screen(score);return

        if head in snake:
            game_over_screen(score);return

        snake.insert(0,head)

        ate=False

        if head==food:
            score+=10
            food=rand_pos()
            ate=True

        if head in poisons:
            score=max(0,score-5)
            poisons.remove(head)
            poisons+=new_items(1,snake,[food])
            ate=True

        if head in speed_items:
            speed+=2
            speed_items.remove(head)
            speed_items+=new_items(1,snake,[food])
            ate=True

        if head in slow_items:
            speed=max(3,speed-2)
            slow_items.remove(head)
            slow_items+=new_items(1,snake,[food])
            ate=True

        if not ate:
            snake.pop()

        if len(snake)>=WIN_LENGTH:
            win_screen(score);return

        # DRAW
        screen.fill(GRAY)
        grid()

        screen.blit(apple_img,food)
        for p in poisons:screen.blit(poison_img,p)
        for s in speed_items:screen.blit(fast_img,s)
        for s in slow_items:screen.blit(slow_img,s)

        screen.blit(pygame.transform.scale(hole_img,(hole.width,hole.height)),
                    (hole.x,hole.y))

        draw_snake(snake)

        screen.blit(F.render(f"Score:{score}",True,WHITE),(10,10))
        draw_speed(speed)

        pygame.display.flip()

# ------------------ RUN ------------------
while True:
    start_screen()
    main()