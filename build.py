import sys, os
PROJ='/home/claude/proj2/AniGanghwaWorld'
sys.path.insert(0, PROJ); os.chdir(PROJ)
from eudplib import *
LoadMap('base/base_map.scx')
CompressPayload(True)
import sounds, datinit, game
mods=[sounds, datinit, game]
@EUDFunc
def main():
    for m in mods:
        if hasattr(m,'onPluginStart'): m.onPluginStart()
    if EUDInfLoop()():
        for m in mods:
            if hasattr(m,'beforeTriggerExec'): m.beforeTriggerExec()
        RunTrigTrigger()
        for m in reversed(mods):
            if hasattr(m,'afterTriggerExec'): m.afterTriggerExec()
        EUDDoEvents()
    EUDEndInfLoop()
os.makedirs('out', exist_ok=True)
SaveMap(sys.argv[1] if len(sys.argv)>1 else 'out/AniGanghwaWorld_new.scx', main)
