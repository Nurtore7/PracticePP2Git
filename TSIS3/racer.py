import pygame
import random

class PlayerCar:
    def __init__(self, x, y, image_path, color_tint=None):
        self.image_original = pygame.image.load(image_path).convert_alpha()
        self.image_original = pygame.transform.scale(self.image_original, (50, 80))
        
        if color_tint:
            self.image_original = self.apply_color_tint(self.image_original, color_tint)
        
        self.image = self.image_original
        self.x = x
        self.y = y
        self.width = 50
        self.height = 80
        self.speed = 5
        self.base_speed = 5
        self.lane = 1
        self.lane_positions = [140, 300, 460]
        self.active_powerup = None
        self.powerup_timer = 0
        self.shield_active = False
        
        self.x = self.lane_positions[self.lane] - (self.width // 2)
        self.tilt_angle = 0
        self.tilt_timer = 0
    
    def apply_color_tint(self, image, color):
        tinted = image.copy()
        for x in range(tinted.get_width()):
            for y in range(tinted.get_height()):
                r, g, b, a = tinted.get_at((x, y))
                if a > 0:
                    new_r = int(r * color[0] / 255)
                    new_g = int(g * color[1] / 255)
                    new_b = int(b * color[2] / 255)
                    tinted.set_at((x, y), (new_r, new_g, new_b, a))
        return tinted
    
    def move_left(self):
        if self.lane > 0:
            self.lane -= 1
            self.x = self.lane_positions[self.lane] - (self.width // 2)
            self.tilt_angle = -20
            self.tilt_timer = 10
    
    def move_right(self):
        if self.lane < 2:
            self.lane += 1
            self.x = self.lane_positions[self.lane] - (self.width // 2)
            self.tilt_angle = 20
            self.tilt_timer = 10
    
    def activate_powerup(self, powerup_type):
        self.active_powerup = powerup_type
        if powerup_type == "nitro":
            self.powerup_timer = 300
        elif powerup_type == "shield":
            self.powerup_timer = -1
            self.shield_active = True
    
    def update(self):
        if self.active_powerup == "nitro":
            self.powerup_timer -= 1
        
        if self.tilt_timer > 0:
            self.tilt_timer -= 1
            if self.tilt_timer == 0:
                self.tilt_angle = 0
    
    def draw(self, screen):
        if self.shield_active:
            shield_radius = 45
            shield_surface = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (0, 255, 255, 128), 
                             (shield_radius, shield_radius), shield_radius)
            screen.blit(shield_surface, (self.x - 20, self.y - 10))
        
        if self.tilt_angle != 0:
            rotated_image = pygame.transform.rotate(self.image, self.tilt_angle)
            new_rect = rotated_image.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
            screen.blit(rotated_image, new_rect)
        else:
            screen.blit(self.image, (self.x, self.y))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class EnemyCar:
    def __init__(self, x, y, image_path):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 80))
        self.x = x
        self.y = y
        self.width = 50
        self.height = 80
        
    def update(self, speed):
        self.y += speed
    
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Obstacle:
    def __init__(self, x, y, obstacle_type, image=None):
        self.x = x
        self.y = y
        self.type = obstacle_type
        self.image = image
        
        if image:
            self.width = image.get_width()
            self.height = image.get_height()
        else:
            self.width = 105
            self.height = 105
        
    def update(self, speed):
        self.y += speed
    
    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class PowerUp:
    def __init__(self, x, y, power_type, image=None):
        self.x = x
        self.y = y
        self.type = power_type
        self.image = image
        self.lifetime = 300
        
        if image:
            self.width = image.get_width()
            self.height = image.get_height()
        else:
            self.width = 75
            self.height = 75
        
    def update(self, speed):
        self.y += speed
        self.lifetime -= 1
        return self.lifetime > 0
    
    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            if self.type == "shield":
                pygame.draw.rect(screen, (0, 200, 255), 
                               (self.x, self.y, self.width, self.height))
                pygame.draw.circle(screen, (0, 100, 255), 
                                 (self.x + 37, self.y + 37), 25)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.animation_frame = 0
        
    def update(self, speed):
        self.y += speed
        self.animation_frame += 1
    
    def draw(self, screen):
        size = 15 + abs(self.animation_frame % 20 - 10) // 5
        pygame.draw.circle(screen, (255, 215, 0), 
                         (self.x + 10, self.y + 10), size)
        pygame.draw.circle(screen, (255, 255, 0), 
                         (self.x + 10, self.y + 10), size // 2)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)