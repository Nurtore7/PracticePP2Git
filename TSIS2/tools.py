# tools.py
import pygame
import math

class Tool:
    """Base class for all drawing tools"""
    def __init__(self):
        self.start_pos = None
        self.current_pos = None
        self.drawing = False
    
    def handle_event(self, surface, mouse_pos, mouse_pressed):
        pass
    
    def draw_preview(self, surface):
        pass

class Pencil(Tool):
    """Freehand drawing tool"""
    def __init__(self, brush_size=5):
        super().__init__()
        self.last_pos = None
        self.brush_size = brush_size
        self.color = (0, 0, 0)
    
    def handle_event(self, surface, mouse_pos, mouse_pressed):
        if mouse_pressed[0]:
            if self.last_pos is None:
                self.last_pos = mouse_pos
            pygame.draw.line(surface, self.color, self.last_pos, mouse_pos, self.brush_size)
            self.last_pos = mouse_pos
            return surface
        else:
            self.last_pos = None
        return None
    
    def draw_preview(self, surface):
        pass

class Line(Tool):
    """Straight line tool"""
    def __init__(self, brush_size=5):
        super().__init__()
        self.start_pos = None
        self.end_pos = None
        self.brush_size = brush_size
        self.color = (0, 0, 0)
        self.drawing = False
    
    def handle_event(self, surface, mouse_pos, mouse_pressed):
        if mouse_pressed[0] and not self.drawing:
            self.start_pos = mouse_pos
            self.drawing = True
            self.end_pos = mouse_pos
        elif not mouse_pressed[0] and self.drawing:
            if self.start_pos and self.end_pos:
                pygame.draw.line(surface, self.color, self.start_pos, self.end_pos, self.brush_size)
            self.start_pos = None
            self.end_pos = None
            self.drawing = False
            return surface
        return None
    
    def update_end_pos(self, mouse_pos):
        if self.drawing:
            self.end_pos = mouse_pos
    
    def draw_preview(self, surface):
        if self.drawing and self.start_pos and self.end_pos:
            pygame.draw.line(surface, self.color, self.start_pos, self.end_pos, self.brush_size)

class Rectangle(Tool):
    """Rectangle tool"""
    def __init__(self, brush_size=5):
        super().__init__()
        self.start_pos = None
        self.end_pos = None
        self.brush_size = brush_size
        self.color = (0, 0, 0)
        self.drawing = False
    
    def handle_event(self, surface, mouse_pos, mouse_pressed):
        if mouse_pressed[0] and not self.drawing:
            self.start_pos = mouse_pos
            self.drawing = True
            self.end_pos = mouse_pos
        elif not mouse_pressed[0] and self.drawing:
            if self.start_pos and self.end_pos:
                x = min(self.start_pos[0], self.end_pos[0])
                y = min(self.start_pos[1], self.end_pos[1])
                width = abs(self.end_pos[0] - self.start_pos[0])
                height = abs(self.end_pos[1] - self.start_pos[1])
                rect = pygame.Rect(x, y, width, height)
                pygame.draw.rect(surface, self.color, rect, self.brush_size)
            self.start_pos = None
            self.end_pos = None
            self.drawing = False
            return surface
        return None
    
    def update_end_pos(self, mouse_pos):
        if self.drawing:
            self.end_pos = mouse_pos
    
    def draw_preview(self, surface):
        if self.drawing and self.start_pos and self.end_pos:
            x = min(self.start_pos[0], self.end_pos[0])
            y = min(self.start_pos[1], self.end_pos[1])
            width = abs(self.end_pos[0] - self.start_pos[0])
            height = abs(self.end_pos[1] - self.start_pos[1])
            rect = pygame.Rect(x, y, width, height)
            pygame.draw.rect(surface, self.color, rect, self.brush_size)

class Circle(Tool):
    """Circle tool"""
    def __init__(self, brush_size=5):
        super().__init__()
        self.start_pos = None
        self.end_pos = None
        self.brush_size = brush_size
        self.color = (0, 0, 0)
        self.drawing = False
    
    def handle_event(self, surface, mouse_pos, mouse_pressed):
        if mouse_pressed[0] and not self.drawing:
            self.start_pos = mouse_pos
            self.drawing = True
            self.end_pos = mouse_pos
        elif not mouse_pressed[0] and self.drawing:
            if self.start_pos and self.end_pos:
                radius = int(math.hypot(self.end_pos[0] - self.start_pos[0], 
                                        self.end_pos[1] - self.start_pos[1]))
                pygame.draw.circle(surface, self.color, self.start_pos, radius, self.brush_size)
            self.start_pos = None
            self.end_pos = None
            self.drawing = False
            return surface
        return None
    
    def update_end_pos(self, mouse_pos):
        if self.drawing:
            self.end_pos = mouse_pos
    
    def draw_preview(self, surface):
        if self.drawing and self.start_pos and self.end_pos:
            radius = int(math.hypot(self.end_pos[0] - self.start_pos[0], 
                                    self.end_pos[1] - self.start_pos[1]))
            pygame.draw.circle(surface, self.color, self.start_pos, radius, self.brush_size)

class Square(Tool):
    """Square tool"""
    def __init__(self, brush_size=5):
        super().__init__()
        self.start_pos = None
        self.end_pos = None
        self.brush_size = brush_size
        self.color = (0, 0, 0)
        self.drawing = False
    
    def handle_event(self, surface, mouse_pos, mouse_pressed):
        if mouse_pressed[0] and not self.drawing:
            self.start_pos = mouse_pos
            self.drawing = True
            self.end_pos = mouse_pos
        elif not mouse_pressed[0] and self.drawing:
            if self.start_pos and self.end_pos:
                size = min(abs(self.end_pos[0] - self.start_pos[0]), 
                          abs(self.end_pos[1] - self.start_pos[1]))
                if self.end_pos[0] > self.start_pos[0]:
                    x = self.start_pos[0]
                else:
                    x = self.start_pos[0] - size
                if self.end_pos[1] > self.start_pos[1]:
                    y = self.start_pos[1]
                else:
                    y = self.start_pos[1] - size
                rect = pygame.Rect(x, y, size, size)
                pygame.draw.rect(surface, self.color, rect, self.brush_size)
            self.start_pos = None
            self.end_pos = None
            self.drawing = False
            return surface
        return None
    
    def update_end_pos(self, mouse_pos):
        if self.drawing:
            self.end_pos = mouse_pos
    
    def draw_preview(self, surface):
        if self.drawing and self.start_pos and self.end_pos:
            size = min(abs(self.end_pos[0] - self.start_pos[0]), 
                      abs(self.end_pos[1] - self.start_pos[1]))
            if self.end_pos[0] > self.start_pos[0]:
                x = self.start_pos[0]
            else:
                x = self.start_pos[0] - size
            if self.end_pos[1] > self.start_pos[1]:
                y = self.start_pos[1]
            else:
                y = self.start_pos[1] - size
            rect = pygame.Rect(x, y, size, size)
            pygame.draw.rect(surface, self.color, rect, self.brush_size)

class RightTriangle(Tool):
    """Right triangle tool"""
    def __init__(self, brush_size=5):
        super().__init__()
        self.start_pos = None
        self.end_pos = None
        self.brush_size = brush_size
        self.color = (0, 0, 0)
        self.drawing = False
    
    def handle_event(self, surface, mouse_pos, mouse_pressed):
        if mouse_pressed[0] and not self.drawing:
            self.start_pos = mouse_pos
            self.drawing = True
            self.end_pos = mouse_pos
        elif not mouse_pressed[0] and self.drawing:
            if self.start_pos and self.end_pos:
                points = [self.start_pos, 
                         (self.end_pos[0], self.start_pos[1]), 
                         self.end_pos]
                pygame.draw.polygon(surface, self.color, points, self.brush_size)
            self.start_pos = None
            self.end_pos = None
            self.drawing = False
            return surface
        return None
    
    def update_end_pos(self, mouse_pos):
        if self.drawing:
            self.end_pos = mouse_pos
    
    def draw_preview(self, surface):
        if self.drawing and self.start_pos and self.end_pos:
            points = [self.start_pos, 
                     (self.end_pos[0], self.start_pos[1]), 
                     self.end_pos]
            pygame.draw.polygon(surface, self.color, points, self.brush_size)

class EquilateralTriangle(Tool):
    """Equilateral triangle tool"""
    def __init__(self, brush_size=5):
        super().__init__()
        self.start_pos = None
        self.end_pos = None
        self.brush_size = brush_size
        self.color = (0, 0, 0)
        self.drawing = False
    
    def handle_event(self, surface, mouse_pos, mouse_pressed):
        if mouse_pressed[0] and not self.drawing:
            self.start_pos = mouse_pos
            self.drawing = True
            self.end_pos = mouse_pos
        elif not mouse_pressed[0] and self.drawing:
            if self.start_pos and self.end_pos:
                width = abs(self.end_pos[0] - self.start_pos[0])
                height = int(width * math.sqrt(3) / 2)
                if self.end_pos[0] > self.start_pos[0]:
                    x1, x2, x3 = self.start_pos[0], self.end_pos[0], self.start_pos[0] + width//2
                else:
                    x1, x2, x3 = self.end_pos[0], self.start_pos[0], self.end_pos[0] + width//2
                y1 = self.start_pos[1]
                y2 = self.start_pos[1]
                y3 = self.start_pos[1] - height
                points = [(x1, y1), (x2, y2), (x3, y3)]
                pygame.draw.polygon(surface, self.color, points, self.brush_size)
            self.start_pos = None
            self.end_pos = None
            self.drawing = False
            return surface
        return None
    
    def update_end_pos(self, mouse_pos):
        if self.drawing:
            self.end_pos = mouse_pos
    
    def draw_preview(self, surface):
        if self.drawing and self.start_pos and self.end_pos:
            width = abs(self.end_pos[0] - self.start_pos[0])
            height = int(width * math.sqrt(3) / 2)
            if self.end_pos[0] > self.start_pos[0]:
                x1, x2, x3 = self.start_pos[0], self.end_pos[0], self.start_pos[0] + width//2
            else:
                x1, x2, x3 = self.end_pos[0], self.start_pos[0], self.end_pos[0] + width//2
            y1 = self.start_pos[1]
            y2 = self.start_pos[1]
            y3 = self.start_pos[1] - height
            points = [(x1, y1), (x2, y2), (x3, y3)]
            pygame.draw.polygon(surface, self.color, points, self.brush_size)

class Triangle(Tool):
    """Generic triangle tool"""
    def __init__(self, brush_size=5):
        super().__init__()
        self.start_pos = None
        self.end_pos = None
        self.brush_size = brush_size
        self.color = (0, 0, 0)
        self.drawing = False
    
    def handle_event(self, surface, mouse_pos, mouse_pressed):
        if mouse_pressed[0] and not self.drawing:
            self.start_pos = mouse_pos
            self.drawing = True
            self.end_pos = mouse_pos
        elif not mouse_pressed[0] and self.drawing:
            if self.start_pos and self.end_pos:
                points = [self.start_pos, 
                         (self.end_pos[0], self.start_pos[1]), 
                         ((self.start_pos[0] + self.end_pos[0]) // 2, self.end_pos[1])]
                pygame.draw.polygon(surface, self.color, points, self.brush_size)
            self.start_pos = None
            self.end_pos = None
            self.drawing = False
            return surface
        return None
    
    def update_end_pos(self, mouse_pos):
        if self.drawing:
            self.end_pos = mouse_pos
    
    def draw_preview(self, surface):
        if self.drawing and self.start_pos and self.end_pos:
            points = [self.start_pos, 
                     (self.end_pos[0], self.start_pos[1]), 
                     ((self.start_pos[0] + self.end_pos[0]) // 2, self.end_pos[1])]
            pygame.draw.polygon(surface, self.color, points, self.brush_size)

class Rhombus(Tool):
    """Rhombus tool"""
    def __init__(self, brush_size=5):
        super().__init__()
        self.start_pos = None
        self.end_pos = None
        self.brush_size = brush_size
        self.color = (0, 0, 0)
        self.drawing = False
    
    def handle_event(self, surface, mouse_pos, mouse_pressed):
        if mouse_pressed[0] and not self.drawing:
            self.start_pos = mouse_pos
            self.drawing = True
            self.end_pos = mouse_pos
        elif not mouse_pressed[0] and self.drawing:
            if self.start_pos and self.end_pos:
                center_x = (self.start_pos[0] + self.end_pos[0]) // 2
                center_y = (self.start_pos[1] + self.end_pos[1]) // 2
                dx = abs(self.end_pos[0] - self.start_pos[0]) // 2
                dy = abs(self.end_pos[1] - self.start_pos[1]) // 2
                points = [(center_x, center_y - dy), 
                         (center_x + dx, center_y),
                         (center_x, center_y + dy),
                         (center_x - dx, center_y)]
                pygame.draw.polygon(surface, self.color, points, self.brush_size)
            self.start_pos = None
            self.end_pos = None
            self.drawing = False
            return surface
        return None
    
    def update_end_pos(self, mouse_pos):
        if self.drawing:
            self.end_pos = mouse_pos
    
    def draw_preview(self, surface):
        if self.drawing and self.start_pos and self.end_pos:
            center_x = (self.start_pos[0] + self.end_pos[0]) // 2
            center_y = (self.start_pos[1] + self.end_pos[1]) // 2
            dx = abs(self.end_pos[0] - self.start_pos[0]) // 2
            dy = abs(self.end_pos[1] - self.start_pos[1]) // 2
            points = [(center_x, center_y - dy), 
                     (center_x + dx, center_y),
                     (center_x, center_y + dy),
                     (center_x - dx, center_y)]
            pygame.draw.polygon(surface, self.color, points, self.brush_size)

class Eraser(Tool):
    """Eraser tool"""
    def __init__(self, brush_size=20):
        super().__init__()
        self.last_pos = None
        self.brush_size = brush_size
        self.color = (255, 255, 255)
    
    def handle_event(self, surface, mouse_pos, mouse_pressed):
        if mouse_pressed[0]:
            if self.last_pos is None:
                self.last_pos = mouse_pos
            pygame.draw.line(surface, self.color, self.last_pos, mouse_pos, self.brush_size)
            self.last_pos = mouse_pos
            return surface
        else:
            self.last_pos = None
        return None
    
    def draw_preview(self, surface):
        pass

class FloodFill(Tool):
    """Flood fill tool"""
    def __init__(self):
        super().__init__()
        self.color = (0, 0, 0)
    
    def handle_event(self, surface, mouse_pos, mouse_pressed):
        if mouse_pressed[0]:
            self.flood_fill(surface, mouse_pos, self.color)
            return surface
        return None
    
    def flood_fill(self, surface, pos, new_color):
        """Flood fill algorithm using stack"""
        try:
            target_color = surface.get_at(pos)
            if target_color == new_color:
                return
            
            width, height = surface.get_size()
            stack = [pos]
            visited = set()
            
            while stack:
                x, y = stack.pop()
                if (x, y) in visited:
                    continue
                if x < 0 or x >= width or y < 0 or y >= height:
                    continue
                if surface.get_at((x, y)) != target_color:
                    continue
                
                surface.set_at((x, y), new_color)
                visited.add((x, y))
                
                stack.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])
        except:
            pass
    
    def draw_preview(self, surface):
        pass

class Text(Tool):
    """Text tool for adding text to canvas"""
    def __init__(self, font_size=32):
        super().__init__()
        self.text_position = None
        self.current_text = ""
        self.active = False
        self.font = None
        self.font_size = font_size
        self.color = (0, 0, 0)
        self.cursor_visible = True
        self.cursor_timer = 0
    
    def initialize_font(self):
        pygame.font.init()
        self.font = pygame.font.SysFont('arial', self.font_size)
    
    def activate(self, mouse_pos):
        self.text_position = mouse_pos
        self.active = True
        self.current_text = ""
        self.cursor_timer = pygame.time.get_ticks()
        self.cursor_visible = True
    
    def handle_event(self, surface, mouse_pos, mouse_pressed):
        if not self.active and mouse_pressed[0]:
            self.activate(mouse_pos)
            return self
        return None
    
    def handle_text_input(self, event, canvas):
        if not self.active:
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.current_text and self.text_position and self.font:
                    text_surface = self.font.render(self.current_text, True, self.color)
                    canvas.blit(text_surface, self.text_position)
                self.active = False
                self.current_text = ""
                self.text_position = None
                return canvas
            elif event.key == pygame.K_ESCAPE:
                self.active = False
                self.current_text = ""
                self.text_position = None
                return None
            elif event.key == pygame.K_BACKSPACE:
                self.current_text = self.current_text[:-1]
            else:
                if event.unicode and event.unicode.isprintable():
                    self.current_text += event.unicode
        
        current_time = pygame.time.get_ticks()
        if current_time - self.cursor_timer > 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = current_time
        
        return None
    
    def draw_preview(self, surface):
        if self.active and self.text_position and self.font:
            display_text = self.current_text
            if self.cursor_visible:
                display_text += "|"
            text_surface = self.font.render(display_text, True, self.color)
            surface.blit(text_surface, self.text_position)