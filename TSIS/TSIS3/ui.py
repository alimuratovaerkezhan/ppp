import pygame
import sys
from persistence import load_settings, save_settings, load_leaderboard

pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
DARK_GREEN = (30, 150, 30)
BLUE = (50, 150, 255)
DARK_BLUE = (30, 100, 200)
YELLOW = (255, 220, 50)
ORANGE = (255, 140, 0)
DARK_ORANGE = (200, 100, 0)
LIGHT_GRAY = (200, 200, 200)
MEDIUM_GRAY = (120, 120, 130)
DARK_GRAY = (40, 40, 50)
GOLD = (255, 200, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
LIGHT_BLUE = (100, 200, 255)
SILVER = (192, 192, 192)
BRONZE = (205, 127, 50)

class Button:
    def __init__(self, x, y, w, h, text, color, hover_color=None, text_color=WHITE, font_size=24):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color if hover_color else (
            min(255, color[0] + 40),
            min(255, color[1] + 40),
            min(255, color[2] + 40)
        )
        self.text_color = text_color
        self.is_hovered = False
        self.font = pygame.font.SysFont("Arial", font_size, bold=True)
        self.shadow = True
    
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        
        if self.shadow:
            shadow_rect = self.rect.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            pygame.draw.rect(surface, DARK_GRAY, shadow_rect, border_radius=8)
        
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=8)
        
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def check_click(self, pos):
        return self.rect.collidepoint(pos)

class TextInput:
    def __init__(self, x, y, w, h, max_length=15):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.max_length = max_length
        self.active = False
        self.font = pygame.font.SysFont("Arial", 28)
        self.color_inactive = DARK_GRAY
        self.color_active = LIGHT_BLUE
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(self.text) < self.max_length and event.unicode.isprintable():
                    self.text += event.unicode
    
    def draw(self, surface):
        color = self.color_active if self.active else self.color_inactive
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        display_text = self.text + ("|" if self.active else "")
        text_surf = self.font.render(display_text, True, WHITE)
        surface.blit(text_surf, (self.rect.x + 15, self.rect.y + self.rect.height//2 - 14))
    
    def get_text(self):
        return self.text.strip() if self.text.strip() else "Player"

def draw_gradient_background(surface, width, height):
    for y in range(height):
        color_value = 20 + int(y * 30 / height)
        color = (color_value, color_value, color_value + 20)
        pygame.draw.line(surface, color, (0, y), (width, y))

def draw_panel(surface, x, y, w, h, alpha=200):
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    panel.fill((20, 20, 40, alpha))
    surface.blit(panel, (x, y))
    pygame.draw.rect(surface, (100, 100, 150, 150), (x, y, w, h), 2, border_radius=12)

def show_username_input(screen, width, height):
    clock = pygame.time.Clock()
    input_box = TextInput(width//2 - 180, height//2 - 30, 360, 60, 20)
    
    title_font = pygame.font.SysFont("Arial", 52, bold=True)
    instruction_font = pygame.font.SysFont("Arial", 20)
    subtitle_font = pygame.font.SysFont("Arial", 24)
    
    waiting = True
    while waiting:
        draw_gradient_background(screen, width, height)
        
        draw_panel(screen, width//2 - 250, height//2 - 120, 500, 220, 220)
        
        title = title_font.render("WELCOME!", True, GOLD)
        title_rect = title.get_rect(center=(width//2, height//2 - 90))
        screen.blit(title, title_rect)
        
        subtitle = subtitle_font.render("Enter your name to start racing", True, LIGHT_GRAY)
        sub_rect = subtitle.get_rect(center=(width//2, height//2 - 45))
        screen.blit(subtitle, sub_rect)
        
        instruction = instruction_font.render("Press ENTER when done", True, CYAN)
        inst_rect = instruction.get_rect(center=(width//2, height//2 + 90))
        screen.blit(instruction, inst_rect)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            input_box.handle_event(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and input_box.text:
                waiting = False
        
        input_box.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    
    return input_box.get_text()

def show_main_menu(screen, width, height):
    clock = pygame.time.Clock()
    btn_w, btn_h = 220, 65
    center_x = width // 2 - btn_w // 2
    
    play_btn = Button(center_x, height//2 - 70, btn_w, btn_h, "▶ PLAY", GREEN, DARK_GREEN)
    leaderboard_btn = Button(center_x, height//2 + 10, btn_w, btn_h, "🏆 LEADERBOARD", BLUE, DARK_BLUE)
    settings_btn = Button(center_x, height//2 + 90, btn_w, btn_h, "⚙ SETTINGS", ORANGE, DARK_ORANGE)
    quit_btn = Button(center_x, height//2 + 170, btn_w, btn_h, "✖ QUIT", RED, (180, 30, 30))
    
    title_font = pygame.font.SysFont("Arial", 72, bold=True)
    subtitle_font = pygame.font.SysFont("Arial", 22)
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.check_click(mouse_pos):
                    return "play"
                if leaderboard_btn.check_click(mouse_pos):
                    return "leaderboard"
                if settings_btn.check_click(mouse_pos):
                    return "settings"
                if quit_btn.check_click(mouse_pos):
                    return "quit"
        
        play_btn.update(mouse_pos)
        leaderboard_btn.update(mouse_pos)
        settings_btn.update(mouse_pos)
        quit_btn.update(mouse_pos)
        
        draw_gradient_background(screen, width, height)
        
        draw_panel(screen, width//2 - 280, 40, 560, 120, 180)
        
        title = title_font.render("RACER", True, GOLD)
        title_rect = title.get_rect(center=(width//2, 85))
        screen.blit(title, title_rect)
        
        subtitle = subtitle_font.render("Collect coins • Avoid obstacles • Use power-ups", True, LIGHT_GRAY)
        sub_rect = subtitle.get_rect(center=(width//2, 135))
        screen.blit(subtitle, sub_rect)
        
        play_btn.draw(screen)
        leaderboard_btn.draw(screen)
        settings_btn.draw(screen)
        quit_btn.draw(screen)
        
        version = pygame.font.SysFont("Arial", 12).render("v3.0", True, MEDIUM_GRAY)
        screen.blit(version, (width - 50, height - 20))
        
        pygame.display.flip()
        clock.tick(60)

def show_leaderboard_screen(screen, width, height):
    clock = pygame.time.Clock()
    back_btn = Button(width//2 - 90, height - 80, 180, 50, "◀ BACK", DARK_GRAY, MEDIUM_GRAY)
    title_font = pygame.font.SysFont("Arial", 48, bold=True)
    header_font = pygame.font.SysFont("Arial", 22, bold=True)
    entry_font = pygame.font.SysFont("Arial", 18)
    entries = load_leaderboard()
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.check_click(mouse_pos):
                    return
        
        back_btn.update(mouse_pos)
        draw_gradient_background(screen, width, height)
        
        draw_panel(screen, 30, 30, width - 60, height - 60, 200)
        
        title = title_font.render("LEADERBOARD", True, GOLD)
        title_rect = title.get_rect(center=(width//2, 70))
        screen.blit(title, title_rect)
        
        headers = ["#", "NAME", "SCORE", "DISTANCE", "COINS"]
        x_positions = [60, 140, 300, 500, 680]
        
        for i, header in enumerate(headers):
            header_text = header_font.render(header, True, CYAN)
            screen.blit(header_text, (x_positions[i], 130))
        
        pygame.draw.line(screen, GOLD, (40, 155), (width - 40, 155), 2)
        
        if not entries:
            empty_text = entry_font.render("✨ No scores yet! Play a game first! ✨", True, YELLOW)
            empty_rect = empty_text.get_rect(center=(width//2, 300))
            screen.blit(empty_text, empty_rect)
        else:
            for i, entry in enumerate(entries[:10]):
                y = 175 + i * 38
                
                if i == 0:
                    rank_color = GOLD
                    prefix = "🥇 "
                elif i == 1:
                    rank_color = SILVER
                    prefix = "🥈 "
                elif i == 2:
                    rank_color = BRONZE
                    prefix = "🥉 "
                else:
                    rank_color = WHITE
                    prefix = ""
                
                rank_text = entry_font.render(f"{prefix}{i + 1}", True, rank_color)
                name_text = entry_font.render(entry.name[:18], True, WHITE)
                score_text = entry_font.render(str(entry.score), True, YELLOW)
                dist_text = entry_font.render(str(int(entry.distance)), True, GREEN)
                coins_text = entry_font.render(str(entry.coins), True, ORANGE)
                
                screen.blit(rank_text, (x_positions[0], y))
                screen.blit(name_text, (x_positions[1], y))
                screen.blit(score_text, (x_positions[2], y))
                screen.blit(dist_text, (x_positions[3], y))
                screen.blit(coins_text, (x_positions[4], y))
        
        back_btn.draw(screen)
        pygame.display.flip()
        clock.tick(60)

def show_settings_screen(screen, width, height):
    clock = pygame.time.Clock()
    settings = load_settings()
    
    btn_w, btn_h = 260, 55
    center_x = width // 2 - btn_w // 2
    
    sound_btn = Button(center_x, 200, btn_w, btn_h, 
                       f"SOUND: {'ON' if settings['sound_enabled'] else 'OFF'}", 
                       GREEN if settings['sound_enabled'] else RED,
                       None, WHITE, 22)
    
    car_color_btn = Button(center_x, 280, btn_w, btn_h,
                           f"CAR: {settings['car_color'].upper()}", BLUE,
                           DARK_BLUE, WHITE, 22)
    
    difficulty_btn = Button(center_x, 360, btn_w, btn_h,
                            f"DIFFICULTY: {settings['difficulty'].upper()}", ORANGE,
                            DARK_ORANGE, WHITE, 22)
    
    save_btn = Button(center_x, 460, btn_w, btn_h, "SAVE", GREEN, DARK_GREEN, WHITE, 24)
    back_btn = Button(center_x, 530, btn_w, btn_h, "BACK", DARK_GRAY, MEDIUM_GRAY, WHITE, 24)
    
    title_font = pygame.font.SysFont("Arial", 52, bold=True)
    
    car_colors = ["green", "red", "blue", "yellow"]
    color_index = car_colors.index(settings['car_color']) if settings['car_color'] in car_colors else 0
    difficulties = ["easy", "normal", "hard"]
    diff_index = difficulties.index(settings['difficulty']) if settings['difficulty'] in difficulties else 1
    
    color_preview = {
        "green": (0, 180, 0),
        "red": (200, 0, 0),
        "blue": (0, 0, 200),
        "yellow": (200, 200, 0)
    }
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if sound_btn.check_click(mouse_pos):
                    settings['sound_enabled'] = not settings['sound_enabled']
                    sound_btn.text = f"SOUND: {'ON' if settings['sound_enabled'] else 'OFF'}"
                    sound_btn.color = GREEN if settings['sound_enabled'] else RED
                if car_color_btn.check_click(mouse_pos):
                    color_index = (color_index + 1) % len(car_colors)
                    settings['car_color'] = car_colors[color_index]
                    car_color_btn.text = f"CAR: {settings['car_color'].upper()}"
                if difficulty_btn.check_click(mouse_pos):
                    diff_index = (diff_index + 1) % len(difficulties)
                    settings['difficulty'] = difficulties[diff_index]
                    difficulty_btn.text = f"DIFFICULTY: {settings['difficulty'].upper()}"
                if save_btn.check_click(mouse_pos):
                    save_settings(settings)
                    # FIXED: After saving, return to main menu
                    return
                if back_btn.check_click(mouse_pos):
                    return
        
        sound_btn.update(mouse_pos)
        car_color_btn.update(mouse_pos)
        difficulty_btn.update(mouse_pos)
        save_btn.update(mouse_pos)
        back_btn.update(mouse_pos)
        
        draw_gradient_background(screen, width, height)
        
        draw_panel(screen, width//2 - 300, 40, 600, 550, 200)
        
        title = title_font.render("SETTINGS", True, GOLD)
        title_rect = title.get_rect(center=(width//2, 100))
        screen.blit(title, title_rect)
        
        car_preview_x = width//2 + 150
        car_preview_y = 295
        car_surf = pygame.Surface((60, 80), pygame.SRCALPHA)
        car_color = color_preview.get(settings['car_color'], (0, 180, 0))
        pygame.draw.rect(car_surf, car_color, (8, 15, 44, 55))
        pygame.draw.rect(car_surf, (135, 206, 235), (15, 20, 30, 20))
        pygame.draw.circle(car_surf, (30, 30, 30), (15, 68), 8)
        pygame.draw.circle(car_surf, (30, 30, 30), (45, 68), 8)
        screen.blit(car_surf, (car_preview_x, car_preview_y))
        
        sound_btn.draw(screen)
        car_color_btn.draw(screen)
        difficulty_btn.draw(screen)
        save_btn.draw(screen)
        back_btn.draw(screen)
        
        info_text = pygame.font.SysFont("Arial", 14).render("Changes are saved when you press SAVE", True, LIGHT_GRAY)
        screen.blit(info_text, (width//2 - info_text.get_width()//2, 610))
        
        pygame.display.flip()
        clock.tick(60)

def show_game_over_screen(screen, width, height, score, distance, coins):
    clock = pygame.time.Clock()
    retry_btn = Button(width//2 - 140, height//2 + 100, 130, 55, "RETRY", GREEN, DARK_GREEN, WHITE, 22)
    menu_btn = Button(width//2 + 10, height//2 + 100, 130, 55, "MENU", BLUE, DARK_BLUE, WHITE, 22)
    
    title_font = pygame.font.SysFont("Arial", 60, bold=True)
    big_font = pygame.font.SysFont("Arial", 32, bold=True)
    medium_font = pygame.font.SysFont("Arial", 24)
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_btn.check_click(mouse_pos):
                    return "retry"
                if menu_btn.check_click(mouse_pos):
                    return "menu"
        
        retry_btn.update(mouse_pos)
        menu_btn.update(mouse_pos)
        
        draw_gradient_background(screen, width, height)
        
        draw_panel(screen, 30, 30, width - 60, height - 60, 220)
        
        game_over = title_font.render("GAME OVER", True, RED)
        go_rect = game_over.get_rect(center=(width//2, 110))
        screen.blit(game_over, go_rect)
        
        y_pos = 190
        stats = [
            ("FINAL SCORE", str(score), YELLOW),
            ("DISTANCE", f"{int(distance)} meters", GREEN),
            ("COINS COLLECTED", str(coins), ORANGE),
        ]
        
        for title_text, value_text, color in stats:
            title_surf = medium_font.render(title_text, True, LIGHT_GRAY)
            title_rect = title_surf.get_rect(center=(width//2, y_pos))
            screen.blit(title_surf, title_rect)
            
            value_surf = big_font.render(value_text, True, color)
            value_rect = value_surf.get_rect(center=(width//2, y_pos + 35))
            screen.blit(value_surf, value_rect)
            
            y_pos += 85
        
        pygame.draw.line(screen, GOLD, (80, y_pos - 20), (width - 80, y_pos - 20), 2)
        
        retry_btn.draw(screen)
        menu_btn.draw(screen)
        
        tip_text = pygame.font.SysFont("Arial", 14).render("TIP: Collect power-ups to boost your score!", True, CYAN)
        screen.blit(tip_text, (width//2 - tip_text.get_width()//2, height - 45))
        
        pygame.display.flip()
        clock.tick(60)