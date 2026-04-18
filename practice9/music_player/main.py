import pygame
import os

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

storage = ["music/Justin_Bieber.mp3", "music/love.mp3"]

cur = 0
paused = False


def play_music():
    global paused
    pygame.mixer.music.stop()

    if not os.path.exists(storage[cur]):
        return

    pygame.mixer.music.load(storage[cur])
    pygame.mixer.music.play(-1)
    paused = False


def stop_music():
    global paused
    pygame.mixer.music.stop()
    paused = False


def next_track():
    global cur
    cur = (cur + 1) % len(storage)
    play_music()


def previous_track():
    global cur
    cur = (cur - 1) % len(storage)
    play_music()


def pause_music():
    global paused
    if pygame.mixer.music.get_busy() and not paused:
        pygame.mixer.music.pause()
        paused = True
    elif paused:
        pygame.mixer.music.unpause()
        paused = False


screen = pygame.display.set_mode((700, 550))
pygame.display.set_caption("Music Player")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

play_music()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                if not pygame.mixer.music.get_busy() and not paused:
                    play_music()
                elif paused:
                    pause_music()

            elif event.key == pygame.K_s:
                stop_music()

            elif event.key == pygame.K_n:
                next_track()

            elif event.key == pygame.K_b:
                previous_track()

            elif event.key == pygame.K_q:
                running = False

    screen.fill((255, 255, 255))

    track_name = os.path.basename(storage[cur]).replace('.mp3', '')
    screen.blit(font.render(f"Now Playing: {track_name}", True, (0, 0, 0)), (50, 50))

    screen.blit(
        small_font.render(f"Track {cur + 1} of {len(storage)}", True, (100, 100, 100)),
        (50, 100)
    )

    if paused:
        status = "PAUSED"
        color = (255, 0, 0)
    elif pygame.mixer.music.get_busy():
        status = "PLAYING"
        color = (0, 150, 0)
    else:
        status = "STOPPED"
        color = (150, 0, 0)

    screen.blit(small_font.render(status, True, color), (50, 130))

    y_offset = 200
    screen.blit(small_font.render("Playlist:", True, (0, 0, 0)), (50, y_offset))

    for i, track in enumerate(storage):
        name = os.path.basename(track).replace('.mp3', '')
        text = f"> {name}" if i == cur else f"  {name}"
        screen.blit(
            small_font.render(text, True, (0, 150, 0) if i == cur else (100, 100, 100)),
            (70, y_offset + 30 + i * 25)
        )

    screen.blit(
        small_font.render(
            "Controls: P Play | S Stop | N Next | B Previous | Q Quit",
            True,
            (50, 50, 50)
        ),
        (50, 500)
    )

    pygame.display.flip()
    clock.tick(60)

pygame.quit()