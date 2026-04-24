"""
=========================================================
  RACER GAME — Practice 10, Task 1
  Controls: LEFT / RIGHT arrow keys to move the car
  Avoid enemy cars, collect coins!
=========================================================
"""

import pygame
import random
import sys

# ── Initialise pygame ─────────────────────────────────
pygame.init()

# ── Window / display settings ─────────────────────────
SCREEN_W, SCREEN_H = 500, 700
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Racer")

clock = pygame.time.Clock()
FPS   = 60

# ── Colours ───────────────────────────────────────────
WHITE  = (255, 255, 255)
BLACK  = (  0,   0,   0)
GRAY   = (100, 100, 100)
DKGRAY = ( 50,  50,  50)
RED    = (220,  30,  30)
BLUE   = ( 30,  30, 220)
YELLOW = (255, 215,   0)
GREEN  = ( 0,  200,  50)

# ── Road geometry ─────────────────────────────────────
ROAD_LEFT  = 80          # left edge of road
ROAD_RIGHT = 420         # right edge of road
ROAD_W     = ROAD_RIGHT - ROAD_LEFT
LANE_W     = ROAD_W // 3 # three lanes

# ── Fonts ─────────────────────────────────────────────
font_big   = pygame.font.SysFont("Arial", 32, bold=True)
font_small = pygame.font.SysFont("Arial", 22)


# ══════════════════════════════════════════════════════
#  HELPER — draw a simple car rectangle with windows
# ══════════════════════════════════════════════════════
def draw_car(surface, rect, color):
    """Draw a stylised car shape inside *rect* using *color*."""
    pygame.draw.rect(surface, color, rect, border_radius=6)
    # windshield (top)
    w_rect = pygame.Rect(rect.x + 8, rect.y + 6, rect.width - 16, rect.height // 4)
    pygame.draw.rect(surface, (180, 230, 255), w_rect, border_radius=3)
    # rear window (bottom)
    r_rect = pygame.Rect(rect.x + 8, rect.bottom - rect.height // 4 - 6,
                         rect.width - 16, rect.height // 4)
    pygame.draw.rect(surface, (180, 230, 255), r_rect, border_radius=3)


# ══════════════════════════════════════════════════════
#  CLASS — Player car
# ══════════════════════════════════════════════════════
class PlayerCar:
    WIDTH  = 50
    HEIGHT = 80
    SPEED  = 6  # pixels per frame when moving sideways

    def __init__(self):
        # Start in the middle lane, near the bottom
        self.rect = pygame.Rect(
            ROAD_LEFT + LANE_W + (LANE_W - self.WIDTH) // 2,
            SCREEN_H - self.HEIGHT - 30,
            self.WIDTH, self.HEIGHT
        )

    def move(self, keys):
        """Slide left/right; clamp to road boundaries."""
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.SPEED

        # Don't leave the road
        self.rect.x = max(ROAD_LEFT, min(self.rect.x, ROAD_RIGHT - self.WIDTH))

    def draw(self, surface):
        draw_car(surface, self.rect, BLUE)


# ══════════════════════════════════════════════════════
#  CLASS — Enemy car (falls from top)
# ══════════════════════════════════════════════════════
class EnemyCar:
    WIDTH  = 50
    HEIGHT = 80

    def __init__(self, speed):
        # Pick a random lane
        lane = random.randint(0, 2)
        x = ROAD_LEFT + lane * LANE_W + (LANE_W - self.WIDTH) // 2
        self.rect  = pygame.Rect(x, -self.HEIGHT, self.WIDTH, self.HEIGHT)
        self.speed = speed
        self.color = random.choice([(220, 50, 50), (50, 180, 50), (200, 100, 20)])

    def update(self):
        """Move downward each frame."""
        self.rect.y += self.speed

    def is_off_screen(self):
        return self.rect.top > SCREEN_H

    def draw(self, surface):
        draw_car(surface, self.rect, self.color)


# ══════════════════════════════════════════════════════
#  CLASS — Coin (appears randomly on the road)
# ══════════════════════════════════════════════════════
class Coin:
    RADIUS = 12

    def __init__(self, speed):
        # Random x within road, start above screen
        x = random.randint(ROAD_LEFT + self.RADIUS, ROAD_RIGHT - self.RADIUS)
        self.rect  = pygame.Rect(x - self.RADIUS, -self.RADIUS * 2,
                                 self.RADIUS * 2, self.RADIUS * 2)
        self.speed = speed

    def update(self):
        """Move downward each frame."""
        self.rect.y += self.speed

    def is_off_screen(self):
        return self.rect.top > SCREEN_H

    def draw(self, surface):
        # Gold coin circle with a star-like inner mark
        cx, cy = self.rect.centerx, self.rect.centery
        pygame.draw.circle(surface, YELLOW, (cx, cy), self.RADIUS)
        pygame.draw.circle(surface, (200, 160, 0), (cx, cy), self.RADIUS, 2)
        # small "$" symbol in the centre
        lbl = font_small.render("$", True, (150, 100, 0))
        surface.blit(lbl, lbl.get_rect(center=(cx, cy)))


# ══════════════════════════════════════════════════════
#  ROAD DRAWING
# ══════════════════════════════════════════════════════
class Road:
    STRIPE_H   = 60   # height of each dashed stripe
    STRIPE_GAP = 40   # gap between stripes
    STRIPE_W   = 8    # width of lane divider

    def __init__(self):
        self.offset = 0   # scrolling offset

    def update(self, speed):
        """Advance the road scroll by *speed* pixels."""
        self.offset = (self.offset + speed) % (self.STRIPE_H + self.STRIPE_GAP)

    def draw(self, surface):
        # Road background
        pygame.draw.rect(surface, DKGRAY,
                         (ROAD_LEFT, 0, ROAD_W, SCREEN_H))
        # Road edges (white lines)
        pygame.draw.line(surface, WHITE, (ROAD_LEFT,  0), (ROAD_LEFT,  SCREEN_H), 4)
        pygame.draw.line(surface, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, SCREEN_H), 4)

        # Dashed lane dividers (two internal dividers)
        for lane in range(1, 3):
            x = ROAD_LEFT + lane * LANE_W
            y = -self.STRIPE_H + self.offset
            while y < SCREEN_H:
                pygame.draw.rect(surface, WHITE,
                                 (x - self.STRIPE_W // 2, y,
                                  self.STRIPE_W, self.STRIPE_H))
                y += self.STRIPE_H + self.STRIPE_GAP


# ══════════════════════════════════════════════════════
#  HUD — score, coins, speed
# ══════════════════════════════════════════════════════
def draw_hud(surface, score, coins, speed_level):
    # Score — top left
    score_surf = font_big.render(f"Score: {score}", True, WHITE)
    surface.blit(score_surf, (10, 10))

    # Speed level — top left, below score
    spd_surf = font_small.render(f"Speed: {speed_level}", True, GREEN)
    surface.blit(spd_surf, (10, 50))

    # Coins — TOP RIGHT corner
    coin_text = font_big.render(f"Coins: {coins}", True, YELLOW)
    surface.blit(coin_text, (SCREEN_W - coin_text.get_width() - 10, 10))


# ══════════════════════════════════════════════════════
#  GAME-OVER screen
# ══════════════════════════════════════════════════════
def show_game_over(surface, score, coins):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    lines = [
        font_big.render("GAME OVER", True, RED),
        font_big.render(f"Score : {score}", True, WHITE),
        font_big.render(f"Coins : {coins}", True, YELLOW),
        font_small.render("Press R to restart or Q to quit", True, GRAY),
    ]
    total_h = sum(l.get_height() + 10 for l in lines)
    y = (SCREEN_H - total_h) // 2
    for surf in lines:
        surface.blit(surf, ((SCREEN_W - surf.get_width()) // 2, y))
        y += surf.get_height() + 10

    pygame.display.flip()

    # Wait for input
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True   # restart
                if event.key == pygame.K_q:
                    pygame.quit(); sys.exit()


# ══════════════════════════════════════════════════════
#  MAIN GAME LOOP
# ══════════════════════════════════════════════════════
def run_game():
    road        = Road()
    player      = PlayerCar()
    enemies     = []
    coins       = []

    score       = 0          # increments every frame survived
    coin_count  = 0          # number of coins collected
    base_speed  = 4          # starting scroll/enemy speed
    speed_level = 1          # displayed speed level

    # Timers (milliseconds)
    enemy_timer     = 0
    coin_timer      = 0
    ENEMY_INTERVAL  = 1500   # spawn an enemy every 1.5 s
    COIN_INTERVAL   = 2000   # spawn a coin  every 2.0 s

    running = True
    while running:
        dt = clock.tick(FPS)   # milliseconds since last frame

        # ── Events ────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        # ── Score & speed ─────────────────────────────
        score      += 1
        speed_level = 1 + score // 300   # level up every 300 frames
        cur_speed   = base_speed + speed_level - 1

        # ── Road scroll ───────────────────────────────
        road.update(cur_speed)

        # ── Spawn enemies ─────────────────────────────
        enemy_timer += dt
        if enemy_timer >= ENEMY_INTERVAL:
            enemies.append(EnemyCar(speed=cur_speed))
            enemy_timer = 0
            # As the game progresses, reduce spawn interval (min 600 ms)
            ENEMY_INTERVAL = max(600, 1500 - speed_level * 80)

        # ── Spawn coins randomly ─────────────────────
        coin_timer += dt
        if coin_timer >= COIN_INTERVAL:
            if random.random() < 0.7:   # 70 % chance each interval
                coins.append(Coin(speed=cur_speed - 1))
            coin_timer = 0

        # ── Player movement ───────────────────────────
        keys = pygame.key.get_pressed()
        player.move(keys)

        # ── Update enemies ────────────────────────────
        for e in enemies:
            e.update()
        enemies = [e for e in enemies if not e.is_off_screen()]

        # ── Update coins ──────────────────────────────
        for c in coins:
            c.update()
        coins = [c for c in coins if not c.is_off_screen()]

        # ── Collision — enemy → game over ────────────
        for e in enemies:
            if player.rect.colliderect(e.rect):
                if show_game_over(screen, score, coin_count):
                    return   # restart requested — exit and re-call

        # ── Collision — coin → collect ────────────────
        for c in coins[:]:
            if player.rect.colliderect(c.rect):
                coin_count += 1
                coins.remove(c)

        # ── Draw ──────────────────────────────────────
        screen.fill(GRAY)         # grass / shoulder colour
        road.draw(screen)

        for e in enemies:
            e.draw(screen)
        for c in coins:
            c.draw(screen)

        player.draw(screen)
        draw_hud(screen, score, coin_count, speed_level)

        pygame.display.flip()


# ── Entry point ───────────────────────────────────────
if __name__ == "__main__":
    while True:
        run_game()   # loop allows restarting after game-over
