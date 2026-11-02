import pickle, sys, os, re
sys.path.insert(0,'/home/claude/tools'); sys.path.insert(0,'/home/claude/proj2/AniGanghwaWorld')
from emu import Emu, Unit, DEATHS, KILLS
from mapinfo import Chk
import config as C
class PL: pass
data, prt, ort, root, strx, forc = pickle.load(open('/home/claude/tools/emu_dump.pkl','rb'))
pl=PL(); pl.data,pl.prttable,pl.orttable=data,prt,ort
e=Emu(pl, root, strx, Chk('/home/claude/proj2/base_g.chk')); e.forces=list(forc[:8])
def dmg(u, d):
    d=d*256
    if u.shr >= d: u.shr -= d; return
    d -= u.shr; u.shr = 0; u.hpr -= d
    if u.hpr <= 0:
        e.units.remove(u); return 'dead'
for _ in range(60): e.run_frame()
# --- 타수형 영웅
x0,y0,x1,y1=e.loc(C.FIELD[0])
h=Unit(7777, 89, 0, (x0+x1)//2, (y0+y1)//2, e.frame); e.units.append(h)
e.run_frame()
print('89 start hp', h.hpr/256, 'shield', h.shr/256)
hits=0
while h in e.units and hits < 400:
    r=dmg(h, 30000); hits+=1
    if r=='dead': break
    e.run_frame()
print('89 died after hits', hits)
# 스바루(타수형) 쉴드 65535 넘는 한방
h2=Unit(7778, 96, 0, (x0+x1)//2, (y0+y1)//2, e.frame); e.units.append(h2); e.run_frame()
print('96 hp', h2.hpr/256, 'sh', h2.shr/256)
# --- 타수 보스: 6-3 스테이지 강제 진입
# --- 타수 보스 : 보스는 10초 뒤 처치(일반), 146/145 는 큰 데미지로 때림
def line(k):
    a=0x640B60+218*k; b=bytes(e.rbyte(a+i) for i in range(200)); return b.split(b'\0')[0].decode('utf8','replace')
shown=len(e.log); f=0; hitboss_seen=False; t_first=None
while f < 16*1400:
    e.run_frame(); f+=1
    for u in list(e.units):
        if u.owner==7 and u.type in (140,141,142,136,137,134,175) and e.frame-u.born>16*6: e.units.remove(u)
        elif u.owner==5 and u.type in (146,145) and u.hpr is not None:
            if t_first is None: t_first=e.frame
            if dmg(u, 500000)=='dead': print('!!! 타수보스가 데미지로 죽음', u.type, e.frame)
        elif u.owner==5 and e.frame-u.born>16*3 and not u.inv:
            e.units.remove(u); e.wr(DEATHS+4*5+48*u.type, e.rd(DEATHS+4*5+48*u.type)+1)
    while shown < len(e.log):
        fr,cp,t=e.log[shown]; shown+=1
        if cp==0 and ('마인부우' in t or '블랙' in t or 'Clear' in t or 'Defeat' in t or 'DEFEAT' in t or '자마스' in t):
            print('[%5.1fs] %s'%(fr/16, t.replace('\n',' / ')[:120]))
    if t_first and (e.frame-t_first) % 16 == 0 and e.frame-t_first < 400:
        print('   HUD:', line(C.HIT_HUD_LINE)[:80], [ (u.type,u.hpr//256) for u in e.units if u.owner==5 and u.type in (146,145)])
    if e.victory or e.defeat: break
