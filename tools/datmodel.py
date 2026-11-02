import re,struct,os
ED='/home/claude/g_EUD-Editor-3/EUD Editor 3/Data'
OFF={}
for l in open(ED+'/Offset.txt',encoding='utf-8-sig'):
    if '=' in l:
        k,v=l.strip().split('=',1); OFF[k]=int(v,16)
def parse_def(path):
    txt=open(path,encoding='utf-8',errors='replace').read()
    hdr=dict(re.findall(r'^(\w+)=(.*)$',txt.split('[FORMAT]')[0],re.M))
    fmt={}
    for k,v in re.findall(r'^(\d+\w+)=(.*)$',txt.split('[FORMAT]')[1],re.M):
        m=re.match(r'(\d+)(\w+)',k); fmt.setdefault(int(m.group(1)),{})[m.group(2)]=v.strip()
    return hdr,fmt
class Mem:
    def __init__(s): s.m={}
    def wb(s,a,b):
        for i,x in enumerate(b): s.m[a+i]=x
    def rb(s,a,n): return bytes(s.m.get(a+i,0) for i in range(n))
    def r(s,a,n): return int.from_bytes(s.rb(a,n),'little')
    def rd(s,a): return s.r(a,4)
    def wd(s,a,v): s.wb(a,(v&0xffffffff).to_bytes(4,'little'))
def load_defaults(mem):
    D=ED+'/DatFiles/'
    for name in ('units','weapons','flingy','sprites','images','upgrades','techdata','orders'):
        hdr,fmt=parse_def(D+name+'.def')
        data=open(D+name+'.dat','rb').read(); pos=0
        n=int(hdr.get('InputEntrycount',hdr.get('Entrycount','0')))
        for i in range(int(hdr['Varcount'])):
            f=fmt[i]; sz=int(f['Size']); vs=int(f.get('VarStart',0)); ve=int(f.get('VarEnd',n-1))
            cnt=ve-vs+1; key=name+'_'+f['Name'].split(':')[0]
            blob=data[pos:pos+sz*cnt]; pos+=sz*cnt
            if key in OFF: mem.wb(OFF[key]+sz*vs*0 if False else OFF[key], blob) if vs==0 else mem.wb(OFF[key],blob)
        assert pos==len(data),(name,pos,len(data))
    return mem
