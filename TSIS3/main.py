# ИГРОВОЙ ДВИЖОК - ОСНОВНОЙ КЛАСС ИГРЫ
import pygame  # Библиотека для создания игр и графики
import sys     # Системные функции (выход из программы)
import random  # Генерация случайных чисел (спавн объектов)
import os      # Работа с файловой системой (пути к файлам)
from persistence import DataManager  # Класс для сохранения/загрузки данных (рекорды, настройки)
from racer import PlayerCar, Obstacle, EnemyCar, PowerUp, Coin  # Классы игровых объектов
from ui import UIManager  # Класс управления пользовательским интерфейсом

# ГЛАВНЫЙ КЛАСС ИГРЫ
class Game:
    def __init__(self):
        # ИНИЦИАЛИЗАЦИЯ PYGAME
        pygame.init()  # Запуск всех модулей Pygame (графика, звук, события)
        pygame.mixer.init()  # Инициализация звуковой системы
        
        # ПОЛУЧАЕМ ПУТЬ К ПАПКЕ СКРИПТА
        # __file__ - путь к текущему файлу
        # os.path.abspath - превращает в абсолютный путь
        # os.path.dirname - берёт только папку (без имени файла)
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        # МЕНЯЕМ ТЕКУЩУЮ РАБОЧУЮ ДИРЕКТОРИЮ на папку скрипта
        # Это нужно, чтобы все относительные пути работали корректно
        os.chdir(self.script_dir)
        
        # СОЗДАЁМ ОКНО ИГРЫ: 600 пикс ширина, 700 пикс высота
        self.screen = pygame.display.set_mode((600, 700))
        pygame.display.set_caption("Racing Game")  # Заголовок окна
        self.clock = pygame.time.Clock()  # Объект для контроля FPS
        self.running = True  # Флаг работы основного цикла
        
        # ОПРЕДЕЛЯЕМ ПУТЬ К ПАПКЕ С АССЕТАМИ (изображения, звуки)
        self.assets_dir = os.path.join(self.script_dir, "assets")
        
        # ЗАГРУЗКА ИЗОБРАЖЕНИЙ
        try:
            # Сохраняем пути к файлам изображений
            self.player_img = os.path.join(self.assets_dir, "Player.png")
            self.enemy_img = os.path.join(self.assets_dir, "Enemy.png")
            self.barrier_img = os.path.join(self.assets_dir, "Barrier.png")
            self.nitro_img = os.path.join(self.assets_dir, "Nitro.png")
            self.oil_img = os.path.join(self.assets_dir, "Oil.png")
            
            # ЗАГРУЖАЕМ ФОН ДОРОГИ
            # .convert() - оптимизирует изображение для быстрого отображения в Pygame
            self.road_img = pygame.image.load(os.path.join(self.assets_dir, "AnimatedStreet.png")).convert()
            self.road_img = pygame.transform.scale(self.road_img, (600, 700))  # Растягиваем под размер окна
            
            # ЗАГРУЖАЕМ И МАСШТАБИРУЕМ ПРЕПЯТСТВИЯ И БОНУСЫ
            # .convert_alpha() - сохраняет прозрачность (альфа-канал)
            self.barrier_surf = pygame.image.load(self.barrier_img).convert_alpha()
            self.barrier_surf = pygame.transform.scale(self.barrier_surf, (105, 105))
            
            self.nitro_surf = pygame.image.load(self.nitro_img).convert_alpha()
            self.nitro_surf = pygame.transform.scale(self.nitro_surf, (155, 155))
            
            self.oil_surf = pygame.image.load(self.oil_img).convert_alpha()
            self.oil_surf = pygame.transform.scale(self.oil_surf, (115, 115))
            
        except Exception as e:
            # Если не удалось загрузить изображения - выводим ошибку и выходим
            print(f"Ошибка загрузки изображений: {e}")
            print("Проверьте папку assets/")
            sys.exit()  # Аварийное завершение программы
        
        # ЗАГРУЗКА ЗВУКА
        try:
            sound_path = os.path.join(self.script_dir, "crash.wav")
            self.crash_sound = pygame.mixer.Sound(sound_path)  # Создаём звуковой объект
        except:
            self.crash_sound = None  # Если звука нет - игнорируем
        
        # СОЗДАЁМ МЕНЕДЖЕРЫ
        # DataManager - работает с файлами (сохранения, настройки)
        self.data_manager = DataManager()
        # UIManager - рисует меню, кнопки, таблицу рекордов
        self.ui_manager = UIManager(self.screen, self.data_manager)
        
        # ПАРАМЕТРЫ ИГРЫ (будут сброшены при старте)
        self.player_name = ""  # Имя игрока
        self.score = 0         # Очки игры
        self.distance = 0      # Пройденная дистанция (условные единицы)
        self.coins = 0         # Количество собранных монет
        self.game_speed = 5    # Текущая скорость игры (чем выше, тем быстрее едут объекты)
        self.road_y = 0        # Смещение фона для анимации движения
        
        # СПИСКИ ИГРОВЫХ ОБЪЕКТОВ
        self.obstacles = []    # Препятствия (барьеры, масло)
        self.traffic_cars = [] # Машины противников
        self.powerups = []     # Бонусы (нитро, щит)
        self.coins_list = []   # Монеты
        
        # ТАЙМЕРЫ ДЛЯ ПОЯВЛЕНИЯ ОБЪЕКТОВ
        self.spawn_timer = 0        # Счётчик для спавна врагов/препятствий
        self.difficulty_timer = 0   # Таймер увеличения сложности
        
        # ТАЙМЕРЫ ДЛЯ МОНЕТ НА КАЖДОЙ ПОЛОСЕ
        # 3 полосы: левая (140px), центральная (300px), правая (460px)
        self.coin_timers = [0, 0, 0]  # Текущие счётчики для каждой полосы
        # Случайные задержки между появлением монет на каждой полосе (40-100 кадров)
        self.coin_delays = [random.randint(40, 100), random.randint(40, 100), random.randint(40, 100)]
        
        # НАСТРОЙКИ СЛОЖНОСТИ (словарь в словаре)
        # spawn_delay - задержка между спавном (чем меньше, тем чаще спавн)
        # start_speed, min_speed, max_speed - параметры скорости
        self.difficulty_settings = {
            "easy": {"spawn_delay": 70, "start_speed": 5, "max_speed": 10, "min_speed": 5},
            "normal": {"spawn_delay": 50, "start_speed": 8, "max_speed": 12, "min_speed": 8},
            "hard": {"spawn_delay": 35, "start_speed": 12, "max_speed": 16, "min_speed": 12}
        }
    
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    def play_sound(self, sound):
        """Воспроизводит звук, если звук включён в настройках"""
        # Проверяем флаг звука в настройках и что звук существует
        if self.data_manager.settings["sound"] and sound:
            sound.play()
    
    def clamp_speed(self, speed):
        """Ограничивает скорость в пределах min и max для текущей сложности"""
        # Получаем текущую сложность из настроек
        difficulty = self.data_manager.settings["difficulty"]
        # Берём минимальную и максимальную скорость для этой сложности
        min_speed = self.difficulty_settings[difficulty]["min_speed"]
        max_speed = self.difficulty_settings[difficulty]["max_speed"]
        # max(min_speed, min(speed, max_speed)) - ограничиваем скорость диапазоном
        return max(min_speed, min(speed, max_speed))
    
    # СБРОС ИГРЫ ДО НАЧАЛЬНОГО СОСТОЯНИЯ
    def reset_game(self):
        """Сбрасывает все игровые переменные перед началом новой игры"""
        self.score = 0
        self.distance = 0
        self.coins = 0
        self.road_y = 0
        
        # ОЧИЩАЕМ ВСЕ СПИСКИ ОБЪЕКТОВ
        self.obstacles.clear()
        self.traffic_cars.clear()
        self.powerups.clear()
        self.coins_list.clear()
        
        # Устанавливаем скорость в зависимости от сложности
        difficulty = self.data_manager.settings["difficulty"]
        self.game_speed = self.difficulty_settings[difficulty]["start_speed"]
        
        # СОЗДАЁМ ИГРОКА
        car_color = self.data_manager.settings["car_color"]  # Цвет машины из настроек
        # Машина игрока: x=300-25 (центрируем на средней полосе), y=550, изображение, цвет
        self.player = PlayerCar(300 - 25, 550, self.player_img, car_color)
        self.player.base_speed = self.game_speed  # Базовая скорость игрока
        self.player.speed = self.game_speed        # Текущая скорость
        # Обновляем позиции полос для игрока (левая, центр, правая)
        self.player.lane_positions = [140, 300, 460]
        
        # СБРАСЫВАЕМ ТАЙМЕРЫ
        self.spawn_timer = 0
        self.difficulty_timer = 0
        
        # Сбрасываем таймеры монет с новыми случайными задержками
        self.coin_timers = [0, 0, 0]
        self.coin_delays = [random.randint(40, 100), random.randint(40, 100), random.randint(40, 100)]
    
    def get_centered_x(self, lane_center, object_width):
        """Возвращает X координату для центрирования объекта на полосе"""
        # Вычитаем половину ширины объекта, чтобы он оказался по центру полосы
        return lane_center - (object_width // 2)
    
    # МЕТОДЫ СОЗДАНИЯ ОБЪЕКТОВ (СПАВН)
    def spawn_traffic(self):
        """Создаёт вражескую машину на случайной полосе"""
        lanes = [140, 300, 460]  # Центры трёх полос
        lane = random.choice(lanes)  # Выбираем случайную полосу
        obj_width = 50  # Ширина вражеской машины
        x = self.get_centered_x(lane, obj_width)  # Центрируем
        # Добавляем машину в список (y = -80 - за пределами экрана сверху)
        self.traffic_cars.append(EnemyCar(x, -80, self.enemy_img))
    
    def spawn_obstacle(self):
        """Создаёт препятствие (барьер или лужа масла) на случайной полосе"""
        lanes = [140, 300, 460]
        lane = random.choice(lanes)
        # Случайный выбор типа препятствия
        obstacle_type = random.choice(["barrier", "oil"])
        if obstacle_type == "barrier":
            obj_width = 105
            x = self.get_centered_x(lane, obj_width)
            self.obstacles.append(Obstacle(x, -105, obstacle_type, self.barrier_surf))
        else:  # oil
            obj_width = 115
            x = self.get_centered_x(lane, obj_width)
            self.obstacles.append(Obstacle(x, -115, obstacle_type, self.oil_surf))
    
    def spawn_powerup(self):
        """Создаёт бонус (нитро или щит) на случайной полосе"""
        lanes = [140, 300, 460]
        lane = random.choice(lanes)
        power_type = random.choice(["nitro", "shield"])
        if power_type == "nitro":
            obj_width = 155
            x = self.get_centered_x(lane, obj_width)
            self.powerups.append(PowerUp(x, -155, power_type, self.nitro_surf))
        else:  # shield
            obj_width = 75
            x = self.get_centered_x(lane, obj_width)
            self.powerups.append(PowerUp(x, -95, power_type))  # Щит без изображения
    
    def spawn_coin_on_lane(self, lane_index):
        """Создаёт монету на конкретной полосе (индекс 0,1,2)"""
        lanes = [140, 300, 460]
        lane_center = lanes[lane_index]
        obj_width = 20  # Ширина монеты
        x = self.get_centered_x(lane_center, obj_width)
        self.coins_list.append(Coin(x, -50))  # y=-50 - выше границы экрана
    
    # ИГРОВАЯ ЛОГИКА
    def update_score(self):
        """Обновляет очки и дистанцию, увеличивает сложность со временем"""
        self.score += 1
        self.distance += 1
        
        # Увеличение сложности со временем
        self.difficulty_timer += 1
        if self.difficulty_timer > 500:  # Каждые ~8 секунд (500 кадров при 60 FPS)
            self.difficulty_timer = 0
            difficulty = self.data_manager.settings["difficulty"]
            max_speed = self.difficulty_settings[difficulty]["max_speed"]
            # Увеличиваем скорость только если не превышаем максимум
            if self.game_speed < max_speed:
                new_speed = min(self.game_speed + 0.5, max_speed)  # +0.5 к скорости
                self.game_speed = self.clamp_speed(new_speed)      # Ограничиваем
                # Обновляем скорость игрока если нет активного нитро
                if self.player.active_powerup != "nitro":
                    self.player.base_speed = self.game_speed
                    self.player.speed = self.game_speed
    
    def check_collisions(self):
        """Проверяет все столкновения игрока с объектами.
           Возвращает False если игра должна закончиться, True если продолжается"""
        
        player_rect = self.player.get_rect()  # Получаем прямоугольник игрока для столкновений
        
        # ПРОВЕРКА СТОЛКНОВЕНИЙ С ТРАФИКОМ (вражеские машины)
        for car in self.traffic_cars[:]:  # [:] - копия списка, чтобы можно было удалять элементы
            if player_rect.colliderect(car.get_rect()):  # Столкновение?
                if self.player.shield_active:  # Если активен щит - защищает!
                    self.player.shield_active = False
                    self.player.active_powerup = None
                    self.traffic_cars.remove(car)  # Уничтожаем вражескую машину
                    self.play_sound(self.crash_sound)
                else:
                    self.play_sound(self.crash_sound)
                    return False  # Игра окончена
        
        # ПРОВЕРКА СТОЛКНОВЕНИЙ С ПРЕПЯТСТВИЯМИ
        for obs in self.obstacles[:]:
            if player_rect.colliderect(obs.get_rect()):
                if self.player.shield_active:  # Щит защищает
                    self.player.shield_active = False
                    self.player.active_powerup = None
                    self.obstacles.remove(obs)
                    self.play_sound(self.crash_sound)
                else:
                    self.play_sound(self.crash_sound)
                    # Масло только замедляет, НЕ заканчивает игру
                    if obs.type == "oil":
                        # Уменьшаем скорость на 3
                        new_speed = self.game_speed - 3
                        self.game_speed = self.clamp_speed(new_speed)
                        # Обновляем скорость игрока
                        if self.player.active_powerup != "nitro":
                            self.player.base_speed = self.game_speed
                            self.player.speed = self.game_speed
                        self.obstacles.remove(obs)  # Убираем лужицу масла
                    else:
                        # Барьер - смерть (игра заканчивается)
                        return False
        
        # ПРОВЕРКА СБОРА БОНУСОВ
        for power in self.powerups[:]:
            if player_rect.colliderect(power.get_rect()):
                self.player.activate_powerup(power.type)  # Активируем эффект бонуса
                # Если это нитро, увеличиваем скорость
                if power.type == "nitro":
                    new_speed = self.game_speed + 3  # +3 к скорости
                    self.game_speed = self.clamp_speed(new_speed)
                    self.player.base_speed = self.game_speed
                    self.player.speed = self.game_speed
                self.powerups.remove(power)  # Убираем бонус с экрана
        
        # ПРОВЕРКА СБОРА МОНЕТ
        for coin in self.coins_list[:]:
            if player_rect.colliderect(coin.get_rect()):
                self.coins += 1      # Увеличиваем счётчик монет
                self.score += 10     # Даём дополнительные очки
                self.coins_list.remove(coin)  # Убираем монету
        
        return True  # Игра продолжается
    
    # ОТРИСОВКА ИГРЫ
    def draw_road(self):
        """Рисует анимированную дорогу (бесконечный прокручивающийся фон)"""
        # Эффект движения: смещаем координату Y фона и рисуем дважды
        self.road_y = (self.road_y + self.game_speed) % self.road_img.get_height()
        # Рисуем первую копию фона
        self.screen.blit(self.road_img, (0, self.road_y - self.road_img.get_height()))
        # Рисуем вторую копию для бесшовного зацикливания
        self.screen.blit(self.road_img, (0, self.road_y))
    
    def draw_hud(self):
        """Рисует интерфейс пользователя: очки, дистанция, монеты, скорость, сложность, бонусы"""
        font = pygame.font.Font(None, 30)  # Шрифт без указания файла (стандартный), размер 30
        
        # ПОЛУПРОЗРАЧНЫЙ ФОНОВЫЙ ПРЯМОУГОЛЬНИК для текста HUD
        s = pygame.Surface((200, 150))  # Создаём поверхность 200x150
        s.set_alpha(180)  # Устанавливаем прозрачность (0-255, 180 - полупрозрачный)
        s.fill((0, 0, 0))  # Заполняем чёрным цветом
        self.screen.blit(s, (0, 0))  # Рисуем в левом верхнем углу
        
        # ОТОБРАЖАЕМ ПОКАЗАТЕЛИ
        self.screen.blit(font.render(f"ОЧКИ: {self.score}", True, (255, 255, 255)), (10, 10))
        self.screen.blit(font.render(f"ДИСТ: {self.distance}", True, (100, 200, 255)), (10, 40))
        self.screen.blit(font.render(f"МОНЕТЫ: {self.coins}", True, (255, 215, 0)), (10, 70))
        
        # Отображаем текущую скорость (умножаем на 10 для красивого отображения)
        speed_display = int(self.game_speed * 10)
        self.screen.blit(font.render(f"СКОР: {speed_display}", True, (255, 100, 0)), (10, 100))
        
        # Отображаем сложность (верхний регистр)
        diff_display = self.data_manager.settings["difficulty"].upper()
        self.screen.blit(font.render(f"{diff_display}", True, (200, 200, 200)), (10, 130))
        
        # ОТОБРАЖАЕМ АКТИВНЫЙ БОНУС (если есть)
        if self.player.active_powerup:
            if self.player.active_powerup == "nitro":
                text = f"НИТРО: {self.player.powerup_timer // 60 + 1}с"  # Оставшиеся секунды
                color = (255, 100, 0)
            elif self.player.active_powerup == "shield":
                text = "ЩИТ АКТИВЕН"
                color = (0, 200, 255)
            
            # Полупрозрачный фон для бонуса
            s2 = pygame.Surface((250, 40))
            s2.set_alpha(180)
            s2.fill((0, 0, 0))
            self.screen.blit(s2, (self.screen.get_width() // 2 - 125, 5))
            
            # Отображаем текст бонуса по центру сверху
            surf = font.render(text, True, color)
            self.screen.blit(surf, (self.screen.get_width() // 2 - surf.get_width() // 2, 15))
    
    def draw_objects(self):
        """Рисует все игровые объекты на экране"""
        for o in self.obstacles: o.draw(self.screen)      # Препятствия
        for c in self.traffic_cars: c.draw(self.screen)   # Вражеские машины
        for p in self.powerups: p.draw(self.screen)       # Бонусы
        for c in self.coins_list: c.draw(self.screen)     # Монеты
        self.player.draw(self.screen)                      # Машина игрока (поверх всего)
    
    # ОБРАБОТКА ВВОДА
    def handle_input(self):
        """Обрабатывает нажатия клавиш для перемещения машины"""
        keys = pygame.key.get_pressed()  # Получаем состояние всех клавиш
        
        # ЗАДЕРЖКА МЕЖДУ ПЕРЕМЕЩЕНИЯМИ (чтобы не перемещалась слишком быстро)
        if not hasattr(self, 'last_move'):
            self.last_move = 0  # Время последнего перемещения
        
        current_time = pygame.time.get_ticks()  # Текущее время в миллисекундах
        
        # ДВИЖЕНИЕ ВЛЕВО (стрелка или клавиша A)
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and current_time - self.last_move > 150:
            self.player.move_left()   # Смещаем игрока влево на одну полосу
            self.last_move = current_time  # Запоминаем время перемещения
        # ДВИЖЕНИЕ ВПРАВО (стрелка или клавиша D)
        elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and current_time - self.last_move > 150:
            self.player.move_right()
            self.last_move = current_time
    
    # ОБНОВЛЕНИЕ ПОЗИЦИЙ ОБЪЕКТОВ
    def update_objects(self):
        """Обновляет позиции всех объектов на основе текущей скорости"""
        
        self.player.update()  # Обновляем состояние игрока (бонусы, скорость)
        
        # ОБНОВЛЕНИЕ ПРЕПЯТСТВИЙ
        for o in self.obstacles[:]:
            o.update(self.game_speed)  # Двигаем вниз со скоростью игры
            if o.y > 700:  # Если ушёл за нижнюю границу экрана
                self.obstacles.remove(o)  # Удаляем из списка
        
        # ОБНОВЛЕНИЕ ВРАЖЕСКИХ МАШИН
        for c in self.traffic_cars[:]:
            c.update(self.game_speed)
            if c.y > 700:
                self.traffic_cars.remove(c)
        
        # ОБНОВЛЕНИЕ БОНУСОВ (update возвращает False если время жизни истекло)
        for p in self.powerups[:]:
            if not p.update(self.game_speed):
                self.powerups.remove(p)  # Удаляем просроченный бонус
        
        # ОБНОВЛЕНИЕ МОНЕТ
        for c in self.coins_list[:]:
            c.update(self.game_speed)
            if c.y > 700:
                self.coins_list.remove(c)
    
    # ОСНОВНОЙ ИГРОВОЙ ЦИКЛ
    def run_game(self):
        """Запускает игровой процесс, возвращает результат (menu/quit)"""
        
        self.reset_game()  # Сбрасываем все параметры перед игрой
        
        # ЗАПРОС ИМЕНИ ИГРОКА
        self.player_name = self.ui_manager.get_username()
        if not self.player_name:  # Если игрок отменил ввод
            return "menu"  # Возвращаемся в меню
        
        # БЕСКОНЕЧНЫЙ ИГРОВОЙ ЦИКЛ
        while True:
            # ОБРАБОТКА СОБЫТИЙ
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # Нажали крестик окна
                    return "quit"
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return "menu"  # Esc - возврат в меню
            
            # ОБНОВЛЕНИЕ СОСТОЯНИЯ ИГРЫ
            self.handle_input()      # Обработка клавиш
            self.update_objects()    # Движение объектов
            
            # УПРАВЛЕНИЕ ПОЯВЛЕНИЕМ ОБЪЕКТОВ
            diff = self.data_manager.settings["difficulty"]
            delay = self.difficulty_settings[diff]["spawn_delay"]  # Задержка для текущей сложности
            
            self.spawn_timer += 1
            if self.spawn_timer > delay:
                self.spawn_timer = 0
                r = random.random()  # Случайное число от 0 до 1
                # Вероятности появления объектов (40%, 10%, 10%)
                if r < 0.4:        # 40% - вражеская машина
                    self.spawn_traffic()
                elif r < 0.5:      # 10% - препятствие
                    self.spawn_obstacle()
                elif r < 0.6:      # 10% - бонус
                    self.spawn_powerup()
                # Остальные 40% - ничего не появляется
            
            # МОНЕТЫ ПОЯВЛЯЮТСЯ В РАЗНОЕ ВРЕМЯ НА РАЗНЫХ ПОЛОСАХ
            for i in range(3):  # 3 полосы
                self.coin_timers[i] += 1
                if self.coin_timers[i] > self.coin_delays[i]:
                    self.coin_timers[i] = 0
                    # Новая случайная задержка для этой полосы
                    self.coin_delays[i] = random.randint(40, 100)
                    self.spawn_coin_on_lane(i)  # Создаём монету на этой полосе
            
            # ОБНОВЛЕНИЕ ОЧКОВ И СЛОЖНОСТИ
            self.update_score()
            
            # ОБРАБОТКА ЭФФЕКТА НИТРО (возврат к базовой скорости по окончании)
            if self.player.active_powerup == "nitro":
                if self.player.powerup_timer <= 0:  # Время действия нитро закончилось
                    # Возвращаем базовую скорость
                    self.game_speed = self.clamp_speed(self.player.base_speed)
                    self.player.speed = self.game_speed
                    self.player.active_powerup = None
                else:
                    # Обновляем скорость игрока от текущей game_speed
                    self.player.speed = self.game_speed
            
            # ПРОВЕРКА СТОЛКНОВЕНИЙ
            if not self.check_collisions():
                # Игра окончена - показываем экран Game Over и сохраняем рекорд
                return self.ui_manager.show_game_over(self.score, self.distance, 
                                                      self.coins, self.player_name)
            
            # ОТРИСОВКА ВСЕГО НА ЭКРАНЕ
            self.draw_road()      # Фон дороги
            self.draw_objects()   # Все объекты
            self.draw_hud()       # Интерфейс
            
            pygame.display.flip()  # Обновляем экран
            self.clock.tick(60)    # Ограничиваем до 60 кадров в секунду
    
    # ГЛАВНЫЙ МЕТОД УПРАВЛЕНИЯ ПРИЛОЖЕНИЕМ
    def main(self):
        """Главный цикл приложения - переключение между меню и игрой"""
        while self.running:
            # ПОКАЗЫВАЕМ ГЛАВНОЕ МЕНЮ
            result = self.ui_manager.show_main_menu()
            
            if result == "play":  # Нажата кнопка "Играть"
                result = self.run_game()  # Запускаем игру
                if result == "quit":      # Если вышли через крестик
                    self.running = False
            elif result == "leaderboard":  # Таблица рекордов
                self.ui_manager.show_leaderboard()
            elif result == "settings":     # Настройки
                self.ui_manager.show_settings()
            elif result == "quit":         # Выход из игры
                self.running = False
        
        # ЗАВЕРШЕНИЕ РАБОТЫ
        pygame.quit()   # Останавливаем Pygame
        sys.exit()      # Завершаем программу

# ТОЧКА ВХОДА В ПРОГРАММУ
if __name__ == "__main__":
    game = Game()  # Создаём объект игры
    game.main()    # Запускаем главный цикл