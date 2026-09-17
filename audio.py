"""
Audio abstraction layer v0.2.1
- Zero-dependency fallback: winsound (Windows) or terminal bell (POSIX).
- Optional pygame backend: loads .wav from assets/sfx/ OR synthesizes them on the fly.
"""
import sys
import platform
import threading
import config

class AudioSystem:
    def __init__(self):
        self.backend = self._init_backend()

    def _init_backend(self):
        if not config.AUDIO:
            return NullBackend()
        
        # 1. Try Pygame (Optional dependency for real SFX)
        try:
            import pygame
            if not pygame.mixer.get_init():
                # Force mono 16-bit 44100Hz so our array buffers match perfectly
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            return PygameBackend()
        except ImportError:
            pass
        
        # 2. Try Winsound (Windows standard library - actually makes noise)
        if platform.system() == "Windows":
            return WinsoundBackend()
            
        # 3. Fallback (POSIX terminal bell)
        return BellBackend()

    def play(self, event: str):
        """Play an audio event. Never crashes the game."""
        try:
            self.backend.play(event)
        except Exception:
            pass

# --- Backends ---

class NullBackend:
    def play(self, event: str): pass

class BellBackend:
    def play(self, event: str):
        if event in ("draw", "gunshot", "false_start", "match_win"):
            sys.stdout.write("\a\a")
        else:
            sys.stdout.write("\a")
        sys.stdout.flush()

class WinsoundBackend:
    def __init__(self):
        import winsound
        self.winsound = winsound
        self.sounds = {
            "ready":      [(500, 100)],
            "tick":       [(800, 30)],
            "draw":       [(1000, 150), (1200, 150)],
            "gun_draw":   [(600, 50)],
            "gunshot":    [(150, 80), (100, 100)],
            "false_start":[(200, 200), (150, 300)],
            "win":        [(800, 100), (1000, 100), (1200, 200)],
            "lose":       [(400, 200), (300, 300)],
            "match_win":  [(600, 100), (800, 100), (1000, 100), (1200, 300)],
            "game_start": [(400, 100), (600, 100), (800, 200)],
        }

    def play(self, event: str):
        threading.Thread(target=self._play_seq, args=(event,), daemon=True).start()
        
    def _play_seq(self, event):
        seq = self.sounds.get(event, [(500, 100)])
        for freq, dur in seq:
            self.winsound.Beep(freq, dur)

class PygameBackend:
    def __init__(self):
        import pygame
        self.pygame = pygame
        self.sounds = {}
        self._init_synth()
        
    def _init_synth(self):
        """Generate synthetic SFX using standard library math/array."""
        import array, math, random
        sr = 44100
        
        def sine(freq, dur_ms, vol=0.3):
            n = int(sr * dur_ms / 1000.0)
            buf = array.array('h')
            mx = int(32767 * vol)
            for i in range(n):
                buf.append(int(mx * math.sin(2.0 * math.pi * freq * i / sr)))
            return buf
            
        def noise(dur_ms, vol=0.5):
            n = int(sr * dur_ms / 1000.0)
            buf = array.array('h')
            mx = int(32767 * vol)
            for _ in range(n):
                buf.append(random.randint(-mx, mx))
            return buf

        synth_map = {
            "ready":       [sine(500, 100)],
            "tick":        [sine(800, 30)],
            "draw":        [sine(1000, 150), sine(1200, 150)],
            "gun_draw":    [noise(50, 0.2)],
            "gunshot":     [noise(80, 0.8), noise(100, 0.6)],
            "false_start": [sine(200, 200), sine(150, 300)],
            "win":         [sine(800, 100), sine(1000, 100), sine(1200, 200)],
            "lose":        [sine(400, 200), sine(300, 300)],
            "match_win":   [sine(600, 100), sine(800, 100), sine(1000, 100), sine(1200, 300)],
            "game_start":  [sine(400, 100), sine(600, 100), sine(800, 200)],
        }
        
        for event, buffers in synth_map.items():
            full_buf = array.array('h')
            for b in buffers:
                full_buf.extend(b)
            try:
                self.sounds[event] = self.pygame.mixer.Sound(buffer=full_buf)
            except Exception:
                pass

    def play(self, event: str):
        # 1. Play pre-synthesized or loaded sound
        if event in self.sounds:
            try:
                self.sounds[event].play()
                return
            except Exception:
                pass
        
        # 2. Try loading .wav asset (if you ever add them to assets/sfx/)
        path = f"assets/sfx/{event}.wav"
        try:
            snd = self.pygame.mixer.Sound(path)
            self.sounds[event] = snd
            snd.play()
            return
        except Exception:
            pass
            
        # 3. Ultimate fallback (winsound on Windows, bell elsewhere)
        if platform.system() == "Windows":
            WinsoundBackend().play(event)
        else:
            BellBackend().play(event)

# Global instance
audio = AudioSystem()