import pygame
import sys
import os
from datetime import datetime
from tools import Button, ToolType, FloodFill, TextInput

pygame.init()

# Константы - увеличил высоту окна
WIDTH = 1200
HEIGHT = 800
TOOLBAR_HEIGHT = 100
CANVAS_HEIGHT = HEIGHT - TOOLBAR_HEIGHT

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
LIGHT_GRAY = (220, 220, 220)

# Размеры кисти
BRUSH_SIZES = {
    'small': 2,
    'medium': 5,
    'large': 10
}

class PaintApp:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Paint App - Extended Version")
        self.clock = pygame.time.Clock()
        
        # Состояние рисования
        self.drawing = False
        self.start_pos = None
        self.last_pos = None
        self.tool = ToolType.PEN
        self.color = BLACK
        self.brush_size = BRUSH_SIZES['medium']
        self.brush_size_name = 'medium'
        
        # Канвас
        self.canvas = pygame.Surface((WIDTH, CANVAS_HEIGHT))
        self.canvas.fill(WHITE)
        
        # Текстовый ввод
        self.text_input = None
        
        # Создание папки для сохранений
        if not os.path.exists('assets'):
            os.makedirs('assets')
        
        # Создание кнопок
        self.create_buttons()
        
        self.running = True
        
        # Подсказки
        self.show_help = True
        self.help_timer = 180
    
    def create_buttons(self):
        btn_w = 55
        btn_h = 30
        # Отступы
        top_padding = 8
        spacing = 3
        
        # РЯД 1: Цвета (9 кнопок)
        row1_y = CANVAS_HEIGHT + top_padding
        x = 10
        
        self.color_buttons = [
            Button(x, row1_y, btn_w, btn_h, "Black", BLACK, WHITE),
            Button(x + (btn_w + spacing), row1_y, btn_w, btn_h, "Red", RED),
            Button(x + (btn_w + spacing) * 2, row1_y, btn_w, btn_h, "Green", GREEN),
            Button(x + (btn_w + spacing) * 3, row1_y, btn_w, btn_h, "Blue", BLUE),
            Button(x + (btn_w + spacing) * 4, row1_y, btn_w, btn_h, "Yellow", YELLOW),
            Button(x + (btn_w + spacing) * 5, row1_y, btn_w, btn_h, "Orange", ORANGE),
            Button(x + (btn_w + spacing) * 6, row1_y, btn_w, btn_h, "Purple", PURPLE),
            Button(x + (btn_w + spacing) * 7, row1_y, btn_w, btn_h, "Cyan", CYAN),
            Button(x + (btn_w + spacing) * 8, row1_y, btn_w, btn_h, "Pink", PINK),
        ]
        
        # РЯД 2: Инструменты + Размеры + Очистка
        row2_y = row1_y + btn_h + spacing
        
        self.tool_buttons = [
            Button(x, row2_y, btn_w, btn_h, "Pen", LIGHT_GRAY),
            Button(x + (btn_w + spacing), row2_y, btn_w, btn_h, "Line", LIGHT_GRAY),
            Button(x + (btn_w + spacing) * 2, row2_y, btn_w, btn_h, "Rect", LIGHT_GRAY),
            Button(x + (btn_w + spacing) * 3, row2_y, btn_w, btn_h, "Circle", LIGHT_GRAY),
            Button(x + (btn_w + spacing) * 4, row2_y, btn_w, btn_h, "Square", LIGHT_GRAY),
            Button(x + (btn_w + spacing) * 5, row2_y, btn_w, btn_h, "Triangle", LIGHT_GRAY),
            Button(x + (btn_w + spacing) * 6, row2_y, btn_w, btn_h, "EqTri", LIGHT_GRAY),
            Button(x + (btn_w + spacing) * 7, row2_y, btn_w, btn_h, "Rhombus", LIGHT_GRAY),
            Button(x + (btn_w + spacing) * 8, row2_y, btn_w, btn_h, "Eraser", LIGHT_GRAY),
            Button(x + (btn_w + spacing) * 9, row2_y, btn_w, btn_h, "Fill", LIGHT_GRAY),
            Button(x + (btn_w + spacing) * 10, row2_y, btn_w, btn_h, "Text", LIGHT_GRAY),
        ]
        
        # Кнопки размера кисти (в том же ряду, справа)
        size_start_x = x + (btn_w + spacing) * 11 + 20
        self.size_buttons = [
            Button(size_start_x, row2_y, 45, btn_h, "S", LIGHT_GRAY),
            Button(size_start_x + 48, row2_y, 45, btn_h, "M", LIGHT_GRAY),
            Button(size_start_x + 96, row2_y, 45, btn_h, "L", LIGHT_GRAY),
        ]
        
        # Кнопка очистки
        clear_x = size_start_x + 150
        self.clear_btn = Button(clear_x, row2_y, 80, btn_h, "Clear", RED, WHITE)
        
        # Информационная панель (справа вверху)
        info_x = WIDTH - 200
        info_y = CANVAS_HEIGHT + top_padding
        self.info_bg = pygame.Rect(info_x, info_y, 190, 65)
        
        # Выбор первого инструмента
        self.tool_buttons[0].selected = True
        self.size_buttons[1].selected = True
    
    def draw_toolbar(self):
        # Фон панели инструментов
        pygame.draw.rect(self.screen, GRAY, (0, CANVAS_HEIGHT, WIDTH, TOOLBAR_HEIGHT))
        pygame.draw.line(self.screen, BLACK, (0, CANVAS_HEIGHT), (WIDTH, CANVAS_HEIGHT), 2)
        
        # Рисуем все кнопки
        for btn in self.color_buttons:
            btn.draw(self.screen)
        for btn in self.tool_buttons:
            btn.draw(self.screen)
        for btn in self.size_buttons:
            btn.draw(self.screen)
        self.clear_btn.draw(self.screen)
        
        # Информационная панель
        pygame.draw.rect(self.screen, DARK_GRAY, self.info_bg)
        pygame.draw.rect(self.screen, BLACK, self.info_bg, 2)
        
        font = pygame.font.SysFont("Arial", 12)
        tool_text = font.render(f"Tool: {self.tool.value}", True, WHITE)
        color_text = font.render(f"Color: {self.get_color_name()}", True, self.color)
        size_text = font.render(f"Size: {self.brush_size}px", True, WHITE)
        
        self.screen.blit(tool_text, (self.info_bg.x + 5, self.info_bg.y + 8))
        self.screen.blit(color_text, (self.info_bg.x + 5, self.info_bg.y + 26))
        self.screen.blit(size_text, (self.info_bg.x + 5, self.info_bg.y + 44))
        
        # Подсказки внизу экрана
        if self.show_help and self.help_timer > 0:
            help_surface = pygame.Surface((WIDTH, 35))
            help_surface.set_alpha(200)
            help_surface.fill(BLACK)
            self.screen.blit(help_surface, (0, HEIGHT - 35))
            
            font_small = pygame.font.SysFont("Arial", 10)
            tips = "1,2,3 - brush size | Ctrl+S - save | Text: click, type, Enter, Esc | H - hide"
            tip_text = font_small.render(tips, True, WHITE)
            self.screen.blit(tip_text, (10, HEIGHT - 24))
            
            self.help_timer -= 1
        else:
            self.show_help = False
    
    def get_color_name(self):
        colors = {
            BLACK: "Black", RED: "Red", GREEN: "Green", BLUE: "Blue",
            YELLOW: "Yellow", ORANGE: "Orange", PURPLE: "Purple",
            CYAN: "Cyan", PINK: "Pink"
        }
        return colors.get(self.color, "Color")
    
    def draw_on_canvas(self, pos):
        if self.tool == ToolType.PEN:
            pygame.draw.circle(self.canvas, self.color, pos, self.brush_size)
        elif self.tool == ToolType.ERASER:
            pygame.draw.circle(self.canvas, WHITE, pos, self.brush_size + 2)
    
    def draw_line_on_canvas(self, start, end):
        if self.tool == ToolType.PEN:
            pygame.draw.line(self.canvas, self.color, start, end, self.brush_size * 2)
        elif self.tool == ToolType.ERASER:
            pygame.draw.line(self.canvas, WHITE, start, end, (self.brush_size + 2) * 2)
    
    def draw_shape(self, start, end):
        x1, y1 = start
        x2, y2 = end
        rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        
        if self.tool == ToolType.RECT:
            pygame.draw.rect(self.canvas, self.color, rect, self.brush_size)
        elif self.tool == ToolType.SQUARE:
            size = max(abs(x2 - x1), abs(y2 - y1))
            square_rect = pygame.Rect(min(x1, x2), min(y1, y2), size, size)
            pygame.draw.rect(self.canvas, self.color, square_rect, self.brush_size)
        elif self.tool == ToolType.CIRCLE:
            radius = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
            pygame.draw.circle(self.canvas, self.color, start, radius, self.brush_size)
        elif self.tool == ToolType.TRIANGLE:
            points = [start, (x2, y2), (x1, y2)]
            pygame.draw.polygon(self.canvas, self.color, points, self.brush_size)
        elif self.tool == ToolType.EQ_TRIANGLE:
            height = abs(y2 - y1)
            width = abs(x2 - x1)
            points = [start, (start[0] + width, start[1]), (start[0] + width // 2, start[1] - height)]
            pygame.draw.polygon(self.canvas, self.color, points, self.brush_size)
        elif self.tool == ToolType.RHOMBUS:
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            dx = abs(x2 - x1) // 2
            dy = abs(y2 - y1) // 2
            points = [
                (center_x, center_y - dy),
                (center_x + dx, center_y),
                (center_x, center_y + dy),
                (center_x - dx, center_y)
            ]
            pygame.draw.polygon(self.canvas, self.color, points, self.brush_size)
        elif self.tool == ToolType.LINE:
            pygame.draw.line(self.canvas, self.color, start, end, self.brush_size * 2)
    
    def draw_shape_preview(self, start, end):
        x1, y1 = start
        x2, y2 = end
        rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        
        if self.tool == ToolType.RECT:
            pygame.draw.rect(self.screen, self.color, rect, self.brush_size)
        elif self.tool == ToolType.SQUARE:
            size = max(abs(x2 - x1), abs(y2 - y1))
            square_rect = pygame.Rect(min(x1, x2), min(y1, y2), size, size)
            pygame.draw.rect(self.screen, self.color, square_rect, self.brush_size)
        elif self.tool == ToolType.CIRCLE:
            radius = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
            pygame.draw.circle(self.screen, self.color, start, radius, self.brush_size)
        elif self.tool == ToolType.TRIANGLE:
            points = [start, (x2, y2), (x1, y2)]
            pygame.draw.polygon(self.screen, self.color, points, self.brush_size)
        elif self.tool == ToolType.EQ_TRIANGLE:
            height = abs(y2 - y1)
            width = abs(x2 - x1)
            points = [start, (start[0] + width, start[1]), (start[0] + width // 2, start[1] - height)]
            pygame.draw.polygon(self.screen, self.color, points, self.brush_size)
        elif self.tool == ToolType.RHOMBUS:
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            dx = abs(x2 - x1) // 2
            dy = abs(y2 - y1) // 2
            points = [
                (center_x, center_y - dy),
                (center_x + dx, center_y),
                (center_x, center_y + dy),
                (center_x - dx, center_y)
            ]
            pygame.draw.polygon(self.screen, self.color, points, self.brush_size)
        elif self.tool == ToolType.LINE:
            pygame.draw.line(self.screen, self.color, start, end, self.brush_size * 2)
    
    def save_canvas(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"assets/drawing_{timestamp}.png"
        pygame.image.save(self.canvas, filename)
        print(f"Canvas saved as {filename}")
        
        # Показать уведомление
        font = pygame.font.SysFont("Arial", 20)
        save_text = font.render(f"Saved: {filename}", True, GREEN)
        text_rect = save_text.get_rect(center=(WIDTH // 2, CANVAS_HEIGHT // 2))
        
        temp_surface = self.screen.copy()
        self.screen.blit(temp_surface, (0, 0))
        pygame.draw.rect(self.screen, BLACK, text_rect.inflate(20, 10))
        pygame.draw.rect(self.screen, WHITE, text_rect.inflate(20, 10), 2)
        self.screen.blit(save_text, text_rect)
        pygame.display.update()
        pygame.time.wait(1500)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Обработка текстового ввода
            if self.text_input:
                self.text_input.handle_event(event)
                if self.text_input.confirmed:
                    text_surface = self.text_input.font.render(
                        self.text_input.text, True, self.color
                    )
                    self.canvas.blit(text_surface, self.text_input.position)
                    self.text_input = None
                elif self.text_input.cancelled:
                    self.text_input = None
                continue
            
            # Горячие клавиши
            if event.type == pygame.KEYDOWN:
                if event.mod & pygame.KMOD_CTRL and event.key == pygame.K_s:
                    self.save_canvas()
                elif event.key == pygame.K_1:
                    self.set_brush_size('small')
                elif event.key == pygame.K_2:
                    self.set_brush_size('medium')
                elif event.key == pygame.K_3:
                    self.set_brush_size('large')
                elif event.key == pygame.K_h:
                    self.show_help = not self.show_help
                    if self.show_help:
                        self.help_timer = 180
            
            # Обработка мыши
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                
                # Проверка кликов по кнопкам
                for btn in self.color_buttons:
                    if btn.check_click(pos):
                        color_map = {
                            "Black": BLACK, "Red": RED, "Green": GREEN,
                            "Blue": BLUE, "Yellow": YELLOW, "Orange": ORANGE,
                            "Purple": PURPLE, "Cyan": CYAN, "Pink": PINK
                        }
                        self.color = color_map.get(btn.text, BLACK)
                
                for i, btn in enumerate(self.tool_buttons):
                    if btn.check_click(pos):
                        for b in self.tool_buttons:
                            b.selected = False
                        btn.selected = True
                        tools = [
                            ToolType.PEN, ToolType.LINE, ToolType.RECT,
                            ToolType.CIRCLE, ToolType.SQUARE, ToolType.TRIANGLE,
                            ToolType.EQ_TRIANGLE, ToolType.RHOMBUS, ToolType.ERASER,
                            ToolType.FILL, ToolType.TEXT
                        ]
                        self.tool = tools[i]
                
                for i, btn in enumerate(self.size_buttons):
                    if btn.check_click(pos):
                        for b in self.size_buttons:
                            b.selected = False
                        btn.selected = True
                        sizes = ['small', 'medium', 'large']
                        self.set_brush_size(sizes[i])
                
                if self.clear_btn.check_click(pos):
                    self.canvas.fill(WHITE)
                
                # Рисование на канвасе
                if pos[1] < CANVAS_HEIGHT:
                    if self.tool == ToolType.FILL:
                        FloodFill.flood_fill(self.canvas, pos, self.color)
                    elif self.tool == ToolType.TEXT:
                        self.text_input = TextInput(pos)
                    else:
                        self.drawing = True
                        self.start_pos = pos
                        self.last_pos = pos
                        if self.tool not in [ToolType.RECT, ToolType.CIRCLE, ToolType.SQUARE,
                                            ToolType.TRIANGLE, ToolType.EQ_TRIANGLE,
                                            ToolType.RHOMBUS, ToolType.LINE]:
                            self.draw_on_canvas(pos)
            
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.drawing and self.start_pos:
                    if self.tool in [ToolType.RECT, ToolType.CIRCLE, ToolType.SQUARE,
                                    ToolType.TRIANGLE, ToolType.EQ_TRIANGLE,
                                    ToolType.RHOMBUS, ToolType.LINE]:
                        self.draw_shape(self.start_pos, event.pos)
                self.drawing = False
                self.start_pos = None
                self.last_pos = None
            
            elif event.type == pygame.MOUSEMOTION and self.drawing:
                pos = event.pos
                if pos[1] < CANVAS_HEIGHT:
                    if self.tool in [ToolType.RECT, ToolType.CIRCLE, ToolType.SQUARE,
                                    ToolType.TRIANGLE, ToolType.EQ_TRIANGLE,
                                    ToolType.RHOMBUS, ToolType.LINE]:
                        pass
                    else:
                        if self.last_pos:
                            self.draw_line_on_canvas(self.last_pos, pos)
                        self.draw_on_canvas(pos)
                        self.last_pos = pos
    
    def set_brush_size(self, size_name):
        self.brush_size_name = size_name
        self.brush_size = BRUSH_SIZES[size_name]
    
    def draw(self):
        self.screen.blit(self.canvas, (0, 0))
        
        # Предпросмотр фигур
        if self.drawing and self.start_pos and self.tool in [
            ToolType.RECT, ToolType.CIRCLE, ToolType.SQUARE,
            ToolType.TRIANGLE, ToolType.EQ_TRIANGLE,
            ToolType.RHOMBUS, ToolType.LINE
        ]:
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[1] < CANVAS_HEIGHT:
                self.draw_shape_preview(self.start_pos, mouse_pos)
        
        # Отображение текстового ввода
        if self.text_input:
            self.text_input.draw(self.screen)
        
        self.draw_toolbar()
        
        # Отображение текущего размера кисти под курсором
        if self.drawing and self.tool == ToolType.PEN:
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[1] < CANVAS_HEIGHT:
                pygame.draw.circle(self.screen, self.color, mouse_pos, self.brush_size, 1)
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = PaintApp()
    app.run()