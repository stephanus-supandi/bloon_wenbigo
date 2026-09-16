import sys,config
W=62

def clear(): sys.stdout.write('\x1b[2J\x1b[H');sys.stdout.flush()
def out(s): sys.stdout.write(s+'\n');sys.stdout.flush()
def center(s): return s.center(W)
def label_for(ms):
    if ms<config.LABEL_INSANE_MAX_MS:return 'INSANE'
    if ms<config.LABEL_FAST_MAX_MS:return 'FAST'
    if ms<config.LABEL_NORMAL_MAX_MS:return 'NORMAL'
    return 'SLOW'
def rt_bar(ms,width=22):
    filled=max(0,min(width,int(ms/10.0)));return '['+'#'*filled+'-'*(width-filled)+']'
def title_block():
    out('='*W);out(center(f'{config.GAME_TITLE}  {config.VERSION}'));out(center(config.GAME_SUBTITLE));out('='*W)
def scene(l,r,lg,rg,txt,score=None):
    lines=['~  ~  ~   desert plains, high noon   ~  ~  ~',f'  |{l:^26}|{r:^26}|','',r'        \   |   /                \   |   /',r'    _____\  |  /_____        _____\  |  /_____', '   |  SALOON  BOARD  |      |  SALOON  BOARD  |','   |_________________|      |_________________|','',f'      🤠{lg:<28}🤠 {rg}',r'      /|\                            /|\',r'      / \                            / \','  ^^  ^^  ^^  ^^^   ^^  ^^   ^^^  ^^  ^^  ^^','',f'>>>  {txt}  <<<','']
    for x in lines:out(center(x))
    if score is not None:out(center(f'SCORE   {l} {score[0]}  :  {score[1]} {r}'))
IDLE_GUN='  .-.  holster';DRAW_GUN=' 🔫 ----->';BANG_GUN=' 🔫💥====>'
def frame_ready(l,r,score=None):clear();title_block();scene(l,r,IDLE_GUN,IDLE_GUN,'READY  -  press SPACE / ENTER',score)
def frame_pre_duel(l,r,score,b,q):clear();title_block();scene(l,r,IDLE_GUN,IDLE_GUN,'>>> READY <<<',score);out('-'*W);out(center(f'{l}:'));out(center(f'"{b}"'));out('');out(center(f'{r}:'));out(center(f'"{q}"'));out('-'*W)
def frame_announcer(line,score=None):clear();title_block();out('');out(center('ANNOUNCER:'));out(center(f'"{line}"'));out('')
def frame_waiting(l,r,ticks,score=None,extra=None):clear();title_block();scene(l,r,IDLE_GUN,IDLE_GUN,'WAIT...'+' .'*(ticks%4),score); 

def frame_draw(l,r,score=None):clear();title_block();scene(l,r,DRAW_GUN,DRAW_GUN,'***  D R A W !  ***',score)
def frame_shot(shooter,l,r,score=None):clear();title_block();scene(l,r,BANG_GUN if shooter==l else DRAW_GUN,BANG_GUN if shooter==r else DRAW_GUN,f'BANG!  {shooter} FIRES!',score)
def frame_result(lines,l,r,score=None,dialogue_lines=None):
    clear();title_block();scene(l,r,IDLE_GUN,IDLE_GUN,'RESULT',score)
    for x in lines:out(center(x))
    if dialogue_lines:
        out('-'*W)
        for x in dialogue_lines:out(center(x))
        out('-'*W)
def frame_match_end(lines,dialogue_lines=None):
    clear();out('='*W);out(center('M A T C H   C O M P L E T E'));out('='*W)
    for x in lines:out(center(x) if len(x)<W else x)
    if dialogue_lines:
        out('-'*W)
        for x in dialogue_lines:out(center(x))
        out('-'*W)
    out('');out(center('SPACE / ENTER = new match   |   R = restart   |   ESC / Q = quit'))
_NAMES=(None,None)
def set_names(l,r):
    global _NAMES;_NAMES=(l,r)
def fs_frame(culprit,score=None,dialogue_lines=None):
    clear();title_block();l,r=_NAMES;scene(l,r,BANG_GUN if culprit==l else IDLE_GUN,BANG_GUN if culprit==r else IDLE_GUN,f'FALSE START!  {culprit} DREW TOO EARLY!',score)
    if dialogue_lines:
        out('-'*W)
        for x in dialogue_lines:out(center(x))
        out('-'*W)