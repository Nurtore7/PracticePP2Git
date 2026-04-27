import pygame
import random

class SnakeGame:
    def __init__(self, screen, config, db, player_id, username):
        self.screen = screen
        self.config = config
        self.db = db
        self.player_id = player_id
        
        # Размер игрового поля на весь экран 800x600
        self.game_width = 800
        self.game_height = 600
        
        # Размер клетки: 800/40 = 20, 600/30 = 20
        self.cell_size = 20
        self.grid_width = 40   # 40 клеток по горизонтали (40 * 20 = 800)
        self.grid_height = 30  # 30 клеток по вертикали (30 * 20 = 600)
        
        self.reset_game()
        
    def reset_game(self):
        # Начальная позиция змейки (по центру)
        start_x = self.grid_width // 2
        start_y = self.grid_height // 2
        self.snake = [(start_x, start_y)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.score = 0
        self.level = 1
        self.speed = 10
        
        self.food = None
        self.poison = None
        self.powerup = None
        self.speed_boost_end = 0
        self.slow_motion_end = 0
        self.shield_active = False
        self.obstacles = []
        self.game_over = False
        self.game_over_reason = ""
        
        self.spawn_food()
        self.personal_best = self.db.get_personal_best(self.player_id)
        self.food_eaten = 0
    
    def generate_obstacles(self):
        """Генерация препятствий с 3 уровня"""
        num_obstacles = min(5 + self.level, 20)
        self.obstacles = []
        
        for _ in range(num_obstacles):
            attempts = 0
            while attempts < 100:
                x = random.randint(1, self.grid_width - 2)
                y = random.randint(1, self.grid_height - 2)
                pos = (x, y)
                if (pos not in self.snake and pos != self.food and 
                    pos not in self.obstacles and pos != self.poison):
                    self.obstacles.append(pos)
                    break
                attempts += 1
    
    def spawn_food(self):
        """Спавн еды"""
        attempts = 0
        while attempts < 100:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            pos = (x, y)
            if (pos not in self.snake and pos not in self.obstacles and
                pos != self.poison and pos != self.food):
                self.food = pos
                
                # Спавн яда (20% шанс)
                if random.random() < 0.2 and not self.poison:
                    self.spawn_poison()
                
                # Спавн бонуса (15% шанс)
                if random.random() < 0.15 and not self.powerup:
                    self.spawn_powerup()
                return
            attempts += 1
    
    def spawn_poison(self):
        """Спавн ядовитой еды"""
        attempts = 0
        while attempts < 100:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            pos = (x, y)
            if (pos not in self.snake and pos not in self.obstacles and
                pos != self.food and pos != self.poison):
                self.poison = pos
                return
            attempts += 1
    
    def spawn_powerup(self):
        """Спавн бонуса"""
        powerup_types = ['speed', 'slow', 'shield']
        self.powerup = {
            'pos': None,
            'type': random.choice(powerup_types),
            'spawn_time': pygame.time.get_ticks()
        }
        
        attempts = 0
        while attempts < 100:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            pos = (x, y)
            if (pos not in self.snake and pos not in self.obstacles and
                pos != self.food and pos != self.poison):
                self.powerup['pos'] = pos
                return
            attempts += 1
        self.powerup = None
    
    def update(self):
        """Обновление игры"""
        if self.game_over:
            return
        
        self.direction = self.next_direction
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # Проверка столкновения с собой
        if new_head in self.snake[1:]:
            if not self.shield_active:
                self.end_game("Self collision!")
                return
            else:
                self.shield_active = False
        
        # Проверка столкновения со стеной
        if (new_head[0] < 0 or new_head[0] >= self.grid_width or
            new_head[1] < 0 or new_head[1] >= self.grid_height):
            if not self.shield_active:
                self.end_game("Hit the wall!")
                return
            else:
                self.shield_active = False
        
        # Проверка столкновения с препятствием
        if new_head in self.obstacles:
            if not self.shield_active:
                self.end_game("Hit an obstacle!")
                return
            else:
                self.shield_active = False
        
        # Съедание еды
        if new_head == self.food:
            self.snake.insert(0, new_head)
            self.score += 10
            self.food_eaten += 1
            self.food = None
            self.poison = None
            self.spawn_food()
            
            # Повышение уровня каждые 5 съеденных еды
            if self.food_eaten % 5 == 0:
                self.level += 1
                if self.level >= 3:
                    self.generate_obstacles()
                self.speed = min(10 + self.level, 20)
            return
        
        # Съедание яда
        if new_head == self.poison:
            # Укорачиваем змею на 2 сегмента
            for _ in range(2):
                if len(self.snake) > 1:
                    self.snake.pop()
            
            if len(self.snake) <= 1:
                self.end_game("You became too short!")
                return
            
            self.snake.insert(0, new_head)
            self.poison = None
            self.spawn_food()
            return
        
        # Съедание бонуса
        if self.powerup and new_head == self.powerup['pos']:
            self.activate_powerup(self.powerup['type'])
            self.powerup = None
            self.spawn_food()
        
        # Удаление просроченного бонуса (8 секунд)
        if self.powerup:
            current_time = pygame.time.get_ticks()
            if current_time - self.powerup['spawn_time'] > 8000:
                self.powerup = None
                self.spawn_food()
        
        # Обычное движение
        self.snake.insert(0, new_head)
        self.snake.pop()
        
        # Обновление времени действия бонусов
        current_time = pygame.time.get_ticks()
        if self.speed_boost_end and current_time > self.speed_boost_end:
            self.speed_boost_end = 0
            self.speed = 10 + self.level if self.level < 20 else 20
        
        if self.slow_motion_end and current_time > self.slow_motion_end:
            self.slow_motion_end = 0
            self.speed = 10 + self.level if self.level < 20 else 20
    
    def activate_powerup(self, powerup_type):
        """Активация бонуса"""
        current_time = pygame.time.get_ticks()
        
        if powerup_type == 'speed':
            self.speed_boost_end = current_time + 5000
            self.speed = min(self.speed + 5, 30)
        elif powerup_type == 'slow':
            self.slow_motion_end = current_time + 5000
            self.speed = max(self.speed - 5, 5)
        elif powerup_type == 'shield':
            self.shield_active = True
    
    def end_game(self, reason):
        """Завершение игры"""
        self.game_over = True
        self.game_over_reason = reason
        self.db.save_game_session(self.player_id, self.score, self.level)
    
    def draw(self):
        """Отрисовка игры"""
        # Фон игрового поля
        game_rect = pygame.Rect(0, 0, self.game_width, self.game_height)
        pygame.draw.rect(self.screen, (15, 15, 15), game_rect)
        pygame.draw.rect(self.screen, (50, 50, 50), game_rect, 2)
        
        # Рисуем сетку (grid) на весь экран
        if self.config.grid_overlay:
            for x in range(0, self.game_width + 1, self.cell_size):
                pygame.draw.line(self.screen, (35, 35, 35), (x, 0), (x, self.game_height), 1)
            for y in range(0, self.game_height + 1, self.cell_size):
                pygame.draw.line(self.screen, (35, 35, 35), (0, y), (self.game_width, y), 1)
        
        # Рисуем препятствия
        for obs in self.obstacles:
            rect = pygame.Rect(
                obs[0] * self.cell_size,
                obs[1] * self.cell_size,
                self.cell_size - 1,
                self.cell_size - 1
            )
            pygame.draw.rect(self.screen, (80, 80, 80), rect)
            pygame.draw.rect(self.screen, (120, 120, 120), rect, 1)
        
        # Рисуем змейку
        for i, segment in enumerate(self.snake):
            rect = pygame.Rect(
                segment[0] * self.cell_size,
                segment[1] * self.cell_size,
                self.cell_size - 1,
                self.cell_size - 1
            )
            # Голова - ярче
            if i == 0:
                color = self.config.snake_color
                pygame.draw.rect(self.screen, color, rect)
                # Глаза
                eye_size = self.cell_size // 5
                if self.direction == (1, 0):  # Вправо
                    pygame.draw.circle(self.screen, (255, 255, 255), 
                                      (rect.right - eye_size, rect.top + eye_size), eye_size // 2)
                    pygame.draw.circle(self.screen, (255, 255, 255), 
                                      (rect.right - eye_size, rect.bottom - eye_size), eye_size // 2)
                elif self.direction == (-1, 0):  # Влево
                    pygame.draw.circle(self.screen, (255, 255, 255), 
                                      (rect.left + eye_size, rect.top + eye_size), eye_size // 2)
                    pygame.draw.circle(self.screen, (255, 255, 255), 
                                      (rect.left + eye_size, rect.bottom - eye_size), eye_size // 2)
                elif self.direction == (0, -1):  # Вверх
                    pygame.draw.circle(self.screen, (255, 255, 255), 
                                      (rect.left + eye_size, rect.top + eye_size), eye_size // 2)
                    pygame.draw.circle(self.screen, (255, 255, 255), 
                                      (rect.right - eye_size, rect.top + eye_size), eye_size // 2)
                else:  # Вниз
                    pygame.draw.circle(self.screen, (255, 255, 255), 
                                      (rect.left + eye_size, rect.bottom - eye_size), eye_size // 2)
                    pygame.draw.circle(self.screen, (255, 255, 255), 
                                      (rect.right - eye_size, rect.bottom - eye_size), eye_size // 2)
            else:
                pygame.draw.rect(self.screen, self.config.snake_color, rect)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
        
        # Рисуем еду
        if self.food:
            rect = pygame.Rect(
                self.food[0] * self.cell_size,
                self.food[1] * self.cell_size,
                self.cell_size - 1,
                self.cell_size - 1
            )
            pygame.draw.rect(self.screen, (255, 0, 0), rect)
            # Сияние
            pygame.draw.circle(self.screen, (255, 100, 100), rect.center, self.cell_size // 3)
        
        # Рисуем яд
        if self.poison:
            rect = pygame.Rect(
                self.poison[0] * self.cell_size,
                self.poison[1] * self.cell_size,
                self.cell_size - 1,
                self.cell_size - 1
            )
            pygame.draw.rect(self.screen, (139, 0, 0), rect)
            # Череп и кости (упрощенно)
            pygame.draw.line(self.screen, (0, 0, 0), rect.topleft, rect.bottomright, 2)
            pygame.draw.line(self.screen, (0, 0, 0), rect.topright, rect.bottomleft, 2)
        
        # Рисуем бонусы
        if self.powerup:
            rect = pygame.Rect(
                self.powerup['pos'][0] * self.cell_size,
                self.powerup['pos'][1] * self.cell_size,
                self.cell_size - 1,
                self.cell_size - 1
            )
            
            if self.powerup['type'] == 'speed':
                color = (255, 255, 0)
                icon = "⚡"
            elif self.powerup['type'] == 'slow':
                color = (0, 255, 255)
                icon = "🐢"
            else:  # shield
                color = (255, 0, 255)
                icon = "🛡️"
            
            pygame.draw.rect(self.screen, color, rect)
            # Иконка
            icon_font = pygame.font.Font(None, self.cell_size)
            icon_surf = icon_font.render(icon, True, (255, 255, 255))
            icon_rect = icon_surf.get_rect(center=rect.center)
            self.screen.blit(icon_surf, icon_rect)
        
        # UI текст (справа от игрового поля - но т.к. поле 800, текст будет поверх)
        # Для красоты сделаем полупрозрачный фон
        font = pygame.font.Font(None, 28)
        
        # Фон для текста
        text_bg = pygame.Surface((150, 120))
        text_bg.set_alpha(180)
        text_bg.fill((0, 0, 0))
        self.screen.blit(text_bg, (5, 5))
        
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        level_text = font.render(f"Level: {self.level}", True, (255, 255, 255))
        best_text = font.render(f"Best: {self.personal_best}", True, (255, 255, 255))
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (10, 40))
        self.screen.blit(best_text, (10, 70))
        
        # Активные эффекты
        y_offset = 110
        if self.speed_boost_end:
            time_left = max(0, (self.speed_boost_end - pygame.time.get_ticks()) // 1000)
            boost_text = font.render(f"⚡ Speed: {time_left}s", True, (255, 255, 0))
            self.screen.blit(boost_text, (10, y_offset))
            y_offset += 25
        
        if self.slow_motion_end:
            time_left = max(0, (self.slow_motion_end - pygame.time.get_ticks()) // 1000)
            slow_text = font.render(f"🐢 Slow: {time_left}s", True, (0, 255, 255))
            self.screen.blit(slow_text, (10, y_offset))
            y_offset += 25
        
        if self.shield_active:
            shield_text = font.render(f"🛡️ Shield", True, (255, 0, 255))
            self.screen.blit(shield_text, (10, y_offset))
    
    def handle_event(self, event):
        """Обработка нажатий клавиш"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and self.direction != (0, 1):
                self.next_direction = (0, -1)
            elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                self.next_direction = (0, 1)
            elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                self.next_direction = (-1, 0)
            elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                self.next_direction = (1, 0)