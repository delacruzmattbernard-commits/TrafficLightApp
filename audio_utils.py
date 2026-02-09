import threading
import numpy as np
import pygame
import pygame.mixer

class AudioManager:
    def __init__(self):
        self.enabled = True
        # Initialize pygame mixer
        pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
        # Sound configurations: frequency in Hz, duration in ms
        self.sound_configs = {
            'red': {'freq': 800, 'duration': 4000},    # Longer beep for red to ensure awareness
            'yellow': {'freq': 1000, 'duration': 300}, # Short for yellow
            'green': {'freq': 1200, 'duration': 300}   # Short for green
        }

    def play_sound(self, color):
        """Play beep for the given color if audio is enabled"""
        if not self.enabled or color not in self.sound_configs:
            return
        config = self.sound_configs[color]
        # Play in a separate thread to avoid blocking the UI
        threading.Thread(target=self._play_beep, args=(config['freq'], config['duration'])).start()

    def _play_beep(self, freq, duration):
        try:
            # Generate beep sound using numpy and pygame
            sample_rate = 44100
            t = np.linspace(0, duration / 1000, int(sample_rate * duration / 1000), False)
            wave = np.sin(freq * 2 * np.pi * t) * 0.5  # 0.5 for volume
            # Convert to 16-bit signed integers
            wave = (wave * 32767).astype(np.int16)
            # Create stereo by duplicating mono
            wave = np.column_stack((wave, wave))
            # Create pygame Sound object
            sound = pygame.sndarray.make_sound(wave)
            sound.play()
        except Exception as e:
            print(f"Error playing beep: {e}")

    def toggle_audio(self):
        """Toggle audio on/off"""
        self.enabled = not self.enabled
        return self.enabled

    def is_enabled(self):
        return self.enabled
