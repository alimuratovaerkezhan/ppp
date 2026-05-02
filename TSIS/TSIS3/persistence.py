import json
import os
from datetime import datetime

SETTINGS_FILE = "settings.json"
LEADERBOARD_FILE = "leaderboard.json"

DEFAULT_SETTINGS = {
    "sound_enabled": True,
    "car_color": "green",
    "difficulty": "normal"
}

class LeaderboardEntry:
    def __init__(self, name, score, distance, coins, date=None):
        self.name = name
        self.score = score
        self.distance = distance
        self.coins = coins
        self.date = date if date else datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def to_dict(self):
        return {
            "name": self.name,
            "score": self.score,
            "distance": self.distance,
            "coins": self.coins,
            "date": self.date
        }
    
    @staticmethod
    def from_dict(data):
        return LeaderboardEntry(
            data["name"],
            data["score"],
            data["distance"],
            data["coins"],
            data.get("date", "")
        )

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS.copy()

def save_leaderboard(entries):
    try:
        data = [entry.to_dict() for entry in entries]
        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving leaderboard: {e}")
        return False

def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    
    try:
        with open(LEADERBOARD_FILE, 'r') as f:
            data = json.load(f)
        return [LeaderboardEntry.from_dict(entry) for entry in data]
    except Exception as e:
        print(f"Error loading leaderboard: {e}")
        return []

def add_score_to_leaderboard(name, score, distance, coins, max_entries=10):
    entries = load_leaderboard()
    new_entry = LeaderboardEntry(name, score, distance, coins)
    entries.append(new_entry)
    entries.sort(key=lambda x: x.score, reverse=True)
    entries = entries[:max_entries]
    save_leaderboard(entries)
    return entries