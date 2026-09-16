import random
from dataclasses import dataclass
from typing import Optional,Tuple
@dataclass
class RoundPlan:
    reaction:float
    false_start:bool
    fs_time:Optional[float]
class Gunslinger:
    def __init__(self,cfg:dict):
        self.name=cfg['name']; self.tagline=cfg['tagline']; self.base_rt=cfg['base_rt']; self.variance=cfg['variance']; self.false_start_prob=cfg['false_start_prob']; self.lapse_chance=cfg['lapse_chance']; self.lapse_range:Tuple[float,float]=tuple(cfg['lapse_range']); self.rt_clamp:Tuple[float,float]=tuple(cfg['rt_clamp'])
    def generate_reaction(self):
        rt=self.base_rt+random.gauss(0.0,self.variance)
        if random.random()<self.lapse_chance: rt+=random.uniform(*self.lapse_range)
        lo,hi=self.rt_clamp; return min(max(rt,lo),hi)
    def plan_round(self,wait_duration):
        reaction=self.generate_reaction(); fs=random.random()<self.false_start_prob; fs_time=None
        if fs: fs_time=random.uniform(0.4,max(0.5,wait_duration-0.3))
        return RoundPlan(reaction,fs,fs_time)