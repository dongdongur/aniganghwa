import emu, collections, atexit
PAGES=collections.Counter()
_orig=emu.Emu.wr
def wr(s,a,v):
    a&=0xFFFFFFFF
    if not (0x30000000<=a<0x32000000 or 0x191943C8<=a<0x19400000 or 0x58A364<=a<0x58A364+4*12*228):
        PAGES[a>>12]+=1
    return _orig(s,a,v)
emu.Emu.wr=wr
def dump():
    import pickle; pickle.dump(PAGES, open('/tmp/wpages_%d.pkl'%__import__('os').getpid(),'wb'))
atexit.register(dump)
