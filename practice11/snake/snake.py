import pygame
import random
import time

pygame.init()

# -------- SETTINGS --------
WIDTH, HEIGHT = 600, 400
CELL = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

clock = pygame.time.Clock()

WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
BLACK = (0, 0, 0)

font = pygame.font.SysFont("Verdana", 20)
big_font = pygame.font.SysFont("Verdana", 40)

# -------- GAME STATE --------
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"

state = MENU

# -------- GAME VARIABLES --------
def reset_game():
    global snake, direction, food_pos, food_weight
    global food_spawn_time, score, level, speed

    snake = [(100, 100)]
    direction = (CELL, 0)

    score = 0
    level = 1
    speed = 7

    generate_food()

# -------- FOOD --------
def generate_food():
    global food_pos, food_weight, food_spawn_time
    
    while True:
        x = random.randrange(0, WIDTH, CELL)
        y = random.randrange(0, HEIGHT, CELL)
        if (x, y) not in snake:
            food_pos = (x, y)
            break
    
    food_weight = random.randint(1, 3)
    food_spawn_time = time.time()

# -------- DRAW --------
def draw_snake():
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (*segment, CELL, CELL))

def draw_food():
    if food_weight == 1:
        color = RED
    elif food_weight == 2:
        color = BLUE
    else:
        color = (255, 165, 0)
    
    pygame.draw.rect(screen, color, (*food_pos, CELL, CELL))

def draw_info():
    text = font.render(f"Score: {score}  Level: {level}", True, WHITE)
    screen.blit(text, (10, 10))

def draw_menu():
    screen.fill(BLACK)
    
    title = big_font.render("SNAKE GAME", True, GREEN)
    start = font.render("Press SPACE to Start", True, WHITE)
    
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))
    screen.blit(start, (WIDTH//2 - start.get_width()//2, 200))

def draw_game_over():
    screen.fill(BLACK)
    
    over = big_font.render("GAME OVER", True, RED)
    score_text = font.render(f"Score: {score}", True, WHITE)
    restart = font.render("Press R to Restart", True, WHITE)
    
    screen.blit(over, (WIDTH//2 - over.get_width()//2, 120))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 180))
    screen.blit(restart, (WIDTH//2 - restart.get_width()//2, 220))

# -------- LOGIC --------
def check_collision():
    head_x, head_y = snake[0]
    
    if head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT:
        return True
    
    if snake[0] in snake[1:]:
        return True
    
    return False

def update_level():
    global level, speed
    new_level = score // 5 + 1
    if new_level > level:
        level = new_level
        speed += 2

# -------- INIT --------
reset_game()

# -------- MAIN LOOP --------
running = True
while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if state == MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    reset_game()
                    state = PLAYING
        
        elif state == PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != (0, CELL):
                    direction = (0, -CELL)
                if event.key == pygame.K_DOWN and direction != (0, -CELL):
                    direction = (0, CELL)
                if event.key == pygame.K_LEFT and direction != (CELL, 0):
                    direction = (-CELL, 0)
                if event.key == pygame.K_RIGHT and direction != (-CELL, 0):
                    direction = (CELL, 0)
        
        elif state == GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                    state = PLAYING
    
    # -------- GAME RUNNING --------
    if state == PLAYING:
        screen.fill(BLACK)
        
        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        snake.insert(0, head)
        
        if head == food_pos:
            score += food_weight
            generate_food()
        else:
            snake.pop()
        
        # Food timer
        if time.time() - food_spawn_time > 5:
            generate_food()
        
        update_level()
        
        if check_collision():
            state = GAME_OVER
        
        draw_snake()
        draw_food()
        draw_info()
    
    elif state == MENU:
        draw_menu()
    
    elif state == GAME_OVER:
        draw_game_over()
    
    pygame.display.flip()
    clock.tick(speed)

pygame.quit()