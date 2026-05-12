import pygame
import random
import sys, os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(__file__)
    return os.path.join(base, relative_path)

pygame.init()
pygame.mixer.init()

# ------------------ 설정 ------------------
CELL = 30
GRID_WIDTH = 40
GRID_HEIGHT = 33

WIDTH = CELL * GRID_WIDTH
HEIGHT = CELL * GRID_HEIGHT

BASE_SPEED = 10
MAX_SPEED = 18

ITEM_SCALE = int(CELL * 1.6)
SPEED_UP_TIME = 4000
MARGIN = 1

SLOW_DURATION = 5000
SLOW_FACTOR = 0.45

WIN_LENGTH = 25

# ------------------ 화면 ------------------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GROW SNAKE GROW")
clock = pygame.time.Clock()

# ------------------ 배경 ------------------
background_img = pygame.image.load(resource_path("asset\grass_background.jpg")).convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

# ------------------ 사운드 ------------------
eat_sound = pygame.mixer.Sound(resource_path("asset\eating_apple.mp3"))
slowdown_sound = pygame.mixer.Sound(resource_path("asset\slowdown.mp3"))

bgm = pygame.mixer.Sound(resource_path("asset\\retro_arcade_bgm_music.mp3"))
bgm.set_volume(0.2)

# ------------------ 이미지 ------------------
def load_img(path):
    return pygame.transform.scale(
        pygame.image.load(path).convert_alpha(),
        (ITEM_SCALE, ITEM_SCALE)
    )

apple_img = load_img(resource_path("asset\\apple.png"))
poison_img = load_img(resource_path("asset\poison_apple.png"))
slow_img = load_img(resource_path("asset\snail_time.png"))

# ------------------ 색상 ------------------
WHITE = (255,255,255)
BLACK = (0,0,0)
GREEN = (0,150,0)
HEAD = (0,255,0)
GRAY = (40,40,40)

# ------------------ 폰트 ------------------
font = pygame.font.SysFont("malgungothic", 28)
big_font = pygame.font.SysFont("malgungothic", 60)

# ------------------ 격자 ------------------
def grid():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    for x in range(0, WIDTH, CELL):
        pygame.draw.line(overlay,(255,255,255,60),(x,0),(x,HEIGHT),2)

    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(overlay,(255,255,255,60),(0,y),(WIDTH,y),2)

    pygame.draw.rect(overlay,(255,255,255,140),(0,0,WIDTH,HEIGHT),3)
    screen.blit(overlay,(0,0))

# ------------------ 아이템 ------------------
def draw_item(img,pos):
    offset=(ITEM_SCALE-CELL)//2
    screen.blit(img,(pos[0]-offset,pos[1]-offset))

# ------------------ 위치 ------------------
def safe_pos(snake,food,poisons,slow_items):
    while True:
        p=(random.randrange(MARGIN,GRID_WIDTH-MARGIN)*CELL,
           random.randrange(MARGIN,GRID_HEIGHT-MARGIN)*CELL)
        if p not in snake and p!=food and p not in poisons and p not in slow_items:
            return p

def respawn_items(snake):
    food=safe_pos(snake,None,[],[])
    poisons=[safe_pos(snake,food,[],[])]
    slow_items=[safe_pos(snake,food,poisons,[])]
    return food,poisons,slow_items

def spawn_poison(snake,food,poisons,slow_items,max_p):
    while len(poisons)<max_p:
        poisons.append(safe_pos(snake,food,poisons,slow_items))

# ------------------ 뱀 ------------------
def draw_head(pos,d):
    x,y=pos
    pygame.draw.rect(screen,HEAD,(x,y,CELL,CELL),border_radius=6)

    if d==(CELL,0): eyes=[(x+22,y+8),(x+22,y+22)]
    elif d==(-CELL,0): eyes=[(x+8,y+8),(x+8,y+22)]
    elif d==(0,-CELL): eyes=[(x+8,y+8),(x+22,y+8)]
    else: eyes=[(x+8,y+22),(x+22,y+22)]

    for ex,ey in eyes:
        pygame.draw.circle(screen,BLACK,(ex,ey),4)

def draw_snake(snake,d):
    for i,s in enumerate(snake):
        if i==0:
            draw_head(s,d)
        else:
            pygame.draw.rect(screen,GREEN,(*s,CELL,CELL))
            pygame.draw.rect(screen,BLACK,(*s,CELL,CELL),1)

# ------------------ HUD ------------------
def draw_hud(score,speed,elapsed):
    m=elapsed//60
    s=elapsed%60
    screen.blit(font.render(f"Score:{score}",True,WHITE),(10,10))
    screen.blit(font.render(f"Speed:{speed}",True,WHITE),(10,40))
    screen.blit(font.render(f"Time:{m:02}:{s:02}",True,WHITE),(10,70))

# ------------------ WIN ------------------
def win_screen(score):
    victory_music = pygame.mixer.Sound(resource_path("asset\retro_arcade_victory_music.mp3"))
    victory_music.play(-1)
    victory_music.set_volume(0.1)

    while True:
        screen.fill((20,20,40))

        screen.blit(big_font.render("게임 승리!",True,WHITE),(WIDTH//2-160,200))
        screen.blit(font.render(f"점수:{score}",True,WHITE),(WIDTH//2-80,300))
        screen.blit(font.render("CLICK TO MENU",True,WHITE),(WIDTH//2-160,420))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                victory_music.stop()
                pygame.quit()
                sys.exit()

            if e.type==pygame.MOUSEBUTTONDOWN:
                victory_music.stop()
                return

# ------------------ GAME OVER ------------------
def game_over_screen(score):
    bgm.stop()

    over_music = pygame.mixer.Sound(resource_path("asset\game_over.mp3"))
    over_music.play(-1)

    while True:
        screen.fill(GRAY)
        screen.blit(big_font.render("게임 오버",True,(220,50,50)),(WIDTH//2-200,250))
        screen.blit(font.render(f"Score:{score}",True,WHITE),(WIDTH//2-80,350))
        screen.blit(font.render("CLICK TO RESTART",True,WHITE),(WIDTH//2-140,450))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                over_music.stop()
                pygame.quit()
                sys.exit()

            if e.type==pygame.MOUSEBUTTONDOWN:
                over_music.stop()
                return

# ------------------ START ------------------
def start_screen():
    start_btn=pygame.Rect(WIDTH//2-160,HEIGHT//2,140,70)
    info_btn=pygame.Rect(WIDTH//2+20,HEIGHT//2,140,70)

    pygame.event.clear()

    while True:
        screen.fill(GRAY)
        screen.blit(big_font.render("Grow Snake Grow",True,WHITE),(WIDTH//2-200,250))

        pygame.draw.rect(screen,(0,200,0),start_btn,border_radius=10)
        pygame.draw.rect(screen,(0,120,255),info_btn,border_radius=10)

        screen.blit(font.render("START",True,WHITE),(start_btn.x+25,start_btn.y+20))
        screen.blit(font.render("INFO",True,WHITE),(info_btn.x+40,info_btn.y+20))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit();sys.exit()

            if e.type==pygame.MOUSEBUTTONDOWN:
                if start_btn.collidepoint(e.pos): return
                if info_btn.collidepoint(e.pos): info_screen()

# ------------------ INFO ------------------
def info_screen():
    pygame.event.clear()

    while True:
        screen.fill(GRAY)
        screen.blit(big_font.render("INFO",True,WHITE),(WIDTH//2-80,120))

        items=[
            (apple_img," +10점, 길이 증가"),
            (poison_img,"-5점, 길이 증가"),
            (slow_img,"잠깐동안 게임 속도 감소")
        ]

        y=220
        for img,text in items:
            screen.blit(img,(WIDTH//2-220,y))
            screen.blit(font.render(text,True,WHITE),(WIDTH//2-120,y+10))
            y+=120

        screen.blit(font.render("WIN:점수 0 이상 유지 ,뱀 길이 25칸",True,WHITE),(WIDTH//2-160,y+40))
        screen.blit(font.render("CLICK TO BACK",True,WHITE),(WIDTH//2-120,y+100))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit();sys.exit()
            if e.type==pygame.MOUSEBUTTONDOWN:
                pygame.event.clear()
                return

# ------------------ GAME ------------------
def main():
    bgm.play(-1)

    snake=[((GRID_WIDTH//2)*CELL,(GRID_HEIGHT//2)*CELL)]
    d=(CELL,0)
    speed=BASE_SPEED

    score=15

    start_time=pygame.time.get_ticks()
    last_speed=start_time

    food,poisons,slow_items=respawn_items(snake)
    slow_end=0

    while True:
        now=pygame.time.get_ticks()
        elapsed=(now-start_time)//1000

        if now-last_speed>SPEED_UP_TIME:
            speed=min(MAX_SPEED,speed+1)
            last_speed=now

        for e in pygame.event.get():
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_UP and d!=(0,CELL): d=(0,-CELL)
                if e.key==pygame.K_DOWN and d!=(0,-CELL): d=(0,CELL)
                if e.key==pygame.K_LEFT and d!=(CELL,0): d=(-CELL,0)
                if e.key==pygame.K_RIGHT and d!=(-CELL,0): d=(CELL,0)

                if e.key==pygame.K_F5:
                    snake.append(snake[-1])

        head=(snake[0][0]+d[0],snake[0][1]+d[1])

        if head in snake or head[0]<0 or head[1]<0 or head[0]>=WIDTH or head[1]>=HEIGHT:
            game_over_screen(score)
            return

        snake.insert(0,head)
        ate=False

        if head==food:
            eat_sound.play()
            score+=10
            food,poisons,slow_items=respawn_items(snake)
            ate=True

        max_p=1+(len(snake)//3)
        spawn_poison(snake,food,poisons,slow_items,max_p)

        for p in poisons[:]:
            if head==p:
                eat_sound.play()
                score-=5
                poisons.remove(p)
                spawn_poison(snake,food,poisons,slow_items,max_p)
                ate=True

                if score<0:
                    game_over_screen(score)
                    return

        if head in slow_items and now>slow_end:
            slowdown_sound.play()
            slow_end=now+SLOW_DURATION
            food,poisons,slow_items=respawn_items(snake)

        current_speed=int(speed*SLOW_FACTOR) if now<slow_end else speed
        clock.tick(current_speed)

        if len(snake)>=WIN_LENGTH:
            bgm.stop()
            win_screen(score)
            return

        if not ate:
            snake.pop()

        screen.blit(background_img,(0,0))
        grid()

        draw_item(apple_img,food)
        for p in poisons:
            draw_item(poison_img,p)
        for s in slow_items:
            draw_item(slow_img,s)

        draw_snake(snake,d)
        draw_hud(score,current_speed,elapsed)

        pygame.display.flip()

# ------------------ RUN ------------------
while True:
    start_screen()
    main()