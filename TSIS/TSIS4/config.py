import json
import os

class Config:
    def __init__(self, filename="settings.json"):
        self.filename = filename
        self.default_settings = {
            "snake_color": [0, 255, 0],
            "grid_overlay": True,
            "sound": True
        }
        self.settings = self.load()
    
    def load(self):
        """Load settings from JSON file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    loaded = json.load(f)
                    settings = self.default_settings.copy()
                    settings.update(loaded)
                    print("Settings loaded from file")
                    return settings
            except Exception as e:
                print(f"Error loading settings: {e}")
        
        print("Using default settings")
        return self.default_settings.copy()
    
    def save(self):
        """Save settings to JSON file"""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.settings, f, indent=4)
            print("Settings saved")
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get(self, key):
        return self.settings.get(key, self.default_settings.get(key))
    
    def set(self, key, value):
        self.settings[key] = value
        self.save()
    
    def get_snake_color(self):
        color = self.get("snake_color")
        return tuple(color)
    
    def set_snake_color(self, color):
        self.set("snake_color", list(color))
    
    def get_grid_overlay(self):
        return self.get("grid_overlay")
    
    def set_grid_overlay(self, value):
        self.set("grid_overlay", value)
    
    def get_sound(self):
        return self.get("sound")
    
    def set_sound(self, value):
        self.set("sound", value)