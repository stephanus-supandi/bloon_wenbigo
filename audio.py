import platform,sys,threading,config
class NullBackend:
    def play(self,event): pass
class BellBackend:
    def play(self,event):
        sys.stdout.write('\a\a' if event in ('draw','gunshot','false_start','match_win') else '\a'); sys.stdout.flush()
class WinsoundBackend:
    def __init__(self):
        import winsound; self.winsound=winsound
        self.sounds={'ready':[(500,100)],'tick':[(800,30)],'draw':[(1000,150),(1200,150)],'gunshot':[(150,80),(100,100)],'false_start':[(200,200),(150,300)],'win':[(800,100),(1000,100),(1200,200)],'lose':[(400,200),(300,300)],'match_win':[(600,100),(800,100),(1000,100),(1200,300)],'game_start':[(400,100),(600,100),(800,200)]}
    def play(self,event): threading.Thread(target=self._seq,args=(event,),daemon=True).start()
    def _seq(self,event):
        for f,d in self.sounds.get(event,[(500,100)]): self.winsound.Beep(f,d)
class PygameBackend:
    def __init__(self):
        import pygame; self.pygame=pygame; self.sounds={}; self._init_synth()
    def _init_synth(self):
        import array,math,random
        sr=44100
        def sine(freq,dur,vol=.3):
            n=int(sr*dur/1000); m=int(32767*vol); b=array.array('h')
            for i in range(n): b.append(int(m*math.sin(2*math.pi*freq*i/sr)))
            return b
        def noise(dur,vol=.5):
            n=int(sr*dur/1000); m=int(32767*vol); return array.array('h',(random.randint(-m,m) for _ in range(n)))
        mp={'ready':[sine(500,100)],'tick':[sine(800,30)],'draw':[sine(1000,150),sine(1200,150)],'gunshot':[noise(80,.8),noise(100,.6)],'false_start':[sine(200,200),sine(150,300)],'win':[sine(800,100),sine(1000,100),sine(1200,200)],'lose':[sine(400,200),sine(300,300)],'match_win':[sine(600,100),sine(800,100),sine(1000,100),sine(1200,300)],'game_start':[sine(400,100),sine(600,100),sine(800,200)]}
        for e,bufs in mp.items():
            full=array.array('h')
            for b in bufs: full.extend(b)
            try:self.sounds[e]=self.pygame.mixer.Sound(buffer=full)
            except Exception:pass
    def play(self,event):
        if event in self.sounds:
            try:self.sounds[event].play();return
            except Exception:pass
        if platform.system()=='Windows': WinsoundBackend().play(event)
        else: BellBackend().play(event)
class AudioSystem:
    def __init__(self): self.backend=self._init()
    def _init(self):
        if not config.AUDIO:return NullBackend()
        try:
            import pygame
            if not pygame.mixer.get_init(): pygame.mixer.init(frequency=44100,size=-16,channels=1,buffer=512)
            return PygameBackend()
        except ImportError: pass
        return WinsoundBackend() if platform.system()=='Windows' else BellBackend()
    def play(self,event):
        try:self.backend.play(event)
        except Exception:pass
audio=AudioSystem()