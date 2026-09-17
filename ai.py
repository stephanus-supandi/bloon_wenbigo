"""
AI reaction-time model.

This is NOT `time.sleep(random())` dressed up as intelligence.
Each Gunslinger has a small stochastic model:

    reaction = base_rt
             + gaussian noise (variance)
             + occasional "flinch" lapse (lapse_chance / lapse_range)

clamped to a physically sensible range. The result is the AI's
*planned* reaction for the round; duel.py then measures the ACTUAL
elapsed time from the DRAW signal to the shot with perf_counter().
"""

import random
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class RoundPlan:
    """An AI's pre-committed plan for one round."""
    reaction: float            # planned reaction time (seconds)
    false_start: bool          # will it jump the gun?
    fs_time: Optional[float]   # seconds after WAIT begins when it flinches

class Gunslinger:
    def __init__(self, cfg: dict):
        self.name: str             = cfg["name"]
        self.tagline: str          = cfg["tagline"]
        self.base_rt: float        = cfg["base_rt"]
        self.variance: float       = cfg["variance"]
        self.false_start_prob: float = cfg["false_start_prob"]
        self.lapse_chance: float   = cfg["lapse_chance"]
        self.lapse_range: Tuple[float, float] = tuple(cfg["lapse_range"])
        self.rt_clamp: Tuple[float, float]    = tuple(cfg["rt_clamp"])

    def generate_reaction(self) -> float:
        """Sample one reaction time (seconds) from this AI's model."""
        rt = self.base_rt + random.gauss(0.0, self.variance)
        if random.random() < self.lapse_chance:          # bad-round spike
            rt += random.uniform(*self.lapse_range)
        lo, hi = self.rt_clamp
        return min(max(rt, lo), hi)                      # clamp

    def plan_round(self, wait_duration: float) -> RoundPlan:
        """
        Decide this AI's behaviour for the upcoming round.
        The plan is made BEFORE the signal, like a real duelist's nerves.
        """
        reaction = self.generate_reaction()
        fs = random.random() < self.false_start_prob
        fs_time = None
        if fs:
            # flinch somewhere between 0.4s after WAIT begins and 0.3s
            # before the signal would have fired
            fs_time = random.uniform(0.4, max(0.5, wait_duration - 0.3))
        return RoundPlan(reaction=reaction, false_start=fs, fs_time=fs_time)