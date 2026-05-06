import pygame
import math

pygame.init()

screen = pygame.display.set_mode((1200, 600))
clock = pygame.time.Clock()

radius = 2   
mode = 'blue'
points = []
strokes = []
figures = []
figures_perm = []
drawing = True
drawing_mode = 1
fig_start = (0, 0)

text = """
P = Stop/Draw
Z = Draw rectangle
X = Draw circle
L = Draw line
C = Eraser
A = Clear
"""

r = pygame.Rect(30, 150, 30, 30)
g = pygame.Rect(30, 200, 30, 30)
b = pygame.Rect(30, 250, 30, 30)


def drawLineBetween(screen, index, start, end, width, color_mode):
    dx = start[0] - end[0]
    dy = start[1] - end[1]
    iterations = max(abs(dx), abs(dy))

    if iterations == 0:
        return

    for i in range(iterations):
        t = i / iterations
        x = int((1 - t) * start[0] + t * end[0])
        y = int((1 - t) * start[1] + t * end[1])

        if color_mode == 'blue':
            color = (0, 0, 255)
        elif color_mode == 'red':
            color = (255, 0, 0)
        elif color_mode == 'green':
            color = (0, 255, 0)
        elif color_mode == 'erase':
            color = (0, 0, 0)

        pygame.draw.circle(screen, color, (x, y), width)


def drawfig(screen, start, end, width, color_mode, draw_mode):
    x1, y1 = start
    x2, y2 = end

    if color_mode == 'blue':
        color = (0, 0, 255)
    elif color_mode == 'red':
        color = (255, 0, 0)
    elif color_mode == 'green':
        color = (0, 255, 0)
    elif color_mode == 'erase':
        color = (0, 0, 0)

    if draw_mode == 2:
        rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        pygame.draw.rect(screen, color, rect, width)

    elif draw_mode == 3:
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        r = int(math.hypot(x2 - x1, y2 - y1) / 2)
        pygame.draw.circle(screen, color, (cx, cy), max(1, r), width)


def main():
    global mode, radius, drawing_mode, points, figures, strokes, figures_perm, fig_start, drawing

    running = True

    while running:
        pressed = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        alt_held = pressed[pygame.K_LALT] or pressed[pygame.K_RALT]
        ctrl_held = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_l:
                    drawing_mode = 1
                elif event.key == pygame.K_z:
                    drawing_mode = 2
                elif event.key == pygame.K_x:
                    drawing_mode = 3
                elif event.key == pygame.K_a:
                    strokes = []
                    figures_perm = []
                    points = []

                elif event.key == pygame.K_c:
                    mode = 'erase'

                elif event.key == pygame.K_p:
                    drawing = not drawing

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:
                    radius = max(1, radius + 1)

                    if drawing_mode in (2, 3):
                        fig_start = mouse_pos

                    if drawing_mode == 1 and points:
                        strokes.append((points.copy(), mode, radius))
                        points = []

                elif event.button == 3:
                    radius = max(1, radius - 1)

                if r.collidepoint(mouse_pos):
                    mode = 'red'
                elif g.collidepoint(mouse_pos):
                    mode = 'green'
                elif b.collidepoint(mouse_pos):
                    mode = 'blue'

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if drawing_mode == 1:
                        strokes.append((points.copy(), mode, radius))
                        points = []

                    if drawing_mode in (2, 3):
                        figures_perm.append(((fig_start, mouse_pos), mode, radius, drawing_mode))
                        figures = []

            if event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:
                    if drawing_mode == 1:
                        points.append(mouse_pos)
                        points = points[-256:]

                    if drawing_mode in (2, 3):
                        figures = [(fig_start, mouse_pos)]

        screen.fill((0, 0, 0))

        for pts, col_mode, rad in strokes:
            for i in range(len(pts) - 1):
                drawLineBetween(screen, i, pts[i], pts[i + 1], rad, col_mode)

        for coords, col_mode, rad, d_mode in figures_perm:
            st, et = coords
            drawfig(screen, st, et, rad, col_mode, d_mode)

        if drawing and len(points) > 1:
            for i in range(len(points) - 1):
                drawLineBetween(screen, i, points[i], points[i + 1], radius, mode)

        if drawing_mode in (2, 3) and figures:
            s, e = figures[0]
            drawfig(screen, s, e, radius, mode, drawing_mode)

        
        font = pygame.font.SysFont(None, 26)
        p_text = font.render(text, True, (255, 255, 255))
        screen.blit(p_text, (10, 10))

        
        pygame.draw.rect(screen, (0, 0, 255), b)
        pygame.draw.rect(screen, (255, 0, 0), r)
        pygame.draw.rect(screen, (0, 255, 0), g)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


main()