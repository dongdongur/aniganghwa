import struct,sys
sys.path.insert(0,'/home/claude/tools')
def secs(d):
    i=0;r={}
    while i+8<=len(d):
        n=d[i:i+4];s=struct.unpack('<i',d[i+4:i+8])[0]
        if s<0 or i+8+s>len(d): break
        r[n]=(i+8,s); i+=8+s
    return r
class Chk:
    def __init__(s,path):
        d=open(path,'rb').read(); s.d=d; s.sec=secs(d)
        o,n=s.sec[b'STRx']; S=d[o:o+n]; s.S=S
        cnt=struct.unpack('<I',S[:4])[0]; s.offs=struct.unpack('<%dI'%cnt,S[4:4+4*cnt])
        o,n=s.sec[b'UNIx']; U=d[o:o+n]
        s.use=list(U[:228]); s.names=struct.unpack('<228H',U[3192:3192+456])
        o,n=s.sec[b'MRGN']; M=d[o:o+n]
        s.locs={}
        for i in range(n//20):
            l,t,r,b,st,fl=struct.unpack('<IIIIHH',M[20*i:20*i+20])
            s.locs[i+1]=(l,t,r,b,s.gs(st))
    def gs(s,i):
        if i==0 or i>len(s.offs): return ''
        o=s.offs[i-1]; e=s.S.index(b'\0',o); return s.S[o:e].decode('utf8','replace')
    def uname(s,u):
        return s.gs(s.names[u]) if (u<228 and not s.use[u]) else '(기본)'
