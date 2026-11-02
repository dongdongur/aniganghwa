import pickle, sys
sys.path.insert(0,'/home/claude/tools'); sys.path.insert(0,'/home/claude/proj2/AniGanghwaWorld')
from emu import Emu, Unit
from mapinfo import Chk
import config as C
class PL: pass
data, prt, ort, root, strx, forc = pickle.load(open('/home/claude/tools/emu_dump.pkl','rb'))
pl=PL(); pl.data,pl.prttable,pl.orttable=data,prt,ort
e=Emu(pl, root, strx, Chk('/home/claude/proj2/base_g.chk')); e.forces=list(forc[:8])
for _ in range(20): e.run_frame()
n0=len(e.log)
for t in (89, 127, 182, 179):
    u=[x for x in e.units if x.type==t][0]
    e.mem[0x6284B8]=e.CU0+336*u.slot
    _orig=e.sync_in
    e.run_frame(); e.mem[0x6284B8]=e.CU0+336*u.slot; e.run_frame()
    for fr,cp,txt in e.log[n0:]:
        print('P%d'%(cp+1), txt.replace('\n',' / ')[:230])
    n0=len(e.log)
    e.mem[0x6284B8]=0; e.run_frame()
