import pickle, sys
sys.path.insert(0,'/home/claude/tools'); sys.path.insert(0,'/home/claude/proj2/AniGanghwaWorld')
from emu import Emu, Unit, DEATHS
from mapinfo import Chk
import config as C
class PL: pass
data, prt, ort, root, strx, forc = pickle.load(open('/home/claude/tools/emu_dump.pkl','rb'))
pl=PL(); pl.data,pl.prttable,pl.orttable=data,prt,ort
e=Emu(pl, root, strx, Chk('/home/claude/proj2/base_g.chk')); e.forces=list(forc[:8])
WAVES={ch['wave'] for ch in C.CHAPTERS}; ROST={u for u,c in C.RUSH_ROSTER}
shown=0
def kill(u):
    e.units.remove(u); e.wr(DEATHS+4*u.owner+48*u.type, e.rd(DEATHS+4*u.owner+48*u.type)+1)
def show():
    global shown
    while shown<len(e.log):
        fr,cp,t=e.log[shown]; shown+=1
        if cp==0 and any(k in t for k in ('합 동','보스 러시','러시')): print('[%5.1fs] %s'%(fr/16,t.replace('\n',' / ')[:130]))
# --- 합동기
for _ in range(40): e.run_frame()
x0,y0,x1,y1=e.loc(42); cx,cy=(x0+x1)//2,(y0+y1)//2
b=Unit(9001,210,5,cx,cy,e.frame); e.units.append(b)
e.units.append(Unit(9002,126,0,cx+40,cy,e.frame)); e.units.append(Unit(9003,168,1,cx-40,cy,e.frame))
e.run_frame(); hp0=b.hpr
for _ in range(80): e.run_frame()
show(); print('combo damage', (hp0-b.hpr)//256 if b in e.units else 'dead')
e.units=[u for u in e.units if u.uid not in (9001,9002,9003)]
# --- 보스 러시 : 3장까지 진행
hero=None
for f in range(16*400):
    e.run_frame()
    if f%16==0:
        for u in list(e.units):
            if u.owner==7 and u.type in WAVES and f-u.born>16*8: kill(u)
            elif u.owner==5 and f-u.born>16*4 and not u.inv: kill(u)
            elif u.owner==7 and u.type in ROST and f-u.born>16*3: kill(u)
    show()
    if hero is None and any('보스 러시 개방' in t for _,_,t in e.log):
        x0,y0,x1,y1=e.loc(C.RUSH_PAD[0]); hero=Unit(4243, 89, 0, (x0+x1)//2,(y0+y1)//2, e.frame); e.units.append(hero)
        print('rush signs', [(u.owner,u.x,u.y) for u in e.units if u.type==C.RUSH_SIGN_UNIT])
    if f>16*200 and hero is not None and not e.inloc(hero, C.INF_ROOM) and any('도전 종료' in t or '모두 쓰러' in t for _,_,t in e.log): break
print('score', e.score.get((0,7)))
