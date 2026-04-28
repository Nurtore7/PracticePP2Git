# tools.py
# Модуль с инструментами для рисования в графическом редакторе на Pygame

# ИМПОРТ МОДУЛЕЙ
import pygame  # Библиотека для создания игр и графических приложений
import math    # Математические функции (sqrt, hypot и др.)

# БАЗОВЫЙ КЛАСС ДЛЯ ВСЕХ ИНСТРУМЕНТОВ РИСОВАНИЯ
class Tool:
    """Base class for all drawing tools"""
    def __init__(self):
        self.start_pos = None      # Начальная позиция рисования (для фигур)
        self.current_pos = None    # Текущая позиция мыши
        self.drawing = False       # Флаг: идёт ли рисование в данный момент
    
    def handle_event(self, surface, mouse_pos, mouse_pressed):
        """Обработка событий мыши - переопределяется в дочерних классах"""
        pass
    
    def draw_preview(self, surface):
        """Отрисовка предпросмотра фигуры (пунктир или контур) - переопределяется"""
        pass

# ИНСТРУМЕНТ "КАРАНДАШ" - СВОБОДНОЕ РИСОВАНИЕ ОТ РУКИ
class Pencil(Tool):
    """Freehand drawing tool"""
    def __init__(self, brush_size=5):
        super().__init__()  # Вызов конструктора родительского класса
        self.last_pos = None      # Предыдущая позиция для рисования линии
        self.brush_size = brush_size  # Толщина кисти
        self.color = (0, 0, 0)    # Чёрный цвет (RGB)
    
    def handle_event(self, surface, mouse_pos, mouse_pressed):
        # Если зажата левая кнопка мыши (индекс 0)
        if mouse_pressed[0]:
            # Если это первый кадр рисования - запоминаем позицию
            if self.last_pos is None:
                self.last_pos = mouse_pos
            # Рисуем линию от предыдущей позиции до текущей
            pygame.draw.line(surface, self.color, self.last_pos, mouse_pos, self.brush_size)
            self.last_pos = mouse_pos  # Обновляем последнюю позицию
            return surface  # Возвращаем изменённую поверхность
        else:
            self.last_pos = None  # Сбрасываем при отпускании кнопки
        return None  # Ничего не изменилось
    
    def draw_preview(self, surface):
        pass  # Для карандаша предпросмотр не нужен

# ИНСТРУМЕНТ "ЛИНИЯ" - ПРЯМАЯ ЛИНИЯ ОТ НАЧАЛА ДО КОНЦА
class Line(Tool):
    """Straight line tool"""
    def __init__(self, brush_size=5):
        super().__init__()
        self.start_pos = None   # Начало линии
        self.end_pos = None     # Конец линии
        self.brush_size = brush_size
        self.color = (0, 0, 0)
        self.drawing = False    # Флаг процесса рисования
    
    def handle_event(self, surface, mouse_pos, mouse_pressed):
        # Начало рисования: нажали кнопку, но ещё не рисуем
        if mouse_pressed[0] and not self.drawing:
            self.start_pos = mouse_pos
            self.drawing = True
            self.end_pos = mouse_pos
        # Завершение рисования: отпустили кнопку
        elif not mouse_pressed[0] and self.drawing:
            if self.start_pos and self.end_pos:
                # Рисуем финальную линию на основном холсте
                pygame.draw.line(surface, self.color, self.start_pos, self.end_pos, self.brush_size)
            # Сбрасываем состояние
            self.start_pos = None
            self.end_pos = None
            self.drawing = False
            return surface  # Возвращаем изменённую поверхность
        return None
    
    def update_end_pos(self, mouse_pos):
        """Обновляет конечную точку при движении мыши (для предпросмотра)"""
        if self.drawing:
            self.end_pos = mouse_pos
    
    def draw_preview(self, surface):
        """Отрисовка предпросмотра линии (резиновая нить)"""
        if self.drawing and self.start_pos and self.end_pos:
            pygame.draw.line(surface, self.color, self.start_pos, self.end_pos, self.brush_size)

# ИНСТРУМЕНТ "ПРЯМОУГОЛЬНИК"
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
                # Вычисляем координаты прямоугольника (левая верхняя точка)
                x = min(self.start_pos[0], self.end_pos[0])
                y = min(self.start_pos[1], self.end_pos[1])
                # Ширина и высота (всегда положительные)
                width = abs(self.end_pos[0] - self.start_pos[0])
                height = abs(self.end_pos[1] - self.start_pos[1])
                rect = pygame.Rect(x, y, width, height)  # Создаём объект прямоугольника
                # Рисуем только контур (последний параметр - толщина линии)
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

# ИНСТРУМЕНТ "ОКРУЖНОСТЬ/КРУГ"
class Circle(Tool):
    """Circle tool"""
    def __init__(self, brush_size=5):
        super().__init__()
        self.start_pos = None  # Центр окружности
        self.end_pos = None     # Точка для определения радиуса
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
                # Вычисляем радиус как расстояние между двумя точками
                # math.hypot = sqrt(dx^2 + dy^2) - евклидово расстояние
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

# ИНСТРУМЕНТ "КВАДРАТ" (с равными сторонами)
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
                # Сторона квадрата = минимальная из разницы по X и Y
                size = min(abs(self.end_pos[0] - self.start_pos[0]), 
                          abs(self.end_pos[1] - self.start_pos[1]))
                # Определяем левую верхнюю точку в зависимости от направления
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

# ИНСТРУМЕНТ "ПРЯМОУГОЛЬНЫЙ ТРЕУГОЛЬНИК"
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
                # Три вершины: начальная, (X конца, Y начала), конечная
                points = [self.start_pos, 
                         (self.end_pos[0], self.start_pos[1]),  # Прямой угол
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

# ИНСТРУМЕНТ "РАВНОСТОРОННИЙ ТРЕУГОЛЬНИК"
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
                # Ширина = расстояние по X
                width = abs(self.end_pos[0] - self.start_pos[0])
                # Высота равностороннего треугольника: (√3/2) * сторона
                height = int(width * math.sqrt(3) / 2)
                # Вычисляем координаты трёх вершин в зависимости от направления
                if self.end_pos[0] > self.start_pos[0]:
                    x1, x2, x3 = self.start_pos[0], self.end_pos[0], self.start_pos[0] + width//2
                else:
                    x1, x2, x3 = self.end_pos[0], self.start_pos[0], self.end_pos[0] + width//2
                y1 = self.start_pos[1]
                y2 = self.start_pos[1]
                y3 = self.start_pos[1] - height  # Вершина вверх
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

# ИНСТРУМЕНТ "ПРОИЗВОЛЬНЫЙ ТРЕУГОЛЬНИК" (равнобедренный с основанием внизу)
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
                # Три точки: левая нижняя, правая нижняя, средняя верхняя
                points = [self.start_pos, 
                         (self.end_pos[0], self.start_pos[1]),  # Правая нижняя
                         ((self.start_pos[0] + self.end_pos[0]) // 2, self.end_pos[1])]  # Верхняя
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

# ИНСТРУМЕНТ "РОМБ" (с диагоналями по осям)
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
                # Центр ромба - середина между начальной и конечной точкой
                center_x = (self.start_pos[0] + self.end_pos[0]) // 2
                center_y = (self.start_pos[1] + self.end_pos[1]) // 2
                # Полудиагонали
                dx = abs(self.end_pos[0] - self.start_pos[0]) // 2
                dy = abs(self.end_pos[1] - self.start_pos[1]) // 2
                # Четыре вершины: верх, право, низ, лево
                points = [(center_x, center_y - dy),  # Верх
                         (center_x + dx, center_y),   # Право
                         (center_x, center_y + dy),   # Низ
                         (center_x - dx, center_y)]   # Лево
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

# ИНСТРУМЕНТ "ЛАСТИК" (рисует белым цветом)
class Eraser(Tool):
    """Eraser tool"""
    def __init__(self, brush_size=20):
        super().__init__()
        self.last_pos = None
        self.brush_size = brush_size
        self.color = (255, 255, 255)  # Белый цвет (фоновый)
    
    def handle_event(self, surface, mouse_pos, mouse_pressed):
        if mouse_pressed[0]:
            if self.last_pos is None:
                self.last_pos = mouse_pos
            # Рисуем белыми линиями - стираем
            pygame.draw.line(surface, self.color, self.last_pos, mouse_pos, self.brush_size)
            self.last_pos = mouse_pos
            return surface
        else:
            self.last_pos = None
        return None
    
    def draw_preview(self, surface):
        pass

# ИНСТРУМЕНТ "ЗАЛИВКА" (алгоритм заливки связной области)
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
        """Алгоритм заливки с использованием стека (не рекурсивный)"""
        try:
            # Цвет, который нужно заменить
            target_color = surface.get_at(pos)
            if target_color == new_color:
                return  # Если цвета совпадают - ничего не делаем
            
            width, height = surface.get_size()
            stack = [pos]           # Стек для обхода пикселей
            visited = set()         # Множество посещённых пикселей (чтобы не зациклиться)
            
            while stack:
                x, y = stack.pop()   # Берём пиксель из стека
                if (x, y) in visited:
                    continue
                if x < 0 or x >= width or y < 0 or y >= height:
                    continue  # Выход за границы
                if surface.get_at((x, y)) != target_color:
                    continue  # Другой цвет - граница области
                
                surface.set_at((x, y), new_color)  # Закрашиваем
                visited.add((x, y))                 # Отмечаем как посещённый
                
                # Добавляем соседние пиксели (4 направления)
                stack.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])
        except:
            pass  # Игнорируем ошибки (например, выход за пределы)
    
    def draw_preview(self, surface):
        pass

# ИНСТРУМЕНТ "ТЕКСТ" - ДЛЯ ДОБАВЛЕНИЯ ТЕКСТА НА ХОЛСТ
class Text(Tool):
    """Text tool for adding text to canvas"""
    def __init__(self, font_size=32):
        super().__init__()
        self.text_position = None   # Позиция вставки текста
        self.current_text = ""      # Вводимый текст
        self.active = False         # Активен ли режим ввода
        self.font = None            # Объект шрифта
        self.font_size = font_size  # Размер шрифта
        self.color = (0, 0, 0)      # Цвет текста
        self.cursor_visible = True  # Видимость курсора (мигание)
        self.cursor_timer = 0       # Таймер для мигания курсора
    
    def initialize_font(self):
        """Инициализация системы шрифтов и создание шрифта"""
        pygame.font.init()  # Инициализируем шрифты Pygame
        self.font = pygame.font.SysFont('arial', self.font_size)  # Системный шрифт Arial
    
    def activate(self, mouse_pos):
        """Активация текстового инструмента в указанной позиции"""
        self.text_position = mouse_pos
        self.active = True
        self.current_text = ""
        self.cursor_timer = pygame.time.get_ticks()  # Запоминаем текущее время
        self.cursor_visible = True
    
    def handle_event(self, surface, mouse_pos, mouse_pressed):
        """Обработка клика для активации текстового поля"""
        if not self.active and mouse_pressed[0]:
            self.activate(mouse_pos)
            return self  # Возвращаем себя для передачи фокуса
        return None
    
    def handle_text_input(self, event, canvas):
        """Обработка ввода текста с клавиатуры"""
        if not self.active:
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:  # Enter - завершить ввод
                if self.current_text and self.text_position and self.font:
                    # Отрисовываем текст на холсте с помощью шрифта
                    text_surface = self.font.render(self.current_text, True, self.color)
                    canvas.blit(text_surface, self.text_position)
                self.active = False
                self.current_text = ""
                self.text_position = None
                return canvas  # Возвращаем изменённый холст
            elif event.key == pygame.K_ESCAPE:  # Escape - отмена
                self.active = False
                self.current_text = ""
                self.text_position = None
                return None
            elif event.key == pygame.K_BACKSPACE:  # Backspace - удалить последний символ
                self.current_text = self.current_text[:-1]
            else:
                # Добавляем печатаемый символ
                if event.unicode and event.unicode.isprintable():
                    self.current_text += event.unicode
        
        # Мигание курсора (каждые 500 мс)
        current_time = pygame.time.get_ticks()
        if current_time - self.cursor_timer > 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = current_time
        
        return None
    
    def draw_preview(self, surface):
        """Отрисовка предпросмотра текста с мигающим курсором"""
        if self.active and self.text_position and self.font:
            display_text = self.current_text
            if self.cursor_visible:
                display_text += "|"  # Добавляем символ курсора
            text_surface = self.font.render(display_text, True, self.color)
            surface.blit(text_surface, self.text_position)