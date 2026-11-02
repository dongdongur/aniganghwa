# -*- coding: utf-8 -*-
# =====================================================================
#  원본 맵의 EUD 설정을 게임 시작 때 한 번 적용합니다.
#   1) datinit_data.WRITES : 유닛·무기·이미지 수치 6,094곳 (HP·공격력·가격 등)
#   2) eudfix_data.BUTTONSETS : 유닛별 버튼 146세트 (게이트웨이 소환권 등)
#      - 원본은 버튼 데이터를 맵 안에 넣고 주소로 연결함. 새 맵 안에 다시 담고 주소를 새로 연결.
#   3) eudfix_data.REQ_UNITS : 생산 요구조건 표 (드라군·다크 등 잠금 해제)
#   4) eudfix_data.TBL : 버튼 이름·툴팁 글자표 (stat_txt)
#   5) eudfix_data.EXTRA : 빠져 있던 1회성 값 (게임 속도 등)
# =====================================================================
from eudplib import *
from datinit_data import WRITES
import eudfix_data as F

_MOD = {7: SetTo, 8: Add, 9: Subtract}
BUTTONSET_TABLE = 0x5187E8
REQ_UNITS_ADDR = 0x514178
STAT_TXT_PTR = 0x6D5A30

_btn_db = {u: Db(data) for u, (cnt, data) in F.BUTTONSETS.items()}
_req = F.REQ_UNITS + b"\0" * (-len(F.REQ_UNITS) % 4)
def _patched_tbl():
    """원본 툴팁 글자표에 새 버튼 문구를 덮어씀 (영문 클라이언트에서 보임)"""
    import struct
    import config as C
    t = F.TBL
    n = struct.unpack_from("<H", t, 0)[0]
    offs = struct.unpack_from("<%dH" % n, t, 2)
    strs = [t[o:t.index(b"\0", o)] for o in offs]
    for idx, txt in zip(getattr(C, "AUTO_BTN_STR", []), getattr(C, "AUTO_BTN_TEXT", [])):
        strs[idx - 1] = txt.encode("cp949")
    head = 2 + 2 * n
    data = bytearray(); new_offs = []
    for s_ in strs:
        new_offs.append(head + len(data)); data += s_ + b"\0"
    assert head + len(data) < 65536, "툴팁 글자표가 너무 큽니다"
    return struct.pack("<H", n) + struct.pack("<%dH" % n, *new_offs) + bytes(data)


_TBL = _patched_tbl()
_tbl_db = Db(_TBL + b"\0" * (-len(_TBL) % 4))


def _actions():
    acts = [SetMemory(a, _MOD[m], v) for a, m, v in WRITES]
    for a, m, v, mask in F.EXTRA:
        if mask:
            acts.append(SetMemoryX(a, _MOD[m], v, mask))
        else:
            acts.append(SetMemory(a, _MOD[m], v))
    for u, (cnt, data) in sorted(F.BUTTONSETS.items()):
        base = BUTTONSET_TABLE + 12 * u
        acts.append(SetMemory(base, SetTo, cnt))
        acts.append(SetMemory(base + 4, SetTo, _btn_db[u]))
    for i in range(0, len(_req), 4):
        acts.append(SetMemory(REQ_UNITS_ADDR + i, SetTo, int.from_bytes(_req[i:i + 4], "little")))
    acts.append(SetMemory(STAT_TXT_PTR, SetTo, _tbl_db))
    return acts


def onPluginStart():
    acts = _actions()
    for i in range(0, len(acts), 64):
        DoActions(acts[i:i + 64])
