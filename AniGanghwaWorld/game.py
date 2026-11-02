# -*- coding: utf-8 -*-
# =====================================================================
#  애니강화월드 새 버전 - 게임 로직 (챕터 / 에피소드 전체)
#   - 수치는 config.py, 개별칭호는 titles.py 에서 고칩니다.
# =====================================================================
from eudplib import *

import config as C
import titles
import systems
import extras

P_BOSS = C.BOSS_OWNER
P_WAVE = C.WAVE_OWNER

# ---------------------------------------------------------------------
#  스테이지 목록 펼치기
# ---------------------------------------------------------------------
# 지역별 원래 민가 수 (스테이지 시작할 때 부서진 만큼 다시 지음)
HOUSES = {56: 12, 93: 15}
P_ALLY = C.ALLY_COMPUTERS[0]          # P5 (주황) : 지켜야 하는 아군 영웅


def _aslist(v, n):
    if isinstance(v, (list, tuple)):
        return list(v) + [v[-1]] * (n - len(v))
    return [v] * n


def _norm(st):
    """스테이지 dict 의 빠진 항목을 기본값으로 채운다."""
    n = max(1, len(st.get("phases", [])))
    st.setdefault("check", C.BOSS_AREA)
    st["entries"] = _aslist(st.get("entry", st["arena"]), n)
    st["exits"] = st.get("exit")
    if st["exits"] is not None and not isinstance(st["exits"], (list, tuple)):
        st["exits"] = [st["exits"]]
    st["exits"] = st["exits"] or []
    st.setdefault("phase_spawn", [st.get("spawn", st["arena"])] + [None] * (n - 1))
    st.setdefault("lines", [""])
    st.setdefault("adds", [])
    st.setdefault("extra", [])
    st.setdefault("phase_extra", {})
    st.setdefault("phase_stats", {})
    st.setdefault("allies", [])
    st.setdefault("ringout", [])
    st.setdefault("timed", [])
    st.setdefault("hits", {})
    # 스킬을 쓰는 유닛 목록
    units = list(st.get("phases", [])) + [u for u, _ in st["extra"]]
    for k, lst in st["phase_extra"].items():
        units += [x[0] for x in lst]
    units += [t["unit"] for t in st["timed"]]
    if st["kind"] == "count":
        units.append(st["count"][0])
    st["skillmap"] = dict(C.BOSS_SKILLS)
    st["skillmap"].update(st.get("skills", {}))
    if st.get("guard"):
        units.append(st["guard"][1])
    seen = []
    for u in units:
        if u in st["skillmap"] and u not in seen:
            seen.append(u)
    st["skill_units"] = seen
    return st


STAGES = []          # (챕터 번호, 챕터 안 순서, 스테이지 dict)
for _ci, _ch in enumerate(C.CHAPTERS):
    for _si, _st in enumerate(_ch["stages"]):
        STAGES.append((_ci, _si, _norm(_st)))

# ---------------------------------------------------------------------
#  상태 값
# ---------------------------------------------------------------------
ST_DIFF, ST_WAVE, ST_BOSS, ST_BREAK, ST_CLEAR, ST_OVER = 0, 1, 2, 3, 4, 5

state = EUDVariable(ST_DIFF)
tick = EUDVariable(0)
diff = EUDVariable(0)          # 0 = EASY, 1 = HARD
chap = EUDVariable(0)          # 지금 챕터
gi = EUDVariable(0)            # 지금 스테이지 (전체 번호)
phase = EUDVariable(0)         # 보스 형태
spawned = EUDVariable(0)       # 여러 마리 처치 스테이지에서 나온 수
add_cd = EUDVariable(0)        # 마신족·거인 다시 생기기까지 남은 틱
entered = EUDVariable(0)       # 전멸 패배 판정용 (한 번이라도 들어왔는지)
stage_t = EUDVariable(0)       # 스테이지 시작 후 지난 틱
hits_left = EUDVariable(0)     # 타수 보스 남은 타수
hp_mult = EUDVariable(100)     # 보스 체력 배율 (난이도 x 인원수, %)
playing = EUDVariable(0)       # 웨이브·보스 진행 중이면 1
SHIELD_FULL = 65535 * 256

kill_step = [EUDVariable(0) for _ in C.HUMANS]

# 스킬 타이머: (스테이지, 보스, 스킬 번호)
skill_cnt = {}
skill_rm = {}
for _g, (_ci, _si, _st) in enumerate(STAGES):
    for _b in _st["skill_units"]:
        for _j in range(len(_st["skillmap"][_b])):
            skill_cnt[(_g, _b, _j)] = EUDVariable(0)
            skill_rm[(_g, _b, _j)] = EUDVariable(0)
# 힘의대회 보스 상태: 0 등장 전 / 1 첫 목숨 / 2 두 번째 목숨 / 3 탈락
timed_st = {}
for _g, (_ci, _si, _st) in enumerate(STAGES):
    for _k, _t in enumerate(_st["timed"]):
        timed_st[(_g, _k)] = EUDVariable(0)


# ---------------------------------------------------------------------
#  메시지 / 공통
# ---------------------------------------------------------------------
def say_all(text):
    if text:
        DoActions(DisplayTextAll(text))


def say_to(p, text):
    f_setcurpl(p)
    DoActions(DisplayText(text))


def defeat_all(reason):
    say_all("\x13\x08" + reason)
    for p in C.HUMANS:
        f_setcurpl(p)
        DoActions(Defeat())
    state << ST_OVER


def victory_all():
    for p in C.HUMANS:
        f_setcurpl(p)
        DoActions(Victory())
    state << ST_OVER


def give(p, ore, gas, pt):
    acts = []
    if ore:
        acts.append(SetResources(p, Add, ore, Ore))
    if gas:
        acts.append(SetResources(p, Add, gas, Gas))
    if pt:
        acts.append(SetScore(p, Add, pt, Custom))
    if acts:
        DoActions(acts)


# 보스 체력 배율 대상 유닛 (원래 체력을 시작할 때 기억해 둠)
SCALE_UNITS = set()
for _ci, _si, _st in STAGES:
    SCALE_UNITS |= set(_st.get("phases", [])) | {u for u, _ in _st["extra"]} | {t["unit"] for t in _st["timed"]}
    if _st["kind"] == "count":
        SCALE_UNITS.add(_st["count"][0])
    SCALE_UNITS -= set(_st["hits"])
base_hp = {u: EUDVariable(0) for u in sorted(SCALE_UNITS)}


def scale_hp(u, const_hp=None):
    """보스를 만들기 직전에 체력(units.dat)을 난이도·인원수 배율로 맞춘다."""
    if u not in base_hp:
        return
    base = const_hp if const_hp is not None else base_hp[u]
    hp = EUDVariable()
    hp << base * hp_mult // 100
    if EUDIf()(hp >= 16777215):
        hp << 16777215
    EUDEndIf()
    f_dwwrite(0x662350 + 4 * u, hp * 256)


def _set_x(addr, value, size):
    """units.dat 같은 표의 1·2·4바이트 칸 하나를 바꾼다."""
    base = addr & ~3
    sh = (addr & 3) * 8
    mask = ((1 << (size * 8)) - 1) << sh
    return SetMemoryX(base, SetTo, (value << sh) & 0xFFFFFFFF, mask)


def stat_actions(u, hp, sh, ar):
    """유닛 종류의 체력·쉴드·방어력을 게임 중에 바꾼다 (새로 생기는 유닛부터 적용)."""
    acts = []
    if hp is not None:
        acts.append(SetMemory(0x662350 + 4 * u, SetTo, min(hp, 16777215) * 256))
    if sh is not None:
        acts.append(_set_x(0x660E00 + 2 * u, min(sh, 65535), 2))
    if ar is not None:
        acts.append(_set_x(0x65FEC8 + u, min(ar, 255), 1))
    return acts


def _name_sid(u):
    """맵에 저장된 유닛 이름 문자열 번호 (UNIx)."""
    import struct
    unix = GetChkTokenized().getsection(b"UNIx")
    return struct.unpack_from("<H", unix, 228 * 14 + 2 * u)[0]


def rename_actions(u, name):
    """유닛 이름을 게임 중에 바꾼다 (지난 챕터 보스 칸을 새 에피소드 보스로 재활용)."""
    sid = _name_sid(u)
    if not sid:
        raise Exception("유닛 %d 은 맵에 이름이 지정되어 있지 않아 이름을 바꿀 수 없습니다." % u)
    return [SetMemory(0x191943C8 + 4 * sid, SetTo, Db(name.encode("utf-8") + b"\0") - 0x191943C8)]


# ---------------------------------------------------------------------
#  게임 시작 + 난이도 선택
# ---------------------------------------------------------------------
def on_start():
    DoActions([
        LeaderBoardScore(Custom, "강화포인트"),
        LeaderBoardComputerPlayers(Disable),
        SetCountdownTimer(SetTo, C.DIFF_WAIT),
        SetMissionObjectives(C.MISSION_TEXT),
    ])
    for p in C.HUMANS:
        DoActions(SetResources(p, SetTo, C.START_GAS, Gas))
    # 난이도 SELECT: 방에 있는 가장 앞 번호 플레이어에게 (P1 자리가 비어 있어도 고를 수 있게)
    made = EUDVariable(0)
    for p in C.HUMANS:
        if EUDIf()([made == 0, f_playerexist(p) == 1]):
            DoActions(CreateUnit(1, C.U_SELECT, C.SELECT_LOC, p))
            made << 1
        EUDEndIf()
    # 동맹: 사람(P1~P4) <-> 마을 컴퓨터(P5, P7) 아군 / 보스(P6), 웨이브(P8) 적
    for p in C.HUMANS:
        f_setcurpl(p)
        DoActions([SetAllianceStatus(q, Ally) for q in C.ALLY_COMPUTERS] +
                  [SetAllianceStatus(q, Enemy) for q in (P_BOSS, P_WAVE)])
    for q in C.ALLY_COMPUTERS:
        f_setcurpl(q)
        DoActions([SetAllianceStatus(Force1, Ally)])
    say_all("\x13\x1f애니강화월드 \x04새 버전 \x05(%s)" % C.VERSION_TEXT)
    say_all("\x13" + C.GAME_START_TEXT)
    say_all("\x13\x05( 강화표·퓨전·신화 조합은 F10 -> 미션 오브젝트에서 확인 )")
    say_all(C.DIFF_TEXT)
    titles.ShowTitles()


def start_chapter(ci):
    ch = C.CHAPTERS[ci]
    chap << ci
    acts = [SetCountdownTimer(SetTo, ch["first"])]
    for u, name, hp, sh, ar in ch.get("units", []):
        acts += rename_actions(u, name) + stat_actions(u, hp, sh, ar)
    DoActions(acts)
    for u, name, hp, sh, ar in ch.get("units", []):
        if u in base_hp:
            base_hp[u] << hp
    for d in (0, 1, 2):
        if EUDIf()(diff == d):
            say_all("\x13\x1f" + ch["intro"][min(d, 1)])
            if d == 2:
                say_all("\x13\x08[HELL] \x04웨이브 패배조건 %d마리, 보스 체력 %d%%" % (wave_limits(ch)[2], C.BOSS_HP_DIFF[2]))
        EUDEndIf()
    # 웨이브 안내판
    wname, whp, wsh = C.WAVE_INFO.get(ch["wave"], ("?", "?", "?"))
    for u, name, hp, sh, ar in ch.get("units", []):
        if u == ch["wave"]:
            wname, whp, wsh = name, "{:,}".format(hp), "{:,}".format(sh)
    say_all(C.WAVE_BOARD % (ci + 1, wname, whp, wsh))
    systems.on_chapter_start(ci)
    if ch.get("story"):
        say_all(ch["story"])
    # 다음 챕터 첫 스테이지가 미리 입장형이면 안내
    g0 = [g for g, (c, s, st) in enumerate(STAGES) if c == ci][0]
    if STAGES[g0][2].get("pre_entry"):
        say_all("\x13\x07지금부터 시작 전까지 출전 발판으로 1명씩 미리 입장할 수 있습니다.")
    state << ST_WAVE


def wave_limits(ch):
    """(EASY, HARD, HELL) 웨이브 패배 마릿수"""
    if "limit" in ch:
        e, h = ch["limit"]
        return [e, h, max(h - 20, 30)]
    return list(C.WAVE_DEFEAT_LIMIT3)


def choose_difficulty():
    p1 = Force1
    pick = [(2, Bring(p1, AtLeast, 1, C.U_SELECT, C.HELL_LOC)),
            (1, Bring(p1, AtLeast, 1, C.U_SELECT, C.HARD_LOC)),
            (0, Bring(p1, AtLeast, 1, C.U_SELECT, C.EASY_LOC)),
            (0, CountdownTimer(AtMost, 0))]
    for d, cond in pick:
        if EUDIf()([state == ST_DIFF, tick >= 24, cond]):
            diff << d
            DoActions([RemoveUnitAt(All, C.U_SELECT, loc, p1)
                       for loc in (C.SELECT_LOC, C.EASY_LOC, C.HARD_LOC, C.HELL_LOC)])
            # 인원수
            n = EUDVariable(0)
            for p in C.HUMANS:
                if EUDIf()(f_playerexist(p) == 1):
                    n += 1
                EUDEndIf()
            for k in range(1, 5):
                if EUDIf()(n == k):
                    hp_mult << C.BOSS_HP_DIFF[d] * C.BOSS_HP_PLAYERS[k - 1] // 100
                    say_all("\x13%s난이도 : %s \x04( %d인 / 보스 체력 %d%% )"
                            % ("\x07" if d == 0 else "\x08", C.DIFF_NAMES[d], k,
                               C.BOSS_HP_DIFF[d] * C.BOSS_HP_PLAYERS[k - 1] // 100))
                EUDEndIf()
            if C.DIFF_END_CHAPTER[d]:
                say_all("\x13\x05(%s 는 챕터 %d 까지입니다)" % (C.DIFF_NAMES[d], C.DIFF_END_CHAPTER[d]))
            systems.on_select_done()
            start_chapter(0)
        EUDEndIf()


# ---------------------------------------------------------------------
#  스테이지 진행
# ---------------------------------------------------------------------
def rebuild_houses(loc):
    n = HOUSES.get(loc, 0)
    for k in range(n):
        if EUDIf()(Bring(C.U_HOUSE_OWNER, Exactly, k, C.U_HOUSE, loc)):
            DoActions(CreateUnit(n - k, C.U_HOUSE, loc, C.U_HOUSE_OWNER))
        EUDEndIf()


RENAMED_AT = {}
for _ci, _ch in enumerate(C.CHAPTERS):
    for _u, *_r in _ch.get("units", []):
        RENAMED_AT.setdefault(_u, _ci)


def voice_all(u, ci):
    """보스 등장 음성 (재활용된 보스 칸은 원래 보스 목소리라 생략)"""
    if u in C.BOSS_VOICE and ci < RENAMED_AT.get(u, 999):
        for p in C.HUMANS:
            f_setcurpl(p)
            DoActions(PlayWAV("staredit\\wav\\%s.wav" % C.BOSS_VOICE[u]))


STAGE_CH = {id(_st): _ci for _ci, _si, _st in STAGES}


def create_boss(u, loc, st, k):
    """보스 형태 하나를 만든다 (체력 배율 적용 후). 남은 액션 목록을 돌려줌."""
    acts = []
    stats = st["phase_stats"].get(k)
    if stats:
        DoActions(stat_actions(u, *stats))
        scale_hp(u, stats[0])
    else:
        scale_hp(u)
    voice_all(u, STAGE_CH.get(id(st), 0))
    acts.append(CreateUnit(1, u, loc, P_BOSS))
    for x in st["phase_extra"].get(k, []):
        acts.append(CreateUnit(1, x[0], x[1], P_BOSS))
        if len(x) > 2 and x[2]:
            acts.append(SetInvincibility(Enable, x[0], P_BOSS, C.ANYWHERE))
    return acts


def spawn_stage(g):
    ci, si, st = STAGES[g]
    acts = [SetCountdownTimer(SetTo, st["time"])]
    for u, *rest in st.get("unit_stats", []):
        acts += stat_actions(u, *rest)
    for u, n in st["hits"].items():
        # 타수 보스: 체력을 아주 크게 두고 매 프레임 되돌림 (한 프레임에 아무리 세게 맞아도 1타)
        acts += stat_actions(u, C.HIT_BOSS_HP, 0, 255) + [_set_x(0x6647B0 + u, 0, 1)]
    if st["kind"] == "count":
        u, total, alive = st["count"]
        acts.append(SetDeaths(P_BOSS, SetTo, 0, u))
        spawned << 0
        scale_hp(u)
    elif st["kind"] != "tournament":
        if st.get("phases"):
            acts += create_boss(st["phases"][0], st["phase_spawn"][0], st, 0)
            if st["phases"][0] in st["hits"]:
                hits_left << st["hits"][st["phases"][0]]
        for u, loc in st["extra"]:
            scale_hp(u)
            acts.append(CreateUnit(1, u, loc, P_BOSS))
    for u, n in st["allies"]:
        acts.append(CreateUnit(n, u, st.get("ally_loc", st["arena"]), P_ALLY))
    DoActions(acts)
    if st.get("village"):
        rebuild_houses(st["village"])
    for key, v in skill_cnt.items():
        if key[0] == g:
            v << 0
    for key, v in timed_st.items():
        if key[0] == g:
            v << 0
    say_all("\x13\x1f" + st["intro"])
    say_all("\x13\x04" + st["lines"][0])
    phase << 0
    entered << 0
    stage_t << 0
    add_cd << 0
    state << ST_BOSS


def heal_humans(area):
    acts = []
    for p in C.HUMANS:
        acts += [ModifyUnitHitPoints(All, "Men", p, area, 100),
                 ModifyUnitShields(All, "Men", p, area, 100)]
    DoActions(acts)


def clear_stage(g):
    ci, si, st = STAGES[g]
    say_all("\x13\x1f" + st["clear"])
    for p in C.HUMANS:
        give(p, *st["reward"])
        DoActions([MoveUnit(All, "Men", p, C.BOSS_AREA, C.FIELD[p]),
                   MoveUnit(All, "Men", p, st["arena"], C.FIELD[p]),
                   MoveUnit(All, "Men", p, st["check"], C.FIELD[p])])
    DoActions([RemoveUnitAt(All, "Men", C.BOSS_AREA, P_BOSS),
               RemoveUnitAt(All, "Men", st["arena"], P_BOSS),
               RemoveUnitAt(All, "Men", st["check"], P_BOSS),
               RemoveUnitAt(All, "Men", st["arena"], P_ALLY)])
    if g + 1 < len(STAGES):
        gi << g + 1
        if STAGES[g + 1][0] == ci:
            DoActions(SetCountdownTimer(SetTo, C.BREAK_TIME))
            state << ST_BREAK
            if STAGES[g + 1][2].get("pre_entry"):
                say_all("\x13\x07다음 스테이지는 시작 전에만 입장할 수 있습니다. 출전 발판으로 1명씩 들어가세요!")
        else:
            ends = [d for d in range(3) if C.DIFF_END_CHAPTER[d] == ci + 1]
            if ends:
                if EUDIf()([diff == d for d in ends] if len(ends) == 1 else diff == ends[0]):
                    say_all(C.DIFF_END_TEXT[ends[0]])
                    DoActions(SetCountdownTimer(SetTo, 10))
                    state << ST_CLEAR
                if EUDElse()():
                    start_chapter(ci + 1)
                EUDEndIf()
            else:
                start_chapter(ci + 1)
    else:
        say_all(C.ALL_CLEAR_TEXT)
        DoActions(SetCountdownTimer(SetTo, 10))
        state << ST_CLEAR


def boss_skills(g, st):
    """이 스테이지 보스들의 스킬 (원본 주기 기준)."""
    room = st["check"]
    for b in st["skill_units"]:
        skills = st["skillmap"][b]
        if EUDIf()([state == ST_BOSS, gi == g, Command(P_BOSS, AtLeast, 1, b)]):
            DoActions(MoveLocation(C.SKILL_LOC, b, P_BOSS, C.ANYWHERE))
            for p in C.HUMANS:
                if EUDIf()(Bring(p, AtLeast, 1, "Men", room)):
                    DoActions(MoveLocation(C.TARGET_LOC, "Men", p, room))
                EUDEndIf()
            if st["kind"] != "escape":      # 도망가는 보스(2-2)는 우리 유닛을 쫓지 않고 숲 출구로만 이동
                if EUDIf()([tick % 24 == 0, Bring(Force1, AtLeast, 1, "Men", room)]):
                    DoActions(Order(b, P_BOSS, C.ANYWHERE, Attack, C.TARGET_LOC))
                EUDEndIf()
            for j, sk in enumerate(skills):
                cnt = skill_cnt[(g, b, j)]
                rm = skill_rm[(g, b, j)]
                if EUDIf()(Bring(Force1, AtLeast, 1, "Men", room)):
                    cnt += 1
                EUDEndIf()
                if EUDIf()(cnt >= sk["every"]):
                    cnt << 0
                    acts = []
                    if sk.get("text"):
                        acts.append(DisplayTextAll(sk["text"]))
                    if sk["effect"]:
                        acts += [CreateUnit(1, sk["effect"], C.SKILL_LOC, P_BOSS),
                                 KillUnitAt(All, sk["effect"], C.SKILL_LOC, P_BOSS)]
                    if sk["pull"]:
                        for p in C.HUMANS:
                            acts.append(MoveUnit(All, "Men", p, room, C.SKILL_LOC))
                    if sk["shield"]:
                        acts.append(ModifyUnitShields(All, b, P_BOSS, C.ANYWHERE, 100))
                    if sk.get("heal"):
                        acts.append(ModifyUnitHitPoints(All, b, P_BOSS, C.ANYWHERE, 100))
                    if sk["village"]:
                        acts.append(KillUnitAt(sk["village"], C.U_HOUSE, room, C.U_HOUSE_OWNER))
                    if sk.get("hpcut"):
                        for p in C.HUMANS:
                            acts.append(ModifyUnitHitPoints(All, "Men", p, room, sk["hpcut"]))
                    if sk.get("jump"):
                        # 보스가 대상(우리 유닛 / 주황 아군) 앞으로 순간이동, 대상 쉴드 0
                        who = P_ALLY if sk["jump"] == "ally" else None
                        if who is not None:
                            acts.append(MoveLocation(C.TARGET_LOC, "Men", who, room))
                        acts.append(MoveUnit(1, b, P_BOSS, C.ANYWHERE, C.TARGET_LOC))
                        for p in C.HUMANS + ([who] if who is not None else []):
                            acts.append(ModifyUnitShields(All, "Men", p, C.TARGET_LOC, 0))
                    if sk.get("summon"):
                        acts.append(CreateUnit(1, sk["summon"], C.SKILL_LOC, P_BOSS))
                    if sk["attacker"]:
                        acts += [CreateUnit(1, sk["attacker"], C.SKILL_LOC, P_BOSS),
                                 Order(sk["attacker"], P_BOSS, C.SKILL_LOC, Attack, C.TARGET_LOC)]
                    DoActions(acts)
                    if sk["attacker"]:
                        rm << max(sk["dur"], 1)
                EUDEndIf()
                if sk["attacker"]:
                    if EUDIf()(rm >= 1):
                        rm -= 1
                        if EUDIf()(rm == 0):
                            DoActions(RemoveUnitAt(1, sk["attacker"], C.ANYWHERE, P_BOSS))
                        EUDEndIf()
                    EUDEndIf()
        EUDEndIf()


def stage_logic(g):
    global spawned, add_cd, entered, stage_t, hits_left
    ci, si, st = STAGES[g]
    kind = st["kind"]

    def on():
        return [state == ST_BOSS, gi == g]

    stage_t += 1

    # --- 보스 형태 변화 / 처치
    if kind in ("kill", "escape"):
        phases = st["phases"]
        for k, u in enumerate(phases):
            if EUDIf()(on() + [phase == k, Command(P_BOSS, Exactly, 0, u)]):
                for x in st["phase_extra"].get(k, []):
                    DoActions(RemoveUnit(x[0], P_BOSS))
                if k + 1 < len(phases):
                    loc = st["phase_spawn"][k + 1] or C.SKILL_LOC
                    acts = create_boss(phases[k + 1], loc, st, k + 1)
                    if "phase_time" in st:
                        acts.append(SetCountdownTimer(SetTo, st["phase_time"][k + 1]))
                    if phases[k + 1] in st["hits"]:
                        hits_left << st["hits"][phases[k + 1]]
                    if st.get("follow") and st["phase_spawn"][k + 1]:
                        for p in C.HUMANS:
                            acts.append(MoveUnit(All, "Men", p, st["check"], st["entries"][k + 1]))
                    DoActions(acts)
                    if st.get("heal_on_phase"):
                        heal_humans(st["check"])
                    say_all("\x13\x04" + st["lines"][min(k + 1, len(st["lines"]) - 1)])
                    phase << k + 1
                else:
                    clear_stage(g)
            EUDEndIf()
    elif kind == "survive":
        bosses = [Command(P_BOSS, Exactly, 0, u) for u, _ in st["extra"]]
        if EUDIf()(on() + bosses):
            clear_stage(g)
        EUDEndIf()
        if EUDIf()(on() + [CountdownTimer(AtMost, 0)]):
            clear_stage(g)
        EUDEndIf()
    elif kind == "count":
        u, total, alive = st["count"]
        if EUDIf()(on() + [spawned < total, Command(P_BOSS, AtMost, alive - 1, u)]):
            DoActions(CreateUnit(1, u, st["arena"], P_BOSS))
            spawned += 1
        EUDEndIf()
        if EUDIf()(on() + [Deaths(P_BOSS, AtLeast, total, u)]):
            clear_stage(g)
        EUDEndIf()
    elif kind == "tournament":
        # 시간에 맞춰 보스 입장, 목숨 2개, 두 번째까지 쓰러뜨리면 탈락 + 우리 유닛 회복
        for k, t in enumerate(st["timed"]):
            v = timed_st[(g, k)]
            if EUDIf()(on() + [v == 0, stage_t >= t["at"] * 24]):
                scale_hp(t["unit"])
                voice_all(t["unit"], ci)
                DoActions([CreateUnit(1, t["unit"], t.get("loc", st["arena"]), P_BOSS)])
                say_all("\x13\x04" + t["lines"][0])
                v << 1
            EUDEndIf()
            if EUDIf()(on() + [v == 1, Command(P_BOSS, Exactly, 0, t["unit"])]):
                DoActions([CreateUnit(1, t["unit"], C.SKILL_LOC, P_BOSS)])
                say_all("\x13\x04" + t["lines"][-1])
                v << 2
            EUDEndIf()
            if EUDIf()(on() + [v == 2, Command(P_BOSS, Exactly, 0, t["unit"])]):
                say_all("\x13\x1f" + t["out"])
                heal_humans(st["check"])
                v << 3
            EUDEndIf()
        if EUDIf()(on() + [timed_st[(g, k)] == 3 for k in range(len(st["timed"]))]):
            clear_stage(g)
        EUDEndIf()
        if EUDIf()(on() + [CountdownTimer(AtMost, 0)]):
            say_all("\x13\x07힘의대회 종료까지 살아남았습니다!")
            clear_stage(g)
        EUDEndIf()

    # --- 패배 조건
    if kind not in ("survive", "tournament"):
        if EUDIf()(on() + [CountdownTimer(AtMost, 0)]):
            defeat_all("보스 제한시간 초과 - You Defeat")
        EUDEndIf()
    if st.get("village"):
        if EUDIf()(on() + [Bring(C.U_HOUSE_OWNER, Exactly, 0, C.U_HOUSE, st["village"])]):
            defeat_all("마을이 모두 파괴되었습니다 - You Defeat")
        EUDEndIf()
    if kind == "escape":
        if EUDIf()(on() + [Bring(P_BOSS, AtLeast, 1, st["phases"][-1], st["goal"])]):
            defeat_all("여성형 거인이 숲을 빠져나갔습니다 - You Defeat")
        EUDEndIf()
    if st.get("protect"):
        if EUDIf()(on() + [stage_t >= 48, Bring(P_ALLY, Exactly, 0, "Men", st["arena"])]):
            defeat_all("주황 아군 유닛이 모두 쓰러졌습니다 - You Defeat")
        EUDEndIf()
    if st.get("protect_unit"):
        u = st["protect_unit"]
        if EUDIf()(on() + [stage_t >= 48, Command(P_ALLY, Exactly, 0, u)]):
            defeat_all(st.get("protect_text", "지켜야 할 아군이 쓰러졌습니다 - You Defeat"))
        EUDEndIf()
    if st.get("wipe"):
        if EUDIf()(on() + [Bring(Force1, AtLeast, 1, "Men", st["check"])]):
            entered << 1
        EUDEndIf()
        if EUDIf()(on() + [entered == 1, Bring(Force1, Exactly, 0, "Men", st["check"])]):
            defeat_all("출전한 유닛이 전멸했습니다 - You Defeat")
        EUDEndIf()

    # --- 타수 보스: 공격력과 상관없이 한 번 맞을 때마다 1 깎임 (체력 표시 = 남은 타수)
    for u, n in st["hits"].items():
        if EUDIf()(on() + [Command(P_BOSS, AtLeast, 1, u)]):
            for ptr, epd in EUDLoopPlayerUnit(P_BOSS):
                if EUDIf()(MemoryXEPD(epd + 0x64 // 4, Exactly, u, 0xFFFF)):
                    if EUDIf()(MemoryEPD(epd + 2, AtMost, C.HIT_BOSS_HP * 256 - 1)):
                        if EUDIf()(hits_left >= 1):
                            hits_left -= 1
                        EUDEndIf()
                        DoActions(SetMemoryEPD(epd + 2, SetTo, C.HIT_BOSS_HP * 256))
                    EUDEndIf()
                EUDEndIf()
            if EUDIf()(hits_left == 0):
                DoActions(KillUnit(u, P_BOSS))
            EUDEndIf()
            # 남은 타수 표시 (모든 플레이어 화면 왼쪽 글줄)
            if EUDIf()(tick % 12 == 7):
                f_printAt(C.HIT_HUD_LINE, "\x08【 타수 보스 】 \x04남은 타수 \x07{} \x04/ %d \x05(공격력과 상관없이 1대 = 1타)" % n, hits_left)
            EUDEndIf()
        EUDEndIf()

    # --- 호위가 살아 있으면 보스 무적 (예: 환영여단이 있으면 클로로 무적)
    if st.get("guard"):
        b, gu = st["guard"]
        if EUDIf()(on() + [tick % 12 == 0, Command(P_BOSS, AtLeast, 1, gu)]):
            DoActions(SetInvincibility(Enable, b, P_BOSS, C.ANYWHERE))
        if EUDElseIf()(on() + [tick % 12 == 0]):
            DoActions(SetInvincibility(Disable, b, P_BOSS, C.ANYWHERE))
        EUDEndIf()

    # --- 장외 (힘의대회 테두리)
    for loc in st["ringout"]:
        for p in C.HUMANS:
            if EUDIf()(on() + [Bring(p, AtLeast, 1, "Men", loc)]):
                DoActions(KillUnitAt(All, "Men", loc, p))
                say_to(p, "\x08[장외] \x04테두리 진흙 필드에 닿아 퇴장당했습니다!")
            EUDEndIf()

    # --- 다시 생기는 적 (거인, 마신족, 괴인)
    for u, loc in st["adds"]:
        if EUDIf()(on() + [Command(P_BOSS, Exactly, 0, u)]):
            add_cd += 1
            if EUDIf()(add_cd >= C.ADD_RESPAWN):
                DoActions(CreateUnit(1, u, loc, P_BOSS))
                add_cd << 0
            EUDEndIf()
        EUDEndIf()

    # --- 이동 명령 (24틱 = 약 1초마다)
    if EUDIf()(on() + [tick % 24 == 12]):
        acts = []
        if kind == "escape":
            acts.append(Order(st["phases"][-1], P_BOSS, C.ANYWHERE, Move, st["goal"]))
        elif st.get("march"):
            acts.append(Order("Men", P_BOSS, st["arena"], Attack, st["march"]))
            for u, loc in st["adds"]:
                acts.append(Order(u, P_BOSS, C.ANYWHERE, Attack, st["march"]))
        if acts:
            DoActions(acts)
    EUDEndIf()

    # --- 출전 (미리 입장형이 아니면 보스전 중에)
    if not st.get("pre_entry"):
        sortie_logic(g, st, on)
    exit_logic(g, st, on)


def sortie_logic(g, st, on):
    for p in C.HUMANS:
        for k, ent in enumerate(st["entries"]):
            cond = on() + [Bring(p, AtLeast, 1, "Men", C.SORTIE[p]),
                           Bring(p, Exactly, 0, "Men", st["check"])]
            if len(set(st["entries"])) > 1:
                cond.append(phase == k)
            if EUDIf()(cond):
                DoActions(MoveUnit(1, "Men", p, C.SORTIE[p], ent))
                say_to(p, "\x07출전! \x04(전투 지역에는 1마리만 들어갈 수 있습니다)")
            EUDEndIf()
            if len(set(st["entries"])) == 1:
                break


def exit_logic(g, st, on):
    blk = st.get("exit_block")
    for p in C.HUMANS:
        for ex in st["exits"]:
            cond = on() + [Bring(p, AtLeast, 1, "Men", ex)]
            if blk:
                cond.append(Bring(P_BOSS, Exactly, 0, blk, st["arena"]))
            if EUDIf()(cond):
                DoActions(MoveUnit(All, "Men", p, ex, C.FIELD[p]))
            EUDEndIf()
            if blk:
                if EUDIf()(on() + [tick % 72 == 0, Bring(p, AtLeast, 1, "Men", ex),
                                   Bring(P_BOSS, AtLeast, 1, blk, st["arena"])]):
                    say_to(p, "\x08%s \x04(먼저 처치하세요)" % st.get("exit_block_text", "적이 있어서 나갈 수 없습니다!"))
                EUDEndIf()


def chapter_flow():
    choose_difficulty()
    # 미리 입장형 스테이지: 시작 전(대기·쉬는 시간)에만 출전
    for g, (ci, si, st) in enumerate(STAGES):
        if st.get("pre_entry"):
            pre = lambda g=g: [gi == g, state >= ST_WAVE, state <= ST_BREAK, state != ST_BOSS]
            sortie_logic(g, st, pre)
    if EUDIf()([state == ST_WAVE, CountdownTimer(AtMost, 0)]):
        for g, (ci, si, st) in enumerate(STAGES):
            if si == 0:
                if EUDIf()(gi == g):
                    spawn_stage(g)
                EUDEndIf()
    EUDEndIf()
    if EUDIf()([state == ST_BREAK, CountdownTimer(AtMost, 0)]):
        for g, (ci, si, st) in enumerate(STAGES):
            if si > 0:
                if EUDIf()(gi == g):
                    spawn_stage(g)
                EUDEndIf()
    EUDEndIf()
    # 테스트 명령어 /스킵 : 대기 중이면 바로 보스, 보스전이면 바로 클리어
    if EUDIf()(extras.skip_req == 1):
        extras.skip_req << 0
        if EUDIf()([state >= ST_WAVE, state != ST_BOSS, state <= ST_BREAK]):
            DoActions(SetCountdownTimer(SetTo, 0))
        EUDEndIf()
        if EUDIf()(state == ST_BOSS):
            g_now = EUDVariable()
            g_now << gi                      # 클리어하면 gi 가 바뀌므로 지금 번호를 따로 기억 (연쇄 클리어 방지)
            for g, (ci, si, st) in enumerate(STAGES):
                if EUDIf()(g_now == g):
                    clear_stage(g)
                EUDEndIf()
        EUDEndIf()
    EUDEndIf()
    for g, (ci, si, st) in enumerate(STAGES):
        if EUDIf()([state == ST_BOSS, gi == g]):
            stage_logic(g)
            boss_skills(g, st)
            if ci + 1 >= C.TELE_FROM_CHAPTER and st["kind"] != "escape":
                ev, cut = C.TELE_RULE(st["name"])
                if EUDIf()([f_div(stage_t, ev)[1] == ev - 1, Bring(Force1, AtLeast, 1, "Men", st["check"])]):
                    extras.tele_start(st["check"], cut)
                EUDEndIf()
        EUDEndIf()
    if EUDIf()([state == ST_CLEAR, CountdownTimer(AtMost, 0)]):
        victory_all()
    EUDEndIf()


# ---------------------------------------------------------------------
#  웨이브 (챕터마다 유닛·패배 마릿수가 바뀜)
# ---------------------------------------------------------------------
def waves():
    for p in C.HUMANS:
        if EUDIf()([state >= ST_WAVE, state <= ST_BREAK, f_playerexist(p) == 1]):
            DoActions(MoveUnit(All, "Men", P_WAVE, C.CORNER[p], C.LOOP_TOP[p]))
            if EUDIf()(Bring(P_WAVE, Exactly, 0, "Men", C.SPAWN[p])):
                for ci, ch in enumerate(C.CHAPTERS):
                    if EUDIf()(chap == ci):
                        DoActions(CreateUnit(1, ch["wave"], C.SPAWN[p], P_WAVE))
                    EUDEndIf()
            EUDEndIf()
            if EUDIf()(tick % 8 == 0):
                DoActions(Order("Men", P_WAVE, C.FIELD[p], Attack, C.CORNER[p]))
            EUDEndIf()
            for ci, ch in enumerate(C.CHAPTERS):
                lim3 = wave_limits(ch)
                for d in (0, 1, 2):
                    lim = lim3[d]
                    if EUDIf()([chap == ci, diff == d, Bring(P_WAVE, AtLeast, lim, "Men", C.FIELD[p])]):
                        defeat_all("웨이브 %d마리 초과 - You Defeat" % lim)
                    EUDEndIf()
        EUDEndIf()


# ---------------------------------------------------------------------
#  뽑기 (게이트웨이 / 랜덤뽑기)
# ---------------------------------------------------------------------
def _is_hidden(u):
    return any(u == line[0] for line in C.HIDDEN_LINES.values())


def gacha():
    for p in C.HUMANS:
        # 게이트웨이에서 나온 유닛은 필드로
        DoActions(MoveUnit(All, "Men", p, C.GATEWAY_AREA, C.FIELD[p]))

        if EUDIf()(Command(p, AtLeast, 1, C.U_RANDOM_DRAW)):
            DoActions(RemoveUnitAt(1, C.U_RANDOM_DRAW, C.ANYWHERE, p))
            r = f_dwrand() % 10000
            for lo, hi, u in C.RANDOM_TABLE:
                if EUDIf()([r >= lo, r <= hi]):
                    if u in C.UNIQUE_UNITS:
                        nobody = [Command(q, Exactly, 0, u) for q in C.HUMANS]
                        if EUDIf()(nobody):
                            DoActions(CreateUnit(1, u, C.FIELD[p], p))
                            say_all("\x13\x1f[특수] \x04전설 유닛이 등장했습니다!")
                        if EUDElse()():
                            DoActions(CreateUnit(1, C.RANDOM_TABLE[0][2], C.FIELD[p], p))
                        EUDEndIf()
                    else:
                        DoActions(CreateUnit(1, u, C.FIELD[p], p))
                        if _is_hidden(u):
                            say_to(p, "\x1f[히든] \x04히든 유닛 획득!")
                EUDEndIf()
        EUDEndIf()


# ---------------------------------------------------------------------
#  강화존
# ---------------------------------------------------------------------
def _steps():
    steps = []
    for line in C.NORMAL_LINES.values():
        for k in range(len(line) - 1):
            steps.append((line[k], line[k + 1], C.GANG_COST[k], C.GANG_RATE[k]))
    for line in C.HIDDEN_LINES.values():
        for k in range(len(line) - 1):
            base = C.HIDDEN_STEP_BASE[k]
            steps.append((line[k], line[k + 1],
                          C.GANG_COST[base] * C.HIDDEN_COST_MUL,
                          C.GANG_RATE[base] // C.HIDDEN_RATE_DIV))
    return steps


STEPS = _steps()
HIDDEN_FROM = {line[k] for line in C.HIDDEN_LINES.values() for k in range(len(line) - 1)}   # 히든은 천장 없음 (원본 "천장 ... (히든X)")
pity = {(p, s[0]): EUDVariable(0) for p in C.HUMANS for s in STEPS}
TOP_UNITS = [line[-1] for line in C.NORMAL_LINES.values()] + \
            [line[-1] for line in C.HIDDEN_LINES.values()]
# 퓨전·신화 유닛은 강화존에 넣어도 돌려보냄 (조합은 플레이어존 퓨전 띠에서)
FUSION_UNITS = sorted({r for r, *_ in C.FUSIONS} | {r for r, *_ in C.MYTHS} | set(C.UNIQUE_UNITS))


def upgrade():
    for p in C.HUMANS:
        zone = C.UPGRADE_ZONE
        for frm, to, cost, rate in STEPS:
            if EUDIf()(Bring(p, AtLeast, 1, frm, zone)):
                if EUDIf()(Score(p, Custom, AtLeast, cost)):
                    DoActions(SetScore(p, Subtract, cost, Custom))
                    pv = pity[(p, frm)]
                    if EUDIf()(f_dwrand() % 100 < rate):
                        DoActions([RemoveUnitAt(1, frm, zone, p),
                                   CreateUnit(1, to, C.FIELD[p], p)])
                        pv << 0
                        say_to(p, "\x07[강화 성공] \x04상위 유닛 획득! (-%d 강화포인트)" % cost)
                        DoActions(PlayWAV("staredit\\wav\\%s.wav" % C.UPGRADE_SUCCESS_VOICE))
                    if EUDElse()():
                        DoActions(MoveUnit(1, frm, p, zone, C.FIELD[p]))
                        if frm in HIDDEN_FROM:
                            say_to(p, "\x08[강화 실패] \x04강화포인트만 사라졌습니다. (-%d, 히든은 천장 없음)" % cost)
                        else:
                            pv += 1
                            if EUDIf()(pv >= C.PITY_LIMIT):
                                pv << 0
                                DoActions(CreateUnit(1, to, C.FIELD[p], p))
                                say_to(p, "\x1f[천장] \x04강화 %d회 실패! 상위 유닛 지급" % C.PITY_LIMIT)
                            if EUDElse()():
                                say_to(p, "\x08[강화 실패] \x04강화포인트만 사라졌습니다. (-%d)" % cost)
                            EUDEndIf()
                    EUDEndIf()
                if EUDElse()():
                    DoActions(MoveUnit(1, frm, p, zone, C.FIELD[p]))
                    say_to(p, "\x08강화포인트가 부족합니다. \x04(필요: %d)" % cost)
                EUDEndIf()
            EUDEndIf()
        for u in TOP_UNITS:
            if EUDIf()(Bring(p, AtLeast, 1, u, zone)):
                DoActions(MoveUnit(All, u, p, zone, C.FIELD[p]))
                say_to(p, "\x04이미 최고 등급입니다. \x05(8★ 이상은 플레이어존 퓨전 띠에서 조합)")
            EUDEndIf()
        for u in FUSION_UNITS:
            if EUDIf()(Bring(p, AtLeast, 1, u, zone)):
                DoActions(MoveUnit(All, u, p, zone, C.FIELD[p]))
                say_to(p, "\x04강화존에서는 강화할 수 없는 유닛입니다. \x05(각성·신화 조합은 퓨전 띠에서)")
            EUDEndIf()


# ---------------------------------------------------------------------
#  판매
# ---------------------------------------------------------------------
def sell():
    for p in C.HUMANS:
        for u, (ore, gas, pt) in C.SELL_TABLE.items():
            if EUDIf()(Bring(p, AtLeast, 1, u, C.SELL[p])):
                DoActions(RemoveUnitAt(1, u, C.SELL[p], p))
                give(p, ore, gas, pt)
                msg = "\x07[판매] \x04+%d 미네랄 +%d 가스" % (ore, gas)
                if pt:
                    msg += " +%d 강화포인트" % pt
                say_to(p, msg)
            EUDEndIf()


# ---------------------------------------------------------------------
#  킬 보상
# ---------------------------------------------------------------------
def kill_rewards():
    for idx, p in enumerate(C.HUMANS):
        ks = kill_step[idx]
        for i, (need, ore, gas, pt) in enumerate(C.KILL_REWARDS):
            if EUDIf()([ks == i, Kills(p, AtLeast, need, "Any unit")]):
                give(p, ore, gas, pt)
                ks << i + 1
                parts = []
                if ore:
                    parts.append("미네랄 +%d" % ore)
                if gas:
                    parts.append("가스 +%d" % gas)
                if pt:
                    parts.append("강화포인트 +%d" % pt)
                say_to(p, "\x07[%dkill 보상] \x04%s" % (need, "  ".join(parts)))
                if need in C.STONE_KILL_REWARDS:
                    systems.add_stone(idx, C.STONE_KILL_REWARDS[need], "(%dkill 보상)" % need)
            EUDEndIf()


# ---------------------------------------------------------------------
#  euddraft 진입점
# ---------------------------------------------------------------------
def onPluginStart():
    pass


# ---------------------------------------------------------------------
#  진단 (테스트용) : 챕터 시작 10초 뒤 웨이브가 실제로 생겼는지 화면에 알려줌
#   확인이 끝나면 config.py 의 SHOW_DIAG = False 로 끄면 됨
# ---------------------------------------------------------------------
diag_t = EUDVariable(0)


def diag():
    global diag_t
    if not getattr(C, "SHOW_DIAG", True):
        return
    if EUDIf()([state == ST_WAVE, diag_t <= 240]):
        diag_t += 1
        if EUDIf()(diag_t == 240):
            if EUDIf()(Bring(P_WAVE, AtLeast, 1, "Any unit", C.ANYWHERE)):
                say_all("\x13\x07[진단] 웨이브 생성 OK")
            if EUDElse()():
                f_simpleprint("\x08[진단] 웨이브 없음 / 유닛140 flags", hptr(f_dwread(0x664080 + 4 * 140)),
                              "group", f_bread(0x6637A0 + 140), "btn160", f_dwread(0x5187E8 + 12 * 160))
            EUDEndIf()
            f_simpleprint("\x05[진단] 게이트웨이 버튼수", f_dwread(0x5187E8 + 12 * 160),
                          "/ 게임속도값", f_dwread(0x5124F0))
        EUDEndIf()
    EUDEndIf()


def beforeTriggerExec():
    # 트리거를 매 프레임 실행 (원본과 같은 속도)
    DoActions(SetMemory(0x6509A0, SetTo, 0))


def afterTriggerExec():
    global tick
    if EUDIf()(tick == 0):
        on_start()
        for u, v in base_hp.items():
            v << f_dwread(0x662350 + 4 * u) // 256
    EUDEndIf()
    playing << 0
    if EUDIf()([state >= ST_WAVE, state <= ST_BREAK]):
        playing << 1
    EUDEndIf()
    if EUDIf()(state != ST_OVER):
        systems.frame(tick, playing)
        extras.frame(tick)
        chapter_flow()
        waves()
        gacha()
        upgrade()
        sell()
        kill_rewards()
        diag()
    EUDEndIf()
    tick += 1
