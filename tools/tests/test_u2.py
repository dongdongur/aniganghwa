import pickle, sys
sys.path.insert(0,'/home/claude/tools'); sys.path.insert(0,'/home/claude/proj2/AniGanghwaWorld')
from emu import Emu, Unit
from mapinfo import Chk
import config as C
class PL: pass
data, prt, ort, root, strx, forc = pickle.load(open('/home/claude/tools/emu_dump.pkl','rb'))
pl=PL(); pl.data,pl.prttable,pl.orttable=data,prt,ort
e=Emu(pl, root, strx, Chk('/home/claude/proj2/base_g.chk')); e.forces=list(forc[:8])
def wbytes(a,b):
    for i,x in enumerate(b):
        k=(a+i)&~3; sh=8*((a+i)&3); e.mem[k]=(e.mem.get(k,0)&~(0xFF<<sh))|(x<<sh)
wbytes(0x57EEEB, b'sdgh17\0')
idx=[0]
def chat(msg):
    k=idx[0]; wbytes(0x640B60+218*k, (b'\x02sdgh17: \x04'+msg.encode('utf8')+b'\0').ljust(218,b'\0'))
    idx[0]=(k+1)%11; e.mem[0x640B58]=idx[0]
shown=0
def run(n, show=True):
    global shown
    for _ in range(n): e.run_frame()
    while shown<len(e.log):
        fr,cp,t=e.log[shown]; shown+=1
        if show: print('[%5.1fs] %s'%(fr/16,t.replace('\n',' / ')[:150]))
run(30, False)
print('183: hp',e.rd(0x662350+4*183)//256,'armor',e.rbyte(0x65FEC8+183),'wpn',e.rbyte(0x6636B8+183),
      'dmg',(e.rd(0x656EB0+2*106)>>16)&0xFFFF,'cd',e.rbyte(0x656FB8+107),'shield',(e.rd(0x660E00+2*182)>>16), 'shEn',e.rbyte(0x6647B0+183))
print('185 hp',e.rd(0x662350+4*185)//256,'wpn',e.rbyte(0x6636B8+185))
chat('/초월석'); run(2,False); chat('/포인트'); run(2,False); chat('/무의식'); run(2,False); chat('/메르엠'); run(2,False)
fx0,fy0,fx1,fy1=e.loc(C.FUSION_AREA)
for u in e.units:
    if u.owner==0 and u.type in (193,): u.x,u.y=(fx0+fx1)//2,(fy0+fy1)//2
run(4)
# 보스 대용: P6 에 유닛 165 를 놓고 HP 확인
boss=Unit(8888,25,5,2000,2000,e.frame); boss.hpr=5000000*256; e.units.append(boss)
g=[u for u in e.units if u.owner==0 and u.type==193][0]
g.order=152; g.tpos=(2000<<16)|2000
run(1); g.order=2
hp0=boss.hpr
last=boss.hpr
for k in range(130):
    run(1, False)
    if boss.hpr!=last: print('  k',k,'boss hp',boss.hpr//256); last=boss.hpr
    if boss not in e.units: print('boss gone', k); break
print('boss damage total', (hp0-boss.hpr)//256)
# 메르엠 자가회복
m=[u for u in e.units if u.owner==0 and u.type==185][0]
m.hpr=50000*256; run(48,False); print('meruem regen ->', m.hpr//256)
print([t[:60] for fr,cp,t in e.log if '궁 극' in t or '은빛' in t])
print('units owned P1 types', sorted({u.type for u in e.units if u.owner==0}))
