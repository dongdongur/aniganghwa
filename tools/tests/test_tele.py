import pickle, sys, os
sys.path.insert(0,'/home/claude/tools'); sys.path.insert(0,'/home/claude/proj2/AniGanghwaWorld')
from emu import Emu, Unit, DEATHS, KILLS
from mapinfo import Chk
import config as C
class PL: pass
data, prt, ort, root, strx, forc = pickle.load(open('/home/claude/tools/emu_dump.pkl','rb'))
pl=PL(); pl.data,pl.prttable,pl.orttable=data,prt,ort
e=Emu(pl, root, strx, Chk('/home/claude/proj2/base_g.chk')); e.forces=list(forc[:8])
WAVES={ch['wave'] for ch in C.CHAPTERS}
EV={st['unit'] for st in C.INF_STAGES}
shown=0; opened=False; hero=None
def kill(u):
    e.units.remove(u); e.wr(DEATHS+4*u.owner+48*u.type, e.rd(DEATHS+4*u.owner+48*u.type)+1)
for f in range(16*700):
    if f==20:
        x0,y0,x1,y1=e.loc(31)
        for u in e.units:
            if u.owner==0 and u.type==45: u.x,u.y=(x0+x1)//2,(y0+y1)//2; break
    e.run_frame()
    if f%16==0:
        for u in list(e.units):
            if u.owner==7 and u.type in WAVES and f-u.born>16*8: kill(u)
            elif u.owner==5 and f-u.born>16*4 and not u.inv: kill(u)
            elif u.owner==7 and u.type in EV and f-u.born>16*25: kill(u)
    while shown<len(e.log):
        fr,cp,t=e.log[shown]; shown+=1
        if cp in (0,) and ('경 고' in t or '무한성' in t or '무 한 성' in t or '상현' in t or '무잔' in t or '각성' in t or 'DEFEAT' in t):
            print('[%5.1fs] %s'%(fr/16,t.replace('\n',' / ')[:140]))
        if '무 한 성' in t: opened=True
    if opened and hero is None:
        x0,y0,x1,y1=e.loc(C.INF_PAD[0]); hero=Unit(4242, 89, 0, (x0+x1)//2,(y0+y1)//2, e.frame); e.units.append(hero)
        print('signs', [(u.owner,u.x,u.y) for u in e.units if u.type==C.INF_SIGN_UNIT])
    if hero is not None and hero not in e.units and f%160==0: pass
    if hero is not None and f%8==0 and hero in e.units:
        hp=getattr(hero,'hp',None)
        if hp!=globals().get('lasthp'):
            print('   hero hp', hp, 'f',f); globals()['lasthp']=hp
    if hero is not None and os.environ.get('DODGE') and shown and '경 고' in e.log[shown-1][2] and e.log[shown-1][0]==e.frame:
        hero.x+=300; print('   dodge')
    if e.victory or e.defeat: break
print('hero in room?', hero and e.inloc(hero, C.INF_ROOM))
