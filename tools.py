# tools.py
import pygame
import math

class Tool:
    def __init__(self):
        self.start_pos = None
        self.current_pos = None
        self.drawing = False
    
    def handle_event(self, surface, mouse_pos, mouse_pressed):
        pass
    
    def draw_preview(self, surface):
        pass

class Pencil(Tool):
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

class Line(Tool):
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
                w = abs(self.end_pos[0] - self.start_pos[0])
                h = abs(self.end_pos[1] - self.start_pos[1])
                pygame.draw.rect(surface, self.color, (x, y, w, h), self.brush_size)
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
            w = abs(self.end_pos[0] - self.start_pos[0])
            h = abs(self.end_pos[1] - self.start_pos[1])
            pygame.draw.rect(surface, self.color, (x, y, w, h), self.brush_size)

class Circle(Tool):
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
                r = int(math.hypot(self.end_pos[0] - self.start_pos[0], self.end_pos[1] - self.start_pos[1]))
                pygame.draw.circle(surface, self.color, self.start_pos, r, self.brush_size)
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
            r = int(math.hypot(self.end_pos[0] - self.start_pos[0], self.end_pos[1] - self.start_pos[1]))
            pygame.draw.circle(surface, self.color, self.start_pos, r, self.brush_size)

class Square(Tool):
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
                size = min(abs(self.end_pos[0] - self.start_pos[0]), abs(self.end_pos[1] - self.start_pos[1]))
                if self.end_pos[0] > self.start_pos[0]:
                    x = self.start_pos[0]
                else:
                    x = self.start_pos[0] - size
                if self.end_pos[1] > self.start_pos[1]:
                    y = self.start_pos[1]
                else:
                    y = self.start_pos[1] - size
                pygame.draw.rect(surface, self.color, (x, y, size, size), self.brush_size)
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
            size = min(abs(self.end_pos[0] - self.start_pos[0]), abs(self.end_pos[1] - self.start_pos[1]))
            if self.end_pos[0] > self.start_pos[0]:
                x = self.start_pos[0]
            else:
                x = self.start_pos[0] - size
            if self.end_pos[1] > self.start_pos[1]:
                y = self.start_pos[1]
            else:
                y = self.start_pos[1] - size
            pygame.draw.rect(surface, self.color, (x, y, size, size), self.brush_size)

class RightTriangle(Tool):
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
                points = [self.start_pos, (self.end_pos[0], self.start_pos[1]), self.end_pos]
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
            points = [self.start_pos, (self.end_pos[0], self.start_pos[1]), self.end_pos]
            pygame.draw.polygon(surface, self.color, points, self.brush_size)

class EquilateralTriangle(Tool):
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
                points = [self.start_pos, (self.end_pos[0], self.start_pos[1]), ((self.start_pos[0] + self.end_pos[0]) // 2, self.end_pos[1])]
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
            points = [self.start_pos, (self.end_pos[0], self.start_pos[1]), ((self.start_pos[0] + self.end_pos[0]) // 2, self.end_pos[1])]
            pygame.draw.polygon(surface, self.color, points, self.brush_size)

class Rhombus(Tool):
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
                cx = (self.start_pos[0] + self.end_pos[0]) // 2
                cy = (self.start_pos[1] + self.end_pos[1]) // 2
                dx = abs(self.end_pos[0] - self.start_pos[0]) // 2
                dy = abs(self.end_pos[1] - self.start_pos[1]) // 2
                points = [(cx, cy - dy), (cx + dx, cy), (cx, cy + dy), (cx - dx, cy)]
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
            cx = (self.start_pos[0] + self.end_pos[0]) // 2
            cy = (self.start_pos[1] + self.end_pos[1]) // 2
            dx = abs(self.end_pos[0] - self.start_pos[0]) // 2
            dy = abs(self.end_pos[1] - self.start_pos[1]) // 2
            points = [(cx, cy - dy), (cx + dx, cy), (cx, cy + dy), (cx - dx, cy)]
            pygame.draw.polygon(surface, self.color, points, self.brush_size)

class Eraser(Tool):
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

class FloodFill(Tool):
    def __init__(self):
        super().__init__()
        self.color = (0, 0, 0)
    
    def handle_event(self, surface, mouse_pos, mouse_pressed):
        if mouse_pressed[0]:
            self.flood_fill(surface, mouse_pos, self.color)
            return surface
        return None
    
    def flood_fill(self, surface, pos, new_color):
        try:
            target = surface.get_at(pos)
            if target == new_color:
                return
            w, h = surface.get_size()
            stack = [pos]
            visited = set()
            while stack:
                x, y = stack.pop()
                if (x, y) in visited or x < 0 or x >= w or y < 0 or y >= h:
                    continue
                if surface.get_at((x, y)) != target:
                    continue
                surface.set_at((x, y), new_color)
                visited.add((x, y))
                stack.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])
        except:
            pass

class Text(Tool):
    def __init__(self, font_size=32):
        super().__init__()
        self.text_position = None
        self.current_text = ""
        self.active = False
        self.font = None
        self.font_size = font_size
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
        print(f"Text activated at {mouse_pos}")