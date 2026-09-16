import random,config
BLOON_PRE=["You ready?","I don't need a plan.","Let's get this over with.","Blink and you'll miss me.","My finger's itching."]
QWENY_PRE=["Probability favors me.","Take your time.","I've already calculated this.","Try not to disappoint me.","Variables are set."]
BLOON_WIN=["Too slow.","Told ya.","Speed wins.","Easy."]
QWENY_WIN=["As predicted.","The numbers were clear.","That was inevitable.","Calculated."]
BLOON_LOSE=["That was bullshit.","Again.","My gun jammed.","I demand a rematch."]
QWENY_LOSE=["Interesting.","Unexpected.","Recalculating.","Anomaly detected."]
FS_REACTIONS=["Nice reflex.","Too eager.","Whoa.","Nerves of glass."]
ANNOUNCER_INTRO=["Two artificial gunslingers enter the street.","One signal. One shot."]
ANNOUNCER_PRE_DRAW=["Ladies and gentlemen...","The algorithms are armed.","Please remain calm."]
ANNOUNCER_ROUND_WIN=["And that's another one for {winner}.","{winner} was faster by {diff} milliseconds.","The stopwatch has spoken."]
ANNOUNCER_FALSE_START=["Too early!","Nerves got the better of {culprit}.","A costly flinch."]
ANNOUNCER_MATCH_END=["Five rounds. Two machines. One winner.","The desert has its champion.","Apparently these machines have unresolved issues."]
def get_pre_duel():
    return (random.choice(BLOON_PRE),random.choice(QWENY_PRE)) if config.DIALOGUE else (None,None)
def get_post_duel(winner,loser):
    if not config.DIALOGUE:return None,None
    wp=BLOON_WIN if winner=='BLOON' else QWENY_WIN; lp=BLOON_LOSE if loser=='BLOON' else QWENY_LOSE
    return random.choice(wp),random.choice(lp)
def get_announcer_intro(): return random.choice(ANNOUNCER_INTRO) if config.ANNOUNCER else None
def get_announcer_pre_draw(): return random.choice(ANNOUNCER_PRE_DRAW) if config.ANNOUNCER else None
def get_announcer_round_win(winner,diff_ms): return random.choice(ANNOUNCER_ROUND_WIN).format(winner=winner,diff=int(diff_ms)) if config.ANNOUNCER else None
def get_announcer_false_start(culprit): return random.choice(ANNOUNCER_FALSE_START).format(culprit=culprit) if config.ANNOUNCER else None
def get_announcer_match_end(): return random.choice(ANNOUNCER_MATCH_END) if config.ANNOUNCER else None