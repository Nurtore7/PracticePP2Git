# paint.py
import pygame
import sys
from datetime import datetime
from tools import *

class PaintApp:
    def __init__(self):
        pygame.init()
        
        info = pygame.display.Info()
        self.screen_width = info.current_w
        self.screen_height = info.current_h
        
        self.toolbar_width = 220
        self.canvas_width = self.screen_width - self.toolbar_width
        self.canvas_height = self.screen_height
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption("Paint Application")
        
        # Создаем чистый белый холст
        self.canvas = pygame.Surface((self.canvas_width, self.canvas_height))
        self.canvas.fill((255, 255, 255))
        
        self.current_color = (0, 0, 0)
        self.colors = [
            (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255),
            (255, 255, 0), (255, 0, 255), (0, 255, 255), (255, 255, 255)
        ]
        
        self.brush_sizes = {pygame.K_1: 2, pygame.K_2: 5, pygame.K_3: 10}
        self.current_brush_size = 5
        
        self.current_tool = "pencil"
        self.tools = {
            "pencil": Pencil(self.current_brush_size),
            "line": Line(self.current_brush_size),
            "rectangle": Rectangle(self.current_brush_size),
            "circle": Circle(self.current_brush_size),
            "square": Square(self.current_brush_size),
            "right_triangle": RightTriangle(self.current_brush_size),
            "equilateral_triangle": EquilateralTriangle(self.current_brush_size),
            "triangle": Triangle(self.current_brush_size),
            "rhombus": Rhombus(self.current_brush_size),
            "eraser": Eraser(20),
            "flood_fill": FloodFill(),
            "text": Text(36)
        }
        
        self.tools["text"].initialize_font()
        self.update_brush_sizes()
        self.create_toolbar()
        
        self.is_drawing = False
        self.clock = pygame.time.Clock()
        self.toolbar_font = pygame.font.SysFont('arial', 18)
    
    def update_brush_sizes(self):
        for tool_name, tool in self.tools.items():
            if hasattr(tool, 'brush_size'):
                tool.brush_size = self.current_brush_size
            if hasattr(tool, 'color') and tool_name != "eraser" and tool_name != "text":
                tool.color = self.current_color
    
    def create_toolbar(self):
        self.toolbar_buttons = []
        
        buttons = [
            ("Pencil", "pencil"), ("Line", "line"), ("Rectangle", "rectangle"),
            ("Circle", "circle"), ("Square", "square"), ("Right Tri", "right_triangle"),
            ("Equil Tri", "equilateral_triangle"), ("Triangle", "triangle"),
            ("Rhombus", "rhombus"), ("Eraser", "eraser"), ("Flood Fill", "flood_fill"),
            ("Text", "text")
        ]
        
        button_height = 40
        button_width = self.toolbar_width - 20
        start_y = 10
        
        for i, (label, tool_name) in enumerate(buttons):
            button_rect = pygame.Rect(10, start_y + i * 45, button_width, button_height)
            self.toolbar_buttons.append({
                'rect': button_rect, 'tool': tool_name, 'label': label
            })
        
        color_size = 35
        colors_start_y = start_y + len(buttons) * 45 + 10
        
        for i, color in enumerate(self.colors):
            row = i // 2
            col = i % 2
            x = 10 + col * 40
            y = colors_start_y + row * 40
            button_rect = pygame.Rect(x, y, color_size, color_size)
            self.toolbar_buttons.append({
                'rect': button_rect, 'tool': 'color', 'color_value': color
            })
        
        save_rect = pygame.Rect(10, self.screen_height - 60, button_width, 40)
        self.toolbar_buttons.append({
            'rect': save_rect, 'tool': 'save', 'label': 'SAVE (Ctrl+S)'
        })
        
        self.brush_info_rect = pygame.Rect(10, self.screen_height - 120, button_width, 30)
    
    def draw_toolbar(self):
        toolbar_surface = pygame.Surface((self.toolbar_width, self.screen_height))
        toolbar_surface.fill((240, 240, 240))
        
        pygame.draw.line(toolbar_surface, (180, 180, 180), (0, 0), (0, self.screen_height), 3)
        
        for button in self.toolbar_buttons:
            if button['tool'] == 'color':
                pygame.draw.rect(toolbar_surface, button['color_value'], button['rect'])
                pygame.draw.rect(toolbar_surface, (0, 0, 0), button['rect'], 2)
            else:
                if button['tool'] == self.current_tool:
                    color = (180, 180, 255)
                else:
                    color = (230, 230, 230)
                pygame.draw.rect(toolbar_surface, color, button['rect'])
                pygame.draw.rect(toolbar_surface, (100, 100, 100), button['rect'], 2)
                
                if 'label' in button and button['label']:
                    text = self.toolbar_font.render(button['label'], True, (0, 0, 0))
                    text_rect = text.get_rect(center=button['rect'].center)
                    toolbar_surface.blit(text, text_rect)
        
        brush_text = self.toolbar_font.render(f"Brush: {self.current_brush_size}px", True, (0, 0, 0))
        text_rect = brush_text.get_rect(center=self.brush_info_rect.center)
        toolbar_surface.blit(brush_text, text_rect)
        
        y = self.screen_height - 200
        instructions = ["1,2,3 = Brush size", "ESC = Exit", "Ctrl+S = Save"]
        for instr in instructions:
            text = self.toolbar_font.render(instr, True, (80, 80, 80))
            toolbar_surface.blit(text, (10, y))
            y += 25
        
        self.screen.blit(toolbar_surface, (self.canvas_width, 0))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.save_canvas()
                if event.key in self.brush_sizes:
                    self.current_brush_size = self.brush_sizes[event.key]
                    self.update_brush_sizes()
            
            # Обработка текста
            if self.current_tool == "text" and self.tools["text"].active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # Сохраняем текст на canvas
                        text_obj = self.tools["text"]
                        if text_obj.current_text and text_obj.text_position:
                            text_surface = text_obj.font.render(text_obj.current_text, True, (0, 0, 0))
                            self.canvas.blit(text_surface, text_obj.text_position)
                            print(f"✅ Text saved: '{text_obj.current_text}'")
                        text_obj.active = False
                        text_obj.current_text = ""
                        text_obj.text_position = None
                    elif event.key == pygame.K_ESCAPE:
                        self.tools["text"].active = False
                        self.tools["text"].current_text = ""
                        self.tools["text"].text_position = None
                    elif event.key == pygame.K_BACKSPACE:
                        self.tools["text"].current_text = self.tools["text"].current_text[:-1]
                    else:
                        if event.unicode and event.unicode.isprintable():
                            self.tools["text"].current_text += event.unicode
                    continue
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.tools["text"].active = False
                    self.tools["text"].current_text = ""
                    self.tools["text"].text_position = None
                    continue
            
            # Обработка мыши
            mouse_pos = pygame.mouse.get_pos()
            canvas_pos = (mouse_pos[0], mouse_pos[1])
            mouse_pressed = pygame.mouse.get_pressed()
            on_canvas = (canvas_pos[0] < self.canvas_width and canvas_pos[0] >= 0)
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if canvas_pos[0] >= self.canvas_width:
                    self.check_toolbar_click(mouse_pos)
                elif on_canvas:
                    if self.current_tool == "flood_fill":
                        self.tools["flood_fill"].color = self.current_color
                        result = self.tools["flood_fill"].handle_event(self.canvas, canvas_pos, mouse_pressed)
                        if result:
                            self.canvas = result
                    elif self.current_tool == "text":
                        if not self.tools["text"].active:
                            self.tools["text"].activate(canvas_pos)
                    else:
                        self.is_drawing = True
                        result = self.tools[self.current_tool].handle_event(self.canvas, canvas_pos, mouse_pressed)
                        if result:
                            self.canvas = result
            
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.is_drawing and on_canvas and self.current_tool not in ["text", "flood_fill"]:
                    result = self.tools[self.current_tool].handle_event(self.canvas, canvas_pos, mouse_pressed)
                    if result:
                        self.canvas = result
                    self.is_drawing = False
            
            elif event.type == pygame.MOUSEMOTION:
                if on_canvas:
                    if hasattr(self.tools[self.current_tool], 'update_end_pos'):
                        self.tools[self.current_tool].update_end_pos(canvas_pos)
                    
                    if self.is_drawing and self.current_tool in ["pencil", "eraser"]:
                        result = self.tools[self.current_tool].handle_event(self.canvas, canvas_pos, mouse_pressed)
                        if result:
                            self.canvas = result
        
        return True
    
    def check_toolbar_click(self, mouse_pos):
        x, y = mouse_pos
        toolbar_x = x - self.canvas_width
        
        for button in self.toolbar_buttons:
            if button['rect'].collidepoint(toolbar_x, y):
                if button['tool'] == 'color':
                    self.current_color = button['color_value']
                    self.update_brush_sizes()
                elif button['tool'] == 'save':
                    self.save_canvas()
                elif button['tool'] == 'eraser':
                    self.current_tool = button['tool']
                    self.tools["eraser"].color = (255, 255, 255)
                else:
                    self.current_tool = button['tool']
                    if button['tool'] != "text":
                        self.tools["text"].active = False
                return True
        return False
    
    def save_canvas(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"canvas_{timestamp}.png"
        pygame.image.save(self.canvas, filename)
        print(f"✅ Canvas saved: {filename}")
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            
            # Отображаем canvas
            display = self.canvas.copy()
            
            # Предпросмотр текста
            if self.current_tool == "text" and self.tools["text"].active:
                text_obj = self.tools["text"]
                if text_obj.text_position and text_obj.font:
                    display_text = text_obj.current_text
                    if text_obj.cursor_visible:
                        display_text += "|"
                    text_surface = text_obj.font.render(display_text, True, (0, 0, 0))
                    display.blit(text_surface, text_obj.text_position)
                    
                    # Обновление курсора
                    current_time = pygame.time.get_ticks()
                    if current_time - text_obj.cursor_timer > 500:
                        text_obj.cursor_visible = not text_obj.cursor_visible
                        text_obj.cursor_timer = current_time
            
            # Предпросмотр фигур
            elif self.current_tool in ["line", "rectangle", "circle", "square", "right_triangle", "equilateral_triangle", "triangle", "rhombus"]:
                if hasattr(self.tools[self.current_tool], 'drawing') and self.tools[self.current_tool].drawing:
                    self.tools[self.current_tool].draw_preview(display)
            
            self.screen.fill((255, 255, 255))
            self.screen.blit(display, (0, 0))
            self.draw_toolbar()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = PaintApp()
    app.run()