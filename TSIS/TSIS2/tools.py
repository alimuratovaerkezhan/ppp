import pygame
from enum import Enum

class ToolType(Enum):
    PEN = "Pen"
    LINE = "Line"
    RECT = "Rect"
    CIRCLE = "Circle"
    SQUARE = "Square"
    TRIANGLE = "Triangle"
    EQ_TRIANGLE = "EqTriangle"
    RHOMBUS = "Rhombus"
    ERASER = "Eraser"
    FILL = "Fill"
    TEXT = "Text"

class Button:
    def __init__(self, x, y, w, h, text, color, text_color=(0, 0, 0)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.selected = False
        self.font = pygame.font.SysFont("Arial", 14)
    
    def draw(self, surface):
        color = self.color
        if self.selected:
            color = (
                min(255, color[0] + 50),
                min(255, color[1] + 50),
                min(255, color[2] + 50)
            )
        
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def check_click(self, pos):
        return self.rect.collidepoint(pos)

class FloodFill:
    @staticmethod
    def flood_fill(surface, start_pos, fill_color):
        """Алгоритм заливки с использованием стека"""
        try:
            # Получаем цвет в начальной точке
            start_color = surface.get_at(start_pos)
            
            # Если цвета совпадают, ничего не делаем
            if start_color == fill_color:
                return
            
            # Используем стек вместо рекурсии для избежания RecursionError
            stack = [start_pos]
            width, height = surface.get_size()
            
            # Множество посещенных пикселей
            visited = set()
            
            while stack:
                x, y = stack.pop()
                
                # Проверка границ
                if x < 0 or x >= width or y < 0 or y >= height:
                    continue
                
                # Проверка, был ли уже посещен
                if (x, y) in visited:
                    continue
                
                # Получаем цвет текущего пикселя
                current_color = surface.get_at((x, y))
                
                # Если цвет совпадает с начальным, закрашиваем
                if current_color == start_color:
                    surface.set_at((x, y), fill_color)
                    visited.add((x, y))
                    
                    # Добавляем соседние пиксели в стек
                    stack.append((x + 1, y))
                    stack.append((x - 1, y))
                    stack.append((x, y + 1))
                    stack.append((x, y - 1))
        except Exception as e:
            print(f"Flood fill error: {e}")

class TextInput:
    def __init__(self, position):
        self.position = position
        self.text = ""
        self.active = True
        self.confirmed = False
        self.cancelled = False
        self.font = pygame.font.SysFont("Arial", 24)
        self.cursor_visible = True
        self.cursor_timer = 0
    
    def handle_event(self, event):
        if not self.active:
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.confirmed = True
                self.active = False
            elif event.key == pygame.K_ESCAPE:
                self.cancelled = True
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                # Добавляем символ, если это печатаемый символ
                if event.unicode and event.unicode.isprintable():
                    self.text += event.unicode
    
    def draw(self, surface):
        if not self.active:
            return
        
        # Обновление курсора
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
        
        # Рендерим текст
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(topleft=self.position)
        
        # Фон для текста
        padding = 5
        bg_rect = text_rect.inflate(padding * 2, padding)
        pygame.draw.rect(surface, (255, 255, 255), bg_rect)
        pygame.draw.rect(surface, (0, 0, 0), bg_rect, 2)
        
        # Рисуем текст
        surface.blit(text_surface, text_rect)
        
        # Рисуем курсор
        if self.cursor_visible:
            cursor_x = text_rect.right
            cursor_y = text_rect.y
            pygame.draw.line(surface, (0, 0, 0), 
                           (cursor_x, cursor_y), 
                           (cursor_x, cursor_y + self.font.get_height()), 2)