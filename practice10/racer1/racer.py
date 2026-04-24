import pygame
import random

pygame.init()

# ===== экран =====
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer - Real Movement")

clock = pygame.time.Clock()
FPS = 60

# ===== изображения =====
bg = pygame.image.load('resources/AnimatedStreet.png')
player_img = pygame.image.load('resources/Player.png')
enemy_img = pygame.image.load('resources/Enemy.png')
coin_img = pygame.image.load('resources/dollar.png').convert_alpha()
coin_img = pygame.transform.scale(coin_img, (40, 40))

# ===== фон движение =====
bg_y1 = 0
bg_y2 = -HEIGHT
bg_speed = 6

# ===== игрок =====
player_rect = player_img.get_rect(center=(WIDTH//2, HEIGHT-80))
player_speed = 5

# ===== враг =====
enemy_rect = enemy_img.get_rect()
enemy_speed = 6
enemy_rect.x = random.randint(0, WIDTH - enemy_rect.w)
enemy_rect.y = -100

# ===== монета =====
coin_rect = coin_img.get_rect()
coin_speed = 5
coin_rect.x = random.randint(0, WIDTH - coin_rect.w)
coin_rect.y = -200

# ===== счёт =====
score = 0
font = pygame.font.SysFont("Verdana", 25)
big_font = pygame.font.SysFont("Verdana", 60)

game_over = False

# ===== GAME LOOP =====
running = True
while running:

    clock.tick(FPS)

    # ===== EVENTS =====
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                # restart
                game_over = False
                score = 0
                enemy_rect.y = -100
                coin_rect.y = -200
                player_rect.center = (WIDTH//2, HEIGHT-80)

    # ===== фон движение (ВАЖНО!) =====
    bg_y1 += bg_speed
    bg_y2 += bg_speed

    if bg_y1 >= HEIGHT:
        bg_y1 = -HEIGHT
    if bg_y2 >= HEIGHT:
        bg_y2 = -HEIGHT

    screen.blit(bg, (0, bg_y1))
    screen.blit(bg, (0, bg_y2))

    if not game_over:

        # ===== управление игроком =====
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_rect.left > 0:
            player_rect.x -= player_speed
        if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
            player_rect.x += player_speed

        # ===== враг движение =====
        enemy_rect.y += enemy_speed
        if enemy_rect.top > HEIGHT:
            enemy_rect.y = -100
            enemy_rect.x = random.randint(0, WIDTH - enemy_rect.w)
            score += 1  # за выживание

        # ===== монета движение =====
        coin_rect.y += coin_speed
        if coin_rect.top > HEIGHT:
            coin_rect.y = -200
            coin_rect.x = random.randint(0, WIDTH - coin_rect.w)

        # ===== столкновения =====
        if player_rect.colliderect(enemy_rect):
            game_over = True

        if player_rect.colliderect(coin_rect):
            score += 1
            coin_rect.y = -200
            coin_rect.x = random.randint(0, WIDTH - coin_rect.w)

        # ===== рисование =====
        screen.blit(player_img, player_rect)
        screen.blit(enemy_img, enemy_rect)
        screen.blit(coin_img, coin_rect)

    else:
        # GAME OVER
        text = big_font.render("GAME OVER", True, (255,0,0))
        screen.blit(text, (30, 250))

        restart = font.render("Press R to restart", True, (255,255,255))
        screen.blit(restart, (80, 330))

    # ===== SCORE =====
    score_text = font.render(f"Score: {score}", True, (255,255,255))
    screen.blit(score_text, (10, 10))

    pygame.display.update()

pygame.quit()