import pygame
import random
import math

# ---------------- SETTINGS ----------------
WIDTH, HEIGHT = 900, 600
FPS = 60
GRAVITY = 0.08
PARTICLES_PER_CLICK = 10

# ------------------------------------------

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("✨ Fancy Particle Playground")
clock = pygame.time.Clock()

particles = []


class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        angle = random.uniform(0, math.tau)
        speed = random.uniform(2, 6)

        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.life = random.randint(50, 90)
        self.max_life = self.life

        self.size = random.randint(4, 7)

        self.color = pygame.Color(
            random.randint(150, 255),
            random.randint(120, 255),
            random.randint(150, 255)
        )

    def update(self):
        self.x += self.vx
        self.y += self.vy

        self.vy += GRAVITY
        self.life -= 1

    def draw(self, surface):
        if self.life <= 0:
            return

        alpha = int(255 * (self.life / self.max_life))

        glow_surface = pygame.Surface((self.size*4, self.size*4), pygame.SRCALPHA)
        color = (*self.color[:3], alpha)

        pygame.draw.circle(
            glow_surface,
            color,
            (self.size*2, self.size*2),
            self.size
        )

        surface.blit(
            glow_surface,
            (self.x - self.size*2, self.y - self.size*2)
        )

    def alive(self):
        return self.life > 0


def draw_background(surface, t):
    for y in range(HEIGHT):
        wave = math.sin(y * 0.01 + t)
        c = int(50 + 40 * wave)

        color = (10, c, 80 + c // 2)
        pygame.draw.line(surface, color, (0, y), (WIDTH, y))


def spawn_particles(x, y):
    for _ in range(PARTICLES_PER_CLICK):
        particles.append(Particle(x, y))


def update_particles():
    for p in particles:
        p.update()

    particles[:] = [p for p in particles if p.alive()]


def draw_particles(surface):
    for p in particles:
        p.draw(surface)


def main():
    running = True
    time = 0

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        if mouse_buttons[0]:
            spawn_particles(*mouse_pos)

        time += 0.03

        draw_background(screen, time)

        update_particles()
        draw_particles(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()