# МОДУЛЬ ИГРОВЫХ ОБЪЕКТОВ - ВСЕ КЛАССЫ ДЛЯ РИСОВАНИЯ И ЛОГИКИ
import pygame
import random

# КЛАСС МАШИНЫ ИГРОКА
class PlayerCar:
    def __init__(self, x, y, image_path, color_tint=None):
        # ЗАГРУЗКА ИЗОБРАЖЕНИЯ МАШИНЫ
        # convert_alpha() - оптимизирует изображение с сохранением прозрачности
        self.image_original = pygame.image.load(image_path).convert_alpha()
        # Масштабируем до размера 50x80 пикселей
        self.image_original = pygame.transform.scale(self.image_original, (50, 80))
        
        # НАЛОЖЕНИЕ ЦВЕТОВОГО ОТТЕНКА (кастомизация цвета машины)
        if color_tint:
            self.image_original = self.apply_color_tint(self.image_original, color_tint)
        
        self.image = self.image_original  # Текущее изображение (может быть повёрнуто)
        self.x = x          # X координата
        self.y = y          # Y координата
        self.width = 50     # Ширина машины
        self.height = 80    # Высота машины
        self.speed = 5      # Текущая скорость
        self.base_speed = 5 # Базовая скорость (без бонусов)
        self.lane = 1       # Текущая полоса (0-левая, 1-центр, 2-правая)
        self.lane_positions = [140, 300, 460]  # X координаты центров трёх полос
        self.active_powerup = None    # Активный бонус ("nitro" или "shield")
        self.powerup_timer = 0         # Таймер действия бонуса (кадры)
        self.shield_active = False     # Флаг активного щита
        
        # Вычисляем начальную X позицию на основе текущей полосы
        self.x = self.lane_positions[self.lane] - (self.width // 2)
        self.tilt_angle = 0   # Угол наклона при повороте (эффект при смене полосы)
        self.tilt_timer = 0   # Таймер длительности эффекта наклона
    
    def apply_color_tint(self, image, color):
        """Накладывает цветовой оттенок на изображение
           Аргументы:
           image - исходное изображение
           color - кортеж (R, G, B) целевого цвета
           Возвращает: новое изображение с оттенком
        """
        # Создаём копию изображения
        tinted = image.copy()
        # Проходим по каждому пикселю изображения
        for x in range(tinted.get_width()):
            for y in range(tinted.get_height()):
                # Получаем цвет пикселя (R, G, B, Alpha - прозрачность)
                r, g, b, a = tinted.get_at((x, y))
                if a > 0:  # Только непрозрачные пиксели
                    # Умножаем каждый цветовой канал на соответствующий канал оттенка
                    # Пример: если цвет оттенка красный (255,0,0), то белый станет красным
                    new_r = int(r * color[0] / 255)
                    new_g = int(g * color[1] / 255)
                    new_b = int(b * color[2] / 255)
                    tinted.set_at((x, y), (new_r, new_g, new_b, a))
        return tinted
    
    def move_left(self):
        """Перемещение на левую полосу"""
        if self.lane > 0:  # Проверка: не крайняя левая полоса
            self.lane -= 1
            # Пересчитываем X позицию для новой полосы
            self.x = self.lane_positions[self.lane] - (self.width // 2)
            # Эффект наклона при повороте
            self.tilt_angle = -20  # Наклон влево на 20 градусов
            self.tilt_timer = 10   # Эффект длится 10 кадров
    
    def move_right(self):
        """Перемещение на правую полосу"""
        if self.lane < 2:  # Проверка: не крайняя правая полоса
            self.lane += 1
            self.x = self.lane_positions[self.lane] - (self.width // 2)
            self.tilt_angle = 20   # Наклон вправо на 20 градусов
            self.tilt_timer = 10
    
    def activate_powerup(self, powerup_type):
        """Активация бонуса
           nitro - ускорение (действует 300 кадров)
           shield - щит (защищает от одного столкновения, действует бесконечно)
        """
        self.active_powerup = powerup_type
        if powerup_type == "nitro":
            self.powerup_timer = 300  # 5 секунд при 60 FPS (300/60=5)
        elif powerup_type == "shield":
            self.powerup_timer = -1    # Бесконечный (до первого столкновения)
            self.shield_active = True
    
    def update(self):
        """Обновление состояния игрока (каждый кадр)"""
        # Уменьшаем таймер нитро
        if self.active_powerup == "nitro":
            self.powerup_timer -= 1
        
        # Обновляем эффект наклона (постепенно возвращаем угол в 0)
        if self.tilt_timer > 0:
            self.tilt_timer -= 1
            if self.tilt_timer == 0:
                self.tilt_angle = 0  # Возвращаем машину в горизонтальное положение
    
    def draw(self, screen):
        """Отрисовка машины игрока с эффектами (щит, наклон)"""
        
        # РИСУЕМ ЩИТ (полупрозрачный голубой круг вокруг машины)
        if self.shield_active:
            shield_radius = 45
            # Создаём поверхность с альфа-каналом для прозрачности
            shield_surface = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
            # Рисуем голубой круг с прозрачностью 128 (полупрозрачный)
            pygame.draw.circle(shield_surface, (0, 255, 255, 128), 
                             (shield_radius, shield_radius), shield_radius)
            screen.blit(shield_surface, (self.x - 20, self.y - 10))
        
        # РИСУЕМ МАШИНУ С УЧЁТОМ НАКЛОНА
        if self.tilt_angle != 0:
            # Поворачиваем изображение на угол tilt_angle
            rotated_image = pygame.transform.rotate(self.image, self.tilt_angle)
            # Получаем новый прямоугольник с центром в том же месте
            new_rect = rotated_image.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
            screen.blit(rotated_image, new_rect)
        else:
            # Без наклона - рисуем как есть
            screen.blit(self.image, (self.x, self.y))
    
    def get_rect(self):
        """Возвращает прямоугольник для проверки столкновений"""
        return pygame.Rect(self.x, self.y, self.width, self.height)


# КЛАСС ВРАЖЕСКОЙ МАШИНЫ
class EnemyCar:
    def __init__(self, x, y, image_path):
        # Загружаем и масштабируем изображение врага
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 80))
        self.x = x      # X позиция
        self.y = y      # Y позиция (обычно отрицательная - выше экрана)
        self.width = 50
        self.height = 80
        
    def update(self, speed):
        """Движение вниз со скоростью игры"""
        self.y += speed
    
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


# КЛАСС ПРЕПЯТСТВИЯ (БАРЬЕР ИЛИ МАСЛО)
class Obstacle:
    def __init__(self, x, y, obstacle_type, image=None):
        self.x = x
        self.y = y
        self.type = obstacle_type  # "barrier" или "oil"
        self.image = image
        
        # Определяем размеры в зависимости от типа и наличия изображения
        if image:
            self.width = image.get_width()
            self.height = image.get_height()
        else:
            # Значения по умолчанию (запасные)
            self.width = 105
            self.height = 105
        
    def update(self, speed):
        self.y += speed
    
    def draw(self, screen):
        # Рисуем только если есть изображение
        if self.image:
            screen.blit(self.image, (self.x, self.y))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


# КЛАСС БОНУСА (НИТРО ИЛИ ЩИТ)
class PowerUp:
    def __init__(self, x, y, power_type, image=None):
        self.x = x
        self.y = y
        self.type = power_type  # "nitro" или "shield"
        self.image = image
        self.lifetime = 300  # Время жизни на экране (300 кадров)
        
        # Определяем размеры
        if image:
            self.width = image.get_width()
            self.height = image.get_height()
        else:
            # Для щита без изображения (рисуем программно)
            self.width = 75
            self.height = 75
        
    def update(self, speed):
        """Обновление позиции и времени жизни.
           Возвращает False если бонус должен исчезнуть"""
        self.y += speed
        self.lifetime -= 1
        return self.lifetime > 0  # True - жив, False - пора удалить
    
    def draw(self, screen):
        if self.image:
            # Рисуем загруженное изображение
            screen.blit(self.image, (self.x, self.y))
        else:
            # РИСУЕМ ЩИТ ПРОГРАММНО (если нет изображения)
            if self.type == "shield":
                # Прямоугольник-основа
                pygame.draw.rect(screen, (0, 200, 255), 
                               (self.x, self.y, self.width, self.height))
                # Круг-символ щита
                pygame.draw.circle(screen, (0, 100, 255), 
                                 (self.x + 37, self.y + 37), 25)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


# КЛАСС МОНЕТЫ (С АНИМАЦИЕЙ ПУЛЬСАЦИИ)
class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.animation_frame = 0  # Счётчик для анимации
        
    def update(self, speed):
        self.y += speed
        self.animation_frame += 1  # Увеличиваем кадр анимации каждый тик
    
    def draw(self, screen):
        # АНИМАЦИЯ ПУЛЬСАЦИИ: размер меняется со временем
        # animation_frame % 20 - значение от 0 до 19
        # abs(... - 10) - от 10 до 0 до 10 (треугольная волна)
        # //5 - деление на 5 даёт значения 0,1,2
        # 15 + ... - размер от 15 до 17
        size = 15 + abs(self.animation_frame % 20 - 10) // 5
        
        # Внешний круг (золотой)
        pygame.draw.circle(screen, (255, 215, 0), 
                         (self.x + 10, self.y + 10), size)
        # Внутренний круг (светло-жёлтый) - блик
        pygame.draw.circle(screen, (255, 255, 0), 
                         (self.x + 10, self.y + 10), size // 2)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)