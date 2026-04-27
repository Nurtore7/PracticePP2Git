import json
import os

class DataManager:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.settings_file = os.path.join(self.script_dir, "settings.json")
        self.leaderboard_file = os.path.join(self.script_dir, "leaderboard.json")
        self.load_settings()
        self.load_leaderboard()
    
    def load_settings(self):
        default_settings = {
            "sound": True,
            "car_color": (255, 0, 0),
            "difficulty": "normal"
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    if "car_color" in loaded:
                        loaded["car_color"] = tuple(loaded["car_color"])
                    self.settings = loaded
            except:
                self.settings = default_settings
        else:
            self.settings = default_settings
            self.save_settings()
    
    def save_settings(self):
        settings_to_save = self.settings.copy()
        settings_to_save["car_color"] = list(settings_to_save["car_color"])
        
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings_to_save, f, indent=4, ensure_ascii=False)
    
    def load_leaderboard(self):
        if os.path.exists(self.leaderboard_file):
            try:
                with open(self.leaderboard_file, 'r', encoding='utf-8') as f:
                    self.leaderboard = json.load(f)
            except:
                self.leaderboard = []
        else:
            self.leaderboard = []
    
    def save_leaderboard(self):
        with open(self.leaderboard_file, 'w', encoding='utf-8') as f:
            json.dump(self.leaderboard[:10], f, indent=4, ensure_ascii=False)
    
    def add_score(self, name, score, distance, coins):
        self.leaderboard.append({
            "name": name,
            "score": score,
            "distance": distance,
            "coins": coins
        })
        self.leaderboard.sort(key=lambda x: x["score"], reverse=True)
        self.leaderboard = self.leaderboard[:10]
        self.save_leaderboard()
    
    def get_top_scores(self):
        return self.leaderboard