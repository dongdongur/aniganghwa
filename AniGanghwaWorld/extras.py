# -*- coding: utf-8 -*-
# =====================================================================
#  애니강화월드 - 추가 기능
#   1) 새 9★/10★ 영웅 (빈 유닛 칸에 기존 영웅 능력치·모습 복사)
#   2) 조합 도감 (중립 유닛 클릭 -> 조합법·공격형태·성능·스킬 설명)
#   3) 자동강화 패널 (게이트웨이 아래 건물 버튼 : ON/OFF, 목표 ▲▼)
#   4) 궁극기 각성 (9★/10★ 을 퓨전 띠에 올려 P 스킬 해금)
#   5) 타수형 영웅 초기 설정
# =====================================================================
import struct
from eudplib import *

import config as C
import systems as S
from gallery_data import GALLERY_TEXT

HUM = C.HUMANS

# units.dat 필드 (주소, 한 유닛 크기). 이름 문자열·요구조건 번호·부분 배열은 제외
UNIT_FIELDS = [
    (0x6644F8, 1), (0x6607C0, 2), (0x660C38, 2), (0x6610B0, 4), (0x6605F0, 1), (0x6647B0, 1),
    (0x660E00, 2), (0x662350, 4), (0x663150, 1), (0x660FC8, 1), (0x663DD0, 1), (0x662EA0, 1),
    (0x662268, 1), (0x664898, 1), (0x663320, 1), (0x663A50, 1), (0x6636B8, 1), (0x6645E0, 1),
    (0x6616E0, 1), (0x65FC18, 1), (0x660178, 1), (0x664080, 4), (0x662DB8, 1), (0x663238, 1),
    (0x6635D0, 1), (0x662180, 1), (0x65FEC8, 1), (0x662098, 1), (0x65FFB0, 2), (0x662BF0, 2),
    (0x662860, 4), (0x6617C8, 8), (0x662F88, 2), (0x663888, 2), (0x65FD00, 2), (0x660428, 2),
    (0x6637A0, 1), (0x6646C8, 1), (0x663CE8, 1), (0x664410, 1), (0x660988, 1), (0x663408, 2),
    (0x663EB8, 2), (0x6606D8, 1), (0x661518, 2),
]
LOOK_FIELDS = [(0x6644F8, 1), (0x662F88, 2), (0x6617C8, 8), (0x662860, 4), (0x65FFB0, 2), (0x662BF0, 2)]


WEAPON_FIELDS = [(0x6572E0, 2), (0x656CA8, 4), (0x6573E8, 1), (0x657998, 2), (0x656A18, 4), (0x657470, 4),
                 (0x6571D0, 1), (0x657258, 1), (0x656670, 1), (0x657040, 1), (0x6566F8, 1), (0x656888, 2),
                 (0x6570C8, 2), (0x657780, 2), (0x656EB0, 2), (0x657678, 2), (0x656FB8, 1), (0x6564E0, 1),
                 (0x656990, 1), (0x657888, 1), (0x657910, 1), (0x656C20, 1), (0x656568, 2), (0x656780, 2)]


def _copy_weapon(dst, src_var):
    for addr, sz in WEAPON_FIELDS:
        if sz == 1:
            f_bwrite(addr + dst, f_bread(addr + src_var))
        elif sz == 2:
            f_wwrite(addr + 2 * dst, f_wread(addr + 2 * src_var))
        else:
            f_dwwrite(addr + 4 * dst, f_dwread(addr + 4 * src_var))


FLINGY_FIELDS = [(0x6C9EF8, 4), (0x6C9C78, 2), (0x6C9930, 4), (0x6C9E20, 1), (0x6CA240, 1), (0x6C9858, 1)]
IMAGE_FIELDS = [(0x668AA0, 4), (0x66E860, 1), (0x66C150, 1), (0x66D4D8, 1), (0x667718, 1), (0x669E28, 1),
                (0x669A40, 1), (0x66EC48, 4), (0x66C538, 4), (0x66B1B0, 4), (0x66A210, 4), (0x667B00, 4),
                (0x666778, 4), (0x66D8C0, 4)]


def _make_look(lk):
    """빈 flingy/sprite/image 칸에 다른 모습의 그림을 복사하고 색 효과를 입힘 (빌드 때 칸 번호 계산)"""
    ff, tf = lk["from_flingy"], lk["slot_flingy"]
    fs = f_wread(0x6CA318 + 2 * ff)               # 원래 그림묶음
    ts = f_wread(0x6CA318 + 2 * tf)               # 새 칸의 그림묶음 (그대로 둠)
    fi = f_wread(0x666160 + 2 * fs)
    ti = f_wread(0x666160 + 2 * ts)
    mf = f_bread(0x6644F8 + lk["unit"])            # 이동 속도는 지금 모습(look_from) 것을 그대로 유지
    for addr, sz in FLINGY_FIELDS:                 # 이동 정보
        if sz == 1:
            f_bwrite(addr + tf, f_bread(addr + mf))
        elif sz == 2:
            f_wwrite(addr + 2 * tf, f_wread(addr + 2 * mf))
        else:
            f_dwwrite(addr + 4 * tf, f_dwread(addr + 4 * mf))
    f_bwrite(0x666570 + ts, f_bread(0x666570 + fs))          # 그림묶음 정보
    f_bwrite(0x665C48 + ts, f_bread(0x665C48 + fs))
    for addr in (0x665E50, 0x665AC0, 0x665FD8):              # 체력바·선택원 (130번부터 있는 칸)
        f_bwrite(addr + ts - 130, f_bread(addr + fs - 130))
    for addr, sz in IMAGE_FIELDS:                            # 그림
        if sz == 1:
            f_bwrite(addr + ti, f_bread(addr + fi))
        else:
            f_dwwrite(addr + 4 * ti, f_dwread(addr + 4 * fi))
    f_bwrite(0x669E28 + ti, lk["draw"])
    f_bwrite(0x669A40 + ti, lk["remap"])
    f_bwrite(0x6644F8 + lk["unit"], tf)


def _copy(fields, dst, src):
    for addr, sz in fields:
        if sz == 1:
            f_bwrite(addr + dst, f_bread(addr + src))
        elif sz == 2:
            f_wwrite(addr + 2 * dst, f_wread(addr + 2 * src))
        elif sz == 4:
            f_dwwrite(addr + 4 * dst, f_dwread(addr + 4 * src))
        else:
            f_dwwrite(addr + 8 * dst, f_dwread(addr + 8 * src))
            f_dwwrite(addr + 8 * dst + 4, f_dwread(addr + 8 * src + 4))


def _setb(addr, v):
    return SetMemoryX(addr & ~3, SetTo, v << (8 * (addr & 3)), 0xFF << (8 * (addr & 3)))


def _setw(addr, v):
    return SetMemoryX(addr & ~3, SetTo, v << (8 * (addr & 3)), 0xFFFF << (8 * (addr & 3)))


# ---------------------------------------------------------------------
#  자동강화 패널 버튼 (원본 게이트웨이 버튼과 같은 조건/동작 함수 사용)
# ---------------------------------------------------------------------
COND_CAN_BUILD, ACT_TRAIN = 0x428E60, 0x4234B0
_panel_btns = Db(b"".join(
    struct.pack("<HHIIHHHH", k + 1, C.AUTO_BTN_ICON[k], COND_CAN_BUILD, ACT_TRAIN,
                C.U_AUTO_BTN[k], C.U_AUTO_BTN[k], C.AUTO_BTN_STR[k], C.AUTO_BTN_STR[k])
    for k in range(3)))


# ---------------------------------------------------------------------
#  맵 정보 (빌드할 때 base 맵에서 읽음)
# ---------------------------------------------------------------------
def _map_info():
    chkt = GetChkTokenized()
    mr = chkt.getsection("MRGN")
    gl, gt, gr, gb = struct.unpack_from("<IIII", mr, (C.GALLERY_LOC - 1) * 20)
    import os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools_dev"))
    from add_gallery import gallery_positions
    gal = gallery_positions(gl, gt, gr, gb)
    un = chkt.getsection("UNIT")
    gates = {}
    for i in range(len(un) // 36):
        x, y, t = struct.unpack_from("<HHH", un, i * 36 + 4)
        owner = un[i * 36 + 16]
        if t == 160 and owner in HUM:
            gates[owner] = (x, y)
    return gal, gates


GALLERY_POS, GATES = _map_info()
TEMP = C.TEMP_LOC
_TL = 0x58DC60 + 20 * (TEMP - 1)


def _create_at(n, unit, owner, x, y):
    return [SetMemory(_TL, SetTo, x - 16), SetMemory(_TL + 4, SetTo, y - 16),
            SetMemory(_TL + 8, SetTo, x + 16), SetMemory(_TL + 12, SetTo, y + 16),
            CreateUnit(n, unit, TEMP, owner)]


# ---------------------------------------------------------------------
#  게임 시작 때 한 번
# ---------------------------------------------------------------------
def init_units():
    # 1) 새 9★/10★
    for h in C.NEW_HEROES:
        u = h["unit"]
        _copy(UNIT_FIELDS, u, h["stat_from"])
        _copy(LOOK_FIELDS, u, h["look_from"])
        acts = []
        if "hp" in h:
            acts.append(SetMemory(0x662350 + 4 * u, SetTo, h["hp"] * 256))
        if "armor" in h:
            acts.append(_setb(0x65FEC8 + u, h["armor"]))
        if "gfx" in h:                             # 그림만 다른 모습으로 (유닛 정보 칸만 바꿈 -> 안전)
            acts.append(_setb(0x6644F8 + u, h["gfx"]))
        DoActions(acts) if acts else None
        if "weapon" in h:                          # 전용 무기 (원래 무기를 복사한 뒤 수치 변경)
            w = h["weapon"]
            _copy_weapon(w["id"], f_bread(0x6636B8 + h["stat_from"]))
            DoActions([_setb(0x6636B8 + u, w["id"]), _setb(0x6616E0 + u, w["id"]),
                       _setw(0x656EB0 + 2 * w["id"], w["dmg"]), _setw(0x657678 + 2 * w["id"], w["bonus"]),
                       _setb(0x6564E0 + w["id"], w["factor"]), _setb(0x656FB8 + w["id"], w["cooldown"])])
    # 1-2) 새 모습 (색 입힌 그림)
    for lk in getattr(C, "NEW_LOOKS", []):
        _make_look(lk)
    # 2) 자동강화 패널 = 게이트웨이 복사 + 템플러 아카이브 모습, 버튼 3개
    _copy(UNIT_FIELDS, C.U_AUTO_PANEL, 160)
    P_ = C.U_AUTO_PANEL
    acts = [_setb(0x6644F8 + P_, 60),                                    # 포톤 캐논 모양 (2x2칸, 소환소 방에 들어감)
            SetMemory(0x662860 + 4 * P_, SetTo, 64 | (64 << 16)),        # 배치 크기 64x64
            SetMemory(0x6617C8 + 8 * P_, SetTo, 32 | (32 << 16)),        # 유닛 크기 (왼쪽, 위)
            SetMemory(0x6617C8 + 8 * P_ + 4, SetTo, 31 | (31 << 16)),    # 유닛 크기 (오른쪽, 아래)
            SetMemory(0x5187E8 + 12 * C.U_AUTO_PANEL, SetTo, 3),
            SetMemory(0x5187E8 + 12 * C.U_AUTO_PANEL + 4, SetTo, _panel_btns)]
    # 3) 버튼 표시 유닛 = 공짜·즉시 생산
    for u in C.U_AUTO_BTN:
        _copy(UNIT_FIELDS, u, 65)
        acts += [_setw(0x663888 + 2 * u, 0), _setw(0x65FD00 + 2 * u, 0), _setw(0x660428 + 2 * u, 1),
                 _setb(0x663CE8 + u, 0), _setw(0x660A70 + 2 * u, 0), _setb(0x6637A0 + u, 0x04)]
    # 4) 타수형 영웅 : 쉴드 65535 (맞았는지 감지용)
    for u in C.HIT_HEROES:
        acts += [_setb(0x6647B0 + u, 1), _setw(0x660E00 + 2 * u, 65535)]
    DoActions(acts)
    # 5) 도감 유닛·패널 만들기 (수치를 바꾼 뒤라 모습이 맞게 나옴)
    acts = []
    for u, x, y in GALLERY_POS:
        acts += _create_at(1, u, C.GALLERY_OWNER, x, y)
    acts.append(SetInvincibility(Enable, "Any unit", C.GALLERY_OWNER, C.GALLERY_LOC))
    for p, (x, y) in GATES.items():
        acts += _create_at(1, C.U_AUTO_PANEL, p, x, y + C.AUTO_PANEL_DY)
        acts.append(SetInvincibility(Enable, C.U_AUTO_PANEL, p, C.ANYWHERE))
    DoActions(acts)


# ---------------------------------------------------------------------
#  자동강화
# ---------------------------------------------------------------------
auto_on = [EUDVariable(0) for _ in HUM]
auto_tg = [EUDVariable(C.AUTO_DEFAULT_TARGET) for _ in HUM]


def auto_upgrade(tick):
    for i, p in enumerate(HUM):
        b_on, b_up, b_dn = C.U_AUTO_BTN
        if EUDIf()(Command(p, AtLeast, 1, b_on)):
            DoActions(RemoveUnit(b_on, p))
            if EUDIf()(auto_on[i] == 0):
                auto_on[i] << 1
                S._println(p, "\x1f【자동강화】 \x07ON \x05(목표 {}★)", auto_tg[i])
            if EUDElse()():
                auto_on[i] << 0
                S._println(p, "\x1f【자동강화】 \x08OFF")
            EUDEndIf()
        EUDEndIf()
        if EUDIf()(Command(p, AtLeast, 1, b_up)):
            DoActions(RemoveUnit(b_up, p))
            if EUDIf()(auto_tg[i] <= 6):
                auto_tg[i] += 1
            EUDEndIf()
            S._println(p, "\x1f【자동강화】 \x04목표 \x07{}★", auto_tg[i])
        EUDEndIf()
        if EUDIf()(Command(p, AtLeast, 1, b_dn)):
            DoActions(RemoveUnit(b_dn, p))
            if EUDIf()(auto_tg[i] >= 3):
                auto_tg[i] -= 1
            EUDEndIf()
            S._println(p, "\x1f【자동강화】 \x04목표 \x07{}★", auto_tg[i])
        EUDEndIf()
        # 0.5초마다 1마리씩 강화존으로 (강화존이 비어 있고 강화포인트가 있을 때)
        if EUDIf()([auto_on[i] == 1, tick % 12 == 3 * i, Bring(p, Exactly, 0, "Men", C.UPGRADE_ZONE)]):
            moved = EUDVariable()
            moved << 0
            for t in range(6):
                for line in C.NORMAL_LINES.values():
                    if EUDIf()([moved == 0, auto_tg[i] >= t + 2, Bring(p, AtLeast, 1, line[t], C.FIELD[i]),
                                Score(p, Custom, AtLeast, C.GANG_COST[t])]):
                        DoActions(MoveUnit(1, line[t], p, C.FIELD[i], C.UPGRADE_ZONE))
                        moved << 1
                    EUDEndIf()
        EUDEndIf()
        # 내 화면 왼쪽 글줄에 상태
        if EUDIf()([tick % 24 == 5, f_getuserplayerid() == p]):
            if EUDIf()(auto_on[i] == 1):
                f_printAt(C.AUTO_HUD_LINE, "\x1f【자동강화】 \x07ON \x04▶ 목표 \x07{}★ \x05(게이트 아래 패널: 1 ON/OFF · 2 ▲ · 3 ▼)", auto_tg[i])
            if EUDElse()():
                f_printAt(C.AUTO_HUD_LINE, "\x1f【자동강화】 \x08OFF \x04▶ 목표 {}★ \x05(게이트 아래 패널: 1 ON/OFF · 2 ▲ · 3 ▼)", auto_tg[i])
            EUDEndIf()
        EUDEndIf()


# ---------------------------------------------------------------------
#  조합 도감 / 패널 안내 : 내가 선택한 유닛을 보고 내 화면에만 설명
# ---------------------------------------------------------------------
sel_prev = EUDVariable(0)


def gallery():
    ptr = f_dwread(0x6284B8)                       # 내가 선택한 첫 유닛
    if EUDIf()([ptr >= 0x59CCA8, ptr <= 0x59CCA8 + 336 * 1699]):
        ut = f_wread(ptr + 0x64)
        owner = f_bread(ptr + 0x4C)
        if EUDIfNot()(ut == sel_prev):
            sel_prev << ut
            oldcp = f_getcurpl()
            f_setcurpl(f_getuserplayerid())
            if EUDIf()(owner == C.GALLERY_OWNER):
                EUDSwitch(ut)
                for u, txt in GALLERY_TEXT.items():
                    if EUDSwitchCase()(u):
                        DoActions(DisplayText(txt))
                        EUDBreak()
                EUDEndSwitch()
            EUDEndIf()
            if EUDIf()(ut == C.U_AUTO_PANEL):
                DoActions(DisplayText(
                    "\x13\x1f【 자동강화 패널 】\n\x13\x04버튼 1 : 자동강화 ON/OFF   버튼 2 : 목표 ★ 올리기   버튼 3 : 목표 ★ 내리기\n"
                    "\x13\x05ON 이면 필드의 일반 영웅을 목표 ★ 까지 0.5초마다 1마리씩 강화존으로 보냅니다 (강화포인트가 있을 때만)"))
            EUDEndIf()
            f_setcurpl(oldcp)
        EUDEndIf()
    if EUDElse()():
        sel_prev << 0
    EUDEndIf()


# ---------------------------------------------------------------------
#  궁극기 각성 (퓨전 띠에 9★/10★ 을 올리면)
# ---------------------------------------------------------------------
ult_learn = {(i, h): EUDVariable(0) for i in range(len(HUM)) for h in C.ULT2_SKILLS}


def ult_awaken():
    pt, st = C.ULT_AWAKEN_COST
    for i, p in enumerate(HUM):
        for h in C.ULT2_SKILLS:
            lv = ult_learn[(i, h)]
            if EUDIf()([lv == 0, Bring(p, AtLeast, 1, h, C.FUSION_AREA), inf_clear[i] == 0]):
                DoActions(MoveUnit(All, h, p, C.FUSION_AREA, C.ZONE[i]))
                S._println(p, "\x08[각성 궁극기] \x04무한성 레이드를 먼저 클리어해야 배울 수 있습니다.")
            EUDEndIf()
            if EUDIf()([lv == 0, Bring(p, AtLeast, 1, h, C.FUSION_AREA), inf_clear[i] == 1, Score(p, Custom, AtLeast, pt), S.stone[i] >= st]):
                DoActions([SetScore(p, Subtract, pt, Custom), MoveUnit(All, h, p, C.FUSION_AREA, C.ZONE[i])])
                S.stone[i] -= st
                lv << 1
                f_setcurpl(p)
                DoActions(DisplayText("\x13\x1f━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\x13\x1f【 궁극기 각성 】 \x04%s\n"
                                      "\x13\x04이제 \x07P(패트롤) \x04+ 원하는 곳 클릭으로 각성 궁극기를 쓸 수 있습니다!\n"
                                      "\x13\x1f━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" % C.ULT2_SKILLS[h]["name"]))
            EUDEndIf()



# ---------------------------------------------------------------------
#  보스 패턴 피하기 : 표식 -> TELE_WARN 틱 뒤 폭발 (game.py 보스 + 무한성 공용)
# ---------------------------------------------------------------------
tele_t = EUDVariable(0)       # 0 = 대기, 1~ = 경고 진행 틱
tele_cut = EUDVariable(50)
tele_pick = EUDVariable(0)
TELE_CUTS = sorted(set([r for _, r in C.INF_TELE] + [50, 30]))


def tele_start(room, cut):
    """room 안의 우리 영웅 1명을 골라 표식 시작 (이미 진행 중이면 무시)."""
    global tele_pick, tele_t
    if EUDIf()(tele_t == 0):
        found = EUDVariable()
        found << 0
        for idx, p in enumerate(HUM):
            if EUDIf()([found == 0, tele_pick == idx, Bring(p, AtLeast, 1, "Men", room)]):
                DoActions(MoveLocation(C.TELE_LOC, "Men", p, room))
                found << 1
            EUDEndIf()
        for p in HUM:
            if EUDIf()([found == 0, Bring(p, AtLeast, 1, "Men", room)]):
                DoActions(MoveLocation(C.TELE_LOC, "Men", p, room))
                found << 1
            EUDEndIf()
        tele_pick += 1
        if EUDIf()(tele_pick >= len(HUM)):
            tele_pick << 0
        EUDEndIf()
        if EUDIf()(found == 1):
            tele_t << 1
            tele_cut << cut
            DoActions([CreateUnit(1, C.TELE_MARK, C.TELE_LOC, C.BOSS_OWNER),
                       MinimapPing(C.TELE_LOC), DisplayTextAll(C.TELE_TEXT)])
        EUDEndIf()
    EUDEndIf()


def tele_tick():
    global tele_t
    if EUDIfNot()(tele_t == 0):
        tele_t += 1
        if EUDIf()(tele_t == C.TELE_WARN // 2):
            DoActions([CreateUnit(1, C.TELE_MARK, C.TELE_LOC, C.BOSS_OWNER), MinimapPing(C.TELE_LOC)])
        EUDEndIf()
        if EUDIf()(tele_t >= C.TELE_WARN):
            tele_t << 0
            acts = []
            for fx in C.TELE_BOOM:
                acts += [CreateUnit(1, fx, C.TELE_LOC, C.BOSS_OWNER), KillUnitAt(All, fx, C.TELE_LOC, C.BOSS_OWNER)]
            DoActions(acts)
            for cut in TELE_CUTS:
                if EUDIf()(tele_cut == cut):
                    DoActions([ModifyUnitHitPoints(All, "Men", q, C.TELE_LOC, cut) for q in HUM])
                EUDEndIf()
        EUDEndIf()
    EUDEndIf()


def frame(tick):
    if EUDIf()(tick == 1):
        init_units()
    EUDEndIf()
    auto_upgrade(tick)
    gallery()
    ult_awaken()
    cheats(tick)
    infinity(tick)
    combos()
    boss_rush(tick)
    goal_hud(tick)
    tele_tick()


# ---------------------------------------------------------------------
#  테스트용 채팅 명령어 (config.CHEAT_ID 만)
#   채팅 줄(0x640B60, 11줄)에서 새로 생긴 줄만 읽어 "아이디:" 로 시작하면 명령 확인
# ---------------------------------------------------------------------
skip_req = EUDVariable(0)           # game.py 가 보고 현재 스테이지를 클리어 처리
cheat_p = EUDVariable(99)
chat_prev = EUDVariable(0)
_ID = C.CHEAT_ID.encode("utf-8")
_id_db = Db(_ID + b"\0")
_idc_db = Db(_ID + b":\0")


def _cmd_db(t):
    return Db(t.encode("utf-8") + b"\0")


_CMDS = [("/스킵", "skip"), ("/포인트", "point"), ("/초월석", "stone"), ("/자원", "res"), ("/명령어", "help")]
_cmd_dbs = [(_cmd_db(t), k) for t, k in _CMDS]
_spawn_dbs = [(_cmd_db(t), u) for t, u in C.CHEAT_SPAWN]
HELP = ("\x13\x1f[테스트 명령어] \x04/스킵  /포인트  /초월석  /자원  /명령어\n\x13\x04소환: " +
        "  ".join(t for t, _ in C.CHEAT_SPAWN))


def _do(kind, p, i):
    if kind == "skip":
        skip_req << 1
        DoActions(DisplayTextAll("\x13\x08[테스트] 스테이지 스킵"))
    elif kind == "point":
        DoActions(SetScore(p, Add, C.CHEAT_POINT, Custom))
    elif kind == "stone":
        S.stone[i] += C.CHEAT_STONE
    elif kind == "res":
        DoActions([SetResources(p, Add, C.CHEAT_RES, Ore), SetResources(p, Add, C.CHEAT_RES, Gas)])
    elif kind == "help":
        f_setcurpl(p)
        DoActions(DisplayText(HELP))


def cheats(tick):
    global chat_prev
    if not C.CHEAT_ON:
        return
    if EUDIf()(tick == 3):                        # 방에 아이디가 있는지 찾기
        for p in HUM:
            if EUDIf()(f_memcmp(0x57EEEB + 36 * p, _id_db, len(_ID) + 1) == 0):
                cheat_p << p
            EUDEndIf()
        chat_prev << f_dwread(0x640B58)
    EUDEndIf()
    cur = f_dwread(0x640B58)
    if EUDIf()([tick >= 4, cheat_p <= 7]):
        if EUDWhileNot()(chat_prev == cur):
            line = 0x640B60 + chat_prev * 218
            pos = f_strnstr(line, _idc_db, 40)
            if EUDIf()([pos != 0xFFFFFFFF, pos <= line + 3]):
                for i, p in enumerate(HUM):
                    if EUDIf()(cheat_p == p):
                        for db, kind in _cmd_dbs:
                            if EUDIf()(f_strnstr(line, db, 218) != 0xFFFFFFFF):
                                _do(kind, p, i)
                            EUDEndIf()
                        for db, u in _spawn_dbs:
                            if EUDIf()(f_strnstr(line, db, 218) != 0xFFFFFFFF):
                                DoActions(CreateUnit(1, u, C.FIELD[i], p))
                            EUDEndIf()
                    EUDEndIf()
            EUDEndIf()
            chat_prev += 1
            if EUDIf()(chat_prev >= 11):
                chat_prev << 0
            EUDEndIf()
        EUDEndWhile()
    EUDEndIf()
    chat_prev << cur


# ---------------------------------------------------------------------
#  무한성 레이드 이벤트
# ---------------------------------------------------------------------
INF = C.INF_STAGES
inf_state = EUDVariable(0)       # 0 잠김 1 열림 2 전투 3 대기(다시 열릴 때까지)
inf_stage = EUDVariable(0)
inf_t = EUDVariable(0)           # 지금 단계 경과 틱
inf_cd = EUDVariable(0)          # 대기 남은 틱
inf_join = [EUDVariable(0) for _ in HUM]
inf_clear = [EUDVariable(0) for _ in HUM]
inf_sk = [[EUDVariable(0) for _ in st["skills"]] for st in INF]
_IL = 0x58DC60 + 20 * (C.INF_SKILL_LOC - 1)


def _inf_setup():
    """처음 열릴 때 한 번: 보스 칸 이름·능력치·전용 무기, 입장 표지판"""
    import game
    acts = []
    for st in INF:
        u, w = st["unit"], st["weapon"]
        _copy_weapon(w, C.INF_WEAPON_FROM)
        acts += game.rename_actions(u, st["name"]) + game.stat_actions(u, st["hp"], st["sh"], st["ar"])
        acts += [_setb(0x6647B0 + u, 1), _setb(0x6636B8 + u, w), _setb(0x6616E0 + u, w),
                 _setw(0x656EB0 + 2 * w, st["dmg"]), _setb(0x656FB8 + w, st["cd"]), _setb(0x6564E0 + w, st["factor"]),
                 _setw(0x657678 + 2 * w, st["dmg"] // 10)]
    DoActions(acts)
    _copy(UNIT_FIELDS, C.INF_SIGN_UNIT, 186)                  # 표지판 = 파티레이드 표지판과 같은 모양
    MR = 0x58DC60
    acts = []
    for i, p in enumerate(HUM):
        x0 = struct.unpack_from("<I", _MRGN, (C.INF_PAD[i] - 1) * 20)[0]
        y0 = struct.unpack_from("<I", _MRGN, (C.INF_PAD[i] - 1) * 20 + 4)[0]
        x1 = struct.unpack_from("<I", _MRGN, (C.INF_PAD[i] - 1) * 20 + 8)[0]
        acts += _create_at(1, C.INF_SIGN_UNIT, 6, (x0 + x1) // 2, y0 + 16)
    acts.append(SetInvincibility(Enable, C.INF_SIGN_UNIT, 6, C.ANYWHERE))
    DoActions(acts)


_MRGN = GetChkTokenized().getsection("MRGN")


def _inf_end(win):
    """전투 끝: 방 정리, 참가자 귀환"""
    DoActions([RemoveUnitAt(All, "Any unit", C.INF_ROOM, C.INF_OWNER)] +
              [MoveUnit(All, "Men", p, C.INF_ROOM, C.ZONE[i]) for i, p in enumerate(HUM)])
    for i in range(len(HUM)):
        inf_join[i] << 0
    inf_state << 3
    inf_cd << (C.INF_RETRY if win else C.INF_FAIL_RETRY) * 24


def _inf_spawn(k):
    st = INF[k]
    DoActions([CreateUnit(1, st["unit"], C.INF_ROOM, C.INF_OWNER), DisplayTextAll(st["intro"])])
    inf_t << 0
    for v in inf_sk[k]:
        v << 0


def infinity(tick):
    global inf_cd, inf_t
    import game
    # 열기 (6장 클리어 = 7장 시작 이후, 게임이 끝나지 않았을 때)
    if EUDIf()([inf_state == 0, game.chap >= C.INF_OPEN_CHAPTER, game.state >= game.ST_WAVE, game.state <= game.ST_BREAK]):
        _inf_setup()
        inf_state << 1
        DoActions(DisplayTextAll("\x13\x11━━━━━━━━━━ 【 이벤트 】 무 한 성 레 이 드 ━━━━━━━━━━\n"
                                 "\x13\x04플레이어존 왼쪽 아래 \x08무한성 발판\x04에 영웅을 1명씩 올리면 입장!\n"
                                 "\x13\x05상현 3 → 상현 2 → 상현 1 → 무잔 / 클리어하면 참가자는 각성 궁극기를 배울 수 있습니다"))
    EUDEndIf()
    # 대기 -> 다시 열림
    if EUDIf()(inf_state == 3):
        inf_cd -= 1
        if EUDIf()(inf_cd == 0):
            inf_state << 1
            DoActions(DisplayTextAll("\x13\x11【 무한성 】 \x04무한성이 다시 열렸습니다! \x05(플레이어존 왼쪽 아래 발판)"))
        EUDEndIf()
    EUDEndIf()
    # 입장 (열림 / 전투 중) : 1명만, 이미 들어가 있으면 돌려보냄
    for i, p in enumerate(HUM):
        pad = C.INF_PAD[i]
        if EUDIf()(Bring(p, AtLeast, 1, "Men", pad)):
            if EUDIf()([inf_state >= 1, inf_state <= 2, inf_join[i] == 0, rush_state != 2]):
                DoActions([MoveUnit(1, "Men", p, pad, C.INF_ROOM), MoveUnit(All, "Men", p, pad, C.ZONE[i])])
                inf_join[i] << 1
                S._println(p, "\x11【 무한성 】 \x04입장했습니다. \x05(쓰러지면 다음 도전까지 기다려야 합니다)")
                if EUDIf()(inf_state == 1):
                    inf_state << 2
                    inf_stage << 0
                    _inf_spawn(0)
                EUDEndIf()
            if EUDElse()():
                DoActions(MoveUnit(All, "Men", p, pad, C.ZONE[i]))
                if EUDIf()(rush_state == 2):
                    S._println(p, "\x11【 무한성 】 \x04보스 러시가 진행 중이라 지금은 들어갈 수 없습니다.")
                if EUDElseIf()(inf_state == 3):
                    S._println(p, "\x11【 무한성 】 \x04다시 열릴 때까지 \x07{}초 \x04남았습니다.", inf_cd // 24 + 1)
                if EUDElseIf()(inf_state == 0):
                    S._println(p, "\x11【 무한성 】 \x04챕터 %d 클리어 후 열립니다." % C.INF_OPEN_CHAPTER)
                if EUDElse()():
                    S._println(p, "\x11【 무한성 】 \x04이미 영웅이 들어가 있습니다. \x05(1명만)")
                EUDEndIf()
            EUDEndIf()
        EUDEndIf()
    # 전투
    if EUDIf()(inf_state == 2):
        inf_t += 1
        for k, st in enumerate(INF):
            if EUDIf()(inf_stage == k):
                u = st["unit"]
                # 보스 스킬
                for j, (every, fx, atk, dur, hpcut, text) in enumerate(st["skills"]):
                    c = inf_sk[k][j]
                    c += 1
                    if EUDIf()(c == every):
                        c << 0
                        acts = [MoveLocation(C.INF_SKILL_LOC, u, C.INF_OWNER, C.INF_ROOM)]
                        if fx:
                            acts += [CreateUnit(1, fx, C.INF_SKILL_LOC, C.INF_OWNER), KillUnitAt(All, fx, C.INF_SKILL_LOC, C.INF_OWNER)]
                        if atk:
                            acts += [CreateUnit(2, atk, C.INF_SKILL_LOC, C.INF_OWNER), Order(atk, C.INF_OWNER, C.INF_SKILL_LOC, Attack, C.INF_ROOM)]
                        if hpcut:
                            acts += [ModifyUnitHitPoints(All, "Men", q, C.INF_ROOM, hpcut) for q in HUM]
                        acts.append(DisplayTextAll(text))
                        DoActions(acts)
                    EUDEndIf()
                    if atk:
                        if EUDIf()(c == dur):
                            DoActions(RemoveUnitAt(All, atk, C.INF_ROOM, C.INF_OWNER))
                        EUDEndIf()
                ev, cut = C.INF_TELE[k]
                if EUDIf()(f_div(inf_t, ev)[1] == ev - 1):
                    tele_start(C.INF_ROOM, cut)
                EUDEndIf()
                if EUDIf()(f_div(inf_t, 16)[1] == 0):
                    DoActions(Order(u, C.INF_OWNER, C.INF_ROOM, Attack, C.INF_ROOM))
                EUDEndIf()
                # 처치
                if EUDIf()(Command(C.INF_OWNER, Exactly, 0, u)):
                    pt, stn = st["reward"]
                    if pt or stn:
                        for i, p in enumerate(HUM):
                            if EUDIf()(inf_join[i] == 1):
                                if pt:
                                    DoActions(SetScore(p, Add, pt, Custom))
                                if stn:
                                    S.stone[i] += stn
                            EUDEndIf()
                        DoActions(DisplayTextAll("\x13\x07【 무한성 】 %s \x04처치! \x05(참가자 강화포인트 +%s, 초월석 +%d)"
                                                 % (st["name"], "{:,}".format(pt), stn)))
                    DoActions(RemoveUnitAt(All, "Any unit", C.INF_ROOM, C.INF_OWNER))
                    if k + 1 < len(INF):
                        inf_stage << k + 1
                        _inf_spawn(k + 1)
                    else:
                        for i in range(len(HUM)):
                            if EUDIf()(inf_join[i] == 1):
                                inf_clear[i] << 1
                            EUDEndIf()
                        DoActions(DisplayTextAll(C.INF_CLEAR_TEXT))
                        _inf_end(True)
                EUDEndIf()
                # 실패: 제한시간 / 참가자 전멸
                if EUDIf()(inf_state == 2):
                    if EUDIf()(inf_t >= st["time"] * 24):
                        DoActions(DisplayTextAll("\x13\x08【 무한성 】 \x04제한시간 초과 - 레이드 실패 \x05(%d초 뒤 다시 열림)" % C.INF_FAIL_RETRY))
                        _inf_end(False)
                    if EUDElseIf()(Bring(Force1, Exactly, 0, "Men", C.INF_ROOM)):
                        DoActions(DisplayTextAll("\x13\x08【 무한성 】 \x04참가자 전멸 - 레이드 실패 \x05(%d초 뒤 다시 열림)" % C.INF_FAIL_RETRY))
                        _inf_end(False)
                    EUDEndIf()
                EUDEndIf()
            EUDEndIf()
    EUDEndIf()


# ---------------------------------------------------------------------
#  합동 필살기 : 두 영웅이 같은 전투 구역에 보스와 함께 있으면 자동 발동
# ---------------------------------------------------------------------
combo_cd = [EUDVariable(0) for _ in C.COMBOS]
combo_act = EUDVariable(0)          # 진행 중인 합동기 번호 + 1 (0 = 없음)
combo_t = EUDVariable(0)
combo_p = EUDVariable(0)            # 연출 유닛 주인
combo_x = EUDVariable(0)
combo_y = EUDVariable(0)
_CL = 0x58DC60 + 20 * (C.COMBO_LOC - 1)


def combos():
    global combo_t
    for k in range(len(C.COMBOS)):
        if EUDIf()(combo_cd[k] >= 1):
            combo_cd[k] -= 1
        EUDEndIf()
    # 발동 확인 (진행 중인 합동기가 없을 때, 0.5초마다): 영웅 A 주변(반경 COMBO_RADIUS)에 적이 있어야 함
    if EUDIf()([combo_act == 0, f_div(f_getgametick(), 12)[1] == 0]):
        for k, (a, b, name, dmg, hits, fx, fin) in enumerate(C.COMBOS):
            for area in C.COMBO_AREAS:
                if EUDIf()([combo_act == 0, combo_cd[k] == 0,
                            Bring(Force1, AtLeast, 1, a, area), Bring(Force1, AtLeast, 1, b, area)]):
                    for p in HUM:
                        if EUDIf()([combo_act == 0, Bring(p, AtLeast, 1, a, area)]):
                            DoActions(MoveLocation(C.COMBO_LOC, a, p, area))
                            if EUDIf()(Bring(C.BOSS_OWNER, AtLeast, 1, "Men", C.COMBO_LOC)):
                                combo_p << p
                                combo_act << k + 1
                            if EUDElseIf()(Bring(C.INF_OWNER, AtLeast, 1, "Men", C.COMBO_LOC)):
                                combo_p << p
                                combo_act << k + 1
                            EUDEndIf()
                            if EUDIf()(combo_act == k + 1):
                                lx = EUDVariable()
                                ly = EUDVariable()
                                lx << f_dwread(_CL)                  # 위치 왼쪽·위 + 반경 = 영웅 위치
                                ly << f_dwread(_CL + 4)
                                combo_x << lx + C.COMBO_RADIUS
                                combo_y << ly + C.COMBO_RADIUS
                                combo_t << 0
                                combo_cd[k] << C.COMBO_CD
                                DoActions(DisplayTextAll("\x13\x07━━━━━━━━━━ 【 합 동 필 살 기 】 ━━━━━━━━━━\n\x13\x04" + name))
                                vo = C.ULT2_VOICE.get(a, C.HERO_VOICE.get(a))
                                if vo:
                                    for q in HUM:
                                        f_setcurpl(q)
                                        DoActions(PlayWAV("staredit\\wav\\%s.wav" % vo))
                            EUDEndIf()
                        EUDEndIf()
                EUDEndIf()
    EUDEndIf()
    # 진행 : 6틱마다 연출, 12틱마다 피해
    if EUDIfNot()(combo_act == 0):
        R = C.COMBO_RADIUS
        for k, (a, b, name, dmg, hits, fx, fin) in enumerate(C.COMBOS):
            if EUDIf()(combo_act == k + 1):
                for j in range(hits * 2):
                    if EUDIf()(combo_t == 6 * j):
                        dx, dy = S.RING[(j * 2) % len(S.RING)]
                        S._fx_create(combo_x + dx, combo_y + dy, fx[j % 2], combo_p, 1)
                        if j % 2 == 1:
                            S._area_damage(combo_x - R, combo_y - R, combo_x + R, combo_y + R, dmg)
                    EUDEndIf()
                if EUDIf()(combo_t == 6 * hits * 2):
                    S._fx_create(combo_x, combo_y, fin, combo_p, 3)
                    combo_act << 0
                EUDEndIf()
            EUDEndIf()
        combo_t += 1
    EUDEndIf()


# ---------------------------------------------------------------------
#  보스 러시 (무한성 방을 같이 씀)
# ---------------------------------------------------------------------
rush_state = EUDVariable(0)       # 0 잠김 1 열림 2 전투 3 대기
rush_i = EUDVariable(0)           # 지금 몇 번째 (0부터)
rush_t = EUDVariable(0)
rush_cd = EUDVariable(0)
rush_n = EUDVariable(0)           # 이번 판에 나올 보스 수 (깬 챕터까지)
rush_join = [EUDVariable(0) for _ in HUM]
rush_best = EUDVariable(0)
R_OWN = C.INF_OWNER


def _rush_end():
    global rush_i
    DoActions([RemoveUnitAt(All, "Any unit", C.INF_ROOM, R_OWN)] +
              [MoveUnit(All, "Men", p, C.INF_ROOM, C.ZONE[i]) for i, p in enumerate(HUM)])
    if EUDIf()(rush_i > rush_best):
        rush_best << rush_i
    EUDEndIf()
    f_simpleprint("\x13\x1f【 보스 러시 】 \x04이번 기록", rush_i, "명 처치 / 최고 기록", rush_best)
    for i in range(len(HUM)):
        rush_join[i] << 0
    rush_state << 3
    rush_cd << C.RUSH_RETRY * 24


def _rush_spawn():
    rush_t << 0
    EUDSwitch(rush_i)
    for k, (u, ch) in enumerate(C.RUSH_ROSTER):
        if EUDSwitchCase()(k):
            DoActions([CreateUnit(1, u, C.INF_ROOM, R_OWN),
                       DisplayTextAll("\x13\x1f【 보스 러시 %d 】 \x04다음 상대 등장!" % (k + 1))])
            EUDBreak()
    EUDEndSwitch()


def boss_rush(tick):
    global rush_t, rush_cd, rush_i, rush_n
    import game
    if EUDIf()([rush_state == 0, game.chap >= C.RUSH_OPEN_CHAPTER, game.state >= game.ST_WAVE, game.state <= game.ST_BREAK]):
        rush_state << 1
        _copy(UNIT_FIELDS, C.RUSH_SIGN_UNIT, 186)
        acts = []
        for i, p in enumerate(HUM):
            x0, y0, x1, y1 = struct.unpack_from("<IIII", _MRGN, (C.RUSH_PAD[i] - 1) * 20)
            acts += _create_at(1, C.RUSH_SIGN_UNIT, 6, (x0 + x1) // 2, y0 + 16)
        acts.append(SetInvincibility(Enable, C.RUSH_SIGN_UNIT, 6, C.ANYWHERE))
        acts.append(DisplayTextAll("\x13\x1f【 이벤트 】 보스 러시 개방! \x04플레이어존 아래 가운데 발판에 영웅 1명 -> 깬 챕터의 보스들과 연속 대결"))
        DoActions(acts)
    EUDEndIf()
    if EUDIf()(rush_state == 3):
        rush_cd -= 1
        if EUDIf()(rush_cd == 0):
            rush_state << 1
            DoActions(DisplayTextAll("\x13\x1f【 보스 러시 】 \x04다시 열렸습니다!"))
        EUDEndIf()
    EUDEndIf()
    for i, p in enumerate(HUM):
        pad = C.RUSH_PAD[i]
        if EUDIf()(Bring(p, AtLeast, 1, "Men", pad)):
            if EUDIf()([rush_state >= 1, rush_state <= 2, rush_join[i] == 0, inf_state != 2]):
                DoActions([MoveUnit(1, "Men", p, pad, C.INF_ROOM), MoveUnit(All, "Men", p, pad, C.ZONE[i])])
                rush_join[i] << 1
                if EUDIf()(rush_state == 1):
                    rush_state << 2
                    rush_i << 0
                    rush_n << 0
                    for u, ch in C.RUSH_ROSTER:
                        if EUDIf()(game.chap >= ch):
                            rush_n += 1
                        EUDEndIf()
                    _rush_spawn()
                EUDEndIf()
            if EUDElse()():
                DoActions(MoveUnit(All, "Men", p, pad, C.ZONE[i]))
                if EUDIf()(inf_state == 2):
                    S._println(p, "\x1f【 보스 러시 】 \x04무한성 레이드가 진행 중이라 지금은 들어갈 수 없습니다.")
                if EUDElseIf()(rush_state == 3):
                    S._println(p, "\x1f【 보스 러시 】 \x04다시 열릴 때까지 \x07{}초", rush_cd // 24 + 1)
                if EUDElseIf()(rush_state == 0):
                    S._println(p, "\x1f【 보스 러시 】 \x04챕터 %d 클리어 후 열립니다." % C.RUSH_OPEN_CHAPTER)
                if EUDElse()():
                    S._println(p, "\x1f【 보스 러시 】 \x04이미 영웅이 들어가 있습니다. \x05(1명만)")
                EUDEndIf()
            EUDEndIf()
        EUDEndIf()
    if EUDIf()(rush_state == 2):
        rush_t += 1
        if EUDIf()(f_div(rush_t, 16)[1] == 0):
            DoActions(Order("Men", R_OWN, C.INF_ROOM, Attack, C.INF_ROOM))
        EUDEndIf()
        # 처치 -> 보상, 다음
        if EUDIf()([rush_t >= 24, Bring(R_OWN, Exactly, 0, "Men", C.INF_ROOM)]):
            rush_i += 1
            for i, p in enumerate(HUM):
                if EUDIf()(rush_join[i] == 1):
                    for k in range(1, len(C.RUSH_ROSTER) + 1):
                        if EUDIf()(rush_i == k):
                            DoActions(SetScore(p, Add, C.RUSH_POINT * k, Custom))
                            if k % C.RUSH_STONE_EVERY == 0:
                                S.stone[i] += 1
                        EUDEndIf()
                EUDEndIf()
            f_simpleprint("\x13\x07【 보스 러시 】 \x04", rush_i, "번째 보스 처치! 강화포인트 +", rush_i * C.RUSH_POINT)
            if EUDIf()(rush_i >= rush_n):
                DoActions(DisplayTextAll("\x13\x07【 보스 러시 】 \x04지금까지 깬 보스를 모두 쓰러뜨렸습니다! \x05(초월석 +2)"))
                for i in range(len(HUM)):
                    if EUDIf()(rush_join[i] == 1):
                        S.stone[i] += 2
                    EUDEndIf()
                _rush_end()
            if EUDElse()():
                _rush_spawn()
            EUDEndIf()
        EUDEndIf()
        if EUDIf()(rush_state == 2):
            if EUDIf()(rush_t >= C.RUSH_TIME * 24):
                DoActions(DisplayTextAll("\x13\x08【 보스 러시 】 \x04제한시간 초과 - 도전 종료"))
                _rush_end()
            if EUDElseIf()([rush_t >= 24, Bring(Force1, Exactly, 0, "Men", C.INF_ROOM)]):
                DoActions(DisplayTextAll("\x13\x08【 보스 러시 】 \x04참가 영웅 전멸 - 도전 종료"))
                _rush_end()
            EUDEndIf()
        EUDEndIf()
    EUDEndIf()


# ---------------------------------------------------------------------
#  현재 목표 안내 (내 화면 왼쪽 글줄, 1초마다)
# ---------------------------------------------------------------------
def goal_hud(tick):
    import game
    if EUDIf()(f_div(tick, 24)[1] == 9):
        # 카운트다운 남은 초 읽기 (메모리 대신 기본 조건으로: 2의 거듭제곱씩 빼보며 세고 바로 되돌림)
        tm = EUDVariable()
        tm << 0
        bits = [EUDVariable() for _ in range(12)]
        for bb in reversed(range(12)):
            bits[bb] << 0
            if EUDIf()(CountdownTimer(AtLeast, 2 ** bb)):
                DoActions(SetCountdownTimer(Subtract, 2 ** bb))
                tm += 2 ** bb
                bits[bb] << 1
            EUDEndIf()
        for bb in range(12):
            if EUDIf()(bits[bb] == 1):
                DoActions(SetCountdownTimer(Add, 2 ** bb))
            EUDEndIf()
        st = game.state
        L = C.GOAL_HUD_LINE
        if EUDIf()(st == game.ST_DIFF):
            f_printAt(L, "\x1f【 목표 】 \x04방장이 SELECT 로 난이도를 고르세요 \x05({}초 뒤 EASY)", tm)
        if EUDElseIf()(st == game.ST_WAVE):
            f_printAt(L, "\x1f【 목표 】 \x04웨이브를 막으며 영웅을 강화하세요 \x05- 보스까지 \x07{}초", tm)
        if EUDElseIf()(st == game.ST_BOSS):
            f_printAt(L, "\x1f【 목표 】 \x08보스전! \x04출전 발판으로 영웅을 보내세요 \x05- 남은 시간 \x07{}초", tm)
        if EUDElseIf()(st == game.ST_BREAK):
            f_printAt(L, "\x1f【 목표 】 \x04정비 시간 \x05- 다음 보스까지 \x07{}초", tm)
        EUDEndIf()
        # 이벤트 안내 (다음 줄)
        if EUDIf()(inf_state == 1):
            f_printAt(L + 1, "\x11【 이벤트 】 \x04무한성 레이드 열림 \x05(플레이어존 왼쪽 아래 발판)")
        if EUDElseIf()(inf_state == 2):
            f_printAt(L + 1, "\x11【 이벤트 】 \x04무한성 레이드 진행 중")
        if EUDElseIf()(rush_state == 1):
            f_printAt(L + 1, "\x1f【 이벤트 】 \x04보스 러시 열림 \x05(플레이어존 아래 가운데 발판)")
        if EUDElseIf()(rush_state == 2):
            f_printAt(L + 1, "\x1f【 이벤트 】 \x04보스 러시 {}번째 보스 진행 중", rush_i + 1)
        EUDEndIf()
    EUDEndIf()
