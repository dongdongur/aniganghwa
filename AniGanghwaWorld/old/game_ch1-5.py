# -*- coding: utf-8 -*-
# =====================================================================
#  애니강화월드 새 버전 - 게임 로직 (챕터 1 ~ 5)
#   - 수치는 config.py, 개별칭호는 titles.py 에서 고칩니다.
# =====================================================================
from eudplib import *

import config as C
import titles

P_BOSS = C.BOSS_OWNER
P_WAVE = C.WAVE_OWNER

# ---------------------------------------------------------------------
#  스테이지 목록 펼치기 (챕터 1-1 ~ 5-3 -> 0 ~ 14번)
# ---------------------------------------------------------------------
STAGES = []          # (챕터 번호, 챕터 안 순서, 스테이지 dict)
for _ci, _ch in enumerate(C.CHAPTERS):
    for _si, _st in enumerate(_ch["stages"]):
        STAGES.append((_ci, _si, _st))

# 보스 유닛 -> 전투 지역 (스킬·추적 기준)
BOSS_ARENA = {}
for _ci, _si, _st in STAGES:
    for _u in _st.get("phases", []) + [u for u, _ in _st.get("extra", [])]:
        BOSS_ARENA.setdefault(_u, _st["arena"])
    if _st["kind"] == "count":
        BOSS_ARENA.setdefault(_st["count"][0], _st["arena"])
for _b in C.BOSS_SKILLS:
    BOSS_ARENA.setdefault(_b, C.BOSS_AREA)

# 지역별 원래 민가 수 (스테이지 시작할 때 부서진 만큼 다시 지음)
HOUSES = {56: 12, 93: 15}

# ---------------------------------------------------------------------
#  상태 값
# ---------------------------------------------------------------------
ST_DIFF, ST_WAVE, ST_BOSS, ST_BREAK, ST_CLEAR, ST_OVER = 0, 1, 2, 3, 4, 5

state = EUDVariable(ST_DIFF)
tick = EUDVariable(0)
diff = EUDVariable(0)          # 0 = EASY, 1 = HARD
chap = EUDVariable(0)          # 지금 챕터 (0 ~ 4)
gi = EUDVariable(0)            # 지금 스테이지 (0 ~ 14)
phase = EUDVariable(0)         # 보스 형태
spawned = EUDVariable(0)       # 여러 마리 처치 스테이지에서 나온 수
add_cd = EUDVariable(0)        # 마신족·거인 다시 생기기까지 남은 틱

kill_step = [EUDVariable(0) for _ in C.HUMANS]

skill_cnt = {}
skill_rm = {}
for _b, _skills in C.BOSS_SKILLS.items():
    for _j in range(len(_skills)):
        skill_cnt[(_b, _j)] = EUDVariable(0)
        skill_rm[(_b, _j)] = EUDVariable(0)


# ---------------------------------------------------------------------
#  메시지 / 공통
# ---------------------------------------------------------------------
def say_all(text):
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


# ---------------------------------------------------------------------
#  게임 시작 + 난이도 선택
# ---------------------------------------------------------------------
def on_start():
    DoActions([
        LeaderBoardScore(Custom, "강화포인트"),
        LeaderBoardComputerPlayers(Disable),
        SetCountdownTimer(SetTo, C.DIFF_WAIT),
        CreateUnit(1, C.U_SELECT, C.SELECT_LOC, C.HUMANS[0]),
    ])
    for p in C.HUMANS:
        DoActions(SetResources(p, SetTo, C.START_GAS, Gas))
    # 동맹: 사람(P1~P4) <-> 마을 컴퓨터(P5, P7) 아군 / 보스(P6), 웨이브(P8) 적
    for p in C.HUMANS:
        f_setcurpl(p)
        DoActions([SetAllianceStatus(q, Ally) for q in C.ALLY_COMPUTERS] +
                  [SetAllianceStatus(q, Enemy) for q in (P_BOSS, P_WAVE)])
    for q in C.ALLY_COMPUTERS:
        f_setcurpl(q)
        DoActions([SetAllianceStatus(Force1, Ally)])
    say_all("\x13\x1f애니강화월드 \x04새 버전 \x05(챕터 1~5)")
    say_all("\x13" + C.GAME_START_TEXT)
    say_all(C.DIFF_TEXT)
    titles.ShowTitles()


def start_chapter(ci):
    ch = C.CHAPTERS[ci]
    chap << ci
    DoActions(SetCountdownTimer(SetTo, ch["first"]))
    for d in (0, 1):
        if EUDIf()(diff == d):
            say_all("\x13\x1f" + ch["intro"][d])
        EUDEndIf()
    state << ST_WAVE


def choose_difficulty():
    p1 = C.HUMANS[0]
    pick = [(1, Bring(p1, AtLeast, 1, C.U_SELECT, C.HARD_LOC)),
            (0, Bring(p1, AtLeast, 1, C.U_SELECT, C.EASY_LOC)),
            (0, CountdownTimer(AtMost, 0))]
    for d, cond in pick:
        if EUDIf()([state == ST_DIFF, tick >= 24, cond]):
            diff << d
            DoActions(RemoveUnit(C.U_SELECT, p1))
            if d == 0:
                say_all("\x13\x07난이도 : EASY \x04(웨이브 %d마리 쌓이면 패배)" % C.WAVE_DEFEAT_LIMIT[0])
            else:
                say_all("\x13\x08난이도 : HARD \x04(웨이브 %d마리 쌓이면 패배)" % C.WAVE_DEFEAT_LIMIT[1])
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


def spawn_stage(g):
    ci, si, st = STAGES[g]
    acts = [SetCountdownTimer(SetTo, st["time"])]
    if st["kind"] == "count":
        u, total, alive = st["count"]
        acts.append(SetDeaths(P_BOSS, SetTo, 0, u))
        spawned << 0
    else:
        if st.get("phases"):
            acts.append(CreateUnit(1, st["phases"][0], st["spawn"], P_BOSS))
        for u, loc in st.get("extra", []):
            acts.append(CreateUnit(1, u, loc, P_BOSS))
    DoActions(acts)
    if st.get("village"):
        rebuild_houses(st["village"])
    for b in C.BOSS_SKILLS:
        for j in range(len(C.BOSS_SKILLS[b])):
            skill_cnt[(b, j)] << 0
    say_all("\x13\x1f" + st["intro"])
    say_all("\x13\x04" + st["lines"][0])
    phase << 0
    state << ST_BOSS


def clear_stage(g):
    ci, si, st = STAGES[g]
    say_all("\x13\x1f" + st["clear"])
    for p in C.HUMANS:
        give(p, *st["reward"])
        DoActions([MoveUnit(All, "Men", p, C.BOSS_AREA, C.FIELD[p]),
                   MoveUnit(All, "Men", p, st["arena"], C.FIELD[p])])
    DoActions([RemoveUnitAt(All, "Men", C.BOSS_AREA, P_BOSS),
               RemoveUnitAt(All, "Men", st["arena"], P_BOSS)])
    if g + 1 < len(STAGES):
        gi << g + 1
        if STAGES[g + 1][0] == ci:
            DoActions(SetCountdownTimer(SetTo, C.BREAK_TIME))
            state << ST_BREAK
        else:
            start_chapter(ci + 1)
    else:
        say_all(C.ALL_CLEAR_TEXT)
        DoActions(SetCountdownTimer(SetTo, 10))
        state << ST_CLEAR


def stage_logic(g):
    global spawned, add_cd
    ci, si, st = STAGES[g]
    kind = st["kind"]
    def on():
        return [state == ST_BOSS, gi == g]

    # --- 보스 형태 변화 / 처치
    if kind in ("kill", "escape"):
        phases = st["phases"]
        for k, u in enumerate(phases):
            if EUDIf()(on() + [phase == k, Command(P_BOSS, Exactly, 0, u)]):
                if k + 1 < len(phases):
                    acts = [CreateUnit(1, phases[k + 1], C.SKILL_LOC, P_BOSS)]
                    if "phase_time" in st:
                        acts.append(SetCountdownTimer(SetTo, st["phase_time"][k + 1]))
                    DoActions(acts)
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
            DoActions(CreateUnit(1, u, st["spawn"], P_BOSS))
            spawned += 1
        EUDEndIf()
        if EUDIf()(on() + [Deaths(P_BOSS, AtLeast, total, u)]):
            clear_stage(g)
        EUDEndIf()

    # --- 패배 조건
    if kind != "survive":
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

    # --- 다시 생기는 적 (거인, 마신족)
    for u, loc in st.get("adds", []):
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
            for u, loc in st.get("adds", []):
                acts.append(Order(u, P_BOSS, C.ANYWHERE, Attack, st["march"]))
        if acts:
            DoActions(acts)
    EUDEndIf()

    # --- 출전 (전투 지역에 1마리만)
    check = st.get("check", C.BOSS_AREA)
    for p in C.HUMANS:
        if EUDIf()(on() + [Bring(p, AtLeast, 1, "Men", C.SORTIE[p]),
                         Bring(p, Exactly, 0, "Men", check)]):
            DoActions(MoveUnit(1, "Men", p, C.SORTIE[p], st["entry"]))
            say_to(p, "\x07출전! \x04(전투 지역에는 1마리만 들어갈 수 있습니다)")
        EUDEndIf()
        # 나가기
        if st.get("exit"):
            cond = on() + [Bring(p, AtLeast, 1, "Men", st["exit"])]
            blk = st.get("exit_block")
            if blk:
                cond.append(Bring(P_BOSS, Exactly, 0, blk, st["arena"]))
            if EUDIf()(cond):
                DoActions(MoveUnit(All, "Men", p, st["exit"], C.FIELD[p]))
            EUDEndIf()
            if blk:
                if EUDIf()(on() + [tick % 72 == 0, Bring(p, AtLeast, 1, "Men", st["exit"]),
                                   Bring(P_BOSS, AtLeast, 1, blk, st["arena"])]):
                    say_to(p, "\x08마신족이 있어서 나갈 수 없습니다! \x04(마신족을 먼저 처치)")
                EUDEndIf()


def chapter_flow():
    choose_difficulty()
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
    for g in range(len(STAGES)):
        if EUDIf()([state == ST_BOSS, gi == g]):
            stage_logic(g)
        EUDEndIf()
    if EUDIf()([state == ST_CLEAR, CountdownTimer(AtMost, 0)]):
        victory_all()
    EUDEndIf()


# ---------------------------------------------------------------------
#  웨이브 (챕터마다 유닛이 바뀜)
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
            for d in (0, 1):
                lim = C.WAVE_DEFEAT_LIMIT[d]
                if EUDIf()([diff == d, Bring(P_WAVE, AtLeast, lim, "Men", C.FIELD[p])]):
                    defeat_all("웨이브 %d마리 초과 - You Defeat" % lim)
                EUDEndIf()
        EUDEndIf()


# ---------------------------------------------------------------------
#  보스 스킬
# ---------------------------------------------------------------------
def boss_skills():
    for b, skills in C.BOSS_SKILLS.items():
        room = BOSS_ARENA[b]
        if EUDIf()([state == ST_BOSS, Command(P_BOSS, AtLeast, 1, b)]):
            DoActions(MoveLocation(C.SKILL_LOC, b, P_BOSS, C.ANYWHERE))
            for p in C.HUMANS:
                if EUDIf()(Bring(p, AtLeast, 1, "Men", room)):
                    DoActions(MoveLocation(C.TARGET_LOC, "Men", p, room))
                EUDEndIf()
            # 방 안에 우리 유닛이 있으면 그쪽을 공격
            if EUDIf()([tick % 24 == 0, Bring(Force1, AtLeast, 1, "Men", room)]):
                DoActions(Order(b, P_BOSS, room, Attack, C.TARGET_LOC))
            EUDEndIf()
            for j, sk in enumerate(skills):
                cnt = skill_cnt[(b, j)]
                rm = skill_rm[(b, j)]
                if EUDIf()(Bring(Force1, AtLeast, 1, "Men", room)):
                    cnt += 1
                EUDEndIf()
                if EUDIf()(cnt >= sk["every"]):
                    cnt << 0
                    acts = []
                    if sk["effect"]:
                        acts += [CreateUnit(1, sk["effect"], C.SKILL_LOC, P_BOSS),
                                 KillUnitAt(All, sk["effect"], C.SKILL_LOC, P_BOSS)]
                    if sk["pull"]:
                        for p in C.HUMANS:
                            acts.append(MoveUnit(All, "Men", p, room, C.SKILL_LOC))
                    if sk["shield"]:
                        acts.append(ModifyUnitShields(All, b, P_BOSS, C.ANYWHERE, 100))
                    if sk["village"]:
                        acts.append(KillUnitAt(sk["village"], C.U_HOUSE, room, C.U_HOUSE_OWNER))
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
pity = {(p, s[0]): EUDVariable(0) for p in C.HUMANS for s in STEPS}
TOP_UNITS = [line[-1] for line in C.NORMAL_LINES.values()] + \
            [line[-1] for line in C.HIDDEN_LINES.values()]


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
                    if EUDElse()():
                        DoActions(MoveUnit(1, frm, p, zone, C.FIELD[p]))
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
                say_to(p, "\x04이미 최고 등급입니다.")
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
            EUDEndIf()


# ---------------------------------------------------------------------
#  euddraft 진입점
# ---------------------------------------------------------------------
def onPluginStart():
    pass


def beforeTriggerExec():
    # 트리거를 매 프레임 실행 (원본과 같은 속도)
    DoActions(SetMemory(0x6509A0, SetTo, 0))


def afterTriggerExec():
    global tick
    if EUDIf()(tick == 0):
        on_start()
    EUDEndIf()
    if EUDIf()(state != ST_OVER):
        chapter_flow()
        waves()
        boss_skills()
        gacha()
        upgrade()
        sell()
        kill_rewards()
    EUDEndIf()
    tick += 1
