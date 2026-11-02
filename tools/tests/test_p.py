import pickle, sys
sys.path.insert(0,'/home/claude/tools'); sys.path.insert(0,'/home/claude/proj2/AniGanghwaWorld')
from emu import Emu, Unit
from mapinfo import Chk
import config as C
class PL: pass
data, prt, ort, root, strx, forc = pickle.load(open('/home/claude/tools/emu_dump.pkl','rb'))
pl=PL(); pl.data,pl.prttable,pl.orttable=data,prt,ort
e=Emu(pl, root, strx, Chk('/home/claude/proj2/base_g.chk')); e.forces=list(forc[:8])
for _ in range(80): e.run_frame()
x0,y0,x1,y1=e.loc(C.FIELD[0])
h=Unit(5555,182,0,(x0+x1)//2,(y0+y1)//2,e.frame); e.units.append(h); e.run_frame()
n0=len(e.log)
h.order=152; h.tpos=(600<<16)|500
e.run_frame(); e.run_frame()
h.order=152
for fr,cp,t in e.log[n0:]: print('P%d'%(cp+1), t[:120])
print('hero dest after (patrol cancel => move order):', h.dest)
