import sys, os, struct, time, pickle
PROJ = os.environ.get('PROJ', '/home/claude/proj2/AniGanghwaWorld')
sys.path.insert(0, PROJ); sys.path.insert(0, '/home/claude/tools'); os.chdir(PROJ)
from eudplib import *
from eudplib import core as c
from eudplib.core.mapdata import mapdata
import eudplib.core.allocator.payload as P
from eudplib.maprw.injector.mainloop import main_starter
LoadMap('base/base_map.scx')
CompressPayload(True)
import datinit, game
mods = [datinit, game]
@EUDFunc
def main():
    for m in mods:
        if hasattr(m, 'onPluginStart'): m.onPluginStart()
    if EUDInfLoop()():
        for m in mods:
            if hasattr(m, 'beforeTriggerExec'): m.beforeTriggerExec()
        RunTrigTrigger()
        for m in reversed(mods):
            if hasattr(m, 'afterTriggerExec'): m.afterTriggerExec()
        EUDDoEvents()
    EUDEndInfLoop()
from eudplib.core.eudfunc.trace.tracetool import _reset_trace_map
_reset_trace_map()
jumper = main_starter(main)
mapdata.update_map_data()
payload = c.CreatePayload(jumper)
P.phase = P.PHASE_WRITING
r = c.Evaluate(jumper)
P.phase = 0
print('root', r.offset, r.rlocmode, 'payload', len(payload.data))
chkt = GetChkTokenized()
strx = chkt.getsection('STRx')
open('/home/claude/tools/emu_dump.pkl', 'wb').write(pickle.dumps((payload.data, payload.prttable, payload.orttable, r.offset, strx, chkt.getsection('FORC'))))
