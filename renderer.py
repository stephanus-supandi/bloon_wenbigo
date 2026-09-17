"""
ASCII/ANSI western renderer v0.2.
Includes dialogue box integration.
"""
import sys
import config

W = 62

def clear() -> None:
    sys.stdout.write("\x1b[2J\x1b[H")
    sys.stdout.flush()

def _out(text: str) -> None:
    sys.stdout.write(text + "\n")
    sys.stdout.flush()

def bell() -> None:
    if config.AUDIO:
        sys.stdout.write("\a")
        sys.stdout.flush()

def center(s: str) -> str:
    return s.center(W)

def label_for(ms: float) -> str:
    if ms < config.LABEL_INSANE_MAX_MS: return "INSANE"
    if ms < config.LABEL_FAST_MAX_MS: return "FAST"
    if ms < config.LABEL_NORMAL_MAX_MS: return "NORMAL"
    return "SLOW"

def rt_bar(ms: float, width: int = 22) -> str:
    filled = max(0, min(width, int(ms / 10.0)))
    return "[" + "#" * filled + "-" * (width - filled) + "]"

def title_block() -> None:
    _out("=" * W)
    _out(center(f"{config.GAME_TITLE}  {config.VERSION}"))
    _out(center(config.GAME_SUBTITLE))
    _out("=" * W)

def scene(left_name, right_name, left_gun, right_gun, center_text, score=None):
    _out(center("~  ~  ~   desert plains, high noon   ~  ~  ~"))
    _out(center(f"  |{left_name:^26}|{right_name:^26}|  "))
    _out("")
    _out(center("        \\   |   /                \\   |   /"))
    _out(center("    _____\\  |  /_____        _____\\  |  /_____"))
    _out(center("   |  SALOON  BOARD  |      |  SALOON  BOARD  |"))
    _out(center("   |_________________|      |_________________|"))
    _out("")
    _out(center(f"      \U0001F920{left_gun:<28}\U0001F920 {right_gun}"))
    _out(center("      /|\\                            /|\\"))
    _out(center("      / \\                            / \\"))
    _out(center("  ^^  ^^  ^^  ^^^   ^^  ^^   ^^^  ^^  ^^  ^^"))
    _out("")
    _out(center(f">>>  {center_text}  <<<"))
    _out("")
    if score is not None:
        _out(center(f"SCORE   {left_name} {score[0]}  :  {score[1]} {right_name}"))

IDLE_GUN  = "  .-.  holster"
DRAW_GUN  = " \U0001F52B ----->"
BANG_GUN  = " \U0001F52B\U0001F4A5====>"

def render_dialogue_block(lines: list):
    if not lines: return
    _out("-" * W)
    for ln in lines:
        _out(center(ln) if len(ln) < W else ln)
    _out("-" * W)

def frame_ready(left, right, score=None):
    clear(); title_block()
    scene(left, right, IDLE_GUN, IDLE_GUN, "READY  -  press SPACE / ENTER", score)

def frame_pre_duel(left, right, score, b_line, q_line):
    clear(); title_block()
    scene(left, right, IDLE_GUN, IDLE_GUN, "READY", score)
    _out("-" * W)
    _out("BLOON:")
    _out(f'"{b_line}"')
    _out("")
    _out("QWENY:")
    _out(f'"{q_line}"')
    _out("-" * W)

def frame_announcer(line, score):
    clear(); title_block()
    _out("\n" * 4)
    _out(center(f"ANNOUNCER:"))
    _out(center(f'"{line}"'))
    _out("\n" * 4)
    if score: _out(center(f"SCORE   {score[0]}  :  {score[1]}"))

def frame_waiting(left, right, ticks, score=None, dialogue_lines=None):
    clear(); title_block()
    scene(left, right, IDLE_GUN, IDLE_GUN, "WAIT..." + " ." * (ticks % 4), score)
    render_dialogue_block(dialogue_lines)

def frame_draw(left, right, score=None):
    clear(); title_block()
    bell()
    scene(left, right, DRAW_GUN, DRAW_GUN, "***  D R A W !  ***", score)

def frame_shot(shooter, left, right, score=None):
    clear(); title_block()
    bell()
    lgun = BANG_GUN if shooter == left else DRAW_GUN
    rgun = BANG_GUN if shooter == right else DRAW_GUN
    scene(left, right, lgun, rgun, f"BANG!  {shooter} FIRES!", score)

def frame_result(lines, left, right, score=None, dialogue_lines=None):
    clear(); title_block()
    scene(left, right, IDLE_GUN, IDLE_GUN, "RESULT", score)
    for ln in lines:
        _out(center(ln))
    render_dialogue_block(dialogue_lines)

def fs_frame(culprit, score=None, dialogue_lines=None):
    clear(); title_block()
    bell()
    l, r = _names()
    lgun = BANG_GUN if culprit == l else IDLE_GUN
    rgun = BANG_GUN if culprit == r else IDLE_GUN
    scene(l, r, lgun, rgun, f"FALSE START!  {culprit} DREW TOO EARLY!", score)
    render_dialogue_block(dialogue_lines)

def frame_match_end(lines, dialogue_lines=None):
    clear()
    _out("=" * W)
    _out(center("M A T C H   C O M P L E T E"))
    _out("=" * W)
    for ln in lines:
        _out(center(ln) if len(ln) < W else ln)
    render_dialogue_block(dialogue_lines)
    _out("")
    _out(center("SPACE / ENTER = new match   |   R = restart   |   ESC / Q = quit"))

_LEFT = _RIGHT = None
def set_names(left, right):
    global _LEFT, _RIGHT
    _LEFT, _RIGHT = left, right
def _names(): return (_LEFT, _RIGHT)