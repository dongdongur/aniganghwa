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
def run(n):
    global shown
    for _ in range(n): e.run_frame()
    while shown<len(e.log):
        fr,cp,t=e.log[shown]; shown+=1
        if cp==0 or 'P' in '': print('[%5.1fs] %s'%(fr/16,t.replace('\n',' / ')[:110]))
run(100)
cnt=lambda u: sum(1 for x in e.units if x.owner==0 and x.type==u)
chat('/극의징조 소환'); run(2); chat('/올포원 소환'); run(2)
print('95:',cnt(95),'89:',cnt(89))
chat('/포인트'); run(2); print('score', e.score.get((0,7)))
chat('/스킵'); run(3); chat('/스킵'); run(3); chat('/스킵'); run(40)
# 남이 친 척 (다른 이름)
k=idx[0]; wbytes(0x640B60+218*k, b'\x02someone: /\xea\xb7\xb9\xec\x9d\x98\xec\xa7\x95\xec\xa1\xb0\0'.ljust(218,b'\0')); idx[0]=(k+1)%11; e.mem[0x640B58]=idx[0]
run(3); print('95 after other:',cnt(95))
