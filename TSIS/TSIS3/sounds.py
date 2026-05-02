import pygame
import math
import array
import random

pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)

class SoundManager:
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.sounds = {}
        self.init_sounds()
    
    def clamp(self, value, min_val=-30000, max_val=30000):
        if value > max_val:
            return max_val
        if value < min_val:
            return min_val
        return int(value)
    
    def create_coin_sound(self):
        sample_rate = 22050
        duration = 0.12
        n_samples = int(sample_rate * duration)
        
        buf = array.array('h', [0]) * n_samples
        
        for i in range(n_samples):
            t = float(i) / sample_rate
            freq = 1000 + t * 500
            value = 20000 * math.sin(2 * math.pi * freq * t) * (1 - t / duration)
            buf[i] = self.clamp(value * 0.5)
        
        return pygame.mixer.Sound(buffer=buf.tobytes())
    
    def create_powerup_sound(self):
        sample_rate = 22050
        duration = 0.25
        n_samples = int(sample_rate * duration)
        
        buf = array.array('h', [0]) * n_samples
        
        for i in range(n_samples):
            t = float(i) / sample_rate
            freq = 500 + t * 300
            value = 15000 * math.sin(2 * math.pi * freq * t) * (1 - t / duration)
            value += 8000 * math.sin(2 * math.pi * freq * 2 * t) * (1 - t / duration)
            buf[i] = self.clamp(value * 0.5)
        
        return pygame.mixer.Sound(buffer=buf.tobytes())
    
    def create_crash_sound(self):
        sample_rate = 22050
        duration = 0.35
        n_samples = int(sample_rate * duration)
        
        buf = array.array('h', [0]) * n_samples
        
        for i in range(n_samples):
            t = float(i) / sample_rate
            r = random.randint(-10000, 10000)
            envelope = math.exp(-t * 12)
            freq = 200 * (1 - t / duration)
            tone = 8000 * math.sin(2 * math.pi * freq * t) * envelope
            value = r * 0.3 * envelope + tone * 0.7
            buf[i] = self.clamp(value)
        
        return pygame.mixer.Sound(buffer=buf.tobytes())
    
    def create_engine_sound(self):
        sample_rate = 22050
        duration = 0.2
        n_samples = int(sample_rate * duration)
        
        buf = array.array('h', [0]) * n_samples
        
        for i in range(n_samples):
            t = float(i) / sample_rate
            value = 3000 * math.sin(2 * math.pi * 120 * t)
            value += 2000 * math.sin(2 * math.pi * 240 * t)
            value *= (1 - t / duration)
            buf[i] = self.clamp(value * 0.3)
        
        return pygame.mixer.Sound(buffer=buf.tobytes())
    
    def init_sounds(self):
        try:
            self.sounds = {
                'coin': self.create_coin_sound(),
                'powerup': self.create_powerup_sound(),
                'crash': self.create_crash_sound(),
                'engine': self.create_engine_sound()
            }
            print("Sounds initialized successfully")
        except Exception as e:
            print(f"Error initializing sounds: {e}")
            self.sounds = {}
    
    def play(self, sound_name, loops=0):
        if self.enabled and sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play(loops=loops)
            except:
                pass
    
    def stop(self, sound_name):
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].stop()
            except:
                pass
    
    def set_enabled(self, enabled):
        self.enabled = enabled