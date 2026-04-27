import pygame

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, screen, font):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=10)
        
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class InputBox:
    def __init__(self, x, y, width, height, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.text = ""
        self.active = False
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return self.text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(self.text) < 15:
                    self.text += event.unicode
        return None
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 2)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))

class UIManager:
    def __init__(self, screen, data_manager):
        self.screen = screen
        self.data_manager = data_manager
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        self.font_tiny = pygame.font.Font(None, 24)
        
    def draw_text(self, text, font, color, x, y, center=False):
        surface = font.render(text, True, color)
        rect = surface.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(surface, rect)
    
    def show_main_menu(self):
        self.screen.fill((30, 30, 40))
        
        self.draw_text("RACING GAME", self.font_large, (255, 215, 0),
                      self.screen.get_width() // 2, 100, center=True)
        
        button_width = 250
        button_height = 60
        button_x = self.screen.get_width() // 2 - button_width // 2
        
        play_btn = Button(button_x, 250, button_width, button_height, 
                         "ИГРАТЬ", (0, 100, 0), (0, 150, 0))
        leaderboard_btn = Button(button_x, 330, button_width, button_height,
                                "РЕКОРДЫ", (0, 0, 100), (0, 0, 150))
        settings_btn = Button(button_x, 410, button_width, button_height,
                             "НАСТРОЙКИ", (100, 100, 0), (150, 150, 0))
        quit_btn = Button(button_x, 490, button_width, button_height,
                         "ВЫХОД", (100, 0, 0), (150, 0, 0))
        
        buttons = [play_btn, leaderboard_btn, settings_btn, quit_btn]
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                
                if play_btn.handle_event(event):
                    return "play"
                elif leaderboard_btn.handle_event(event):
                    return "leaderboard"
                elif settings_btn.handle_event(event):
                    return "settings"
                elif quit_btn.handle_event(event):
                    return "quit"
            
            for btn in buttons:
                btn.draw(self.screen, self.font_medium)
            
            pygame.display.flip()
    
    def show_leaderboard(self):
        self.screen.fill((30, 30, 40))
        
        self.draw_text("ТОП 10 РЕКОРДОВ", self.font_large, (255, 215, 0),
                      self.screen.get_width() // 2, 50, center=True)
        
        scores = self.data_manager.get_top_scores()
        
        y = 150
        headers = ["#", "ИМЯ", "ОЧКИ", "ДИСТ", "МОНЕТЫ"]
        x_pos = [50, 120, 350, 480, 580]
        
        for i, header in enumerate(headers):
            self.draw_text(header, self.font_small, (200, 200, 200), x_pos[i], y)
        
        y += 50
        for i, score in enumerate(scores[:10]):
            self.draw_text(str(i + 1), self.font_small, (255, 255, 255), x_pos[0], y)
            self.draw_text(score["name"][:12], self.font_small, (255, 255, 255), x_pos[1], y)
            self.draw_text(str(score["score"]), self.font_small, (255, 255, 255), x_pos[2], y)
            self.draw_text(str(score["distance"]), self.font_small, (255, 255, 255), x_pos[3], y)
            self.draw_text(str(score["coins"]), self.font_small, (255, 255, 255), x_pos[4], y)
            y += 40
        
        back_btn = Button(self.screen.get_width() // 2 - 100, 600, 200, 50,
                         "НАЗАД", (100, 100, 100), (150, 150, 150))
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                
                if back_btn.handle_event(event):
                    return "menu"
            
            back_btn.draw(self.screen, self.font_small)
            pygame.display.flip()
    
    def show_settings(self):
        self.screen.fill((30, 30, 40))
        
        self.draw_text("НАСТРОЙКИ", self.font_large, (255, 215, 0),
                      self.screen.get_width() // 2, 50, center=True)
        
        sound_text = "ЗВУК: ВКЛ" if self.data_manager.settings["sound"] else "ЗВУК: ВЫКЛ"
        sound_btn = Button(200, 150, 200, 50, sound_text, (70, 70, 70), (100, 100, 100))
        
        difficulty_text = f"СЛОЖНОСТЬ: {self.data_manager.settings['difficulty'].upper()}"
        difficulty_btn = Button(200, 230, 200, 50, difficulty_text, (70, 70, 70), (100, 100, 100))
        
        save_btn = Button(200, 400, 200, 50, "СОХРАНИТЬ", (0, 100, 0), (0, 150, 0))
        back_btn = Button(200, 480, 200, 50, "НАЗАД", (100, 100, 100), (150, 150, 150))
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                
                if sound_btn.handle_event(event):
                    self.data_manager.settings["sound"] = not self.data_manager.settings["sound"]
                    sound_btn.text = "ЗВУК: ВКЛ" if self.data_manager.settings["sound"] else "ЗВУК: ВЫКЛ"
                
                if difficulty_btn.handle_event(event):
                    diffs = ["easy", "normal", "hard"]
                    curr = diffs.index(self.data_manager.settings["difficulty"])
                    self.data_manager.settings["difficulty"] = diffs[(curr + 1) % 3]
                    difficulty_btn.text = f"СЛОЖНОСТЬ: {self.data_manager.settings['difficulty'].upper()}"
                
                if save_btn.handle_event(event):
                    self.data_manager.save_settings()
                
                if back_btn.handle_event(event):
                    return "menu"
            
            sound_btn.draw(self.screen, self.font_small)
            difficulty_btn.draw(self.screen, self.font_small)
            save_btn.draw(self.screen, self.font_small)
            back_btn.draw(self.screen, self.font_small)
            
            pygame.display.flip()
    
    def get_username(self):
        self.screen.fill((30, 30, 40))
        
        self.draw_text("ВВЕДИТЕ ВАШЕ ИМЯ", self.font_large, (255, 215, 0),
                      self.screen.get_width() // 2, 150, center=True)
        
        input_box = InputBox(200, 300, 200, 50, self.font_medium)
        confirm_btn = Button(200, 400, 200, 50, "ПОДТВЕРДИТЬ", (0, 100, 0), (0, 150, 0))
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                
                result = input_box.handle_event(event)
                if result and len(result.strip()) > 0:
                    return result.strip()
                
                if confirm_btn.handle_event(event):
                    if len(input_box.text.strip()) > 0:
                        return input_box.text.strip()
            
            self.screen.fill((30, 30, 40))
            self.draw_text("ВВЕДИТЕ ВАШЕ ИМЯ", self.font_large, (255, 215, 0),
                          self.screen.get_width() // 2, 150, center=True)
            input_box.draw(self.screen)
            confirm_btn.draw(self.screen, self.font_small)
            
            pygame.display.flip()
    
    def show_game_over(self, score, distance, coins, player_name):
        self.screen.fill((30, 30, 40))
        
        self.draw_text("ИГРА ОКОНЧЕНА", self.font_large, (255, 0, 0),
                      self.screen.get_width() // 2, 80, center=True)
        
        self.draw_text(f"ИГРОК: {player_name}", self.font_medium, (255, 255, 255),
                      self.screen.get_width() // 2, 180, center=True)
        self.draw_text(f"ОЧКИ: {score}", self.font_medium, (255, 215, 0),
                      self.screen.get_width() // 2, 250, center=True)
        self.draw_text(f"ДИСТАНЦИЯ: {distance}", self.font_medium, (100, 200, 255),
                      self.screen.get_width() // 2, 320, center=True)
        self.draw_text(f"МОНЕТЫ: {coins}", self.font_medium, (255, 255, 0),
                      self.screen.get_width() // 2, 390, center=True)
        
        self.data_manager.add_score(player_name, score, distance, coins)
        
        retry_btn = Button(100, 480, 200, 50, "СЫГРАТЬ СНОВА", (0, 100, 0), (0, 150, 0))
        menu_btn = Button(300, 480, 200, 50, "ГЛАВНОЕ МЕНЮ", (100, 100, 100), (150, 150, 150))
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                
                if retry_btn.handle_event(event):
                    return "retry"
                elif menu_btn.handle_event(event):
                    return "menu"
            
            retry_btn.draw(self.screen, self.font_small)
            menu_btn.draw(self.screen, self.font_small)
            
            pygame.display.flip()