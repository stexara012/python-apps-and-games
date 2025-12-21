import pygame, sys, random

pygame.init()

# ================= CONFIG =================
WIDTH, HEIGHT = 400, 600
FPS = 60

COLORS = {
    "bg_top": (20, 10, 40),
    "bg_bottom": (5, 5, 20),
    "ball": (255, 255, 255),
    "flipper": (150, 0, 255),
    "glow": (220, 120, 255),
    "bumper": (0, 255, 255),
    "debug": (255, 0, 0)
}

# ================= UTILS =================
def draw_gradient(surface):
    for y in range(HEIGHT):
        r = COLORS["bg_top"][0] + (COLORS["bg_bottom"][0]-COLORS["bg_top"][0]) * y // HEIGHT
        g = COLORS["bg_top"][1] + (COLORS["bg_bottom"][1]-COLORS["bg_top"][1]) * y // HEIGHT
        b = COLORS["bg_top"][2] + (COLORS["bg_bottom"][2]-COLORS["bg_top"][2]) * y // HEIGHT
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

# ================= BALL =================
class Ball:
    def __init__(self, x, y, r=8):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(random.choice([-120, 120]), -160)
        self.r = r

    def update(self, dt):
        self.vel.y += 50 * dt
        self.pos += self.vel * dt

    def draw(self, surface):
        pygame.draw.circle(surface, COLORS["ball"], self.pos, self.r)

    @property
    def rect(self):
        return pygame.Rect(self.pos.x-self.r, self.pos.y-self.r, self.r*2, self.r*2)

# ================= FLIPPER =================
class Flipper:
    def __init__(self, x, y, side):
        self.pivot = pygame.Vector2(x, y)
        self.side = side
        self.length = 140
        self.height = 18

        self.image = pygame.Surface((self.length, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, COLORS["flipper"], (0,0,self.length,self.height), border_radius=8)

        match side:
            case "left":
                self.origin = pygame.Vector2(0, self.height//2)
                self.rest = -30
                self.active = 25
                self.key = pygame.K_LEFT
            case "right":
                self.origin = pygame.Vector2(0, self.height//2)
                self.rest = 30
                self.active = -25
                self.key = pygame.K_RIGHT
            case _:
                raise ValueError("Side must be left/right")

        self.angle = self.rest

    def update(self, keys):
        self.angle = self.active if keys[self.key] else self.rest

    def get_rect(self):
        rotated = pygame.transform.rotate(self.image, self.angle)
        offset = self.origin.rotate(-self.angle)
        return rotated.get_rect(center=self.pivot - offset)

    def draw(self, surface, debug=False):
        rect = self.get_rect()
        rotated = pygame.transform.rotate(self.image, self.angle)

        surface.blit(rotated, rect)

        if debug:
            pygame.draw.rect(surface, COLORS["debug"], rect, 1)

    def collide(self, ball):
        if self.get_rect().colliderect(ball.rect):
            ball.vel.y = -abs(ball.vel.y) - 180
            ball.vel.x += -120 if self.side == "left" else 120

# ================= BUMPER =================
class Bumper:
    def __init__(self, x, y, size=22):
        self.pos = pygame.Vector2(x, y)
        self.size = size

    def draw(self, surface):
        s = self.size // 2
        p = self.pos
        pts = [(p.x,p.y-s),(p.x+s,p.y),(p.x,p.y+s),(p.x-s,p.y)]
        pygame.draw.polygon(surface, COLORS["bumper"], pts)
        pygame.draw.polygon(surface, (255,255,255), pts, 2)

    def collide(self, ball):
        if abs(ball.pos.x-self.pos.x)<self.size and abs(ball.pos.y-self.pos.y)<self.size:
            ball.vel *= -1
            return True
        return False

# ================= TRAP CIRCLE =================
class TrapCircle:
    def __init__(self, x, y, radius=20, trap_time=3.0):
        self.pos = pygame.Vector2(x, y)
        self.radius = radius
        self.trap_time = trap_time
        self.trapped_ball = None
        self.trap_start = 0

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 100, 100), self.pos, self.radius)
        pygame.draw.circle(surface, (255, 255, 255), self.pos, self.radius, 2)

    def update(self, ball, current_time):
        if self.trapped_ball is None:
            # Check if ball entered trap
            if (ball.pos - self.pos).length() <= self.radius:
                self.trapped_ball = ball
                self.trap_start = current_time
                ball.vel = pygame.Vector2(0,0)
        else:
            # Release ball after trap_time
            if current_time - self.trap_start >= self.trap_time:
                self.trapped_ball.vel = pygame.Vector2(random.choice([-150,150]), -200)
                self.trapped_ball = None

# ================= GAME =================
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Neon Pinball – Clean Edition")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 26)
        self.debug = False
        self.reset()

    def reset(self):
        self.ball = Ball(WIDTH//2, 120)
        self.flippers = [
            Flipper(85, HEIGHT-60, "left"),
            Flipper(WIDTH-85, HEIGHT-60, "right")
        ]
        self.bumpers = [
            Bumper(100,160),
            Bumper(300,260),
            Bumper(200,460)
        ]
        # Trap circles
        self.traps = [
            TrapCircle(200, 300, 20, 3.0),
            TrapCircle(150, 200, 15, 3.0)
        ]
        self.score = 0
        self.lives = 3

    def run(self):
        while True:
            dt = self.clock.tick(FPS)/1000
            keys = pygame.key.get_pressed()
            current_time = pygame.time.get_ticks() / 1000

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_h:
                    self.debug = not self.debug

            self.ball.update(dt)

            for f in self.flippers:
                f.update(keys)
                f.collide(self.ball)

            for b in self.bumpers:
                if b.collide(self.ball):
                    self.score += 10

            # Update trap circles
            for trap in self.traps:
                trap.update(self.ball, current_time)

            self.handle_walls()

            draw_gradient(self.screen)

            for b in self.bumpers:
                b.draw(self.screen)

            for f in self.flippers:
                f.draw(self.screen, self.debug)

            # Draw trap circles
            for trap in self.traps:
                trap.draw(self.screen)

            self.ball.draw(self.screen)
            self.draw_ui()
            pygame.display.flip()

    def handle_walls(self):
        if self.ball.pos.x < 20 or self.ball.pos.x > WIDTH-20:
            self.ball.vel.x *= -0.6
        if self.ball.pos.y < 20:
            self.ball.vel.y *= -0.9
        if self.ball.pos.y > HEIGHT:
            self.lives -= 1
            self.ball = Ball(WIDTH//2, 120)
            if self.lives <= 0:
                self.reset()

    def draw_ui(self):
        txt = self.font.render(f"Score: {self.score}   Lives: {self.lives}", True, (255,255,255))
        self.screen.blit(txt, (10,10))

# ================= START =================
Game().run()
