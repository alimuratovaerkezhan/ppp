import pygame
import sys
from pygame.locals import *

from game import Game
from db import Database
from config import Config


class Button:
    def __init__(self, x, y, w, h, text, color, hover_color=None, text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color or (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50))
        self.text_color = text_color
        self.hovered = False
    
    def draw(self, surface, font):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
        
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered
    
    def check_click(self, pos):
        return self.rect.collidepoint(pos)


class TextInput:
    def __init__(self, x, y, w, h, max_length=20):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.max_length = max_length
        self.active = True
        self.font = pygame.font.SysFont("Arial", 24)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(self.text) < self.max_length and event.unicode.isprintable():
                    self.text += event.unicode
        return False
    
    def draw(self, surface):
        color = (200, 200, 200) if self.active else (100, 100, 100)
        pygame.draw.rect(surface, (50, 50, 50), self.rect)
        pygame.draw.rect(surface, color, self.rect, 2)
        
        text_surf = self.font.render(self.text + ("_" if self.active else ""), True, (255, 255, 255))
        surface.blit(text_surf, (self.rect.x + 5, self.rect.y + 5))
    
    def get_text(self):
        return self.text.strip()


class ColorPicker:
    def __init__(self, x, y, current_color):
        self.x = x
        self.y = y
        self.current_color = current_color
        self.colors = [
            (0, 255, 0),
            (255, 0, 0),
            (0, 0, 255),
            (255, 255, 0),
            (255, 165, 0),
            (128, 0, 128),
            (255, 192, 203),
            (0, 255, 255)
        ]
        self.size = 30
        try:
            self.selected_index = self.colors.index(current_color) if current_color in self.colors else 0
        except ValueError:
            self.selected_index = 0
            self.current_color = self.colors[0]
    
    def draw(self, surface):
        for i, color in enumerate(self.colors):
            rect = pygame.Rect(self.x + i * (self.size + 5), self.y, self.size, self.size)
            pygame.draw.rect(surface, color, rect)
            if i == self.selected_index:
                pygame.draw.rect(surface, (255, 255, 255), rect, 3)
            else:
                pygame.draw.rect(surface, (100, 100, 100), rect, 1)
    
    def handle_click(self, pos):
        for i in range(len(self.colors)):
            rect = pygame.Rect(self.x + i * (self.size + 5), self.y, self.size, self.size)
            if rect.collidepoint(pos):
                self.selected_index = i
                self.current_color = self.colors[i]
                return True
        return False
    
    def get_color(self):
        return self.current_color


class MainMenu:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.WIDTH = 600
        self.HEIGHT = 400
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Snake Game - Main Menu")
        self.clock = pygame.time.Clock()
        
        try:
            self.db = Database()
            if self.db.conn is None:
                self.db = None
                print("WARNING: Cannot connect to database!")
        except Exception as e:
            print(f"Database error: {e}")
            self.db = None
        
        self.config = Config()
        
        self.font_title = pygame.font.SysFont("Arial", 48, bold=True)
        self.font = pygame.font.SysFont("Arial", 28)
        self.font_small = pygame.font.SysFont("Arial", 20)
        
        self.state = "username"
        self.username = ""
        self.game = None
        self.personal_best = 0
        self.game_over_score = 0
        self.game_over_level = 0
        
        self.username_input = TextInput(self.WIDTH//2 - 150, 200, 300, 40)
        self.color_picker = ColorPicker(300, 230, self.config.get_snake_color())
        
        self.create_buttons()
    
    def create_buttons(self):
        center_x = self.WIDTH // 2
        btn_w = 200
        btn_h = 50
        start_y = 150
        spacing = 70
        
        self.menu_buttons = [
            Button(center_x - btn_w//2, start_y, btn_w, btn_h, "PLAY", (0, 150, 0)),
            Button(center_x - btn_w//2, start_y + spacing, btn_w, btn_h, "LEADERBOARD", (0, 0, 150)),
            Button(center_x - btn_w//2, start_y + spacing * 2, btn_w, btn_h, "SETTINGS", (150, 150, 0)),
            Button(center_x - btn_w//2, start_y + spacing * 3, btn_w, btn_h, "QUIT", (150, 0, 0))
        ]
        
        self.leaderboard_back = Button(self.WIDTH - 100, self.HEIGHT - 60, 80, 40, "BACK", (100, 100, 100))
        self.settings_back = Button(self.WIDTH - 100, self.HEIGHT - 60, 80, 40, "SAVE", (0, 100, 0))
        
        self.retry_buttons = [
            Button(center_x - 110, 300, 100, 40, "RETRY", (0, 150, 0)),
            Button(center_x + 10, 300, 100, 40, "MENU", (150, 0, 0))
        ]
    
    def draw_username_screen(self):
        self.screen.fill((0, 0, 0))
        
        title = self.font_title.render("SNAKE GAME", True, (0, 255, 0))
        self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 50))
        
        prompt = self.font.render("Enter your username:", True, (255, 255, 255))
        self.screen.blit(prompt, (self.WIDTH//2 - prompt.get_width()//2, 150))
        
        self.username_input.draw(self.screen)
        
        info = self.font_small.render("Press ENTER to continue", True, (200, 200, 200))
        self.screen.blit(info, (self.WIDTH//2 - info.get_width()//2, 300))
        
        pygame.display.flip()
    
    def draw_main_menu(self):
        self.screen.fill((0, 0, 0))
        
        title = self.font_title.render("SNAKE GAME", True, (0, 255, 0))
        self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 50))
        
        subtitle = self.font_small.render("Advanced Edition", True, (200, 200, 200))
        self.screen.blit(subtitle, (self.WIDTH//2 - subtitle.get_width()//2, 100))
        
        for button in self.menu_buttons:
            button.draw(self.screen, self.font)
        
        if self.username:
            user_text = self.font_small.render(f"Player: {self.username}", True, (255, 215, 0))
            self.screen.blit(user_text, (10, self.HEIGHT - 30))
        
        if self.personal_best > 0:
            best_text = self.font_small.render(f"Best: {self.personal_best}", True, (255, 215, 0))
            self.screen.blit(best_text, (self.WIDTH - 100, self.HEIGHT - 30))
        
        pygame.display.flip()
    
    def draw_leaderboard(self):
        self.screen.fill((0, 0, 0))
        
        title = self.font_title.render("LEADERBOARD", True, (255, 215, 0))
        self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 30))
        
        if self.db and self.db.conn:
            scores = self.db.get_leaderboard(10)
            
            headers = ["#", "Player", "Score", "Level", "Date"]
            header_y = 100
            x_positions = [40, 130, 280, 380, 460]
            
            for i, header in enumerate(headers):
                text = self.font_small.render(header, True, (255, 255, 255))
                self.screen.blit(text, (x_positions[i], header_y))
            
            y = 140
            for i, score in enumerate(scores, 1):
                username, score_val, level, played_at = score
                date_str = played_at.strftime("%m/%d") if played_at else "Unknown"
                
                rank_text = self.font_small.render(str(i), True, (255, 215, 0) if i <= 3 else (200, 200, 200))
                name_text = self.font_small.render(username[:15], True, (255, 255, 255))
                score_text = self.font_small.render(str(score_val), True, (255, 255, 255))
                level_text = self.font_small.render(str(level), True, (255, 255, 255))
                date_text = self.font_small.render(date_str, True, (200, 200, 200))
                
                self.screen.blit(rank_text, (x_positions[0], y))
                self.screen.blit(name_text, (x_positions[1], y))
                self.screen.blit(score_text, (x_positions[2], y))
                self.screen.blit(level_text, (x_positions[3], y))
                self.screen.blit(date_text, (x_positions[4], y))
                y += 30
                
                if y > self.HEIGHT - 80:
                    break
        else:
            no_data = self.font.render("Database not connected!", True, (255, 0, 0))
            self.screen.blit(no_data, (self.WIDTH//2 - no_data.get_width()//2, 200))
            
            instruction = self.font_small.render("Make sure PostgreSQL is running", True, (200, 200, 200))
            self.screen.blit(instruction, (self.WIDTH//2 - instruction.get_width()//2, 250))
        
        self.leaderboard_back.draw(self.screen, self.font)
        pygame.display.flip()
    
    def draw_settings(self):
        self.screen.fill((0, 0, 0))
        
        title = self.font_title.render("SETTINGS", True, (255, 215, 0))
        self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 30))
        
        grid_text = self.font.render("Grid Overlay:", True, (255, 255, 255))
        self.screen.blit(grid_text, (100, 120))
        
        grid_status = "ON" if self.config.get_grid_overlay() else "OFF"
        grid_color = (0, 255, 0) if self.config.get_grid_overlay() else (255, 0, 0)
        self.grid_btn = Button(300, 110, 80, 35, grid_status, grid_color)
        self.grid_btn.draw(self.screen, self.font)
        
        sound_text = self.font.render("Sound:", True, (255, 255, 255))
        self.screen.blit(sound_text, (100, 180))
        
        sound_status = "ON" if self.config.get_sound() else "OFF"
        sound_color = (0, 255, 0) if self.config.get_sound() else (255, 0, 0)
        self.sound_btn = Button(300, 170, 80, 35, sound_status, sound_color)
        self.sound_btn.draw(self.screen, self.font)
        
        color_text = self.font.render("Snake Color:", True, (255, 255, 255))
        self.screen.blit(color_text, (100, 240))
        
        self.color_picker.draw(self.screen)
        
        self.settings_back.draw(self.screen, self.font)
        
        pygame.display.flip()
    
    def draw_game_over(self):
        self.screen.fill((0, 0, 0))
        
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font_title.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(game_over_text, (self.WIDTH//2 - game_over_text.get_width()//2, 80))
        
        score_text = self.font.render(f"Final Score: {self.game_over_score}", True, (255, 255, 255))
        self.screen.blit(score_text, (self.WIDTH//2 - score_text.get_width()//2, 160))
        
        level_text = self.font.render(f"Level Reached: {self.game_over_level}", True, (0, 255, 0))
        self.screen.blit(level_text, (self.WIDTH//2 - level_text.get_width()//2, 200))
        
        if self.personal_best > 0:
            if self.personal_best < self.game_over_score:
                best_text = self.font.render("NEW PERSONAL BEST!", True, (255, 215, 0))
                self.screen.blit(best_text, (self.WIDTH//2 - best_text.get_width()//2, 240))
            else:
                best_text = self.font.render(f"Personal Best: {self.personal_best}", True, (255, 215, 0))
                self.screen.blit(best_text, (self.WIDTH//2 - best_text.get_width()//2, 240))
        
        for button in self.retry_buttons:
            button.draw(self.screen, self.font)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        clock = pygame.time.Clock()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.state == "username":
                    if self.username_input.handle_event(event):
                        self.username = self.username_input.get_text()
                        if self.username:
                            self.game = Game(self.config, self.db)
                            self.game.set_username(self.username)
                            self.personal_best = self.game.personal_best
                            self.state = "menu"
                    
                elif self.state == "menu":
                    for button in self.menu_buttons:
                        button.check_hover(pygame.mouse.get_pos())
                        if event.type == pygame.MOUSEBUTTONDOWN and button.check_click(event.pos):
                            if button.text == "PLAY":
                                self.game.reset()
                                self.state = "game"
                            elif button.text == "LEADERBOARD":
                                self.state = "leaderboard"
                            elif button.text == "SETTINGS":
                                self.state = "settings"
                            elif button.text == "QUIT":
                                running = False
                
                elif self.state == "game":
                    if self.game:
                        game_over, score, level = self.game.run()
                        if game_over:
                            self.personal_best = max(self.personal_best, score)
                            self.game_over_score = score
                            self.game_over_level = level
                            self.state = "game_over"
                
                elif self.state == "game_over":
                    for button in self.retry_buttons:
                        button.check_hover(pygame.mouse.get_pos())
                        if event.type == pygame.MOUSEBUTTONDOWN and button.check_click(event.pos):
                            if button.text == "RETRY":
                                self.game.reset()
                                self.state = "game"
                            elif button.text == "MENU":
                                self.state = "menu"
                
                elif self.state == "leaderboard":
                    self.leaderboard_back.check_hover(pygame.mouse.get_pos())
                    if event.type == pygame.MOUSEBUTTONDOWN and self.leaderboard_back.check_click(event.pos):
                        self.state = "menu"
                
                elif self.state == "settings":
                    self.draw_settings()
                    self.grid_btn.check_hover(pygame.mouse.get_pos())
                    self.sound_btn.check_hover(pygame.mouse.get_pos())
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.grid_btn.check_click(event.pos):
                            self.config.set_grid_overlay(not self.config.get_grid_overlay())
                        elif self.sound_btn.check_click(event.pos):
                            self.config.set_sound(not self.config.get_sound())
                        elif self.color_picker.handle_click(event.pos):
                            pass
                        elif self.settings_back.check_click(event.pos):
                            self.config.set_snake_color(self.color_picker.get_color())
                            self.state = "menu"
            
            if self.state == "username":
                self.draw_username_screen()
            elif self.state == "menu":
                self.draw_main_menu()
            elif self.state == "leaderboard":
                self.draw_leaderboard()
            elif self.state == "settings":
                self.draw_settings()
            elif self.state == "game_over":
                self.draw_game_over()
            
            clock.tick(60)
        
        if self.db:
            self.db.close()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    menu = MainMenu()
    menu.run()