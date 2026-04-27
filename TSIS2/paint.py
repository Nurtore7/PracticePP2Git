# paint.py
import pygame  # Импорт библиотеки для графики и обработки событий
import sys  # Для системных функций (выход из программы)
from datetime import datetime  # Для получения текущего времени при сохранении файлов
from tools import *  # Импорт всех инструментов (карандаш, линии, фигуры, ластик и т.д.)

class PaintApp:  # Главный класс приложения-рисовалки
    def __init__(self):  # Конструктор - инициализация всех компонентов
        pygame.init()  # Запуск всех модулей Pygame
        
        # Получаем размеры экрана для полноэкранного режима
        info = pygame.display.Info()  # Информация о дисплее
        self.screen_width = info.current_w  # Ширина экрана пользователя
        self.screen_height = info.current_h  # Высота экрана пользователя
        
        # Панель инструментов располагается справа
        self.toolbar_width = 220  # Ширина панели инструментов
        self.canvas_width = self.screen_width - self.toolbar_width  # Ширина области рисования
        self.canvas_height = self.screen_height  # Высота области рисования (весь экран)
        
        # Создаём полноэкранное окно
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption("Paint Application - Fullscreen")  # Заголовок окна
        
        # Создаём холст для рисования
        self.canvas = pygame.Surface((self.canvas_width, self.canvas_height))  # Поверхность для рисунка
        self.canvas.fill((255, 255, 255))  # Заливаем белым цветом
        
        # Настройки цветов
        self.current_color = (0, 0, 0)  # Текущий цвет - чёрный (RGB)
        self.colors = [  # Список доступных цветов для кнопок
            (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255),  # Чёрный, красный, зелёный, синий
            (255, 255, 0), (255, 0, 255), (0, 255, 255), (255, 255, 255)  # Жёлтый, пурпурный, голубой, белый
        ]
        
        # Настройки кисти
        self.brush_sizes = {pygame.K_1: 2, pygame.K_2: 5, pygame.K_3: 10}  
        self.current_brush_size = 5
        
        # Текущий выбранный инструмент
        self.current_tool = "pencil"
        
        # Словарь со всеми инструментами
        self.tools = {
            "pencil": Pencil(self.current_brush_size),  # Карандаш
            "line": Line(self.current_brush_size),  # Линия
            "rectangle": Rectangle(self.current_brush_size),  # Прямоугольник
            "circle": Circle(self.current_brush_size),  # Круг
            "square": Square(self.current_brush_size),  # Квадрат
            "right_triangle": RightTriangle(self.current_brush_size),  # Прямоугольный треугольник
            "equilateral_triangle": EquilateralTriangle(self.current_brush_size),  # Равносторонний треугольник
            "triangle": Triangle(self.current_brush_size),  # Треугольник
            "rhombus": Rhombus(self.current_brush_size),  # Ромб
            "eraser": Eraser(20),  # Ластик (размер 20)
            "flood_fill": FloodFill(),  # Заливка
            "text": Text(36)  # Текст (размер шрифта 36)
        }
        
        # Инициализация шрифта для текстового инструмента
        self.tools["text"].initialize_font()
        
        # Обновляем размеры и цвета для всех инструментов
        self.update_brush_sizes()
        
        # Создаём панель инструментов с кнопками
        self.create_toolbar()
        
        # Переменные состояния
        self.is_drawing = False  # Флаг: рисуем ли мы сейчас (зажата ли кнопка мыши)
        self.clock = pygame.time.Clock()  # Часы для контроля FPS
        self.toolbar_font = pygame.font.SysFont('arial', 18)  # Шрифт для текста на панели
        
        # Выводим информацию о размерах в консоль (для отладки)
        print(f"Fullscreen mode: {self.screen_width}x{self.screen_height}")
        print(f"Canvas size: {self.canvas_width}x{self.canvas_height}")
    
    def update_brush_sizes(self):  # Обновляет размер кисти и цвет для всех инструментов
        for tool_name, tool in self.tools.items():  # Перебираем все инструменты
            if hasattr(tool, 'brush_size'):  # Если у инструмента есть размер кисти
                tool.brush_size = self.current_brush_size  # Устанавливаем текущий размер
            if hasattr(tool, 'color') and tool_name != "eraser":  # Если есть цвет и это не ластик
                tool.color = self.current_color  # Устанавливаем текущий цвет
    
    def create_toolbar(self):  # Создаёт кнопки на панели инструментов
        self.toolbar_buttons = []  # Список для хранения всех кнопок
        
        # Список кнопок инструментов (название на кнопке и внутреннее имя)
        buttons = [
            ("Pencil", "pencil"), ("Line", "line"), ("Rectangle", "rectangle"),
            ("Circle", "circle"), ("Square", "square"), ("Right Tri", "right_triangle"),
            ("Equil Tri", "equilateral_triangle"), ("Triangle", "triangle"),
            ("Rhombus", "rhombus"), ("Eraser", "eraser"), ("Flood Fill", "flood_fill"),
            ("Text", "text")
        ]
        
        # Параметры кнопок
        button_height = 40  # Высота кнопки
        button_width = self.toolbar_width - 20  # Ширина с отступами
        start_y = 10  # Начальная позиция по вертикали
        
        # Создаём кнопки для инструментов
        for i, (label, tool_name) in enumerate(buttons):
            button_rect = pygame.Rect(10, start_y + i * 45, button_width, button_height)  # Прямоугольник кнопки
            self.toolbar_buttons.append({
                'rect': button_rect, 'tool': tool_name, 'label': label  # Сохраняем геометрию и имя
            })
        
        # Кнопки выбора цвета
        color_size = 35  # Размер цветной кнопки
        colors_start_y = start_y + len(buttons) * 45 + 10  # Позиция после кнопок инструментов
        
        for i, color in enumerate(self.colors):  # Перебираем цвета
            row = i // 2  # Строка (2 колонки)
            col = i % 2   # Колонка
            x = 10 + col * 40  # Координата X
            y = colors_start_y + row * 40  # Координата Y
            button_rect = pygame.Rect(x, y, color_size, color_size)  # Прямоугольник кнопки
            self.toolbar_buttons.append({
                'rect': button_rect, 'tool': 'color', 'color_value': color  # Сохраняем цвет
            })
        
        # Кнопка сохранения
        save_rect = pygame.Rect(10, self.screen_height - 60, button_width, 40)
        self.toolbar_buttons.append({
            'rect': save_rect, 'tool': 'save', 'label': 'SAVE (Ctrl+S)'
        })
        
        # Место для отображения информации о кисти
        self.brush_info_rect = pygame.Rect(10, self.screen_height - 120, button_width, 30)
    
    def draw_toolbar(self):  # Рисует панель инструментов на экране
        toolbar_surface = pygame.Surface((self.toolbar_width, self.screen_height))  # Поверхность для панели
        toolbar_surface.fill((240, 240, 240))  # Заливаем светло-серым цветом
        
        # Рисуем границу между холстом и панелью
        pygame.draw.line(toolbar_surface, (180, 180, 180), 
                        (0, 0), (0, self.screen_height), 3)
        
        # Рисуем все кнопки
        for button in self.toolbar_buttons:
            if button['tool'] == 'color':  # Если это цветная кнопка
                pygame.draw.rect(toolbar_surface, button['color_value'], button['rect'])  # Заливаем цветом
                pygame.draw.rect(toolbar_surface, (0, 0, 0), button['rect'], 2)  # Чёрная рамка
            else:  # Если это кнопка инструмента или сохранения
                # Выделяем активный инструмент другим цветом
                if button['tool'] == self.current_tool:
                    color = (180, 180, 255)  # Голубоватый для активного
                else:
                    color = (230, 230, 230)  # Светло-серый для неактивных
                pygame.draw.rect(toolbar_surface, color, button['rect'])  # Заливаем
                pygame.draw.rect(toolbar_surface, (100, 100, 100), button['rect'], 2)  # Серая рамка
                
                # Рисуем текст на кнопке
                if 'label' in button and button['label']:
                    text = self.toolbar_font.render(button['label'], True, (0, 0, 0))  # Рендерим текст
                    text_rect = text.get_rect(center=button['rect'].center)  # Центрируем
                    toolbar_surface.blit(text, text_rect)  # Рисуем текст
        
        # Показываем текущий размер кисти
        brush_text = self.toolbar_font.render(f"Brush: {self.current_brush_size}px", True, (0, 0, 0))
        text_rect = brush_text.get_rect(center=self.brush_info_rect.center)  # Центрируем
        toolbar_surface.blit(brush_text, text_rect)
        
        # Рисуем подсказки по управлению внизу панели
        y = self.screen_height - 200  # Начальная позиция
        instructions = ["1,2,3 = Brush size", "ESC = Exit", "Ctrl+S = Save"]  # Текст подсказок
        for instr in instructions:
            text = self.toolbar_font.render(instr, True, (80, 80, 80))  # Серый текст
            toolbar_surface.blit(text, (10, y))  # Рисуем подсказку
            y += 25  # Сдвигаем вниз
        
        # Помещаем панель на экран справа от холста
        self.screen.blit(toolbar_surface, (self.canvas_width, 0))
    
    def handle_events(self):  # Обработка всех событий (клавиатура, мышь, системные)
        for event in pygame.event.get():  # Получаем все события из очереди
            if event.type == pygame.QUIT:  # Если закрывают окно
                return False  # Выход из программы
            
            # Обработка нажатий клавиш
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # ESC - выход
                    return False
                if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:  # Ctrl+S - сохранение
                    self.save_canvas()
                if event.key in self.brush_sizes:  # Клавиши 1,2,3 - размер кисти
                    self.current_brush_size = self.brush_sizes[event.key]  # Меняем размер
                    self.update_brush_sizes()  # Обновляем у всех инструментов
            
            # Обработка ввода текста (если активен текстовый инструмент)
            if self.current_tool == "text" and self.tools["text"].active:
                if event.type == pygame.KEYDOWN:
                    result = self.tools["text"].handle_text_input(event, self.canvas)  # Передаём нажатие тексту
                    if result is not None:
                        if isinstance(result, pygame.Surface):
                            self.canvas = result  # Обновляем холст с новым текстом
                        self.tools["text"].active = False  # Завершаем режим ввода текста
                    continue  # Пропускаем остальную обработку событий
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.tools["text"].active = False  # Клик мышью отменяет ввод текста
                    continue
            
            # Обработка мыши
            mouse_pos = pygame.mouse.get_pos()  # Позиция курсора
            canvas_pos = (mouse_pos[0], mouse_pos[1])  # Координаты на экране
            mouse_pressed = pygame.mouse.get_pressed()  # Какие кнопки мыши зажаты
            
            # Проверяем, находится ли курсор на холсте (не на панели)
            on_canvas = (canvas_pos[0] < self.canvas_width)
            
            # Нажатие кнопки мыши
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Левая кнопка
                # Проверяем, не нажали ли на панель инструментов
                if canvas_pos[0] >= self.canvas_width:
                    self.check_toolbar_click(mouse_pos)  # Обрабатываем клик по панели
                elif on_canvas:  # Клик на холсте
                    if self.current_tool == "flood_fill":  # Заливка
                        self.tools["flood_fill"].color = self.current_color  # Устанавливаем цвет
                        result = self.tools["flood_fill"].handle_event(self.canvas, canvas_pos, mouse_pressed)
                        if result:
                            self.canvas = result  # Обновляем холст с заливкой
                    elif self.current_tool == "text":  # Текст
                        self.tools["text"].activate(canvas_pos)  # Активируем ввод текста в этой позиции
                    else:  # Остальные инструменты
                        self.is_drawing = True  # Начинаем рисовать
                        result = self.tools[self.current_tool].handle_event(self.canvas, canvas_pos, mouse_pressed)
                        if result:
                            self.canvas = result  # Обновляем холст
            
            # Отпускание кнопки мыши
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.is_drawing and on_canvas:  # Если рисовали и отпустили на холсте
                    result = self.tools[self.current_tool].handle_event(self.canvas, canvas_pos, mouse_pressed)
                    if result:
                        self.canvas = result  # Завершаем рисование фигуры
                    self.is_drawing = False  # Завершаем процесс рисования
            
            # Движение мыши
            elif event.type == pygame.MOUSEMOTION:
                if on_canvas:  # Только если мышь на холсте
                    # Обновляем конечную точку для инструментов, которым это нужно (линии, фигуры)
                    if hasattr(self.tools[self.current_tool], 'update_end_pos'):
                        self.tools[self.current_tool].update_end_pos(canvas_pos)
                    
                    # Если рисуем карандашом или ластиком - рисуем непрерывно
                    if self.is_drawing and self.current_tool in ["pencil", "eraser"]:
                        result = self.tools[self.current_tool].handle_event(self.canvas, canvas_pos, mouse_pressed)
                        if result:
                            self.canvas = result  # Обновляем холст
        
        return True  # Продолжаем работу программы
    
    def check_toolbar_click(self, mouse_pos):  # Обрабатывает клики по панели инструментов
        x, y = mouse_pos  # Координаты клика
        toolbar_x = x - self.canvas_width  # Переводим в систему координат панели
        
        for button in self.toolbar_buttons:  # Перебираем все кнопки
            if button['rect'].collidepoint(toolbar_x, y):  # Если кликнули по кнопке
                if button['tool'] == 'color':  # Кнопка выбора цвета
                    self.current_color = button['color_value']  # Меняем текущий цвет
                    self.update_brush_sizes()  # Обновляем цвет у инструментов
                elif button['tool'] == 'save':  # Кнопка сохранения
                    self.save_canvas()  # Сохраняем рисунок
                elif button['tool'] == 'eraser':  # Ластик
                    self.current_tool = button['tool']  # Активируем ластик
                    self.tools["eraser"].color = (255, 255, 255)  # Ластик рисует белым
                else:  # Обычный инструмент
                    self.current_tool = button['tool']  # Меняем активный инструмент
                    if button['tool'] != "text":  # Если не текст
                        self.tools["text"].active = False  # Выключаем режим ввода текста
                return True  # Клик обработан
        return False  # Клик был мимо кнопок
    
    def save_canvas(self):  # Сохраняет холст в файл
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Формируем временную метку (ГГГГММДД_ЧЧММСС)
        filename = f"canvas_{timestamp}.png"  # Имя файла с датой и временем
        pygame.image.save(self.canvas, filename)  # Сохраняем поверхность как PNG
        print(f"Saved: {filename}")  # Выводим сообщение в консоль
    
    def draw_preview(self):  # Создаёт предпросмотр фигур (например, растягивающийся прямоугольник)
        preview = self.canvas.copy()  # Копируем холст, чтобы не портить оригинал
        mouse_pos = pygame.mouse.get_pos()  # Текущая позиция мыши
        canvas_pos = (mouse_pos[0], mouse_pos[1])  # Координаты на экране
        
        # Если мышь на холсте (не на панели)
        if canvas_pos[0] < self.canvas_width:
            # Показываем предпросмотр для инструментов (кроме заливки)
            if self.current_tool not in ["flood_fill"]:
                if hasattr(self.tools[self.current_tool], 'draw_preview'):
                    self.tools[self.current_tool].draw_preview(preview)  # Рисуем предпросмотр на копии
        
        # Если активен текстовый инструмент и идёт ввод текста
        if self.current_tool == "text" and self.tools["text"].active:
            self.tools["text"].draw_preview(preview)  # Показываем вводимый текст
        
        return preview  # Возвращаем холст с предпросмотром
    
    def run(self):  # Главный цикл программы
        running = True
        while running:  # Бесконечный цикл, пока running == True
            running = self.handle_events()  # Обрабатываем события, если вернёт False - выход
            
            display = self.draw_preview()  # Получаем холст с предпросмотром
            
            # Отрисовка всего на экране
            self.screen.fill((255, 255, 255))  # Очищаем экран белым
            self.screen.blit(display, (0, 0))  # Рисуем холст (с предпросмотром) слева
            self.draw_toolbar()  # Рисуем панель инструментов справа
            
            pygame.display.flip()  # Обновляем окно (показываем отрисованное)
            self.clock.tick(60)  # Ограничиваем до 60 кадров в секунду
        
        pygame.quit()  # Корректно закрываем Pygame
        sys.exit()  # Выходим из программы

# Точка входа в программу
if __name__ == "__main__":
    app = PaintApp()  # Создаём экземпляр приложения
    app.run()  # Запускаем главный цикл