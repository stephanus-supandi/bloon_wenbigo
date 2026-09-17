"""
Explicit state machine + match flow v0.2.
"""
import sys
import time
from enum import Enum, auto
import config
import duel
import renderer as R
import stats
import audio
import dialogue
from ai import Gunslinger

class State(Enum):
    READY = auto(); ROUND = auto(); MATCH_END = auto(); QUIT = auto()

class KeyPoller:
    def __init__(self):
        self.mode = None; self._old = None
        try:
            import msvcrt; self.mode = "win"; return
        except ImportError: pass
        try:
            import termios, tty
            self.fd = sys.stdin.fileno(); self._old = termios.tcgetattr(self.fd)
            tty.setcbreak(self.fd); self.mode = "posix"
        except Exception: self.mode = None

    def poll(self):
        if self.mode == "win":
            import msvcrt
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                if ch in (b"\x00", b"\xe0"): msvcrt.getch(); return None
                return self._norm(ch)
        elif self.mode == "posix":
            import select
            r, _, _ = select.select([sys.stdin], [], [], 0)
            if r: return self._norm(sys.stdin.read(1).encode())
        return None

    def poll_quit(self): return self.poll() in ("esc", "q")
    def wait_key(self):
        if self.mode is None:
            try: input(); return "space"
            except EOFError: return "q"
        while True:
            k = self.poll()
            if k is not None: return k
            time.sleep(0.03)

    @staticmethod
    def _norm(ch: bytes):
        if ch in (b" ", b"\r", b"\n"): return "space"
        if ch in (b"\x1b",): return "esc"
        try: return ch.decode("utf-8", "ignore").lower()
        except Exception: return None

    def close(self):
        if self.mode == "posix" and self._old is not None:
            import termios; termios.tcsetattr(self.fd, termios.TCSADRAIN, self._old)

class Game:
    def __init__(self):
        self.left  = Gunslinger(config.BLOON)
        self.right = Gunslinger(config.QWENY)
        self.keys  = KeyPoller()
        R.set_names(self.left.name, self.right.name)
        self.state = State.READY

    def run(self):
        try:
            while self.state != State.QUIT:
                if self.state == State.READY: self._ready()
                elif self.state == State.ROUND: self._match()
                elif self.state == State.MATCH_END: self._match_end()
        except KeyboardInterrupt: pass
        finally:
            self.keys.close(); R.clear()
            print("Thanks for watching the duel. \U0001F920")

    def _ready(self):
        R.frame_ready(self.left.name, self.right.name, (0, 0))
        k = self.keys.wait_key()
        self.state = State.QUIT if k in ("esc", "q") else State.ROUND

    def _match_end(self):
        k = self.keys.wait_key()
        if k in ("esc", "q"): self.state = State.QUIT
        else: self.state = State.ROUND

    def _match(self):
        ls, rs = stats.AIStats(self.left.name), stats.AIStats(self.right.name)
        ms = stats.MatchStats(ls, rs)
        score_l = score_r = 0
        rounds = 0

        while rounds < config.MAX_ROUNDS:
            self.state = State.ROUND
            context = {"round_num": rounds + 1, "is_first_round": rounds == 0}
            outcome = duel.run_round(self.left, self.right, (score_l, score_r), self.keys, context)
            
            if outcome.reason == "quit": self.state = State.QUIT; return
            if outcome.void: ms.void_rounds += 1; continue
            
            rounds += 1; ms.rounds_completed += 1
            lm, rm = outcome.measured.get(self.left.name), outcome.measured.get(self.right.name)
            
            if outcome.reason == "false_start":
                culprit = self.right.name if outcome.winner == self.left.name else self.left.name
                (ls if culprit == self.left.name else rs).false_starts += 1
                
            if outcome.winner == self.left.name: score_l += 1; ls.wins += 1; rs.losses += 1
            elif outcome.winner == self.right.name: score_r += 1; rs.wins += 1; ls.losses += 1
            
            if lm is not None: ls.record_shot(lm)
            if rm is not None: rs.record_shot(rm)
            if outcome.reason == "tie": ls.draws += 1; rs.draws += 1

            if score_l >= config.WINS_TO_TAKE_MATCH or score_r >= config.WINS_TO_TAKE_MATCH: break

        champ = self.left.name if score_l > score_r else (self.right.name if score_r > score_l else "NOBODY (tied)")
        self._champ = champ; self._score_l = score_l; self._score_r = score_r; self._ms = ms
        self.state = State.MATCH_END

    def _match_end(self):
        champ = getattr(self, '_champ', 'NOBODY')
        score_l, score_r = getattr(self, '_score_l', 0), getattr(self, '_score_r', 0)
        ms = getattr(self, '_ms', None)
        
        if champ != "NOBODY (tied)": audio.audio.play("match_win")
        else: audio.audio.play("lose")

        lines = ["", f"{champ} WINS THE MATCH", "", f"{self.left.name} {score_l}  :  {score_r} {self.right.name}", ""]
        if ms: lines += ms.summary_lines()
        
        end_dialogue = []
        if config.DIALOGUE:
            end_dialogue.extend(["BLOON:", '"Rematch."', "", "QWENY:", '"Whenever you\'re ready."'])
        if config.ANNOUNCER:
            end_dialogue.extend(["", f"ANNOUNCER: {dialogue.get_announcer_match_end()}"])
            
        R.frame_match_end(lines, end_dialogue)
        
        k = self.keys.wait_key()
        if k in ("esc", "q"): self.state = State.QUIT
        else: self.state = State.ROUND