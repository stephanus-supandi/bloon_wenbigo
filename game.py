import sys,time
from enum import Enum,auto
import config,duel,renderer as R,stats,audio,dialogue
from ai import Gunslinger
class State(Enum): READY=auto();ROUND=auto();MATCH_END=auto();QUIT=auto()
class KeyPoller:
    def __init__(self):
        self.mode=None;self._old=None
        try:
            import msvcrt;self.mode='win';return
        except ImportError:pass
        try:
            import termios,tty;self.fd=sys.stdin.fileno();self._old=termios.tcgetattr(self.fd);tty.setcbreak(self.fd);self.mode='posix'
        except Exception:self.mode=None
    def poll(self):
        if self.mode=='win':
            import msvcrt
            if msvcrt.kbhit():
                ch=msvcrt.getch()
                if ch in (b'\x00',b'\xe0'):msvcrt.getch();return None
                return self._norm(ch)
        elif self.mode=='posix':
            import select;r,_,_=select.select([sys.stdin],[],[],0)
            if r:return self._norm(sys.stdin.read(1).encode())
        return None
    def poll_quit(self):return self.poll() in ('esc','q')
    def wait_key(self):
        if self.mode is None:
            try:input();return 'space'
            except EOFError:return 'q'
        while True:
            k=self.poll()
            if k is not None:return k
            time.sleep(.03)
    @staticmethod
    def _norm(ch):
        if ch in (b' ',b'\r',b'\n'):return 'space'
        if ch==b'\x1b':return 'esc'
        return ch.decode('utf-8','ignore').lower()
    def close(self):
        if self.mode=='posix' and self._old is not None:
            import termios;termios.tcsetattr(self.fd,termios.TCSADRAIN,self._old)
class Game:
    def __init__(self):self.left=Gunslinger(config.BLOON);self.right=Gunslinger(config.QWENY);self.keys=KeyPoller();R.set_names(self.left.name,self.right.name);self.state=State.READY
    def run(self):
        try:
            while self.state!=State.QUIT:
                if self.state==State.READY:self._ready()
                elif self.state==State.ROUND:self._match()
                elif self.state==State.MATCH_END:self._match_end()
        finally:self.keys.close();R.clear();print('Thanks for watching the duel. 🤠')
    def _ready(self):R.frame_ready(self.left.name,self.right.name,(0,0));self.state=State.QUIT if self.keys.wait_key() in ('esc','q') else State.ROUND
    def _match(self):
        ls,rs=stats.AIStats(self.left.name),stats.AIStats(self.right.name);ms=stats.MatchStats(ls,rs);sl=sr=rounds=0
        while rounds<config.MAX_ROUNDS:
            o=duel.run_round(self.left,self.right,(sl,sr),self.keys,{'round_num':rounds+1,'is_first_round':rounds==0})
            if o.reason=='quit':self.state=State.QUIT;return
            if o.void:ms.void_rounds+=1;continue
            rounds+=1;ms.rounds_completed+=1;lm=o.measured.get(self.left.name);rm=o.measured.get(self.right.name)
            if o.reason=='false_start':
                culprit=self.right.name if o.winner==self.left.name else self.left.name;(ls if culprit==self.left.name else rs).false_starts+=1
            if o.winner==self.left.name:sl+=1;ls.wins+=1;rs.losses+=1
            elif o.winner==self.right.name:sr+=1;rs.wins+=1;ls.losses+=1
            if lm is not None:ls.record_shot(lm)
            if rm is not None:rs.record_shot(rm)
            if o.reason=='tie':ls.draws+=1;rs.draws+=1
            if sl>=config.WINS_TO_TAKE_MATCH or sr>=config.WINS_TO_TAKE_MATCH:break
        self._champ=self.left.name if sl>sr else self.right.name if sr>sl else 'NOBODY (tied)';self._score=(sl,sr);self._ms=ms;self.state=State.MATCH_END
    def _match_end(self):
        champ=self._champ;sl,sr=self._score;audio.audio.play('match_win' if champ!='NOBODY (tied)' else 'lose');lines=['',f'{champ} WINS THE MATCH','',f'{self.left.name} {sl} : {sr} {self.right.name}','']+self._ms.summary_lines();dlg=['BLOON:','"Rematch."','','QWENY:','"Whenever you\'re ready."'] if config.DIALOGUE else []
        if config.ANNOUNCER:dlg += ['',f'ANNOUNCER: {dialogue.get_announcer_match_end()}']
        R.frame_match_end(lines,dlg);self.state=State.QUIT if self.keys.wait_key() in ('esc','q') else State.ROUND