import pygame
import random

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer")

clock = pygame.time.Clock()
FPS = 60

bg = pygame.image.load("resources/AnimatedStreet.png")

player_img = pygame.image.load("resources/player.png")
enemy_img = pygame.image.load("resources/enemy.png")
coin_img = pygame.image.load("resources/dollar.png")


player_img = pygame.transform.scale(player_img, (50, 80))
enemy_img = pygame.transform.scale(enemy_img, (50, 80))
coin_img = pygame.transform.scale(coin_img, (30, 30))

# SOUND 
pygame.mixer.music.load("resources/background.wav")
pygame.mixer.music.play(-1)

crash_sound = pygame.mixer.Sound("resources/crash.wav")

player_rect = player_img.get_rect(center=(WIDTH // 2, HEIGHT - 100))

enemy_rect = enemy_img.get_rect(center=(random.randint(50, WIDTH - 50), -100))
enemy_speed = 5

bg_y1 = 0
bg_y2 = -HEIGHT

coins = []
coin_spawn_time = 0
coin_count = 0

time_passed = 0

font = pygame.font.SysFont("Verdana", 20)

running = True
while running:
    clock.tick(FPS)
    time_passed += 1

    #EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #PLAYER CONTROL
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_rect.left > 0:
        player_rect.x -= 5
    if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
        player_rect.x += 5

    #SPEED SYSTEM 
    N = 10
    enemy_speed = 5 + (coin_count // N) + (time_passed * 0.0005)
    enemy_speed = min(enemy_speed, 15)  # limit

    bg_y1 += enemy_speed
    bg_y2 += enemy_speed

    if bg_y1 >= HEIGHT:
        bg_y1 = -HEIGHT
    if bg_y2 >= HEIGHT:
        bg_y2 = -HEIGHT

    #ENEMY 
    enemy_rect.y += enemy_speed
    if enemy_rect.top > HEIGHT:
        enemy_rect.center = (random.randint(50, WIDTH - 50), -100)

    # COLLISION 
    if player_rect.colliderect(enemy_rect):
        crash_sound.play()
        pygame.time.delay(1000)
        running = False

    
    coin_spawn_time += 1
    if coin_spawn_time > 60:
        coin_spawn_time = 0

        coin_rect = coin_img.get_rect(
            center=(random.randint(30, WIDTH - 30), -50)
        )

        weight = random.choice([1, 2, 5])  # coin value
        coins.append([coin_rect, weight])

    #COIN LOGIC 
    for coin in coins[:]:
        coin[0].y += enemy_speed

        if coin[0].top > HEIGHT:
            coins.remove(coin)

        if player_rect.colliderect(coin[0]):
            coin_count += coin[1]
            coins.remove(coin)

    screen.blit(bg, (0, bg_y1))
    screen.blit(bg, (0, bg_y2))

    screen.blit(player_img, player_rect)
    screen.blit(enemy_img, enemy_rect)

    for coin in coins:
        screen.blit(coin_img, coin[0])

    #SCORE
    text = font.render(f"Coins: {coin_count}", True, (0, 0, 0))
    screen.blit(text, (WIDTH - 130, 10))

    pygame.display.update()

pygame.quit()