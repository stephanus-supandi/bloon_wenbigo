from typing import List,Optional
class AIStats:
    def __init__(self,name:str): self.name=name; self.wins=0; self.losses=0; self.draws=0; self.false_starts=0; self.reactions=[]
    def record_shot(self,v:float): self.reactions.append(v)
    @property
    def rounds_played(self): return self.wins+self.losses+self.draws
    def avg_ms(self): return sum(self.reactions)/len(self.reactions)*1000 if self.reactions else None
    def fastest_ms(self): return min(self.reactions)*1000 if self.reactions else None
    def slowest_ms(self): return max(self.reactions)*1000 if self.reactions else None
    @staticmethod
    def fmt(v): return f'{v:6.0f} ms' if v is not None else '   ---   '
class MatchStats:
    def __init__(self,left,right): self.left=left; self.right=right; self.rounds_completed=0; self.void_rounds=0
    def summary_lines(self)->List[str]:
        L,R=self.left,self.right
        return ['---------------- STATISTICS ----------------',f"{'':10}{L.name:>12}{R.name:>12}",f"{'Rounds':10}{L.rounds_played:>12}{R.rounds_played:>12}",f"{'Wins':10}{L.wins:>12}{R.wins:>12}",f"{'Losses':10}{L.losses:>12}{R.losses:>12}",f"{'Draws':10}{L.draws:>12}{R.draws:>12}",f"{'False starts':10}{L.false_starts:>12}{R.false_starts:>12}",f"{'Avg RT':10}{self.fmt(L.avg_ms()):>12}{self.fmt(R.avg_ms()):>12}",f"{'Fastest':10}{self.fmt(L.fastest_ms()):>12}{self.fmt(R.fastest_ms()):>12}",f"{'Slowest':10}{self.fmt(L.slowest_ms()):>12}{self.fmt(R.slowest_ms()):>12}",f'Void rounds (double false start): {self.void_rounds}','---------------------------------------------']