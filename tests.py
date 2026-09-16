import config,time
from ai import Gunslinger

def run_tests():
    assert config.DRAW_DELAY_MIN < config.DRAW_DELAY_MAX
    assert config.WINS_TO_TAKE_MATCH == 3
    for cfg in (config.BLOON,config.QWENY):
        g=Gunslinger(cfg); r=g.generate_reaction(); lo,hi=cfg['rt_clamp']; assert lo<=r<=hi
    t=time.perf_counter(); time.sleep(0.001); assert time.perf_counter()>=t
    print('BOSSMEN WENBIGO v0.2 tests: PASS')

if __name__=='__main__': run_tests()
