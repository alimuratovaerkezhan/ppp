import pygame
class Ball:
    def __init__(self, x, y, radius=25):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = 20

    def move(self, keys, width, height):
        if keys[pygame.K_LEFT] and self.x - self.radius > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x + self.radius < width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y - self.radius > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y + self.radius < height:
            self.y += self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), (self.x, self.y), self.radius)