"""Per-match statistics tracking."""

from typing import List, Optional

class AIStats:
    def __init__(self, name: str):
        self.name = name
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.false_starts = 0
        self.reactions: List[float] = []       # valid measured RTs (seconds)

    def record_shot(self, measured_seconds: float) -> None:
        self.reactions.append(measured_seconds)

    @property
    def rounds_played(self) -> int:
        return self.wins + self.losses + self.draws

    def avg_ms(self) -> Optional[float]:
        if not self.reactions:
            return None
        return sum(self.reactions) / len(self.reactions) * 1000.0

    def fastest_ms(self) -> Optional[float]:
        if not self.reactions:
            return None
        return min(self.reactions) * 1000.0

    def slowest_ms(self) -> Optional[float]:
        if not self.reactions:
            return None
        return max(self.reactions) * 1000.0

    @staticmethod
    def _fmt(v: Optional[float]) -> str:
        return f"{v:6.0f} ms" if v is not None else "   ---   "

class MatchStats:
    def __init__(self, left: AIStats, right: AIStats):
        self.left = left
        self.right = right
        self.rounds_completed = 0
        self.void_rounds = 0

    def summary_lines(self) -> List[str]:
        L, R = self.left, self.right
        lines = [
            "---------------- STATISTICS ----------------",
            f"{'':<12}{'BLOON':>10}{'QWENY':>12}",
            f"{'Rounds':<12}{L.rounds_played:>10}{R.rounds_played:>12}",
            f"{'Wins':<12}{L.wins:>10}{R.wins:>12}",
            f"{'Losses':<12}{L.losses:>10}{R.losses:>12}",
            f"{'Draws':<12}{L.draws:>10}{R.draws:>12}",
            f"{'False starts':<12}{L.false_starts:>10}{R.false_starts:>12}",
            f"{'Avg RT':<12}{AIStats._fmt(L.avg_ms()):>10}"
            f"{AIStats._fmt(R.avg_ms()):>12}",
            f"{'Fastest':<12}{AIStats._fmt(L.fastest_ms()):>10}"
            f"{AIStats._fmt(R.fastest_ms()):>12}",
            f"{'Slowest':<12}{AIStats._fmt(L.slowest_ms()):>10}"
            f"{AIStats._fmt(R.slowest_ms()):>12}",
            f"Void rounds (double false start): {self.void_rounds}",
            "---------------------------------------------",
        ]
        return lines