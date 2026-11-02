import pickle, sys, os
sys.path.insert(0,'/home/claude/tools'); sys.path.insert(0,'/home/claude/proj2/AniGanghwaWorld')
from emu import Emu, DEATHS, KILLS
from mapinfo import Chk
import config as C
class PL: pass
data, prt, ort, root, strx, forc = pickle.load(open('/home/claude/tools/emu_dump.pkl','rb'))
pl=PL(); pl.data,pl.prttable,pl.orttable=data,prt,ort
e=Emu(pl, root, strx, Chk('/home/claude/proj2/base_g.chk')); e.forces=list(forc[:8])
shown=0
def run(n):
    global shown
    for _ in range(n):
        e.run_frame()
    while shown < len(e.log):
        fr,cp,t=e.log[shown]; shown+=1
        if cp==0: print('[%5.1fs] %s'%(fr/16, t.replace('\n',' / ')[:200]))
run(40)
import collections
print('P12 units', sum(1 for u in e.units if u.owner==11), 'panels', [(u.owner,u.x,u.y) for u in e.units if u.type==179])
print('new hero hp', [e.rd(0x662350+4*u)//256 for u in (182,183,184,185)], 'gfx', [e.rbyte(0x6644F8+u) for u in (182,183,184,185,179)])
print('panel buttons', e.rd(0x5187E8+12*179), hex(e.rd(0x5187E8+12*179+4)))
# --- 자동강화
e.score[(0,7)] = 100000
f = C.FIELD[0]; x0,y0,x1,y1 = e.loc(f)
from emu import Unit
for k in range(3):
    e.units.append(Unit(9000+k, 65, 0, (x0+x1)//2, (y0+y1)//2, e.frame))
e.units.append(Unit(9100, 176, 0, 100, 100, e.frame))   # ON 버튼
e.units.append(Unit(9101, 177, 0, 100, 100, e.frame))   # ▲
run(60)
z=C.UPGRADE_ZONE
print('score', e.score[(0,7)], 'types now', collections.Counter(u.type for u in e.units if u.owner==0 and u.type in (65,107,115)))
