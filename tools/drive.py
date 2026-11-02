import pickle, sys, time, os
sys.path.insert(0, '/home/claude/tools'); sys.path.insert(0, '/home/claude/proj2/AniGanghwaWorld')
from emu import Emu, Unit, DEATHS, KILLS
from mapinfo import Chk
class PL: pass
data, prt, ort, root, strx, forc = pickle.load(open('/home/claude/tools/emu_dump.pkl', 'rb'))
pl = PL(); pl.data, pl.prttable, pl.orttable = data, prt, ort
chk = Chk(os.environ.get('BASECHK', '/home/claude/proj2/base_g.chk'))
e = Emu(pl, root, strx, chk)
e.forces = list(forc[:8])
SECS = int(sys.argv[1]) if len(sys.argv) > 1 else 60
BOT = os.environ.get('BOT', '1') == '1'
import config as C
WAVES = {ch['wave'] for ch in C.CHAPTERS}
KD = int(os.environ.get('KD','10'))
t0 = time.time(); shown = 0
def kill(u, by=0):
    e.units.remove(u)
    e.wr(DEATHS + 4*u.owner + 48*u.type, e.rd(DEATHS + 4*u.owner + 48*u.type) + 1)
    e.wr(KILLS + 4*by + 48*u.type, e.rd(KILLS + 4*by + 48*u.type) + 1)
for f in range(SECS * 16):
    e.run_frame()
    if BOT and f == 20 and os.environ.get('DIFF'):
        x0,y0,x1,y1 = e.loc(int(os.environ['DIFF']))
        for u in e.units:
            if u.owner == 0 and u.type == 45:
                u.x, u.y = (x0+x1)//2, (y0+y1)//2
                break
    if BOT and f % 16 == 0:
        # 웨이브 처리: P8 유닛 중 오래된 것 처치 (방어 시뮬레이션)
        for u in [u for u in e.units if u.owner == 7 and u.type in WAVES and f - u.born > 16*8]:
            kill(u)
        # 보스: P6 유닛이 10초 살아있으면 처치
        for u in [u for u in e.units if u.owner == 5 and f - u.born > 16*KD and not u.inv]:
            kill(u)
    while shown < len(e.log):
        fr, cp, txt = e.log[shown]; shown += 1
        if cp == 0 or cp > 7:
            print('[%5.1fs P%d] %s' % (fr/16, cp+1, txt.replace('\n', ' / ')[:160]))
    if e.victory or e.defeat:
        break
print('frames', e.frame, 'steps/last', e.steps, 'time', round(time.time()-t0, 1), 'units', len(e.units))
print('unknown', e.events)
pickle.dump(e.units, open('/tmp/units.pkl','wb'))
