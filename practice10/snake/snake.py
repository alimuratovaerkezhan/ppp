import pygame
import random

pygame.init()


WIDTH, HEIGHT = 500, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

clock = pygame.time.Clock()


WHITE = (255,255,255)
BLACK = (0,0,0)
GREEN = (0,255,0)
RED = (255,0,0)


block = 20


snake = [(100,100), (80,100), (60,100)]
direction = "RIGHT"


food_x = random.randrange(0, WIDTH, block)
food_y = random.randrange(0, HEIGHT, block)


score = 0
level = 1

font = pygame.font.SysFont("Verdana", 20)
big_font = pygame.font.SysFont("Verdana", 50)

game_over = False



def move_snake(snake, direction):
    x, y = snake[0]

    if direction == "UP":
        y -= block
    if direction == "DOWN":
        y += block
    if direction == "LEFT":
        x -= block
    if direction == "RIGHT":
        x += block

    new_head = (x, y)
    snake.insert(0, new_head)
    return snake

def check_collision(snake):
    x, y = snake[0]

    
    if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
        return True

    
    if snake[0] in snake[1:]:
        return True

    return False


running = True
while running:

    clock.tick(8 + level*2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != "DOWN":
                direction = "UP"
            if event.key == pygame.K_DOWN and direction != "UP":
                direction = "DOWN"
            if event.key == pygame.K_LEFT and direction != "RIGHT":
                direction = "LEFT"
            if event.key == pygame.K_RIGHT and direction != "LEFT":
                direction = "RIGHT"

    if not game_over:

        screen.fill(BLACK)

        
        snake = move_snake(snake, direction)

        
        if snake[0] == (food_x, food_y):
            score += 1
            food_x = random.randrange(0, WIDTH, block)
            food_y = random.randrange(0, HEIGHT, block)
        else:
            snake.pop()

        
        level = score // 5 + 1

        
        if check_collision(snake):
            game_over = True

        
        for i, segment in enumerate(snake):
            pygame.draw.rect(screen, GREEN, (segment[0], segment[1], block, block))

        
        pygame.draw.rect(screen, RED, (food_x, food_y, block, block))

        
        text = font.render(f"Score: {score} Level: {level}", True, WHITE)
        screen.blit(text, (10,10))

    else:

        text = big_font.render("GAME OVER", True, RED)
        screen.blit(text, (80, 200))

        restart = font.render("Press R to restart", True, WHITE)
        screen.blit(restart, (120, 270))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            snake = [(100,100), (80,100), (60,100)]
            direction = "RIGHT"
            score = 0
            level = 1
            game_over = False

    pygame.display.update()

pygame.quit()