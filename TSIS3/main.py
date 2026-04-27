import pygame
import sys
import random
import os
from persistence import DataManager
from racer import PlayerCar, Obstacle, EnemyCar, PowerUp, Coin
from ui import UIManager

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Получаем путь к папке скрипта
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(self.script_dir)
        
        self.screen = pygame.display.set_mode((600, 700))
        pygame.display.set_caption("Racing Game")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Пути к ассетам
        self.assets_dir = os.path.join(self.script_dir, "assets")
        
        # Загрузка изображений
        try:
            self.player_img = os.path.join(self.assets_dir, "Player.png")
            self.enemy_img = os.path.join(self.assets_dir, "Enemy.png")
            self.barrier_img = os.path.join(self.assets_dir, "Barrier.png")
            self.nitro_img = os.path.join(self.assets_dir, "Nitro.png")
            self.oil_img = os.path.join(self.assets_dir, "Oil.png")
            self.road_img = pygame.image.load(os.path.join(self.assets_dir, "AnimatedStreet.png")).convert()
            self.road_img = pygame.transform.scale(self.road_img, (600, 700))
            
            # Размеры изображений
            self.barrier_surf = pygame.image.load(self.barrier_img).convert_alpha()
            self.barrier_surf = pygame.transform.scale(self.barrier_surf, (105, 105))
            
            self.nitro_surf = pygame.image.load(self.nitro_img).convert_alpha()
            self.nitro_surf = pygame.transform.scale(self.nitro_surf, (155, 155))
            
            self.oil_surf = pygame.image.load(self.oil_img).convert_alpha()
            self.oil_surf = pygame.transform.scale(self.oil_surf, (115, 115))
            
        except Exception as e:
            print(f"Ошибка загрузки изображений: {e}")
            print("Проверьте папку assets/")
            sys.exit()
        
        # Загрузка звука
        try:
            sound_path = os.path.join(self.script_dir, "crash.wav")
            self.crash_sound = pygame.mixer.Sound(sound_path)
        except:
            self.crash_sound = None
        
        self.data_manager = DataManager()
        self.ui_manager = UIManager(self.screen, self.data_manager)
        
        self.player_name = ""
        self.score = 0
        self.distance = 0
        self.coins = 0
        self.game_speed = 5
        self.road_y = 0
        
        self.obstacles = []
        self.traffic_cars = []
        self.powerups = []
        self.coins_list = []
        
        self.spawn_timer = 0
        self.difficulty_timer = 0
        
        # Таймеры для монет на каждой полосе
        self.coin_timers = [0, 0, 0]  # [левая, центр, правая]
        self.coin_delays = [random.randint(40, 100), random.randint(40, 100), random.randint(40, 100)]
        
        # НАСТРОЙКИ СЛОЖНОСТИ
        self.difficulty_settings = {
            "easy": {"spawn_delay": 70, "start_speed": 5, "max_speed": 10, "min_speed": 5},
            "normal": {"spawn_delay": 50, "start_speed": 8, "max_speed": 12, "min_speed": 8},
            "hard": {"spawn_delay": 35, "start_speed": 12, "max_speed": 16, "min_speed": 12}
        }
    
    def play_sound(self, sound):
        if self.data_manager.settings["sound"] and sound:
            sound.play()
    
    def clamp_speed(self, speed):
        """Ограничивает скорость в пределах min и max для текущей сложности"""
        difficulty = self.data_manager.settings["difficulty"]
        min_speed = self.difficulty_settings[difficulty]["min_speed"]
        max_speed = self.difficulty_settings[difficulty]["max_speed"]
        return max(min_speed, min(speed, max_speed))
    
    def reset_game(self):
        self.score = 0
        self.distance = 0
        self.coins = 0
        self.road_y = 0
        
        self.obstacles.clear()
        self.traffic_cars.clear()
        self.powerups.clear()
        self.coins_list.clear()
        
        # Устанавливаем скорость в зависимости от сложности
        difficulty = self.data_manager.settings["difficulty"]
        self.game_speed = self.difficulty_settings[difficulty]["start_speed"]
        
        car_color = self.data_manager.settings["car_color"]
        # Машина игрока 50x80, центрируем на средней полосе (300)
        self.player = PlayerCar(300 - 25, 550, self.player_img, car_color)
        self.player.base_speed = self.game_speed
        self.player.speed = self.game_speed
        # Обновляем позиции полос для игрока
        self.player.lane_positions = [140, 300, 460]
        
        self.spawn_timer = 0
        self.difficulty_timer = 0
        
        # Сбрасываем таймеры монет
        self.coin_timers = [0, 0, 0]
        self.coin_delays = [random.randint(40, 100), random.randint(40, 100), random.randint(40, 100)]
    
    def get_centered_x(self, lane_center, object_width):
        """Возвращает X координату для центрирования объекта на полосе"""
        return lane_center - (object_width // 2)
    
    def spawn_traffic(self):
        lanes = [140, 300, 460]
        lane = random.choice(lanes)
        obj_width = 50
        x = self.get_centered_x(lane, obj_width)
        self.traffic_cars.append(EnemyCar(x, -80, self.enemy_img))
    
    def spawn_obstacle(self):
        lanes = [140, 300, 460]
        lane = random.choice(lanes)
        obstacle_type = random.choice(["barrier", "oil"])
        if obstacle_type == "barrier":
            obj_width = 105
            x = self.get_centered_x(lane, obj_width)
            self.obstacles.append(Obstacle(x, -105, obstacle_type, self.barrier_surf))
        else:
            obj_width = 115
            x = self.get_centered_x(lane, obj_width)
            self.obstacles.append(Obstacle(x, -115, obstacle_type, self.oil_surf))
    
    def spawn_powerup(self):
        lanes = [140, 300, 460]
        lane = random.choice(lanes)
        power_type = random.choice(["nitro", "shield"])
        if power_type == "nitro":
            obj_width = 155
            x = self.get_centered_x(lane, obj_width)
            self.powerups.append(PowerUp(x, -155, power_type, self.nitro_surf))
        else:
            obj_width = 75
            x = self.get_centered_x(lane, obj_width)
            self.powerups.append(PowerUp(x, -95, power_type))
    
    def spawn_coin_on_lane(self, lane_index):
        """Создает монету на конкретной полосе"""
        lanes = [140, 300, 460]
        lane_center = lanes[lane_index]
        obj_width = 20
        x = self.get_centered_x(lane_center, obj_width)
        self.coins_list.append(Coin(x, -50))
    
    def update_score(self):
        self.score += 1
        self.distance += 1
        
        # Увеличение сложности со временем
        self.difficulty_timer += 1
        if self.difficulty_timer > 500:  # Каждые ~8 секунд
            self.difficulty_timer = 0
            difficulty = self.data_manager.settings["difficulty"]
            max_speed = self.difficulty_settings[difficulty]["max_speed"]
            # Увеличиваем скорость только если не превышаем максимум
            if self.game_speed < max_speed:
                new_speed = min(self.game_speed + 0.5, max_speed)
                self.game_speed = self.clamp_speed(new_speed)
                # Обновляем скорость игрока если нет активного нитро
                if self.player.active_powerup != "nitro":
                    self.player.base_speed = self.game_speed
                    self.player.speed = self.game_speed
    
    def check_collisions(self):
        player_rect = self.player.get_rect()
        
        # Проверка столкновений с трафиком
        for car in self.traffic_cars[:]:
            if player_rect.colliderect(car.get_rect()):
                if self.player.shield_active:
                    self.player.shield_active = False
                    self.player.active_powerup = None
                    self.traffic_cars.remove(car)
                    self.play_sound(self.crash_sound)
                else:
                    self.play_sound(self.crash_sound)
                    return False
        
        # Проверка столкновений с препятствиями
        for obs in self.obstacles[:]:
            if player_rect.colliderect(obs.get_rect()):
                if self.player.shield_active:
                    self.player.shield_active = False
                    self.player.active_powerup = None
                    self.obstacles.remove(obs)
                    self.play_sound(self.crash_sound)
                else:
                    self.play_sound(self.crash_sound)
                    # Масло только замедляет, НЕ заканчивает игру
                    if obs.type == "oil":
                        new_speed = self.game_speed - 3
                        self.game_speed = self.clamp_speed(new_speed)
                        # Обновляем скорость игрока
                        if self.player.active_powerup != "nitro":
                            self.player.base_speed = self.game_speed
                            self.player.speed = self.game_speed
                        self.obstacles.remove(obs)
                    else:
                        # Барьер - смерть
                        return False
        
        # Проверка сбора бонусов
        for power in self.powerups[:]:
            if player_rect.colliderect(power.get_rect()):
                self.player.activate_powerup(power.type)
                # Если это нитро, увеличиваем скорость
                if power.type == "nitro":
                    new_speed = self.game_speed + 3
                    self.game_speed = self.clamp_speed(new_speed)
                    self.player.base_speed = self.game_speed
                    self.player.speed = self.game_speed
                self.powerups.remove(power)
        
        # Проверка сбора монет
        for coin in self.coins_list[:]:
            if player_rect.colliderect(coin.get_rect()):
                self.coins += 1
                self.score += 10
                self.coins_list.remove(coin)
        
        return True
    
    def draw_road(self):
        self.road_y = (self.road_y + self.game_speed) % self.road_img.get_height()
        self.screen.blit(self.road_img, (0, self.road_y - self.road_img.get_height()))
        self.screen.blit(self.road_img, (0, self.road_y))
    
    def draw_hud(self):
        font = pygame.font.Font(None, 30)
        
        s = pygame.Surface((200, 150))
        s.set_alpha(180)
        s.fill((0, 0, 0))
        self.screen.blit(s, (0, 0))
        
        self.screen.blit(font.render(f"ОЧКИ: {self.score}", True, (255, 255, 255)), (10, 10))
        self.screen.blit(font.render(f"ДИСТ: {self.distance}", True, (100, 200, 255)), (10, 40))
        self.screen.blit(font.render(f"МОНЕТЫ: {self.coins}", True, (255, 215, 0)), (10, 70))
        
        # Отображаем текущую скорость
        speed_display = int(self.game_speed * 10)
        self.screen.blit(font.render(f"СКОР: {speed_display}", True, (255, 100, 0)), (10, 100))
        
        # Отображаем сложность
        diff_display = self.data_manager.settings["difficulty"].upper()
        self.screen.blit(font.render(f"{diff_display}", True, (200, 200, 200)), (10, 130))
        
        if self.player.active_powerup:
            if self.player.active_powerup == "nitro":
                text = f"НИТРО: {self.player.powerup_timer // 60 + 1}с"
                color = (255, 100, 0)
            elif self.player.active_powerup == "shield":
                text = "ЩИТ АКТИВЕН"
                color = (0, 200, 255)
            
            s2 = pygame.Surface((250, 40))
            s2.set_alpha(180)
            s2.fill((0, 0, 0))
            self.screen.blit(s2, (self.screen.get_width() // 2 - 125, 5))
            
            surf = font.render(text, True, color)
            self.screen.blit(surf, (self.screen.get_width() // 2 - surf.get_width() // 2, 15))
    
    def draw_objects(self):
        for o in self.obstacles: o.draw(self.screen)
        for c in self.traffic_cars: c.draw(self.screen)
        for p in self.powerups: p.draw(self.screen)
        for c in self.coins_list: c.draw(self.screen)
        self.player.draw(self.screen)
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if not hasattr(self, 'last_move'):
            self.last_move = 0
        
        current_time = pygame.time.get_ticks()
        
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and current_time - self.last_move > 150:
            self.player.move_left()
            self.last_move = current_time
        elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and current_time - self.last_move > 150:
            self.player.move_right()
            self.last_move = current_time
    
    def update_objects(self):
        self.player.update()
        
        for o in self.obstacles[:]:
            o.update(self.game_speed)
            if o.y > 700: self.obstacles.remove(o)
        
        for c in self.traffic_cars[:]:
            c.update(self.game_speed)
            if c.y > 700: self.traffic_cars.remove(c)
        
        for p in self.powerups[:]:
            if not p.update(self.game_speed):
                self.powerups.remove(p)
        
        for c in self.coins_list[:]:
            c.update(self.game_speed)
            if c.y > 700: self.coins_list.remove(c)
    
    def run_game(self):
        self.reset_game()
        
        self.player_name = self.ui_manager.get_username()
        if not self.player_name:
            return "menu"
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return "menu"
            
            self.handle_input()
            self.update_objects()
            
            diff = self.data_manager.settings["difficulty"]
            delay = self.difficulty_settings[diff]["spawn_delay"]
            
            self.spawn_timer += 1
            if self.spawn_timer > delay:
                self.spawn_timer = 0
                r = random.random()
                if r < 0.4:
                    self.spawn_traffic()
                elif r < 0.5:
                    self.spawn_obstacle()
                elif r < 0.6:
                    self.spawn_powerup()
            
            # МОНЕТЫ ПОЯВЛЯЮТСЯ В РАЗНОЕ ВРЕМЯ НА РАЗНЫХ ПОЛОСАХ
            for i in range(3):
                self.coin_timers[i] += 1
                if self.coin_timers[i] > self.coin_delays[i]:
                    self.coin_timers[i] = 0
                    self.coin_delays[i] = random.randint(40, 100)  # Разная задержка для каждой полосы
                    self.spawn_coin_on_lane(i)
            
            self.update_score()
            
            # Обновляем скорость игрока от нитро (возврат к базовой)
            if self.player.active_powerup == "nitro":
                if self.player.powerup_timer <= 0:
                    # Возвращаем базовую скорость
                    self.game_speed = self.clamp_speed(self.player.base_speed)
                    self.player.speed = self.game_speed
                    self.player.active_powerup = None
                else:
                    # Обновляем скорость игрока от текущей game_speed
                    self.player.speed = self.game_speed
            
            if not self.check_collisions():
                return self.ui_manager.show_game_over(self.score, self.distance, 
                                                      self.coins, self.player_name)
            
            self.draw_road()
            self.draw_objects()
            self.draw_hud()
            
            pygame.display.flip()
            self.clock.tick(60)
    
    def main(self):
        while self.running:
            result = self.ui_manager.show_main_menu()
            
            if result == "play":
                result = self.run_game()
                if result == "quit":
                    self.running = False
            elif result == "leaderboard":
                self.ui_manager.show_leaderboard()
            elif result == "settings":
                self.ui_manager.show_settings()
            elif result == "quit":
                self.running = False
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.main()