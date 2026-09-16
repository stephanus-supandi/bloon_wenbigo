import random,time
from dataclasses import dataclass,field
from typing import Dict,Optional
import config,renderer as R,audio,dialogue
from ai import Gunslinger
@dataclass
class RoundOutcome:
    winner:Optional[str]; reason:str; measured:Dict[str,Optional[float]]=field(default_factory=dict); void:bool=False
def _sleep_until(t):
    while True:
        rem=t-time.perf_counter()
        if rem<=0:return
        time.sleep(min(rem,0.002))
def run_round(left:Gunslinger,right:Gunslinger,score,keys,context):
    L,Rr=left.name,right.name
    if config.DIALOGUE:
        b,q=dialogue.get_pre_duel();R.frame_pre_duel(L,Rr,score,b,q);audio.audio.play('ready');time.sleep(1.0)
    if config.ANNOUNCER and context.get('is_first_round'):
        R.frame_announcer(dialogue.get_announcer_intro(),score);audio.audio.play('game_start');time.sleep(1.0)
    delay=random.uniform(config.DRAW_DELAY_MIN,config.DRAW_DELAY_MAX);pl,pr=left.plan_round(delay),right.plan_round(delay)
    t0wait=time.perf_counter();next_tick=config.TICK_INTERVAL;ticks=0;R.frame_waiting(L,Rr,ticks,score)
    while True:
        if keys and keys.poll_quit():return RoundOutcome(None,'quit')
        now=time.perf_counter()-t0wait
        if now>=next_tick:
            ticks+=1;next_tick+=config.TICK_INTERVAL;audio.audio.play('tick');R.frame_waiting(L,Rr,ticks,score)
        fsl=pl.false_start and now>=pl.fs_time;fsr=pr.false_start and now>=pr.fs_time
        if fsl and fsr and config.DOUBLE_FS_REPLAY:
            audio.audio.play('false_start');R.fs_frame(f'{L} & {Rr}',score);time.sleep(0.8);return RoundOutcome(None,'double_false_start',void=True)
        if fsl or fsr:
            culprit=L if fsl else Rr;other=Rr if fsl else L;audio.audio.play('gunshot');time.sleep(.12);audio.audio.play('false_start')
            lines=[]
            if config.ANNOUNCER:lines.append(f'ANNOUNCER: {dialogue.get_announcer_false_start(culprit)}')
            if config.DIALOGUE:lines += [f'{culprit}:','"..."','',f'{other}:',f'"{random.choice(dialogue.FS_REACTIONS)}"']
            R.fs_frame(culprit,score,lines);time.sleep(1.8);return RoundOutcome(other,'false_start',{L:None,Rr:None})
        if now>=delay:break
    R.frame_draw(L,Rr,score);t0=time.perf_counter();audio.audio.play('draw')
    measured={L:None,Rr:None}
    for planned,gun in sorted([(pl.reaction,left),(pr.reaction,right)],key=lambda x:x[0]):
        if keys and keys.poll_quit():return RoundOutcome(None,'quit')
        _sleep_until(t0+planned);measured[gun.name]=time.perf_counter()-t0;R.frame_shot(gun.name,L,Rr,score);audio.audio.play('gunshot');time.sleep(config.SHOT_FLASH_HOLD)
    ml,mr=measured[L]*1000,measured[Rr]*1000;diff=abs(ml-mr)
    if diff<config.TIE_TOLERANCE_MS:winner,reason,headline=None,'tie','D R A W';audio.audio.play('lose')
    elif ml<mr:winner,reason,headline=L,'reaction',f'{L} WINS';audio.audio.play('win')
    else:winner,reason,headline=Rr,'reaction',f'{Rr} WINS';audio.audio.play('win')
    lines=['',f'>>> {headline} <<<','',f'{L:<8}{ml:6.0f} ms  {R.rt_bar(ml)}  {R.label_for(ml)}',f'{Rr:<8}{mr:6.0f} ms  {R.rt_bar(mr)}  {R.label_for(mr)}','',('(within tie tolerance - no point)' if reason=='tie' else f'{winner} drew first by {diff:.0f} ms')]
    extra=[]
    if winner and config.DIALOGUE:
        loser=Rr if winner==L else L;wl,ll=dialogue.get_post_duel(winner,loser);extra=[f'{winner}:',f'"{wl}"','',f'{loser}:',f'"{ll}"']
    if winner and config.ANNOUNCER:extra += ['',f'ANNOUNCER: {dialogue.get_announcer_round_win(winner,diff)}']
    R.frame_result(lines,L,Rr,score,extra);time.sleep(config.RESULT_HOLD);return RoundOutcome(winner,reason,measured)