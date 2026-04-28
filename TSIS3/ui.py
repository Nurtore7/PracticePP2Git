# МОДУЛЬ ПОЛЬЗОВАТЕЛЬСКОГО ИНТЕРФЕЙСА - ВСЕ ЭКРАНЫ МЕНЮ И КНОПКИ
import pygame

# КЛАСС КНОПКИ С ЭФФЕКТОМ НАВЕДЕНИЯ
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        # Прямоугольник кнопки (границы и положение)
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text              # Текст на кнопке
        self.color = color            # Обычный цвет (R,G,B)
        self.hover_color = hover_color # Цвет при наведении курсора
        self.is_hovered = False       # Флаг, находится ли курсор на кнопке
        
    def draw(self, screen, font):
        """Отрисовка кнопки с эффектом наведения и белой рамкой"""
        # Выбираем цвет в зависимости от состояния наведения
        color = self.hover_color if self.is_hovered else self.color
        # Рисуем залитый прямоугольник со скруглёнными углами (border_radius=10)
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        # Рисуем белую рамку толщиной 2 пикселя
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=10)
        
        # Отрисовываем текст по центру кнопки
        text_surface = font.render(self.text, True, (255, 255, 255))  # Белый текст
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        """Обработка событий для кнопки
           Возвращает True если кнопка была нажата"""
        if event.type == pygame.MOUSEMOTION:
            # При движении мыши обновляем флаг наведения
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # При клике проверяем, наведён ли курсор на кнопку
            if self.is_hovered:
                return True
        return False

# КЛАСС ПОЛЯ ВВОДА ТЕКСТА
class InputBox:
    def __init__(self, x, y, width, height, font):
        # Прямоугольник поля ввода
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.text = ""                      # Введённый текст
        self.active = False                 # Активно ли поле (в фокусе)
        # Цвета для активного и неактивного состояния
        self.color_inactive = pygame.Color('lightskyblue3')  # Светло-голубой
        self.color_active = pygame.Color('dodgerblue2')      # Ярко-синий
        self.color = self.color_inactive    # Текущий цвет рамки
        
    def handle_event(self, event):
        """Обработка событий для поля ввода
           Возвращает текст при нажатии Enter, иначе None"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # При клике проверяем, попали ли в поле
            self.active = self.rect.collidepoint(event.pos)
            # Меняем цвет рамки в зависимости от активности
            self.color = self.color_active if self.active else self.color_inactive
            
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                # Enter - возвращаем введённый текст
                return self.text
            elif event.key == pygame.K_BACKSPACE:
                # Backspace - удаляем последний символ
                self.text = self.text[:-1]
            else:
                # Добавляем символ, если не превышен лимит в 15 символов
                if len(self.text) < 15:
                    self.text += event.unicode
        return None
    
    def draw(self, screen):
        """Отрисовка поля ввода"""
        # Рисуем рамку (толщина 2 пикселя)
        pygame.draw.rect(screen, self.color, self.rect, 2)
        # Рисуем текст со смещением 5 пикселей от левого края
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))

# КЛАСС УПРАВЛЕНИЯ ВСЕМИ ЭКРАНАМИ ИНТЕРФЕЙСА
class UIManager:
    def __init__(self, screen, data_manager):
        self.screen = screen                # Экран для отрисовки
        self.data_manager = data_manager    # Менеджер данных (настройки, рекорды)
        # Шрифты разных размеров
        self.font_large = pygame.font.Font(None, 72)   # Крупный (заголовки)
        self.font_medium = pygame.font.Font(None, 48)  # Средний (кнопки)
        self.font_small = pygame.font.Font(None, 36)   # Мелкий (подзаголовки)
        self.font_tiny = pygame.font.Font(None, 24)    # Очень мелкий (вспомогательный)
        
    def draw_text(self, text, font, color, x, y, center=False):
        """Универсальный метод для отрисовки текста
           center=True - центрирование по x,y, иначе - левый верхний угол"""
        surface = font.render(text, True, color)
        rect = surface.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(surface, rect)
    
    # === ЭКРАН ГЛАВНОГО МЕНЮ ===
    def show_main_menu(self):
        """Отображает главное меню, возвращает выбранное действие"""
        # Тёмно-серый фон (30,30,40)
        self.screen.fill((30, 30, 40))
        
        # Заголовок игры (золотой)
        self.draw_text("RACING GAME", self.font_large, (255, 215, 0),
                      self.screen.get_width() // 2, 100, center=True)
        
        # Параметры для всех кнопок
        button_width = 250
        button_height = 60
        button_x = self.screen.get_width() // 2 - button_width // 2
        
        # СОЗДАЁМ КНОПКИ
        play_btn = Button(button_x, 250, button_width, button_height, 
                         "ИГРАТЬ", (0, 100, 0), (0, 150, 0))          # Зелёная
        
        leaderboard_btn = Button(button_x, 330, button_width, button_height,
                                "РЕКОРДЫ", (0, 0, 100), (0, 0, 150))  # Синяя
        
        settings_btn = Button(button_x, 410, button_width, button_height,
                             "НАСТРОЙКИ", (100, 100, 0), (150, 150, 0)) # Жёлто-зелёная
        
        quit_btn = Button(button_x, 490, button_width, button_height,
                         "ВЫХОД", (100, 0, 0), (150, 0, 0))            # Красная
        
        buttons = [play_btn, leaderboard_btn, settings_btn, quit_btn]
        
        # ЦИКЛ ОБРАБОТКИ МЕНЮ
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                
                # Проверяем нажатия кнопок
                if play_btn.handle_event(event):
                    return "play"
                elif leaderboard_btn.handle_event(event):
                    return "leaderboard"
                elif settings_btn.handle_event(event):
                    return "settings"
                elif quit_btn.handle_event(event):
                    return "quit"
            
            # ОТРИСОВКА ВСЕХ КНОПОК
            for btn in buttons:
                btn.draw(self.screen, self.font_medium)
            
            pygame.display.flip()  # Обновляем экран
    
    # === ЭКРАН ТАБЛИЦЫ РЕКОРДОВ ===
    def show_leaderboard(self):
        """Отображает топ-10 рекордов"""
        self.screen.fill((30, 30, 40))
        
        # Заголовок
        self.draw_text("ТОП 10 РЕКОРДОВ", self.font_large, (255, 215, 0),
                      self.screen.get_width() // 2, 50, center=True)
        
        # Получаем рекорды из менеджера данных
        scores = self.data_manager.get_top_scores()
        
        # ЗАГОЛОВКИ ТАБЛИЦЫ
        y = 150
        headers = ["#", "ИМЯ", "ОЧКИ", "ДИСТ", "МОНЕТЫ"]
        x_pos = [50, 120, 350, 480, 580]  # X координаты колонок
        
        # Отрисовка заголовков
        for i, header in enumerate(headers):
            self.draw_text(header, self.font_small, (200, 200, 200), x_pos[i], y)
        
        # ОТРИСОВКА СТРОК РЕКОРДОВ
        y += 50
        for i, score in enumerate(scores[:10]):  # Только первые 10
            # Номер места
            self.draw_text(str(i + 1), self.font_small, (255, 255, 255), x_pos[0], y)
            # Имя (обрезаем до 12 символов)
            self.draw_text(score["name"][:12], self.font_small, (255, 255, 255), x_pos[1], y)
            # Очки
            self.draw_text(str(score["score"]), self.font_small, (255, 255, 255), x_pos[2], y)
            # Дистанция
            self.draw_text(str(score["distance"]), self.font_small, (255, 255, 255), x_pos[3], y)
            # Монеты
            self.draw_text(str(score["coins"]), self.font_small, (255, 255, 255), x_pos[4], y)
            y += 40  # Смещение для следующей строки
        
        # Кнопка "Назад"
        back_btn = Button(self.screen.get_width() // 2 - 100, 600, 200, 50,
                         "НАЗАД", (100, 100, 100), (150, 150, 150))
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                
                if back_btn.handle_event(event):
                    return "menu"  # Возврат в главное меню
            
            back_btn.draw(self.screen, self.font_small)
            pygame.display.flip()
    
    # === ЭКРАН НАСТРОЕК ===
    def show_settings(self):
        """Экран настроек: звук, сложность, сохранение"""
        self.screen.fill((30, 30, 40))
        
        # Заголовок
        self.draw_text("НАСТРОЙКИ", self.font_large, (255, 215, 0),
                      self.screen.get_width() // 2, 50, center=True)
        
        # КНОПКА ЗВУКА (переключатель)
        sound_text = "ЗВУК: ВКЛ" if self.data_manager.settings["sound"] else "ЗВУК: ВЫКЛ"
        sound_btn = Button(200, 150, 200, 50, sound_text, (70, 70, 70), (100, 100, 100))
        
        # КНОПКА СЛОЖНОСТИ (циклическое переключение)
        difficulty_text = f"СЛОЖНОСТЬ: {self.data_manager.settings['difficulty'].upper()}"
        difficulty_btn = Button(200, 230, 200, 50, difficulty_text, (70, 70, 70), (100, 100, 100))
        
        # КНОПКА СОХРАНЕНИЯ
        save_btn = Button(200, 400, 200, 50, "СОХРАНИТЬ", (0, 100, 0), (0, 150, 0))
        # КНОПКА ВОЗВРАТА
        back_btn = Button(200, 480, 200, 50, "НАЗАД", (100, 100, 100), (150, 150, 150))
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                
                # ОБРАБОТКА КНОПКИ ЗВУКА
                if sound_btn.handle_event(event):
                    # Переключаем состояние звука
                    self.data_manager.settings["sound"] = not self.data_manager.settings["sound"]
                    # Обновляем текст кнопки
                    sound_btn.text = "ЗВУК: ВКЛ" if self.data_manager.settings["sound"] else "ЗВУК: ВЫКЛ"
                
                # ОБРАБОТКА КНОПКИ СЛОЖНОСТИ (циклическое переключение easy→normal→hard→easy)
                if difficulty_btn.handle_event(event):
                    diffs = ["easy", "normal", "hard"]
                    # Находим индекс текущей сложности
                    curr = diffs.index(self.data_manager.settings["difficulty"])
                    # Переключаем на следующую (с зацикливанием через %)
                    self.data_manager.settings["difficulty"] = diffs[(curr + 1) % 3]
                    # Обновляем текст кнопки
                    difficulty_btn.text = f"СЛОЖНОСТЬ: {self.data_manager.settings['difficulty'].upper()}"
                
                # ОБРАБОТКА СОХРАНЕНИЯ
                if save_btn.handle_event(event):
                    self.data_manager.save_settings()  # Сохраняем настройки в файл
                
                # ВОЗВРАТ В МЕНЮ
                if back_btn.handle_event(event):
                    return "menu"
            
            # ОТРИСОВКА ВСЕХ ЭЛЕМЕНТОВ
            sound_btn.draw(self.screen, self.font_small)
            difficulty_btn.draw(self.screen, self.font_small)
            save_btn.draw(self.screen, self.font_small)
            back_btn.draw(self.screen, self.font_small)
            
            pygame.display.flip()
    
    # === ЭКРАН ВВОДА ИМЕНИ ===
    def get_username(self):
        """Запрашивает имя игрока, возвращает введённую строку"""
        self.screen.fill((30, 30, 40))
        
        # Заголовок
        self.draw_text("ВВЕДИТЕ ВАШЕ ИМЯ", self.font_large, (255, 215, 0),
                      self.screen.get_width() // 2, 150, center=True)
        
        # Поле ввода
        input_box = InputBox(200, 300, 200, 50, self.font_medium)
        # Кнопка подтверждения
        confirm_btn = Button(200, 400, 200, 50, "ПОДТВЕРДИТЬ", (0, 100, 0), (0, 150, 0))
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None  # Выход без имени
                
                # Обработка поля ввода (Enter возвращает текст)
                result = input_box.handle_event(event)
                if result and len(result.strip()) > 0:  # Если текст не пустой
                    return result.strip()
                
                # Обработка кнопки подтверждения
                if confirm_btn.handle_event(event):
                    if len(input_box.text.strip()) > 0:  # Если поле не пустое
                        return input_box.text.strip()
            
            # ОТРИСОВКА (заново, так как экран очищается каждый кадр)
            self.screen.fill((30, 30, 40))
            self.draw_text("ВВЕДИТЕ ВАШЕ ИМЯ", self.font_large, (255, 215, 0),
                          self.screen.get_width() // 2, 150, center=True)
            input_box.draw(self.screen)
            confirm_btn.draw(self.screen, self.font_small)
            
            pygame.display.flip()
    
    # === ЭКРАН КОНЦА ИГРЫ ===
    def show_game_over(self, score, distance, coins, player_name):
        """Отображает итоговую статистику, сохраняет рекорд
           Возвращает "retry" или "menu" """
        self.screen.fill((30, 30, 40))
        
        # Заголовок (красный)
        self.draw_text("ИГРА ОКОНЧЕНА", self.font_large, (255, 0, 0),
                      self.screen.get_width() // 2, 80, center=True)
        
        # СТАТИСТИКА ИГРОКА
        self.draw_text(f"ИГРОК: {player_name}", self.font_medium, (255, 255, 255),
                      self.screen.get_width() // 2, 180, center=True)
        self.draw_text(f"ОЧКИ: {score}", self.font_medium, (255, 215, 0),      # Золотой
                      self.screen.get_width() // 2, 250, center=True)
        self.draw_text(f"ДИСТАНЦИЯ: {distance}", self.font_medium, (100, 200, 255), # Голубой
                      self.screen.get_width() // 2, 320, center=True)
        self.draw_text(f"МОНЕТЫ: {coins}", self.font_medium, (255, 255, 0),    # Жёлтый
                      self.screen.get_width() // 2, 390, center=True)
        
        # СОХРАНЯЕМ РЕЗУЛЬТАТ В ТАБЛИЦУ РЕКОРДОВ
        self.data_manager.add_score(player_name, score, distance, coins)
        
        # КНОПКИ
        retry_btn = Button(100, 480, 200, 50, "СЫГРАТЬ СНОВА", (0, 100, 0), (0, 150, 0))
        menu_btn = Button(300, 480, 200, 50, "ГЛАВНОЕ МЕНЮ", (100, 100, 100), (150, 150, 150))
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                
                if retry_btn.handle_event(event):
                    return "retry"   # Запустить новую игру
                elif menu_btn.handle_event(event):
                    return "menu"    # Вернуться в главное меню
            
            retry_btn.draw(self.screen, self.font_small)
            menu_btn.draw(self.screen, self.font_small)
            
            pygame.display.flip()