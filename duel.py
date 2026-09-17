"""
Single-round duel engine v0.2.
Timing methodology remains strictly isolated from dialogue/audio latency.
"""
import random
import time
from dataclasses import dataclass, field
from typing import Dict, Optional
import config
import renderer as R
import audio
import dialogue
from ai import Gunslinger

@dataclass
class RoundOutcome:
    winner: Optional[str]
    reason: str
    measured: Dict[str, Optional[float]] = field(default_factory=dict)
    void: bool = False

def _sleep_until(target: float) -> None:
    while True:
        remaining = target - time.perf_counter()
        if remaining <= 0: return
        time.sleep(min(remaining, 0.002))

def run_round(left: Gunslinger, right: Gunslinger, score: tuple, keys, context: dict) -> RoundOutcome:
    L, Rr = left.name, right.name

    # ---- PRE-DUEL CINEMATIC ----
    if config.DIALOGUE:
        b_line, q_line = dialogue.get_pre_duel()
        R.frame_pre_duel(L, Rr, score, b_line, q_line)
        audio.audio.play("ready")
        time.sleep(1.5)

    if config.ANNOUNCER and context.get("is_first_round"):
        ann_line = dialogue.get_announcer_intro()
        R.frame_announcer(ann_line, score)
        audio.audio.play("game_start")
        time.sleep(1.5)

    # ---- WAITING ----
    delay = random.uniform(config.DRAW_DELAY_MIN, config.DRAW_DELAY_MAX)
    plan_l = left.plan_round(delay)
    plan_r = right.plan_round(delay)
    
    ann_pre = dialogue.get_announcer_pre_draw() if config.ANNOUNCER else None
    t_start = time.perf_counter()
    next_tick = config.TICK_INTERVAL
    ticks = 0
    
    R.frame_waiting(L, Rr, ticks, score, [f"ANNOUNCER: {ann_pre}"] if ann_pre else None)

    while True:
        if keys is not None and keys.poll_quit():
            return RoundOutcome(None, "quit")
        now = time.perf_counter() - t_start

        if now >= next_tick:
            ticks += 1
            next_tick += config.TICK_INTERVAL
            audio.audio.play("tick")
            R.frame_waiting(L, Rr, ticks, score)

        # False starts
        fs_l = plan_l.false_start and now >= plan_l.fs_time
        fs_r = plan_r.false_start and now >= plan_r.fs_time
        
        if fs_l and fs_r and config.DOUBLE_FS_REPLAY:
            audio.audio.play("false_start")
            R.fs_frame(f"{L} & {Rr}", score)
            time.sleep(1.0)
            return RoundOutcome(None, "double_false_start", void=True)
            
        if fs_l or fs_r:
            culprit = L if fs_l else Rr
            other = Rr if fs_l else L
            
            audio.audio.play("gunshot")
            time.sleep(0.15)
            audio.audio.play("false_start")
            
            fs_lines = []
            if config.ANNOUNCER:
                fs_lines.append(f"ANNOUNCER: {dialogue.get_announcer_false_start(culprit)}")
            if config.DIALOGUE:
                fs_lines.extend([f"{culprit}:", '"..."', "", f"{other}:", 
                                 f'"{random.choice(dialogue.FS_REACTIONS)}"'])
                
            R.fs_frame(culprit, score, fs_lines)
            time.sleep(2.5)
            winner = Rr if fs_l else L
            return RoundOutcome(winner, "false_start", measured={L: None, Rr: None})

        if now >= delay:
            break

    # ---- DRAW SIGNAL ----
    R.frame_draw(L, Rr, score)
    t0 = time.perf_counter()  # TIMING CORE: Stamped exactly here
    audio.audio.play("draw")

    # ---- REACTION / SHOT ----
    order = sorted([(plan_l.reaction, left), (plan_r.reaction, right)], key=lambda x: x[0])
    measured: Dict[str, Optional[float]] = {L: None, Rr: None}

    for planned_rt, gun in order:
        if keys is not None and keys.poll_quit():
            return RoundOutcome(None, "quit")
        _sleep_until(t0 + planned_rt)
        measured[gun.name] = time.perf_counter() - t0  # MEASURED
        R.frame_shot(gun.name, L, Rr, score)
        audio.audio.play("gunshot")
        time.sleep(config.SHOT_FLASH_HOLD)

    # ---- RESULT ----
    ms_l = measured[L] * 1000.0
    ms_r = measured[Rr] * 1000.0
    diff = abs(ms_l - ms_r)

    if diff < config.TIE_TOLERANCE_MS:
        winner, reason = None, "tie"
        headline = "D R A W"
        audio.audio.play("lose")
    elif ms_l < ms_r:
        winner, reason = L, "reaction"
        headline = f"{L} WINS"
        audio.audio.play("win")
    else:
        winner, reason = Rr, "reaction"
        headline = f"{Rr} WINS"
        audio.audio.play("win")

    # Post-duel dialogue
    result_dialogue = []
    if config.DIALOGUE and winner:
        loser = Rr if winner == L else L
        w_line, l_line = dialogue.get_post_duel(winner, loser)
        result_dialogue.extend([f"{winner}:", f'"{w_line}"', "", f"{loser}:", f'"{l_line}"'])
    if config.ANNOUNCER and winner:
        ann_line = dialogue.get_announcer_round_win(winner, diff)
        result_dialogue.extend(["", f"ANNOUNCER: {ann_line}"])

    lines = [
        "", f">>> {headline} <<<", "",
        f"{L:<8}{ms_l:6.0f} ms  {R.rt_bar(ms_l)}  {R.label_for(ms_l)}",
        f"{Rr:<8}{ms_r:6.0f} ms  {R.rt_bar(ms_r)}  {R.label_for(ms_r)}", "",
        ("(within tie tolerance - no point)" if reason == "tie" else f"{winner} drew first by {diff:.0f} ms"),
    ]
    
    R.frame_result(lines, L, Rr, score, result_dialogue)
    time.sleep(config.RESULT_HOLD)
    return RoundOutcome(winner, reason, measured=measured)