import pygame
import sys
from db import Database
from config import Config
from game import SnakeGame

class GameApp:
    def __init__(self):
        pygame.init()
        
        # Фиксированный размер 800x600
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        
        self.config = Config()
        self.db = Database()
        
        self.username = ""
        self.player_id = None
        self.game = None
        self.running = True
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (50, 50, 200)
        self.GREEN = (0, 200, 0)
        self.RED = (200, 0, 0)
        self.GRAY = (100, 100, 100)
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.button_font = pygame.font.Font(None, 48)
        self.text_font = pygame.font.Font(None, 32)
        
        self.clicked = False
        
    def draw_button(self, text, x, y, width, height, color, hover_color=None):
        mouse = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        
        rect = pygame.Rect(x, y, width, height)
        hover = rect.collidepoint(mouse)
        
        if hover and hover_color:
            pygame.draw.rect(self.screen, hover_color, rect)
        else:
            pygame.draw.rect(self.screen, color, rect)
        
        pygame.draw.rect(self.screen, self.WHITE, rect, 3)
        
        text_surface = self.button_font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
        
        if hover and mouse_click[0] and not self.clicked:
            self.clicked = True
            return True
        
        if not mouse_click[0]:
            self.clicked = False
            
        return False
    
    def draw_text_input(self, text, x, y, width, height, active):
        rect = pygame.Rect(x, y, width, height)
        color = self.GREEN if active else self.GRAY
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, self.WHITE, rect, 2)
        
        display_text = text if text else "Enter name"
        text_surface = self.text_font.render(display_text, True, self.WHITE)
        self.screen.blit(text_surface, (x + 10, y + 5))
        
        if active:
            current_time = pygame.time.get_ticks()
            if current_time % 1000 < 500:
                cursor_x = x + 10 + text_surface.get_width()
                pygame.draw.line(self.screen, self.WHITE, 
                               (cursor_x, y + 5), (cursor_x, y + height - 5), 2)
        
        return rect
    
    def main_menu(self):
        username_input_active = True
        input_rect = None
        
        while self.running:
            self.screen.fill(self.BLACK)
            
            # Title
            title = self.title_font.render("SNAKE GAME", True, self.GREEN)
            title_rect = title.get_rect(center=(400, 100))
            self.screen.blit(title, title_rect)
            
            # Username input
            input_label = self.text_font.render("YOUR NAME:", True, self.WHITE)
            input_label_rect = input_label.get_rect(center=(400, 200))
            self.screen.blit(input_label, input_label_rect)
            
            input_rect = self.draw_text_input(self.username, 300, 240, 200, 40, username_input_active)
            
            # Buttons
            if self.draw_button("PLAY", 300, 320, 200, 50, self.BLUE, self.GREEN):
                if self.username.strip():
                    self.player_id = self.db.get_or_create_player(self.username)
                    self.game_loop()
            
            if self.draw_button("SCORES", 300, 390, 200, 50, self.BLUE, self.GREEN):
                self.leaderboard_screen()
            
            if self.draw_button("OPTIONS", 300, 460, 200, 50, self.BLUE, self.GREEN):
                self.settings_screen()
            
            if self.draw_button("QUIT", 300, 530, 200, 50, self.RED, (150, 0, 0)):
                self.running = False
                break
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_rect and input_rect.collidepoint(event.pos):
                        username_input_active = True
                    else:
                        username_input_active = False
                
                if event.type == pygame.KEYDOWN and username_input_active:
                    if event.key == pygame.K_RETURN:
                        if self.username.strip():
                            self.player_id = self.db.get_or_create_player(self.username)
                            self.game_loop()
                    elif event.key == pygame.K_BACKSPACE:
                        self.username = self.username[:-1]
                    else:
                        if len(self.username) < 20 and event.unicode.isprintable():
                            self.username += event.unicode
            
            pygame.display.flip()
            self.clock.tick(60)
    
    def game_loop(self):
        self.game = SnakeGame(self.screen, self.config, self.db, self.player_id, self.username)
        last_time = pygame.time.get_ticks()
        
        while self.running:
            current_time = pygame.time.get_ticks()
            delta = current_time - last_time
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.game.game_over:
                        return
                
                self.game.handle_event(event)
            
            if not self.game.game_over:
                if delta > 1000 // self.game.speed:
                    self.game.update()
                    last_time = current_time
            
            self.screen.fill(self.BLACK)
            self.game.draw()
            
            if self.game.game_over:
                # Затемнение
                overlay = pygame.Surface((800, 600))
                overlay.set_alpha(200)
                overlay.fill((0, 0, 0))
                self.screen.blit(overlay, (0, 0))
                
                # Game Over текст
                go_text = self.title_font.render("GAME OVER", True, self.RED)
                go_rect = go_text.get_rect(center=(400, 150))
                self.screen.blit(go_text, go_rect)
                
                reason_text = self.text_font.render(f"REASON: {self.game.game_over_reason}", True, self.WHITE)
                reason_rect = reason_text.get_rect(center=(400, 220))
                self.screen.blit(reason_text, reason_rect)
                
                score_text = self.text_font.render(f"SCORE: {self.game.score}", True, self.WHITE)
                score_rect = score_text.get_rect(center=(400, 280))
                self.screen.blit(score_text, score_rect)
                
                level_text = self.text_font.render(f"LEVEL: {self.game.level}", True, self.WHITE)
                level_rect = level_text.get_rect(center=(400, 310))
                self.screen.blit(level_text, level_rect)
                
                # Кнопки
                mouse = pygame.mouse.get_pos()
                click = pygame.mouse.get_pressed()
                
                # Retry button
                retry_rect = pygame.Rect(250, 380, 120, 50)
                if retry_rect.collidepoint(mouse):
                    pygame.draw.rect(self.screen, self.GREEN, retry_rect)
                    if click[0]:
                        pygame.time.wait(200)
                        self.game = SnakeGame(self.screen, self.config, self.db, self.player_id, self.username)
                        last_time = pygame.time.get_ticks()
                        continue
                else:
                    pygame.draw.rect(self.screen, (0, 150, 0), retry_rect)
                pygame.draw.rect(self.screen, self.WHITE, retry_rect, 2)
                retry_text = self.button_font.render("RETRY", True, self.WHITE)
                retry_text_rect = retry_text.get_rect(center=retry_rect.center)
                self.screen.blit(retry_text, retry_text_rect)
                
                # Menu button
                menu_rect = pygame.Rect(430, 380, 120, 50)
                if menu_rect.collidepoint(mouse):
                    pygame.draw.rect(self.screen, self.BLUE, menu_rect)
                    if click[0]:
                        pygame.time.wait(200)
                        return
                else:
                    pygame.draw.rect(self.screen, (0, 0, 150), menu_rect)
                pygame.draw.rect(self.screen, self.WHITE, menu_rect, 2)
                menu_text = self.button_font.render("MENU", True, self.WHITE)
                menu_text_rect = menu_text.get_rect(center=menu_rect.center)
                self.screen.blit(menu_text, menu_text_rect)
            
            pygame.display.flip()
            self.clock.tick(60)
    
    def leaderboard_screen(self):
        leaderboard = self.db.get_leaderboard()
        
        while self.running:
            self.screen.fill(self.BLACK)
            
            title = self.title_font.render("TOP SCORES", True, self.GREEN)
            title_rect = title.get_rect(center=(400, 60))
            self.screen.blit(title, title_rect)
            
            # Headers
            headers = ["#", "PLAYER", "SCORE", "LEVEL", "DATE"]
            for i, header in enumerate(headers):
                text = self.text_font.render(header, True, self.WHITE)
                self.screen.blit(text, (50 + i * 150, 130))
            
            # Display entries
            for idx, entry in enumerate(leaderboard[:10]):
                y_pos = 170 + idx * 35
                rank = idx + 1
                username, score, level, played_at = entry
                date_str = played_at.strftime("%m/%d")
                
                texts = [str(rank), username[:15], str(score), str(level), date_str]
                for i, text in enumerate(texts):
                    text_surface = self.text_font.render(text, True, self.WHITE)
                    self.screen.blit(text_surface, (50 + i * 150, y_pos))
            
            # Back button
            mouse = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            
            back_rect = pygame.Rect(350, 520, 100, 40)
            
            if back_rect.collidepoint(mouse):
                pygame.draw.rect(self.screen, self.GREEN, back_rect)
                if click[0]:
                    pygame.time.wait(200)
                    return
            else:
                pygame.draw.rect(self.screen, self.BLUE, back_rect)
            
            pygame.draw.rect(self.screen, self.WHITE, back_rect, 2)
            back_text = self.button_font.render("BACK", True, self.WHITE)
            back_text_rect = back_text.get_rect(center=back_rect.center)
            self.screen.blit(back_text, back_text_rect)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
            
            pygame.display.flip()
            self.clock.tick(60)
    
    def settings_screen(self):
        colors = [(0, 255, 0), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
        color_names = ["GREEN", "YELLOW", "PURPLE", "CYAN"]
        
        while self.running:
            self.screen.fill(self.BLACK)
            
            title = self.title_font.render("GAME OPTIONS", True, self.GREEN)
            title_rect = title.get_rect(center=(400, 80))
            self.screen.blit(title, title_rect)
            
            mouse = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            
            # Grid button
            grid_text = f"GRID: {'ON' if self.config.grid_overlay else 'OFF'}"
            grid_rect = pygame.Rect(300, 160, 200, 50)
            
            if grid_rect.collidepoint(mouse):
                pygame.draw.rect(self.screen, self.GREEN, grid_rect)
                if click[0]:
                    self.config.grid_overlay = not self.config.grid_overlay
                    pygame.time.wait(200)
            else:
                pygame.draw.rect(self.screen, self.BLUE, grid_rect)
            
            pygame.draw.rect(self.screen, self.WHITE, grid_rect, 2)
            grid_surf = self.button_font.render(grid_text, True, self.WHITE)
            grid_text_rect = grid_surf.get_rect(center=grid_rect.center)
            self.screen.blit(grid_surf, grid_text_rect)
            
            # Sound button
            sound_text = f"SOUND: {'ON' if self.config.sound_on else 'OFF'}"
            sound_rect = pygame.Rect(300, 230, 200, 50)
            
            if sound_rect.collidepoint(mouse):
                pygame.draw.rect(self.screen, self.GREEN, sound_rect)
                if click[0]:
                    self.config.sound_on = not self.config.sound_on
                    pygame.time.wait(200)
            else:
                pygame.draw.rect(self.screen, self.BLUE, sound_rect)
            
            pygame.draw.rect(self.screen, self.WHITE, sound_rect, 2)
            sound_surf = self.button_font.render(sound_text, True, self.WHITE)
            sound_text_rect = sound_surf.get_rect(center=sound_rect.center)
            self.screen.blit(sound_surf, sound_text_rect)
            
            # Color label
            color_label = self.text_font.render("SNAKE COLOR:", True, self.WHITE)
            color_label_rect = color_label.get_rect(center=(400, 320))
            self.screen.blit(color_label, color_label_rect)
            
            # Color buttons
            button_w = 85
            button_h = 40
            total_w = (button_w * len(colors)) + (15 * (len(colors) - 1))
            start_x = (800 - total_w) // 2
            
            for i, (color, name) in enumerate(zip(colors, color_names)):
                x = start_x + i * (button_w + 15)
                color_rect = pygame.Rect(x, 350, button_w, button_h)
                
                if color_rect.collidepoint(mouse):
                    pygame.draw.rect(self.screen, self.WHITE, color_rect)
                    if click[0]:
                        self.config.snake_color = color
                        pygame.time.wait(200)
                else:
                    pygame.draw.rect(self.screen, color, color_rect)
                
                pygame.draw.rect(self.screen, self.WHITE, color_rect, 2)
                color_surf = self.text_font.render(name, True, self.WHITE)
                color_text_rect = color_surf.get_rect(center=color_rect.center)
                self.screen.blit(color_surf, color_text_rect)
            
            # Save button
            save_rect = pygame.Rect(300, 440, 200, 50)
            
            if save_rect.collidepoint(mouse):
                pygame.draw.rect(self.screen, self.GREEN, save_rect)
                if click[0]:
                    self.config.save_settings()
                    pygame.time.wait(200)
                    return
            else:
                pygame.draw.rect(self.screen, (0, 150, 0), save_rect)
            
            pygame.draw.rect(self.screen, self.WHITE, save_rect, 2)
            save_surf = self.button_font.render("SAVE & BACK", True, self.WHITE)
            save_text_rect = save_surf.get_rect(center=save_rect.center)
            self.screen.blit(save_surf, save_text_rect)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
            
            pygame.display.flip()
            self.clock.tick(60)
    
    def run(self):
        self.main_menu()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = GameApp()
    app.run()