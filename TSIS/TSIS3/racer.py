import pygame
import sys
import random
import math
from pygame.locals import *

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)

from sounds import SoundManager

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
FPS = 60

INITIAL_SPEED = 5
COINS_FOR_LEVEL_UP = 5
NUM_LANES = 3
LANE_WIDTH = SCREEN_WIDTH // NUM_LANES

# COLORS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 60, 60)
GREEN = (60, 255, 60)
YELLOW = (255, 255, 60)
GOLD = (255, 215, 0)
BLUE = (60, 150, 255)
ORANGE = (255, 140, 60)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (60, 60, 60)
BRONZE = (205, 127, 50)
SILVER = (192, 192, 192)
CYAN = (0, 255, 255)
MEDIUM_GRAY = (120, 120, 120)

NITRO_COLOR = (255, 120, 0)
SHIELD_COLOR = (60, 200, 255)
REPAIR_COLOR = (60, 255, 120)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("RACER GAME")
clock = pygame.time.Clock()

font_medium = pygame.font.SysFont("Arial", 22, bold=True)
font_small = pygame.font.SysFont("Arial", 18, bold=True)
font_tiny = pygame.font.SysFont("Arial", 14)


class Player(pygame.sprite.Sprite):
    def __init__(self, car_color="green"):
        super().__init__()
        self.width = 65
        self.height = 100
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.create_car(car_color)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 120
        self.speed = 7
        self.collision_rect = pygame.Rect(0, 0, 55, 85)
        self.update_collision_rect()
        
        self.has_shield = False
        self.shield_time = 0
        self.nitro_time = 0
        self.invincible_time = 0
    
    def create_car(self, color):
        colors = {"green": (60, 220, 60), "red": (220, 60, 60), "blue": (60, 100, 220), "yellow": (220, 220, 60)}
        main_color = colors.get(color, (60, 200, 60))
        
        self.image.fill((0, 0, 0, 0))
        
        pygame.draw.rect(self.image, main_color, (8, 15, 49, 70))
        pygame.draw.rect(self.image, (min(255, main_color[0]+50), min(255, main_color[1]+50), min(255, main_color[2]+50)), (8, 15, 49, 35))
        pygame.draw.rect(self.image, (100, 200, 240), (14, 20, 37, 22))
        pygame.draw.circle(self.image, (20, 20, 30), (13, 82), 11)
        pygame.draw.circle(self.image, (20, 20, 30), (52, 82), 11)
        pygame.draw.circle(self.image, (80, 80, 90), (13, 82), 6)
        pygame.draw.circle(self.image, (80, 80, 90), (52, 82), 6)
        pygame.draw.circle(self.image, YELLOW, (13, 25), 5)
        pygame.draw.circle(self.image, YELLOW, (52, 25), 5)
        pygame.draw.rect(self.image, WHITE, (26, 45, 13, 7))
    
    def update_collision_rect(self):
        self.collision_rect.centerx = self.rect.centerx
        self.collision_rect.centery = self.rect.centery
    
    def move(self):
        keys = pygame.key.get_pressed()
        if keys[K_LEFT] and self.rect.left > 25:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.right < SCREEN_WIDTH - 25:
            self.rect.x += self.speed
        self.update_collision_rect()
    
    def get_lane(self):
        return min(NUM_LANES - 1, max(0, self.rect.centerx // LANE_WIDTH))
    
    def update_powerups(self):
        if self.nitro_time > 0:
            self.nitro_time -= 1
        if self.shield_time > 0:
            self.shield_time -= 1
            if self.shield_time <= 0:
                self.has_shield = False
        if self.invincible_time > 0:
            self.invincible_time -= 1
    
    def has_nitro(self):
        return self.nitro_time > 0
    
    def has_shield_active(self):
        return self.has_shield and self.shield_time > 0
    
    def is_invincible(self):
        return self.invincible_time > 0 or self.has_shield_active()
    
    def activate_nitro(self):
        self.nitro_time = 180
    
    def activate_shield(self):
        self.has_shield = True
        self.shield_time = 300
        self.invincible_time = 300
    
    def deactivate_shield(self):
        self.has_shield = False
        self.shield_time = 0
    
    def draw(self, surface):
        if self.has_shield_active():
            for r in range(50, 35, -5):
                shield_surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                pygame.draw.circle(shield_surf, SHIELD_COLOR, (r, r), r, 3)
                surface.blit(shield_surf, (self.rect.centerx - r, self.rect.centery - r))
        
        if self.nitro_time > 0:
            flame_h = 20 + (self.nitro_time % 12)
            pygame.draw.polygon(surface, NITRO_COLOR, 
                              [(self.rect.centerx - 8, self.rect.bottom), 
                               (self.rect.centerx, self.rect.bottom + flame_h),
                               (self.rect.centerx + 8, self.rect.bottom)])
        
        surface.blit(self.image, self.rect)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed_multiplier=1.0):
        super().__init__()
        self.width = 65
        self.height = 100
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        self.image.fill((0, 0, 0, 0))
        
        pygame.draw.rect(self.image, RED, (6, 12, 53, 70))
        pygame.draw.rect(self.image, (200, 40, 40), (6, 12, 53, 35))
        pygame.draw.rect(self.image, (80, 80, 110), (12, 18, 41, 22))
        pygame.draw.rect(self.image, BLUE, (20, 65, 25, 6))
        pygame.draw.rect(self.image, RED, (15, 10, 35, 8))
        pygame.draw.circle(self.image, DARK_GRAY, (14, 80), 11)
        pygame.draw.circle(self.image, DARK_GRAY, (51, 80), 11)
        pygame.draw.circle(self.image, MEDIUM_GRAY, (14, 80), 6)
        pygame.draw.circle(self.image, MEDIUM_GRAY, (51, 80), 6)
        
        self.rect = self.image.get_rect()
        self.collision_rect = pygame.Rect(0, 0, 50, 85)
        self.reset_position()
        self.speed_multiplier = speed_multiplier
    
    def reset_position(self):
        min_x = 40 + 5
        max_x = SCREEN_WIDTH - 40 - self.width - 5
        self.rect.x = random.randint(min_x, max(max_x, min_x + 1))
        self.rect.y = -self.rect.height - random.randint(0, 200)
        self.collision_rect.centerx = self.rect.centerx
        self.collision_rect.centery = self.rect.centery
    
    def move(self, base_speed):
        self.rect.y += base_speed * self.speed_multiplier
        self.collision_rect.centerx = self.rect.centerx
        self.collision_rect.centery = self.rect.centery
        if self.rect.top > SCREEN_HEIGHT:
            self.reset_position()
            return True
        return False
    
    def draw(self, surface):
        if pygame.time.get_ticks() % 400 < 200:
            pygame.draw.circle(surface, RED, (self.rect.x + 18, self.rect.y + 16), 6)
            pygame.draw.circle(surface, BLUE, (self.rect.x + 47, self.rect.y + 16), 6)
        else:
            pygame.draw.circle(surface, BLUE, (self.rect.x + 18, self.rect.y + 16), 6)
            pygame.draw.circle(surface, RED, (self.rect.x + 47, self.rect.y + 16), 6)
        
        surface.blit(self.image, self.rect)


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.value = random.choice([1, 2, 3])
        self.size = 32
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.create_coin()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.rotation = 0
    
    def create_coin(self):
        self.image.fill((0, 0, 0, 0))
        
        if self.value == 1:
            color = BRONZE
        elif self.value == 2:
            color = SILVER
        else:
            color = GOLD
        
        center = (self.size // 2, self.size // 2)
        radius = self.size // 2 - 3
        
        pygame.draw.circle(self.image, color, center, radius)
        pygame.draw.circle(self.image, YELLOW if self.value == 3 else WHITE, center, radius - 3)
        
        if self.value == 3:
            points = []
            for i in range(5):
                angle = i * 72 - 90
                x = center[0] + 9 * math.cos(math.radians(angle))
                y = center[1] + 9 * math.sin(math.radians(angle))
                points.append((int(x), int(y)))
            pygame.draw.polygon(self.image, GOLD, points, 2)
        
        font_val = pygame.font.SysFont("Arial", 18, bold=True)
        text = font_val.render(str(self.value), True, BLACK)
        text_rect = text.get_rect(center=center)
        self.image.blit(text, text_rect)
    
    def move(self, speed):
        self.rect.y += speed
        self.rotation += 0.15
        return self.rect.top > SCREEN_HEIGHT
    
    def draw(self, surface):
        rotated = pygame.transform.rotate(self.image, self.rotation * 30)
        new_rect = rotated.get_rect(center=self.rect.center)
        surface.blit(rotated, new_rect)


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # ONLY NITRO AND SHIELD - NO GREEN REPAIR
        self.type = random.choice(["nitro", "shield"])
        self.width = 40
        self.height = 40
        self.lifetime = 300
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.create_powerup()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def create_powerup(self):
        self.image.fill((0, 0, 0, 0))
        
        if self.type == "nitro":
            # ORANGE NITRO
            pygame.draw.rect(self.image, NITRO_COLOR, (7, 10, 26, 23), border_radius=5)
            pygame.draw.rect(self.image, (220, 100, 0), (12, 7, 16, 10), border_radius=3)
            pygame.draw.circle(self.image, WHITE, (20, 25), 5)
            pygame.draw.circle(self.image, WHITE, (20, 31), 5)
            font = pygame.font.SysFont("Arial", 16, bold=True)
            text = font.render("N", True, WHITE)
            self.image.blit(text, (14, 16))
        else:
            # BLUE SHIELD
            pygame.draw.circle(self.image, SHIELD_COLOR, (20, 20), 18)
            pygame.draw.polygon(self.image, WHITE, [(20, 6), (30, 14), (27, 26), (13, 26), (10, 14)])
            font = pygame.font.SysFont("Arial", 16, bold=True)
            text = font.render("S", True, WHITE)
            self.image.blit(text, (14, 14))
    
    def move(self, speed):
        self.rect.y += speed
        self.lifetime -= 1
        return self.rect.top > SCREEN_HEIGHT or self.lifetime <= 0
    
    def draw(self, surface):
        percent = self.lifetime / 300
        pygame.draw.rect(surface, DARK_GRAY, (self.rect.x + 6, self.rect.y - 8, 28, 5), border_radius=3)
        
        if self.type == "nitro":
            bar_color = NITRO_COLOR
        else:
            bar_color = SHIELD_COLOR
        
        pygame.draw.rect(surface, bar_color, (self.rect.x + 6, self.rect.y - 8, 28 * percent, 5), border_radius=3)
        surface.blit(self.image, self.rect)


class RacerGame:
    def __init__(self, settings):
        self.settings = settings
        self.sound_manager = SoundManager(settings.get("sound_enabled", True))
        
        self.running = True
        self.game_over = False
        self.score = 0
        self.coins = 0
        self.distance = 0
        self.level = 1
        
        self.base_speed = INITIAL_SPEED
        self.current_speed = self.base_speed
        self.difficulty_mult = {"easy": 0.7, "normal": 1.0, "hard": 1.5}.get(settings["difficulty"], 1.0)
        
        self.enemy_timer = 0
        self.coin_timer = 0
        self.powerup_timer = 0
        
        self.enemies = []
        self.coins_list = []
        self.powerups = []
        
        self.player = Player(settings["car_color"])
        self.invincible_frames = 0
        self.flash_effect = 0
    
    def spawn_enemy(self):
        if len(self.enemies) < 3:
            self.enemies.append(Enemy(self.difficulty_mult))
    
    def spawn_coin(self):
        for attempt in range(10):
            lane = random.randint(0, NUM_LANES - 1)
            x = lane * LANE_WIDTH + random.randint(20, LANE_WIDTH - 52)
            
            overlap = False
            temp_rect = pygame.Rect(x, -35, 32, 32)
            for enemy in self.enemies:
                if temp_rect.colliderect(enemy.rect):
                    overlap = True
                    break
            
            if not overlap:
                self.coins_list.append(Coin(x, -35))
                return
        
        lane = random.randint(0, NUM_LANES - 1)
        x = lane * LANE_WIDTH + random.randint(20, LANE_WIDTH - 52)
        self.coins_list.append(Coin(x, -35))
    
    def spawn_powerup(self):
        for attempt in range(10):
            lane = random.randint(0, NUM_LANES - 1)
            x = lane * LANE_WIDTH + random.randint(20, LANE_WIDTH - 60)
            
            overlap = False
            temp_rect = pygame.Rect(x, -45, 40, 40)
            for enemy in self.enemies:
                if temp_rect.colliderect(enemy.rect):
                    overlap = True
                    break
            
            if not overlap:
                self.powerups.append(PowerUp(x, -45))
                return
        
        lane = random.randint(0, NUM_LANES - 1)
        x = lane * LANE_WIDTH + random.randint(20, LANE_WIDTH - 60)
        self.powerups.append(PowerUp(x, -45))
    
    def update_spawners(self):
        d = max(1, self.difficulty_mult)
        self.enemy_timer += 1
        if self.enemy_timer >= 55 // int(d):
            self.enemy_timer = 0
            self.spawn_enemy()
        
        self.coin_timer += 1
        if self.coin_timer >= 25 // int(d):
            self.coin_timer = 0
            self.spawn_coin()
        
        self.powerup_timer += 1
        if self.powerup_timer >= 200 // int(d):
            self.powerup_timer = 0
            self.spawn_powerup()
    
    def update_objects(self):
        self.current_speed = self.base_speed
        if self.player.has_nitro():
            self.current_speed += 5
        if self.invincible_frames > 0:
            self.invincible_frames -= 1
        if self.flash_effect > 0:
            self.flash_effect -= 1
        
        for enemy in self.enemies[:]:
            if enemy.move(self.current_speed):
                self.score += 10
            if enemy.rect.top > SCREEN_HEIGHT + 100:
                self.enemies.remove(enemy)
        
        for coin in self.coins_list[:]:
            if coin.move(self.current_speed):
                self.coins_list.remove(coin)
        
        for powerup in self.powerups[:]:
            if powerup.move(self.current_speed):
                self.powerups.remove(powerup)
    
    def check_collisions(self):
        for enemy in self.enemies:
            if self.player.collision_rect.colliderect(enemy.collision_rect):
                if self.invincible_frames <= 0 and not self.player.is_invincible():
                    self.sound_manager.play('crash')
                    self.game_over = True
                    return
                else:
                    self.enemies.remove(enemy)
                    break
        
        for coin in self.coins_list[:]:
            if self.player.collision_rect.colliderect(coin.rect):
                self.coins += 1
                self.score += coin.value * 10
                self.sound_manager.play('coin')
                self.flash_effect = 8
                self.coins_list.remove(coin)
                if self.coins % COINS_FOR_LEVEL_UP == 0 and self.coins > 0:
                    self.level += 1
                    self.base_speed = min(14, self.base_speed + 0.7)
                    self.flash_effect = 20
        
        for powerup in self.powerups[:]:
            if self.player.collision_rect.colliderect(powerup.rect):
                if powerup.type == "nitro":
                    self.player.activate_nitro()
                    self.score += 50
                else:
                    self.player.activate_shield()
                    self.score += 30
                self.sound_manager.play('powerup')
                self.flash_effect = 15
                self.powerups.remove(powerup)
    
    def update_score(self):
        self.distance += self.current_speed * 0.1
        self.score += int(self.current_speed)
    
    def draw_background(self):
        screen.fill((40, 40, 60))
        
        pygame.draw.rect(screen, (45, 45, 55), (40, 0, SCREEN_WIDTH - 80, SCREEN_HEIGHT))
        pygame.draw.rect(screen, (70, 70, 60), (35, 0, 5, SCREEN_HEIGHT))
        pygame.draw.rect(screen, (70, 70, 60), (SCREEN_WIDTH - 40, 0, 5, SCREEN_HEIGHT))
        pygame.draw.line(screen, YELLOW, (40, 0), (40, SCREEN_HEIGHT), 4)
        pygame.draw.line(screen, YELLOW, (SCREEN_WIDTH - 40, 0), (SCREEN_WIDTH - 40, SCREEN_HEIGHT), 4)
        
        for i in range(1, NUM_LANES):
            x = i * LANE_WIDTH
            pygame.draw.line(screen, WHITE, (x, 0), (x, SCREEN_HEIGHT), 3)
        
        line_y = (pygame.time.get_ticks() // 80) % 100
        for i in range(NUM_LANES):
            x = i * LANE_WIDTH + LANE_WIDTH // 2
            for y in range(line_y - 100, SCREEN_HEIGHT, 100):
                pygame.draw.rect(screen, WHITE, (x - 4, y, 8, 30), border_radius=4)
    
    def draw_ui(self):
        panel = pygame.Surface((170, 190), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 200))
        screen.blit(panel, (8, 8))
        pygame.draw.rect(screen, GOLD, (8, 8, 170, 190), 2, border_radius=10)
        
        title = font_small.render("YOUR STATS", True, YELLOW)
        screen.blit(title, (15, 15))
        pygame.draw.line(screen, LIGHT_GRAY, (15, 38), (170, 38), 1)
        
        stats = [
            ("SCORE:", f"{self.score}", GOLD),
            ("COINS:", f"{self.coins}", YELLOW),
            ("LEVEL:", f"{self.level}", CYAN),
            ("DISTANCE:", f"{int(self.distance)}m", GREEN),
            ("SPEED:", f"{int(self.current_speed * 10)}", ORANGE),
        ]
        
        y = 48
        for label, value, color in stats:
            label_text = font_tiny.render(label, True, LIGHT_GRAY)
            screen.blit(label_text, (15, y))
            value_text = font_medium.render(value, True, color)
            screen.blit(value_text, (160 - value_text.get_width(), y - 2))
            y += 28
        
        boost_y = SCREEN_HEIGHT - 70
        if self.player.has_nitro():
            text = font_tiny.render(f"NITRO: {self.player.nitro_time//60}s", True, NITRO_COLOR)
            screen.blit(text, (SCREEN_WIDTH - 120, boost_y))
            boost_y += 20
        if self.player.has_shield_active():
            text = font_tiny.render(f"SHIELD: {self.player.shield_time//60}s", True, SHIELD_COLOR)
            screen.blit(text, (SCREEN_WIDTH - 120, boost_y))
            boost_y += 20
        if self.invincible_frames > 0:
            text = font_tiny.render(f"INVINCIBLE", True, YELLOW)
            screen.blit(text, (SCREEN_WIDTH - 120, boost_y))
        
        coins_needed = COINS_FOR_LEVEL_UP - (self.coins % COINS_FOR_LEVEL_UP)
        if coins_needed == 0:
            coins_needed = COINS_FOR_LEVEL_UP
        progress = (self.coins % COINS_FOR_LEVEL_UP) / COINS_FOR_LEVEL_UP
        
        bar_x = SCREEN_WIDTH - 110
        bar_y = SCREEN_HEIGHT - 25
        bar_w = 90
        bar_h = 8
        
        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        pygame.draw.rect(screen, GOLD, (bar_x, bar_y, bar_w * progress, bar_h), border_radius=4)
        
        next_text = font_tiny.render(f"Next: {coins_needed}", True, LIGHT_GRAY)
        screen.blit(next_text, (bar_x, bar_y - 16))
        
        control_text = font_tiny.render("ARROWS ← → MOVE", True, LIGHT_GRAY)
        screen.blit(control_text, (15, SCREEN_HEIGHT - 25))
    
    def draw_flash(self):
        if self.flash_effect > 0:
            flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash.set_alpha(100 - self.flash_effect * 5)
            flash.fill(WHITE)
            screen.blit(flash, (0, 0))
    
    def draw(self):
        self.draw_background()
        
        for powerup in self.powerups:
            powerup.draw(screen)
        
        for coin in self.coins_list:
            coin.draw(screen)
        
        for enemy in self.enemies:
            enemy.draw(screen)
        
        self.player.draw(screen)
        self.draw_ui()
        self.draw_flash()
    
    def update(self):
        self.player.move()
        self.player.update_powerups()
        self.update_spawners()
        self.update_objects()
        self.check_collisions()
        self.update_score()
    
    def run_game_loop(self):
        while self.running and not self.game_over:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                    return "quit"
            
            self.update()
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)
        
        return "game_over"
    
    def get_final_stats(self):
        return self.score, self.distance, self.coins


def run_game(settings):
    game = RacerGame(settings)
    return game.run_game_loop(), game.get_final_stats()