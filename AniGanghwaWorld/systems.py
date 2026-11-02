# -*- coding: utf-8 -*-
# =====================================================================
#  애니강화월드 새 버전 - 부가 시스템
#   플레이어존 이동, 퓨전 조합, 초월석, 칭호 단계, 일괄 판매/강화, BGM,
#   변환기, 드래곤볼, 던전(뉴비퀘스트), 파티레이드
#   수치는 config.py 의 "부가 시스템" 부분에서 고칩니다.
# =====================================================================
from eudplib import *

import config as C
import titles

HUM = C.HUMANS
P_RAID = C.RAID_OWNER
U_SEL = C.U_SELECT

stone = [EUDVariable(0) for _ in HUM]          # 초월석 개수
tier = [EUDVariable(0) for _ in HUM]           # 칭호 단계
bgm_on = [EUDVariable(1) for _ in HUM]         # BGM 켜짐
conv_open = EUDVariable(0)                     # 변환기 해금
db_stage = [EUDVariable(0) for _ in HUM]       # 드래곤볼 진행 (0~6 일반, 7~13 슈퍼, 14 끝)
db_alive = [EUDVariable(0) for _ in HUM]
db_cd = [EUDVariable(20 * 24) for _ in HUM]   # 시작 20초 뒤 첫 드래곤볼
dg_fruit = [EUDVariable(0) for _ in HUM]       # 던전 파괴 수
dg_jin = [EUDVariable(0) for _ in HUM]
dg_fruit_alive = [EUDVariable(0) for _ in HUM]
dg_jin_alive = [EUDVariable(0) for _ in HUM]
dg_done = [EUDVariable(0) for _ in HUM]
raid_i = EUDVariable(0)                        # 파티레이드 몇 번째 보스
raid_alive = EUDVariable(0)
raid_cd = EUDVariable(C.RAID_START_DELAY * 24)
bgm_pos = EUDVariable(0)
_tick = EUDVariable(0)                         # frame() 에서 게임 틱 복사


def tick_ref():
    return _tick
bgm_t = EUDVariable(0)


def _say(p, text):
    f_setcurpl(p)
    DoActions(DisplayText(text))


def _give(p, ore, gas, pt):
    acts = []
    if ore:
        acts.append(SetResources(p, Add, ore, Ore))
    if gas:
        acts.append(SetResources(p, Add, gas, Gas))
    if pt:
        acts.append(SetScore(p, Add, pt, Custom))
    if acts:
        DoActions(acts)


def _println(p, fmt, *args):
    """p 플레이어 화면에만 (숫자 들어간 문구)"""
    if EUDIf()(f_getuserplayerid() == p):
        f_println(fmt, *args)
    EUDEndIf()


def add_stone(i, n, why=""):
    """i = HUMANS 안 순서"""
    stone[i] += n
    _println(HUM[i], "\x1f[초월석] \x04+%d %s \x05(보유 {}개)" % (n, why), stone[i])


# ---------------------------------------------------------------------
#  시작할 때 (난이도 고른 뒤)
# ---------------------------------------------------------------------
def on_select_done():
    for p in HUM:
        if EUDIf()(f_playerexist(p) == 1):   # 방에 없는 자리에는 만들지 않음
            DoActions([CreateUnit(1, U_SEL, C.BULK_AREA, p), CreateUnit(1, U_SEL, C.BGM_AREA, p)])
        EUDEndIf()
    for i, p in enumerate(HUM):
        if EUDIf()(f_playerexist(p) == 1):
            t = titles.GetTitleTier(p)
            tier[i] << t
            for k in sorted(C.TITLE_NAMES):
                if EUDIf()(t == k):
                    f_setcurpl(p)
                    b = C.TITLE_BONUS[k]
                    DoActions(DisplayText("\x13\x1f《%s》칭호혜택\n\x13【  미네랄 +%d   가스 +%d   강화포인트+%d  】 (%d초마다)"
                                          % (C.TITLE_NAMES[k], b[0], b[1], b[2], C.TITLE_BONUS_PERIOD)))
                EUDEndIf()
            for k, n in C.GUNTRAP_BY_TIER.items():
                if EUDIf()(t == k):
                    DoActions(GiveUnits(n, C.U_GUNTRAP, C.U_HOUSE_OWNER, C.ZONE[i], p))
                    f_setcurpl(p)
                    DoActions(DisplayText("\x13\x1f《%s》프리미엄 [ 건트랩 +%d ] \x04- 드래곤볼 옆 건트랩이 내 것이 됩니다" % (C.TITLE_NAMES[k], n)))
                EUDEndIf()
            for need in C.TITLE_STONE_AT:
                if EUDIf()(t >= need):
                    add_stone(i, 1, "《%s》프리미엄" % C.TITLE_NAMES[need])
                EUDEndIf()
        EUDEndIf()


def on_chapter_start(ci):
    if ci + 1 == C.CONVERT_UNLOCK_CHAPTER:
        if EUDIf()(conv_open == 0):
            conv_open << 1
            for p in HUM:
                if EUDIf()(f_playerexist(p) == 1):
                    DoActions(CreateUnit(1, U_SEL, C.CONV_AREA, p))
                EUDEndIf()
            DoActions([DisplayTextAll("\x13\x1f[SYSTEM] \x04변환기가 열렸습니다! \x05(미네랄 변환 100G▶200M / 가스 변환 100M▶20G)")])
        EUDEndIf()


# ---------------------------------------------------------------------
#  이동 발판
# ---------------------------------------------------------------------
def zones():
    for i, p in enumerate(HUM):
        DoActions([
            MoveUnit(1, "Men", p, C.CONTENT_PAD[i], C.ZONE[i]),       # 『 컨텐츠 』 -> 플레이어존
            MoveUnit(All, "Men", p, C.ZONE_EXIT, C.HUB),              # Player Zone Move -> 허브
            MoveUnit(All, "Men", p, C.HUB_HOME, C.FIELD[i]),          # 허브 -> 내 필드
            MoveUnit(All, "Men", p, C.HUB_ZONE, C.ZONE[i]),           # 허브 -> 플레이어존
            MoveUnit(All, "Men", p, C.DUNGEON_EXIT, C.ZONE[i]),       # 던전 나가기
            MoveUnit(All, "Men", p, C.RAID_EXIT, C.ZONE[i]),          # 레이드 나가기
        ])
        # 허브 판매 발판 (필드 판매와 같은 가격)
        for u, (ore, gas, pt) in C.SELL_TABLE.items():
            if EUDIf()(Bring(p, AtLeast, 1, u, C.HUB_SELL)):
                DoActions(RemoveUnitAt(1, u, C.HUB_SELL, p))
                _give(p, ore, gas, pt)
            EUDEndIf()


# ---------------------------------------------------------------------
#  퓨전 조합 (재료를 퓨전 띠 L068 에 넣으면 자동)
# ---------------------------------------------------------------------
def fusion():
    for i, p in enumerate(HUM):
        for result, mats, cost, stones in C.FUSIONS:
            cond = [Bring(p, AtLeast, n, u, C.FUSION_AREA) for u, n in mats]
            cond.append(Score(p, Custom, AtLeast, cost))
            if C.FUSION_LIMIT_ONE:
                cond.append(Command(p, Exactly, 0, result))
            if stones:
                cond.append(stone[i] >= stones)
            if EUDIf()(cond):
                acts = [RemoveUnitAt(n, u, C.FUSION_AREA, p) for u, n in mats]
                acts += [SetScore(p, Subtract, cost, Custom), CreateUnit(1, result, C.ZONE[i], p),
                         DisplayTextAll("\x13\x1f[퓨전] \x04조합 성공! 새 영웅이 탄생했습니다.")]
                DoActions(acts)
                if stones:
                    stone[i] -= stones
            EUDEndIf()


# ---------------------------------------------------------------------
#  3★ 이하 일괄 판매 / 일괄 강화, BGM, 변환기 (SELECT 유닛을 발판에 올림)
# ---------------------------------------------------------------------
BULK_SELL = {}
for _line in C.NORMAL_LINES.values():
    BULK_SELL[_line[0]] = (100, 50, 10)
    BULK_SELL[_line[1]] = (150, 75, 50)
    BULK_SELL[_line[2]] = (300, 125, 100)
BULK_UP = [line[k] for line in C.NORMAL_LINES.values() for k in range(3)]


def select_pads():
    for i, p in enumerate(HUM):
        # 일괄 판매: 내 필드의 1~3★ 전부
        if EUDIf()(Bring(p, AtLeast, 1, U_SEL, C.BULK_SELL_PAD)):
            DoActions(MoveUnit(1, U_SEL, p, C.BULK_SELL_PAD, C.BULK_AREA))
            for u, (ore, gas, pt) in BULK_SELL.items():
                if EUDWhile()(Bring(p, AtLeast, 1, u, C.FIELD[i])):
                    DoActions(RemoveUnitAt(1, u, C.FIELD[i], p))
                    _give(p, ore, gas, pt)
                EUDEndWhile()
            _say(p, "\x07[일괄 판매] \x04필드의 3★ 이하 유닛을 모두 판매했습니다.")
        EUDEndIf()
        # 일괄 강화: 내 필드의 1~3★ 를 강화존으로 (강화존이 한 마리씩 처리, 실패하면 필드로 돌아옴)
        if EUDIf()(Bring(p, AtLeast, 1, U_SEL, C.BULK_UP_PAD)):
            DoActions([MoveUnit(1, U_SEL, p, C.BULK_UP_PAD, C.BULK_AREA)] +
                      [MoveUnit(All, u, p, C.FIELD[i], C.UPGRADE_ZONE) for u in BULK_UP])
            _say(p, "\x07[일괄 강화] \x04필드의 3★ 이하 유닛을 강화합니다.")
        EUDEndIf()
        # BGM 켜기 / 끄기
        if EUDIf()(Bring(p, AtLeast, 1, U_SEL, C.BGM_ON_PAD)):
            DoActions(MoveUnit(1, U_SEL, p, C.BGM_ON_PAD, C.BGM_AREA))
            bgm_on[i] << 1
            _say(p, "\x07BGM ON")
        EUDEndIf()
        if EUDIf()(Bring(p, AtLeast, 1, U_SEL, C.BGM_OFF_PAD)):
            DoActions(MoveUnit(1, U_SEL, p, C.BGM_OFF_PAD, C.BGM_AREA))
            bgm_on[i] << 0
            _say(p, "\x08BGM OFF")
        EUDEndIf()
        # 변환기 (발판 위에 있는 동안 0.5초마다 1번)
        g_need, ore_get = C.CONV_MINERAL
        o_need, gas_get = C.CONV_GAS
        if EUDIf()([conv_open == 1, tick_ref() % 12 == i, Bring(p, AtLeast, 1, U_SEL, C.CONV_MIN_PAD), Accumulate(p, AtLeast, g_need, Gas)]):
            DoActions([SetResources(p, Subtract, g_need, Gas), SetResources(p, Add, ore_get, Ore)])
        EUDEndIf()
        if EUDIf()([conv_open == 1, tick_ref() % 12 == i, Bring(p, AtLeast, 1, U_SEL, C.CONV_GAS_PAD), Accumulate(p, AtLeast, o_need, Ore)]):
            DoActions([SetResources(p, Subtract, o_need, Ore), SetResources(p, Add, gas_get, Gas)])
        EUDEndIf()


# ---------------------------------------------------------------------
#  BGM (sound 폴더의 M번호_조각.ogg 를 순서대로 이어서 재생)
# ---------------------------------------------------------------------
def _bgm_list():
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    out = []
    for k in C.BGM_PLAYLIST:
        n = 0
        while os.path.exists(os.path.join(here, "sound", "M%d_%d.ogg" % (k, n))):
            out.append("M%d_%d.ogg" % (k, n))
            n += 1
    return out


BGM_FILES = _bgm_list()


def bgm():
    if not BGM_FILES:
        return
    global bgm_t, bgm_pos
    bgm_t += 1
    if EUDIf()(bgm_t >= C.BGM_SEGMENT_TICKS):
        bgm_t << 0
        EUDSwitch(bgm_pos)
        for n, f in enumerate(BGM_FILES):
            if EUDSwitchCase()(n):
                for i, p in enumerate(HUM):
                    if EUDIf()(bgm_on[i] == 1):
                        f_setcurpl(p)
                        DoActions(PlayWAV(f))
                    EUDEndIf()
                EUDBreak()
        EUDEndSwitch()
        bgm_pos += 1
        if EUDIf()(bgm_pos >= len(BGM_FILES)):
            bgm_pos << 0
        EUDEndIf()
    EUDEndIf()


# ---------------------------------------------------------------------
#  드래곤볼 (각자 플레이어존에 1개씩, 잡으면 다음 별)
# ---------------------------------------------------------------------
def dragonballs():
    pts = C.DRAGONBALL_POINTS + C.SUPER_DRAGONBALL_POINTS
    for i, p in enumerate(HUM):
        spot = C.DRAGONBALL_SPOT[i]
        if EUDIf()([f_playerexist(p) == 1, db_alive[i] == 0, db_stage[i] <= 13]):
            if EUDIf()(db_cd[i] >= 1):
                db_cd[i] -= 1
            if EUDElse()():
                if EUDIf()(db_stage[i] <= 6):
                    DoActions(CreateUnit(1, C.U_DRAGONBALL, spot, P_RAID))
                if EUDElse()():
                    DoActions(CreateUnit(1, C.U_SUPER_DRAGONBALL, spot, P_RAID))
                EUDEndIf()
                db_alive[i] << 1
            EUDEndIf()
        EUDEndIf()
        both0 = lambda: [Bring(P_RAID, Exactly, 0, C.U_DRAGONBALL, spot),
                         Bring(P_RAID, Exactly, 0, C.U_SUPER_DRAGONBALL, spot)]
        if EUDIf()([db_alive[i] == 1] + both0()):
            for k, v in enumerate(pts):
                if EUDIf()(db_stage[i] == k):
                    DoActions(SetScore(p, Add, v, Custom))
                    name = "드래곤볼 %d성구" % (k + 1) if k < 7 else "슈퍼 드래곤볼 %d성구" % (k - 6)
                    _say(p, "\x1f[SYSTEM] %s (강화포인트 +%d)" % (name, v))
                EUDEndIf()
            db_stage[i] += 1
            db_alive[i] << 0
            db_cd[i] << C.DRAGONBALL_INTERVAL * 24
        EUDEndIf()


# ---------------------------------------------------------------------
#  던전 (뉴비퀘스트)
# ---------------------------------------------------------------------
def dungeon():
    for i, p in enumerate(HUM):
        room = C.DUNGEON_ROOM[i]
        if EUDIf()([Bring(p, AtLeast, 1, "Men", C.DUNGEON_PAD[i]), Bring(p, Exactly, 0, "Men", room)]):
            DoActions(MoveUnit(1, "Men", p, C.DUNGEON_PAD[i], room))
            _say(p, "\x07[던전] \x04악마의 열매와 인주력을 각 %d개 파괴하면 초월석 +1 (NPC 실버즈 레일리 뉴비퀘스트)" % C.DUNGEON_QUEST)
        EUDEndIf()
        for u, alive, cnt in ((C.U_DEVIL_FRUIT, dg_fruit_alive[i], dg_fruit[i]), (C.U_JINCHURIKI, dg_jin_alive[i], dg_jin[i])):
            if EUDIf()([alive == 0, Bring(p, AtLeast, 1, "Men", room)]):
                DoActions(CreateUnit(1, u, room, P_RAID))
                alive << 1
            EUDEndIf()
            if EUDIf()([alive == 1, Bring(P_RAID, Exactly, 0, u, room)]):
                alive << 0
                cnt += 1
            EUDEndIf()
        if EUDIf()([dg_done[i] == 0, dg_fruit[i] >= C.DUNGEON_QUEST, dg_jin[i] >= C.DUNGEON_QUEST]):
            dg_done[i] << 1
            add_stone(i, 1, "NPC 실버즈 레일리 \" 정점까지 갔다와라! \" 뉴비퀘스트 완료")
        EUDEndIf()


# ---------------------------------------------------------------------
#  파티레이드 (한 번에 1마리 입장, 원본 순서)
# ---------------------------------------------------------------------
def party_raid(playing):
    global raid_i, raid_cd
    for i, p in enumerate(HUM):
        if EUDIf()([raid_alive == 1, Bring(p, AtLeast, 1, "Men", C.RAID_PAD[i]),
                    Bring(Force1, Exactly, 0, "Men", C.RAID_ROOM)]):
            DoActions(MoveUnit(1, "Men", p, C.RAID_PAD[i], C.RAID_ROOM))
            _say(p, "\x07[파티레이드] \x04입장! (한 번에 1명)")
        EUDEndIf()
    if EUDIf()([raid_alive == 0, raid_i < len(C.RAID_CHAIN), playing == 1]):
        if EUDIf()(raid_cd >= 1):
            raid_cd -= 1
        if EUDElse()():
            for k, (boss, minion, text, rw) in enumerate(C.RAID_CHAIN):
                if EUDIf()(raid_i == k):
                    DoActions([CreateUnit(1, boss, C.RAID_ROOM, P_RAID), CreateUnit(1, minion, C.RAID_ROOM, P_RAID),
                               DisplayTextAll("\x13\x07[파티레이드] \x04새 보스 등장 - 플레이어존의 '파티 레이드' 발판으로 1명 입장")])
                EUDEndIf()
            raid_alive << 1
        EUDEndIf()
    EUDEndIf()
    for k, (boss, minion, text, (ore, gas, pt, st)) in enumerate(C.RAID_CHAIN):
        if EUDIf()([raid_alive == 1, raid_i == k, Command(P_RAID, Exactly, 0, boss)]):
            DoActions([DisplayTextAll("\x13\x1f" + text), RemoveUnitAt(All, "Men", C.RAID_ROOM, P_RAID)])
            for i, p in enumerate(HUM):
                if EUDIf()(f_playerexist(p) == 1):
                    _give(p, ore, gas, pt)
                    if st:
                        add_stone(i, st, "(파티레이드)")
                EUDEndIf()
            raid_upgrades(boss)
            raid_i += 1
            raid_alive << 0
            raid_cd << 10 * 24
        EUDEndIf()


# ---------------------------------------------------------------------
#  칭호혜택 (주기적 지급)
# ---------------------------------------------------------------------
def title_bonus(tick):
    if EUDIf()(tick % (C.TITLE_BONUS_PERIOD * 24) == C.TITLE_BONUS_PERIOD * 24 - 1):
        for i, p in enumerate(HUM):
            for k, b in C.TITLE_BONUS.items():
                if EUDIf()(tier[i] == k):
                    _give(p, *b)
                EUDEndIf()
    EUDEndIf()


# =====================================================================
#  영웅 성장: 9★ 신화 조합 / Z 각성 / 공격력 업그레이드 / 궁극기 / 특수 능력
# =====================================================================
casts = {(i, h): EUDVariable(0) for i in range(len(HUM)) for h in C.HERO_SKILLS}
cool = {(i, h): EUDVariable(0) for i in range(len(HUM)) for h in C.HERO_SKILLS}
skill_rm = {(i, h): EUDVariable(0) for i in range(len(HUM)) for h in C.HERO_SKILLS}
awaken = {(i, z): EUDVariable(0) for i in range(len(HUM)) for z, _, _ in C.AWAKENS}
revive = [EUDVariable(0) for _ in HUM]
satella_d = [EUDVariable(0) for _ in HUM]
noon_flag = EUDVariable(0)


def add_upgrade_for_unit(p, unit, n):
    """unit 의 무기가 쓰는 공격력 업그레이드를 플레이어 p 에게 +n (게임 중에 무기 정보를 읽음)"""
    w = f_bread(0x6636B8 + unit)                     # 지상 무기
    if EUDIf()(w == 130):
        w << f_bread(0x6616E0 + unit)                # 공중 무기
    EUDEndIf()
    if EUDIf()(w <= 129):
        upg = f_bread(0x6571D0 + w)
        addr = EUDVariable()
        if EUDIf()(upg <= 45):
            addr << 0x58D2B0 + 46 * p + upg
        if EUDElse()():
            addr << 0x58F32C + 15 * p + upg - 46
        EUDEndIf()
        lv = f_bread(addr)
        if EUDIf()(lv <= 250 - n):
            f_bwrite(addr, lv + n)
        EUDEndIf()
    EUDEndIf()


def myth_and_awaken():
    for i, p in enumerate(HUM):
        # 9★ 신화 / 10★ 조합
        for result, mats, cost, stones, extra in C.MYTHS:
            cond = [Bring(p, AtLeast, n, u, C.FUSION_AREA) for u, n in mats]
            cond += [Score(p, Custom, AtLeast, cost), stone[i] >= stones, Command(Force1, Exactly, 0, result)]
            if extra and extra[0] == "cast":
                cond.append(casts[(i, extra[1])] >= extra[2])
            elif extra and extra[0] == "revive":
                cond.append(revive[i] >= extra[1])
            elif extra and extra[0] == "inf":
                import extras
                cond.append(extras.inf_clear[i] == 1)
            elif extra and extra[0] == "raid":
                idx = [k for k, r in enumerate(C.RAID_CHAIN) if r[0] == extra[1]][0]
                cond.append(raid_i >= idx + 1)
            if EUDIf()(cond):
                DoActions([RemoveUnitAt(n, u, C.FUSION_AREA, p) for u, n in mats] +
                          [SetScore(p, Subtract, cost, Custom), CreateUnit(1, result, C.ZONE[i], p)])
                stone[i] -= stones
                DoActions(DisplayTextAll("\x13\x1f━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\x13\x1f【 신화 】 \x04새로운 신화 영웅이 깨어났습니다!\n\x13\x1f━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"))
            EUDEndIf()
        # Z 각성 (Z 는 남고 재료·초월석만 사용)
        pt, st = C.AWAKEN_COST
        for z, mat, n in C.AWAKENS:
            lv = awaken[(i, z)]
            cond = [Bring(p, AtLeast, 1, z, C.FUSION_AREA), Score(p, Custom, AtLeast, pt), stone[i] >= st, lv < C.AWAKEN_MAX]
            if mat:
                cond.append(Bring(p, AtLeast, n, mat, C.FUSION_AREA))
            if EUDIf()(cond):
                acts = [SetScore(p, Subtract, pt, Custom), MoveUnit(All, z, p, C.FUSION_AREA, C.ZONE[i])]
                if mat:
                    acts.insert(0, RemoveUnitAt(n, mat, C.FUSION_AREA, p))
                DoActions(acts)
                stone[i] -= st
                lv += 1
                add_upgrade_for_unit(p, z, 1)
                _println(p, "\x1f【 각성 】 \x04영웅이 각성했습니다! \x07Lv.{} \x05(공격력 업그레이드 +1, 5단계는 쉴드 자동 회복)", lv)
            EUDEndIf()
            if EUDIf()([lv >= C.AWAKEN_MAX, Command(p, AtLeast, 1, z)]):
                DoActions(ModifyUnitShields(All, z, p, C.ANYWHERE, 100))
            EUDEndIf()


def raid_upgrades(boss):
    for grp, n in C.RAID_UPGRADES.get(boss, []):
        for p in HUM:
            if EUDIf()(f_playerexist(p) == 1):
                add_upgrade_for_unit(p, C.UPGRADE_GROUP[grp], n)
            EUDEndIf()


def _cast(i, p, h, text, atk, cd, loc, c, rm):
    acts = [CreateUnit(1, 13, loc, p), KillUnitAt(All, 13, loc, p)]
    if atk:
        acts += [CreateUnit(1, atk, loc, p), Order(atk, p, loc, Attack, loc)]
    DoActions(acts)
    rm << C.SKILL_DUR
    c << cd
    casts[(i, h)] += 1
    f_setcurpl(p)
    DoActions(DisplayText("\x13\x1f" + text))
    if h in C.HERO_VOICE:
        DoActions(PlayWAV("staredit\\wav\\%s.wav" % C.HERO_VOICE[h]))
    if h in C.SUMMON_ON_SKILL:
        sm = C.SUMMON_ON_SKILL[h]
        if EUDIf()(Command(p, Exactly, 0, sm)):
            DoActions(CreateUnit(1, sm, loc, p))
        EUDEndIf()


HERO_IDS = list(C.HERO_SKILLS)
held_now = {(i, h): EUDVariable(0) for i in range(len(HUM)) for h in HERO_IDS}
held_prev = {(i, h): EUDVariable(0) for i in range(len(HUM)) for h in HERO_IDS}
ORDER_HOLD = 107                                   # 홀드 (단축키 H)
ORDER_PATROL = 152                                 # 패트롤 (단축키 P)
HIT_SHIELD = 65535 * 256
ULT2_IDS = list(C.ULT2_SKILLS)
u2_now = {(i, h): EUDVariable(0) for i in range(len(HUM)) for h in ULT2_IDS}
u2_prev = {(i, h): EUDVariable(0) for i in range(len(HUM)) for h in ULT2_IDS}
u2_cool = {(i, h): EUDVariable(0) for i in range(len(HUM)) for h in ULT2_IDS}
u2_pos = [EUDVariable(0) for _ in HUM]


def _hero_name(h):
    t = C.HERO_SKILLS[h][0]
    return C.HERO_SHORT.get(h) or (t.split("「")[0].strip() if "「" in t else "영웅")


def hero_skills(tick):
    """영웅을 선택하고 H(홀드)를 누르면 궁극기. 쿨타임은 왼쪽 위 글줄에 표시 (본인 화면만)."""
    for i, p in enumerate(HUM):
        loc = C.SKILL_LOC_P[i]
        # 1) 홀드 명령을 받은 영웅 찾기 (게임 명령이라 모든 컴퓨터에서 같게 처리됨)
        for ptr, epd in EUDLoopPlayerUnit(p):
            ut = f_wread_epd(epd + 0x64 // 4, 0)
            # 타수형 영웅: 쉴드가 줄었으면 = 한 대 맞음 -> 체력 1 감소, 쉴드 다시 가득
            EUDSwitch(ut)
            for hu in C.HIT_HEROES:
                if EUDSwitchCase()(hu):
                    if EUDIf()(MemoryEPD(epd + 0x60 // 4, AtMost, HIT_SHIELD - 1)):
                        hp = f_dwread_epd(epd + 2)
                        if EUDIf()(hp >= 256 + 129):
                            f_dwwrite_epd(epd + 2, hp - 256)
                            DoActions(SetMemoryEPD(epd + 0x60 // 4, SetTo, HIT_SHIELD))
                        if EUDElse()():
                            # 마지막 1타 : 쉴드를 채우지 않음 -> 다음 공격에 쓰러짐
                            f_dwwrite_epd(epd + 2, 1)
                        EUDEndIf()
                    EUDEndIf()
                    EUDBreak()
            EUDEndSwitch()
            # 자가 회복 영웅 (메르엠 등): 1초마다 최대 체력의 n%
            for rh in [h_ for h_ in C.NEW_HEROES if h_.get("regen")]:
                if EUDIf()([ut == rh["unit"], _tick % 24 == 0]):
                    hpmax = f_dwread(0x662350 + 4 * rh["unit"])
                    hp = f_dwread_epd(epd + 2)
                    add = f_div(hpmax, 100)[0] * rh["regen"]
                    if EUDIf()(hp + add <= hpmax):
                        f_dwwrite_epd(epd + 2, hp + add)
                    if EUDElse()():
                        f_dwwrite_epd(epd + 2, hpmax)
                    EUDEndIf()
                EUDEndIf()
            # H(홀드) = 궁극기
            if EUDIf()(MemoryXEPD(epd + 0x4C // 4, Exactly, ORDER_HOLD << 8, 0xFF00)):
                EUDSwitch(ut)
                for h in HERO_IDS:
                    if EUDSwitchCase()(h):
                        held_now[(i, h)] << 1
                        EUDBreak()
                EUDEndSwitch()
            EUDEndIf()
            # P(패트롤) = 각성 궁극기 (클릭한 위치 기억)
            if EUDIf()(MemoryXEPD(epd + 0x4C // 4, Exactly, ORDER_PATROL << 8, 0xFF00)):
                EUDSwitch(ut)
                for h in ULT2_IDS:
                    if EUDSwitchCase()(h):
                        u2_now[(i, h)] << 1
                        u2_pos[i] << f_dwread_epd(epd + 0x58 // 4)
                        EUDBreak()
                EUDEndSwitch()
            EUDEndIf()
        # 2) 누른 순간에만 발동
        for h, (text, atk, nkill, cd) in C.HERO_SKILLS.items():
            c = cool[(i, h)]
            rm = skill_rm[(i, h)]
            hn, hp_ = held_now[(i, h)], held_prev[(i, h)]
            # 이 영웅이 없고 쿨타임·소환도 없으면 건너뜀 (트리거 부하 줄이기)
            EUDIfNot()([c == 0, rm == 0, hn == 0, hp_ == 0, Command(p, Exactly, 0, h)])
            if EUDIf()(c >= 1):
                c -= 1
            EUDEndIf()
            if EUDIf()([hn == 1, hp_ == 0]):
                # 홀드를 풀어 줘서 다음에 H 를 다시 누를 수 있게 함
                DoActions([MoveLocation(loc, h, p, C.ANYWHERE), Order(h, p, C.ANYWHERE, Move, loc)])
                if EUDIf()(c == 0):
                    if EUDIf()([Bring(P_RAID, AtLeast, 1, "Men", loc), Bring(p, AtLeast, 1, h, C.FIELD[i])]):
                        DoActions(KillUnitAt(nkill, "Men", loc, P_RAID))     # 내 필드 웨이브 즉사
                    EUDEndIf()
                    _cast(i, p, h, text, atk, cd, loc, c, rm)
                if EUDElse()():
                    _println(p, "\x08[궁극기] \x04%s \x05쿨타임 {}초 남음" % _hero_name(h), c // 24 + 1)
                EUDEndIf()
            EUDEndIf()
            hp_ << hn
            hn << 0
            if EUDIf()(rm >= 1):
                rm -= 1
                if EUDIf()(rm == 0):
                    if atk:
                        DoActions(RemoveUnit(atk, p))
                EUDEndIf()
            EUDEndIf()
            EUDEndIf()


RING = [(0, 0), (96, 0), (-96, 0), (0, 96), (0, -96), (64, 64), (-64, -64), (64, -64), (-64, 64)]
u2_act = [EUDVariable(0) for _ in HUM]      # 지금 나가고 있는 각성 궁극기 (영웅 번호, 0 = 없음)
u2_t = [EUDVariable(0) for _ in HUM]
u2_cx = [EUDVariable(0) for _ in HUM]
u2_cy = [EUDVariable(0) for _ in HUM]


@EUDFunc
def _area_damage(x0, y0, x1, y1, dmg):
    """사각형 안 적(보스 P6 / 레이드·웨이브 P8)에게 피해. 무적 유닛 제외, 일반 공격으로 마무리되도록 최소 1 남김"""
    d = dmg * 256
    for pl_ in (C.BOSS_OWNER, P_RAID):
        for ptr, epd in EUDLoopPlayerUnit(pl_):
            pos = f_dwread_epd(epd + 0x28 // 4)
            x = pos & 0xFFFF
            y = f_div(pos, 65536)[0]
            if EUDIf()([x >= x0, x <= x1, y >= y0, y <= y1,
                        MemoryXEPD(epd + 0xDC // 4, Exactly, 0, 0x04000000)]):
                hp = f_dwread_epd(epd + 2)
                if EUDIf()(hp >= d + 512):
                    f_dwwrite_epd(epd + 2, hp - d)
                if EUDElse()():
                    f_dwwrite_epd(epd + 2, 256)
                EUDEndIf()
            EUDEndIf()


FX_UNITS = sorted({u for d in C.ULT2_SKILLS.values() for u in list(d["fx"]) + [d["finale"]]} |
                  {u for c in getattr(C, "COMBOS", []) for u in list(c[5]) + [c[6]]})
ATK_UNITS = sorted({d["atk"] for d in C.ULT2_SKILLS.values() if d["atk"]})
KIND = {"attack": 1, "heal": 2, "seal": 3}
u2_kind, u2_fx0, u2_fx1, u2_fin, u2_dmg, u2_hits, u2_step, u2_dur, u2_atk, u2_dealt = (
    [EUDVariable(0) for _ in HUM] for _ in range(10))


@EUDFunc
def _fx_create(x, y, unit, pl, n):
    """(x, y) 에 연출 유닛을 만들고 바로 터뜨림"""
    TL = 0x58DC60 + 20 * (C.TEMP_LOC - 1)
    f_dwwrite(TL, x - 16)
    f_dwwrite(TL + 4, y - 16)
    f_dwwrite(TL + 8, x + 16)
    f_dwwrite(TL + 12, y + 16)
    EUDSwitch(pl)
    for q in HUM:
        if EUDSwitchCase()(q):
            EUDSwitch(unit)
            for fu in FX_UNITS:
                if EUDSwitchCase()(fu):
                    if EUDWhileNot()(n == 0):
                        DoActions(CreateUnit(1, fu, C.TEMP_LOC, q))
                        n -= 1
                    EUDEndWhile()
                    DoActions(KillUnitAt(All, fu, C.TEMP_LOC, q))
                    EUDBreak()
            EUDEndSwitch()
            EUDBreak()
    EUDEndSwitch()


def _ult2_tick(i, p):
    """진행 중인 각성 궁극기 1틱 (영웅마다 다른 값은 시전 때 변수에 담아 둠)"""
    t, cx, cy = u2_t[i], u2_cx[i], u2_cy[i]
    R = C.ULT2_RADIUS
    L = C.ULT2_LOC_P[i]
    # 연출: 6틱마다 범위 안 9개 지점을 돌며 폭발
    if EUDIf()(t + 12 <= u2_dur[i]):
        q6, r6 = f_div(t, 6)
        if EUDIf()(r6 == 0):
            k = f_div(q6, len(RING))[1]
            dx, dy = EUDVariable(), EUDVariable()
            EUDSwitch(k)
            for j, (ox, oy) in enumerate(RING):
                if EUDSwitchCase()(j):
                    dx << ox
                    dy << oy
                    EUDBreak()
            EUDEndSwitch()
            if EUDIf()(f_div(q6, 2)[1] == 0):
                _fx_create(cx + dx, cy + dy, u2_fx0[i], p, 1)
            if EUDElse()():
                _fx_create(cx + dx, cy + dy, u2_fx1[i], p, 1)
            EUDEndIf()
        EUDEndIf()
    EUDEndIf()
    # 피해 (공격·봉인)
    if EUDIf()([u2_kind[i] != KIND["heal"], t >= 12, u2_dealt[i] < u2_hits[i]]):
        if EUDIf()(f_div(t - 12, u2_step[i])[1] == 0):
            _area_damage(cx - R, cy - R, cx + R, cy + R, u2_dmg[i])
            u2_dealt[i] += 1
            for h, d in C.ULT2_SKILLS.items():
                if d.get("self_heal"):
                    if EUDIf()(u2_act[i] == h):
                        DoActions([ModifyUnitHitPoints(All, h, p, C.ANYWHERE, 100), ModifyUnitShields(All, h, p, C.ANYWHERE, 100)])
                    EUDEndIf()
            if EUDIf()(u2_dealt[i] == u2_hits[i]):
                _fx_create(cx, cy, u2_fin[i], p, 3)
            EUDEndIf()
        EUDEndIf()
    EUDEndIf()
    # 무한 힐
    if EUDIf()([u2_kind[i] == KIND["heal"], f_div(t, 8)[1] == 0]):
        for q in HUM:
            DoActions([ModifyUnitHitPoints(All, "Men", q, C.ANYWHERE, 100),
                       ModifyUnitShields(All, "Men", q, C.ANYWHERE, 100)])
        if EUDIf()(f_div(t, 24)[1] == 0):
            _fx_create(cx, cy, u2_fin[i], p, 2)
        EUDEndIf()
    EUDEndIf()
    # 봉인: 보스가 제자리에서 못 움직이고 공격도 못 함
    if EUDIf()([u2_kind[i] == KIND["seal"], f_div(t, 4)[1] == 0]):
        DoActions(Order("Any unit", C.BOSS_OWNER, L, Move, L))
    EUDEndIf()
    # 끝
    if EUDIf()(t >= u2_dur[i]):
        for au in ATK_UNITS:
            if EUDIf()(u2_atk[i] == au):
                DoActions(RemoveUnit(au, p))
            EUDEndIf()
        u2_act[i] << 0
    EUDEndIf()


def ult2_skills():
    """각성 궁극기: 9★/10★ 을 선택하고 P(패트롤) + 원하는 곳 클릭 -> 그 자리에 필살기"""
    import extras
    R = C.ULT2_RADIUS
    for i, p in enumerate(HUM):
        L = C.ULT2_LOC_P[i]
        LA = 0x58DC60 + 20 * (L - 1)
        for h, d in C.ULT2_SKILLS.items():
            c = u2_cool[(i, h)]
            hn, hp_ = u2_now[(i, h)], u2_prev[(i, h)]
            EUDIfNot()([c == 0, hn == 0, hp_ == 0])
            if EUDIf()(c >= 1):
                c -= 1
            EUDEndIf()
            if EUDIf()([hn == 1, hp_ == 0]):
                DoActions([MoveLocation(C.SKILL_LOC_P[i], h, p, C.ANYWHERE), Order(h, p, C.ANYWHERE, Move, C.SKILL_LOC_P[i])])
                if EUDIf()(extras.ult_learn[(i, h)] == 0):
                    _println(p, "\x08[각성 궁극기] \x04아직 각성하지 않았습니다. \x05(퓨전 띠에 올리기: %s point + 초월석 %d)"
                             % ("{:,}".format(C.ULT_AWAKEN_COST[0]), C.ULT_AWAKEN_COST[1]))
                if EUDElseIf()(c >= 1):
                    _println(p, "\x08[각성 궁극기] \x04%s \x05쿨타임 {}초 남음" % _hero_name(h), c // 24 + 1)
                if EUDElse()():
                    x = u2_pos[i] & 0xFFFF
                    y = f_div(u2_pos[i], 65536)[0]
                    if EUDIf()(x < R):
                        x << R
                    EUDEndIf()
                    if EUDIf()(y < R):
                        y << R
                    EUDEndIf()
                    u2_cx[i] << x
                    u2_cy[i] << y
                    f_dwwrite(LA, x - R)
                    f_dwwrite(LA + 4, y - R)
                    f_dwwrite(LA + 8, x + R)
                    f_dwwrite(LA + 12, y + R)
                    if d["atk"]:
                        DoActions([CreateUnit(2, d["atk"], L, p), Order(d["atk"], p, L, Attack, L)])
                    u2_act[i] << h
                    u2_t[i] << 0
                    u2_kind[i] << KIND[d["kind"]]
                    u2_fx0[i] << d["fx"][0]
                    u2_fx1[i] << d["fx"][1]
                    u2_fin[i] << d["finale"]
                    u2_dmg[i] << d["dmg"]
                    u2_hits[i] << d["hits"]
                    u2_step[i] << max(6, (d["dur"] - 12) // max(1, d["hits"]))
                    u2_dur[i] << d["dur"]
                    u2_atk[i] << d["atk"]
                    u2_dealt[i] << 0
                    c << C.ULT2_CD
                    DoActions(DisplayTextAll("\x13\x11━━━━━━━━━━ 【 각 성 궁 극 기 】 ━━━━━━━━━━\n\x13\x04" + d["name"]))
                    vo = C.ULT2_VOICE.get(h, C.HERO_VOICE.get(h))
                    if vo:
                        for q in HUM:
                            f_setcurpl(q)
                            DoActions(PlayWAV("staredit\\wav\\%s.wav" % vo))
                EUDEndIf()
            EUDEndIf()
            hp_ << hn
            hn << 0
            EUDEndIf()
        # 진행 중인 각성 궁극기
        if EUDIfNot()(u2_act[i] == 0):
            _ult2_tick(i, p)
            u2_t[i] += 1
        EUDEndIf()


def skill_hud(tick):
    """왼쪽 글줄 위쪽에 내 영웅 궁극기 쿨타임 (최대 C.HUD_LINES 명)"""
    if EUDIf()(tick % 12 == 0):
        for i, p in enumerate(HUM):
            if EUDIf()(f_getuserplayerid() == p):
                ln = EUDVariable(0)
                ln << 0
                for h in HERO_IDS:
                    if EUDIf()([Command(p, AtLeast, 1, h), ln < C.HUD_LINES]):
                        name = _hero_name(h)
                        if h in C.ULT2_SKILLS:
                            import extras
                            hc, pc, lr = cool[(i, h)], u2_cool[(i, h)], extras.ult_learn[(i, h)]
                            if EUDIf()(lr == 0):
                                f_printAt(ln, "\x1f【H】 \x04%s {}초 \x05│ 【P】 각성 필요" % name, hc // 24)
                            if EUDElse()():
                                f_printAt(ln, "\x1f【H】 \x04%s {}초 \x11│ 【P】 \x04{}초 \x05(0초 = READY)" % name, hc // 24, pc // 24)
                            EUDEndIf()
                        else:
                            if EUDIf()(cool[(i, h)] == 0):
                                f_printAt(ln, "\x1f【궁극기 H】 \x04%s \x07READY" % name)
                            if EUDElse()():
                                f_printAt(ln, "\x1f【궁극기 H】 \x04%s \x08{}초" % name, cool[(i, h)] // 24 + 1)
                            EUDEndIf()
                        ln += 1
                    EUDEndIf()
            EUDEndIf()
    EUDEndIf()


def special_heroes(chap_countdown_ok):
    for i, p in enumerate(HUM):
        # 스바루 사망회귀: 쓰러지면 플레이어존에서 다시 살아남
        if EUDIf()(Deaths(p, AtLeast, 1, C.U_SUBARU)):
            DoActions([SetDeaths(p, SetTo, 0, C.U_SUBARU), CreateUnit(1, C.U_SUBARU, C.ZONE[i], p)])
            revive[i] += 1
            _println(p, "\x05[사망회귀] \x04스바루가 되돌아왔습니다. \x05({}회)", revive[i])
            if EUDIf()(revive[i] == 100):
                DoActions(DisplayTextAll("\x13\x1f[SYSTEM] 스바루가 100회 사망회귀를 진행하였습니다."))
            EUDEndIf()
        EUDEndIf()
        # 사테라: 쓰러질 때마다 부활, 4번째마다 모든 궁극기 쿨타임 초기화 + 주변 아군 회복
        if EUDIf()(Deaths(p, AtLeast, 1, C.U_SATELLA)):
            DoActions([SetDeaths(p, SetTo, 0, C.U_SATELLA), CreateUnit(1, C.U_SATELLA, C.ZONE[i], p)])
            satella_d[i] += 1
            if EUDIf()(satella_d[i] >= 4):
                satella_d[i] << 0
                for h in C.HERO_SKILLS:
                    cool[(i, h)] << 0
                DoActions([DisplayTextAll("\x13\x10'사테라 4회 사망'\x04으로 보스 궁극기의 쿨타임이 초기화 되었습니다.\n\x13\x04[ 모든 캐릭터 궁극기 쿨타임 초기화 + 주변아군 체력 풀회복 ]"),
                           ModifyUnitHitPoints(All, "Men", p, C.ANYWHERE, 100)])
            EUDEndIf()
        EUDEndIf()
    # 에스카노르 정오: 카운트다운 1:02 ~ 1:12 동안 무적
    lo, hi = C.NOON_WINDOW
    if EUDIf()([chap_countdown_ok == 1, CountdownTimer(AtLeast, lo), CountdownTimer(AtMost, hi)]):
        DoActions([SetInvincibility(Enable, C.U_ESCANOR, p, C.ANYWHERE) for p in HUM])
        if EUDIf()([noon_flag == 0, Command(Force1, AtLeast, 1, C.U_ESCANOR)]):
            noon_flag << 1
            DoActions(DisplayTextAll("\x13\x11[SYSTEM] 정오 발동 [ 1분 2초 ~ 12초 불사 발동 ]\n\x13\x04에스카노르 「 그리고 지금 네놈에게 가장 안타까운 소식이 하나 추가되었다. 」"))
        EUDEndIf()
    if EUDElse()():
        if EUDIf()(noon_flag == 1):
            noon_flag << 0
            DoActions([SetInvincibility(Disable, C.U_ESCANOR, p, C.ANYWHERE) for p in HUM])
        EUDEndIf()
    EUDEndIf()


def frame(tick, playing):
    """game.afterTriggerExec 에서 매 프레임 호출. playing = 1 이면 게임 진행 중"""
    _tick << tick
    zones()
    fusion()
    myth_and_awaken()
    select_pads()
    bgm()
    if EUDIf()(playing == 1):
        dragonballs()
        dungeon()
        title_bonus(tick)
    EUDEndIf()
    hero_skills(tick)
    ult2_skills()
    skill_hud(tick)
    special_heroes(playing)
    party_raid(playing)
