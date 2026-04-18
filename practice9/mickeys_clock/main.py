import pygame
import datetime

pygame.init()
screen = pygame.display.set_mode((1000, 1000))
clock = pygame.time.Clock()

# Загрузка изображений
minutes = pygame.image.load("images/rightarm.png")
seconds = pygame.image.load("images/sz.png")
casy = pygame.image.load("images/clock1.png").convert()

# Масштабирование
scaled_sec = pygame.transform.scale(
    seconds,
    (int(seconds.get_width() * 1.4), int(seconds.get_height() * 1.4))
)

scaled_min = pygame.transform.scale(
    minutes,
    (int(minutes.get_width() * 1.4), int(minutes.get_height() * 1.4))
)

# Центр вращения
pivot = (508, 508)

def rotate_around_pivot(image, angle, pivot):
    rotated_image = pygame.transform.rotate(image, -angle)
    rotated_rect = rotated_image.get_rect(center=pivot)
    return rotated_image, rotated_rect


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # текущее время
    now = datetime.datetime.now()
    seconds_now = now.second
    minutes_now = now.minute

    # углы вращения
    angle_sec = seconds_now * 6
    angle_min = (minutes_now + seconds_now / 60) * 6  # плавная минутная стрелка

    # вращение
    rotated_sec, rotated_sec_rect = rotate_around_pivot(scaled_sec, angle_sec, pivot)
    rotated_min, rotated_min_rect = rotate_around_pivot(scaled_min, angle_min, pivot)

    # отрисовка
    screen.fill((255, 255, 255))
    screen.blit(casy, (-200, 0))
    screen.blit(rotated_sec, rotated_sec_rect.topleft)
    screen.blit(rotated_min, rotated_min_rect.topleft)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()