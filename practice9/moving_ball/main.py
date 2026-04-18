import pygame
from ball import Ball   # ← ВАЖНО

pygame.init()

width, height = 600, 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Moving Ball")

ball = Ball(300, 200)

clock = pygame.time.Clock()

running = True
while running:
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    ball.move(keys, width, height)
    ball.draw(screen)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()