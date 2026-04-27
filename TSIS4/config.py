import json
import os

class Config:
    def __init__(self):
        self.config_file = 'settings.json'
        self.snake_color = (0, 255, 0)
        self.grid_overlay = True
        self.sound_on = True
        self.load_settings()
        
    def load_settings(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    settings = json.load(f)
                    self.snake_color = tuple(settings.get('snake_color', [0, 255, 0]))
                    self.grid_overlay = settings.get('grid_overlay', True)
                    self.sound_on = settings.get('sound_on', True)
        except:
            pass
    
    def save_settings(self):
        try:
            settings = {
                'snake_color': list(self.snake_color),
                'grid_overlay': self.grid_overlay,
                'sound_on': self.sound_on
            }
            with open(self.config_file, 'w') as f:
                json.dump(settings, f, indent=4)
        except:
            pass