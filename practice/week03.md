3주차 Hello_pygame에 대한 AI 대화

목적:pygame으로 게임 제작. Hello_pygame을 기반으로 새 게임 제작.

입력<<Hello_pygame.py의 각 줄에 대한 설명을 원해.

AI>> 창을 띄우고 파란 원을 화면 가운데 띄우는 프로그램.

게임 실행을 위한 기초 세팅==============================
pygame.init() → Pygame 초기화
screen = pygame.display.set_mode((폭, 높이)) → 게임 창 생성
pygame.display.set_caption() → 창 제목 설정
pygame.time.Clock() → FPS 제어용 시계
while running: → 게임 루프
pygame.event.get() → 입력 이벤트 확인
pygame.display.flip() → 화면 업데이트 

원 그리기====================================
pygame.draw.circle(screen, 색, (x, y), 반지름) → 원 그리기

코드 수정을 통해 
screen.fill()의 색이 배경색을 정하며 기본값은 검정이란 것을 알게 됨.
clock.tick()가 FPS이 된다는 것을 암.

입력<<pygame 실행할 때 FPS가 출력되도록 해줘

fps = clock.get_fps() → FPS 값 받아오기

fps_text = font.render(f"FPS: {fps:.2f}", True, BLACK)
screen.blit(fps_text, (10, 10)) → FPS 값을 화면 좌측 상단에 출력함.

AI>>코드를 추가해줌.

입력<<방향키를 누르면 원의 위치가 그 방향으로 이동하는 기능을 추가해줘

keys = pygame.key.get_pressed() → 키보드 입력을 인식함.

  if keys[pygame.K_LEFT]:
      x -= speed
  if keys[pygame.K_RIGHT]:
      x += speed
  if keys[pygame.K_UP]:
      y -= speed
  if keys[pygame.K_DOWN]:
      y += speed
AI>>각 방향키가 눌렸을때 좌표 값을 이동시키는 코드를 추가시킴.

AI<<도형이 화면 밖으로 나가지 못하도록 경계처리를 해줘

if x < radius:
    x = radius
if x > 1200 - radius:
    x = 1200 - radius
if y < radius:
    y = radius
if y > 800 - radius:
    y = 800 - radius


