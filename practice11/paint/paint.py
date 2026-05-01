import pygame
import math

pygame.init()

#SCREEN 
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint with Clear Button")

clock = pygame.time.Clock()


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

color = BLACK
mode = "draw"

radius = 6
eraser_size = 18

drawing = False
start_pos = (0, 0)
last_pos = (0, 0)


canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill(WHITE)

colors = [
    (BLACK, pygame.Rect(10, 10, 30, 30)),
    (RED, pygame.Rect(50, 10, 30, 30)),
    (GREEN, pygame.Rect(90, 10, 30, 30)),
    (BLUE, pygame.Rect(130, 10, 30, 30)),
]

tools = [
    ("DRAW", pygame.Rect(10, 60, 80, 30), "draw"),
    ("ERASER", pygame.Rect(100, 60, 80, 30), "eraser"),
    ("RECT", pygame.Rect(190, 60, 80, 30), "rectangle"),
    ("SQUARE", pygame.Rect(280, 60, 80, 30), "square"),
    ("CIRCLE", pygame.Rect(370, 60, 80, 30), "circle"),
    ("TRI", pygame.Rect(460, 60, 80, 30), "right_triangle"),
    ("TRI2", pygame.Rect(550, 60, 80, 30), "equilateral_triangle"),
    ("RHOMB", pygame.Rect(640, 60, 80, 30), "rhombus"),
    ("CLEAR", pygame.Rect(730, 60, 80, 30), "clear"),
]

# MAIN LOOP
running = True
while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # MOUSE DOWN
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            drawing = True
            start_pos = pos
            last_pos = pos

            #  COLORS 
            for col, rect in colors:
                if rect.collidepoint(pos):
                    color = col

            # TOOLS 
            for text, rect, tool in tools:
                if rect.collidepoint(pos):

                    #  CLEAR BUTTON
                    if tool == "clear":
                        canvas.fill(WHITE)

                    else:
                        mode = tool

        # MOUSE UP 
        if event.type == pygame.MOUSEBUTTONUP:
            drawing = False
            end_pos = event.pos

            #DRAW SHAPES ON CANVAS 
            if mode == "rectangle":
                pygame.draw.rect(canvas, color,
                                 pygame.Rect(start_pos,
                                 (end_pos[0]-start_pos[0], end_pos[1]-start_pos[1])), 2)

            elif mode == "square":
                side = max(abs(end_pos[0]-start_pos[0]), abs(end_pos[1]-start_pos[1]))
                pygame.draw.rect(canvas, color,
                                 pygame.Rect(start_pos, (side, side)), 2)

            elif mode == "circle":
                r = int(math.hypot(end_pos[0]-start_pos[0],
                                   end_pos[1]-start_pos[1]))
                pygame.draw.circle(canvas, color, start_pos, r, 2)

            elif mode == "right_triangle":
                pygame.draw.polygon(canvas, color,
                                    [start_pos,
                                     (start_pos[0], end_pos[1]),
                                     end_pos], 2)

            elif mode == "equilateral_triangle":
                side = abs(end_pos[0]-start_pos[0])
                height = int((math.sqrt(3)/2)*side)

                p1 = start_pos
                p2 = (start_pos[0]+side, start_pos[1])
                p3 = (start_pos[0]+side//2, start_pos[1]-height)

                pygame.draw.polygon(canvas, color, [p1, p2, p3], 2)

            elif mode == "rhombus":
                mx = (start_pos[0]+end_pos[0])//2
                my = (start_pos[1]+end_pos[1])//2

                points = [
                    (mx, start_pos[1]),
                    (end_pos[0], my),
                    (mx, end_pos[1]),
                    (start_pos[0], my)
                ]
                pygame.draw.polygon(canvas, color, points, 2)

        # FREE DRAW / ERASER 
        if event.type == pygame.MOUSEMOTION and drawing:

            current = event.pos

            if mode == "draw":
                pygame.draw.line(canvas, color, last_pos, current, radius)
                last_pos = current

            elif mode == "eraser":
                pygame.draw.line(canvas, WHITE, last_pos, current, eraser_size)
                last_pos = current

    # RENDER 
    screen.fill(WHITE)
    screen.blit(canvas, (0, 0))

    # -------- DRAW COLORS --------
    for col, rect in colors:
        pygame.draw.rect(screen, col, rect)
        pygame.draw.rect(screen, BLACK, rect, 1)

    # DRAW TOOLS
    for text, rect, tool in tools:
        pygame.draw.rect(screen, (200, 200, 200), rect)
        pygame.draw.rect(screen, BLACK, rect, 1)

        font = pygame.font.SysFont("Arial", 12)
        label = font.render(text, True, BLACK)
        screen.blit(label, (rect.x + 5, rect.y + 7))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()