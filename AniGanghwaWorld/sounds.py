# -*- coding: utf-8 -*-
# 사운드/BGM 넣기
# sound 폴더 안의 파일을 원래 맵과 같은 경로로 맵(MPQ)에 넣어 줍니다.
#   sound/M0_0.ogg                -> M0_0.ogg
#   sound/staredit/wav/1F.wav     -> staredit\wav\1F.wav
# 새 사운드를 추가하려면 sound 폴더에 파일만 넣으면 됩니다.

import os
from eudplib import MPQAddFile

SOUND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sound")


def onPluginStart():
    count = 0
    for root, _dirs, files in os.walk(SOUND_DIR):
        for fn in sorted(files):
            if not fn.lower().endswith((".wav", ".ogg")):
                continue
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, SOUND_DIR)
            mpq_name = rel.replace("/", "\\")
            with open(full, "rb") as f:
                MPQAddFile(mpq_name, f.read())
            count += 1
    print("[sounds] %d개 사운드 파일 추가" % count)
