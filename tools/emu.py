# -*- coding: utf-8 -*-
"""eudplib 트리거 에뮬레이터 (검증용)
 - eudplib 이 만든 payload 를 메모리에 올리고 트리거를 SC 규칙대로 실행
 - 유닛은 간단한 모델 (위치/소유자/종류), 이동은 직선 이동
"""
import struct, sys
sys.path.insert(0, '/home/claude/tools')
import datmodel

M32 = 0xFFFFFFFF
STR_ADDR = 0x191943C8
PAYLOAD_BASE = 0x30000000
LOC_BASE = 0x58DC60
DEATHS = 0x58A364
KILLS = 0x5878A4
ORE, GAS = 0x57F0F0, 0x57F120
TIMER = 0x58D6F4
CURPL = 0x6509B0
FPS_SEC = 16          # 게임 1초 = 16프레임(가장 빠름)


class Unit:
    __slots__ = ('uid', 'type', 'owner', 'x', 'y', 'dest', 'hp', 'inv', 'born', 'hpr', 'shr', 'order', 'tpos', 'slot')

    def __init__(s, uid, t, o, x, y, born):
        s.uid, s.type, s.owner, s.x, s.y = uid, t, o, x, y
        s.dest = None; s.hp = 100; s.inv = False; s.born = born
        s.hpr = None; s.shr = 0; s.order = 2; s.tpos = 0; s.slot = None


class Emu:
    def __init__(s, payload, root_off, strx, chk):
        s.mem = {}
        # dat 기본값
        dm = datmodel.load_defaults(datmodel.Mem())
        for a, b in dm.m.items():
            k = a & ~3
            s.mem[k] = (s.mem.get(k, 0) & ~(0xFF << (8 * (a & 3))) | (b << (8 * (a & 3))))
        s._load(PAYLOAD_BASE, payload.data)
        for o in payload.prttable:
            a = PAYLOAD_BASE + o
            s.mem[a] = (s.mem.get(a, 0) + PAYLOAD_BASE // 4) & M32
        for o in payload.orttable:
            a = PAYLOAD_BASE + o
            s.mem[a] = (s.mem.get(a, 0) + PAYLOAD_BASE) & M32
        s._load(STR_ADDR, strx)
        s.strx = strx
        # 로케이션
        mrgn = chk.d[chk.sec[b'MRGN'][0]:chk.sec[b'MRGN'][0] + chk.sec[b'MRGN'][1]]
        s._load(LOC_BASE, mrgn)
        s.root = PAYLOAD_BASE + root_off
        s.jumper_next = None
        s.units = []
        s.nuid = 1
        s.frame = 0
        s.log = []
        s.events = []
        s.victory = s.defeat = False
        s.wavs = []
        s.timer_paused = False
        s.mem[0x512684] = 0          # 내 플레이어 번호
        s.score = {}
        s.freeslots = list(range(1699, -1, -1))
        s.mem[CURPL] = 0
        # 플레이어 존재 (P1만 사람, P2~P4 없음)
        for p in range(8):
            if p in (1, 2, 3) and not __import__('os').environ.get('ALLP'):
                s.mem[0x51A280 + 12 * p + 8] = (~(0x51A280 + 12 * p + 4)) & M32
        # 맵 배치 유닛
        U = chk.d[chk.sec[b'UNIT'][0]:chk.sec[b'UNIT'][0] + chk.sec[b'UNIT'][1]]
        for i in range(len(U) // 36):
            cls, x, y, t, rel, vs, vp, owner = struct.unpack('<IHHHHHHB', U[36 * i:36 * i + 17])
            s.units.append(Unit(s.nuid, t, owner, x, y, 0)); s.nuid += 1

    def _load(s, base, data):
        data = bytes(data) + b'\0' * (-len(data) % 4)
        for i in range(0, len(data), 4):
            v = int.from_bytes(data[i:i + 4], 'little')
            if v:
                s.mem[base + i] = v

    def rd(s, a):
        a &= M32
        if a & 3:
            lo = s.mem.get(a & ~3, 0); hi = s.mem.get((a & ~3) + 4, 0)
            sh = 8 * (a & 3)
            return ((lo >> sh) | (hi << (32 - sh))) & M32
        return s.mem.get(a, 0)

    def wr(s, a, v):
        s.mem[a & M32] = v & M32

    def rbyte(s, a):
        return (s.rd(a & ~3) >> (8 * (a & 3))) & 0xFF

    # ----- 문자열
    def string(s, sid):
        if sid == 0:
            return ''
        off = s.rd(STR_ADDR + 4 * sid)
        a = STR_ADDR + off
        out = bytearray()
        for k in range(2000):
            b = s.rbyte(a + k)
            if b == 0:
                break
            out.append(b)
        return out.decode('utf8', 'replace')

    # ----- 로케이션
    def loc(s, l):
        b = LOC_BASE + 20 * (l - 1)
        return s.rd(b), s.rd(b + 4), s.rd(b + 8), s.rd(b + 12)

    def inloc(s, u, l):
        if l == 64:
            return True
        x0, y0, x1, y1 = s.loc(l)
        return min(x0, x1) <= u.x <= max(x0, x1) and min(y0, y1) <= u.y <= max(y0, y1)

    def center(s, l):
        x0, y0, x1, y1 = s.loc(l)
        return (x0 + x1) // 2, (y0 + y1) // 2

    # ----- 플레이어 / 유닛 그룹
    def players(s, p):
        if p == 13:
            p = s.rd(CURPL)
        if p < 12:
            return [p]
        if p == 17:
            return list(range(8))
        if 18 <= p <= 21:
            forc = s.forces
            return [i for i in range(8) if forc[i] == p - 18]
        if p in (14,):
            return [5, 6, 7] if True else []
        if p == 15:
            return [0, 1, 2, 3, 4]
        return []

    def utype_match(s, u, t):
        if t == u.type:
            return True
        if t == 229:
            return True
        if t in (230, 231, 232):
            g = s.rbyte(0x6637A0 + u.type)
            return bool(g & {230: 0x8, 231: 0x10, 232: 0x20}[t])
        return False

    def count(s, p, t, l=None):
        ps = s.players(p)
        n = 0
        for u in s.units:
            if u.owner in ps and s.utype_match(u, t) and (l is None or s.inloc(u, l)):
                n += 1
        return n

    # ----- 조건
    def cmp(s, v, c, n):
        if c == 0:
            return v >= n
        if c == 1:
            return v <= n
        if c == 10:
            return v == n
        return False

    def deaths_addr(s, p, unit):
        if p == 13:
            p = s.rd(CURPL)
        return (DEATHS + 4 * p + 48 * unit) & M32

    def cond(s, a):
        lc, pl, amt, w3, w4 = (s.rd(a + 4 * i) for i in range(5))
        unit = w3 & 0xFFFF; cmpt = (w3 >> 16) & 0xFF; ct = (w3 >> 24) & 0xFF
        flags = (w4 >> 8) & 0xFF; eudx = (w4 >> 16) & 0xFFFF
        if flags & 2:
            return True
        if ct == 22:
            return True
        if ct == 23:
            return False
        if ct == 15:
            v = s.rd(s.deaths_addr(pl, unit))
            if eudx == 0x4353:
                v &= lc
            return s.cmp(v, cmpt, amt)
        if ct == 2:
            return s.cmp(s.count(pl, unit), cmpt, amt)
        if ct == 3:
            return s.cmp(s.count(pl, unit, lc), cmpt, amt)
        if ct == 1:
            return s.cmp(s.rd(TIMER), cmpt, amt)
        if ct == 12:
            return s.cmp(s.frame // FPS_SEC, cmpt, amt)
        if ct == 4:
            rt = w4 & 0xFF
            ps = s.players(pl)
            v = sum(s.rd((ORE if rt == 0 else GAS) + 4 * p) for p in ps)
            return s.cmp(v, cmpt, amt)
        if ct == 5:
            ps = s.players(pl)
            v = sum(s.rd(KILLS + 4 * p + 48 * unit) for p in ps) if unit < 228 else \
                sum(s.rd(KILLS + 4 * p + 48 * t) for p in ps for t in range(228))
            return s.cmp(v, cmpt, amt)
        if ct == 11:
            return True
        if ct == 21:
            st = w4 & 0xFF
            return s.cmp(sum(s.score.get((p, st), 0) for p in s.players(pl)), cmpt, amt)
        if ct == 14:
            return s.cmp(0, cmpt, amt)
        s.unknown(('cond', ct))
        return False

    def unknown(s, k):
        if k not in s.events:
            s.events.append(k)

    # ----- 액션
    def act(s, a):
        w = [s.rd(a + 4 * i) for i in range(8)]
        lc, st, wav, tm, pl, num = w[:6]
        unit = w[6] & 0xFFFF; at = (w[6] >> 16) & 0xFF; mod = (w[6] >> 24) & 0xFF
        flags = w[7] & 0xFF; eudx = (w[7] >> 16) & 0xFFFF
        if flags & 2:
            return
        if at == 45:
            ad = s.deaths_addr(pl, unit)
            o = s.rd(ad)
            if mod == 7:
                v = num
            elif mod == 8:
                v = o + num
            elif mod == 9:
                v = o - num
            else:
                v = o
            if eudx == 0x4353:
                v = (o & ~lc) | (v & lc)
            s.wr(ad, v)
            return
        if at == 9:
            txt = s.string(st)
            cp = s.rd(CURPL)
            s.log.append((s.frame, cp, txt))
            return
        if at == 8:
            s.wavs.append((s.frame, s.string(wav)))
            return
        if at == 44:
            n = mod or 1
            x, y = s.center(lc)
            for p in s.players(pl):
                for _ in range(n):
                    s.units.append(Unit(s.nuid, unit, p, x, y, s.frame)); s.nuid += 1
            return
        if at == 39:   # MoveUnit
            x, y = s.center(num)
            k = 0
            for u in list(s.units):
                if u.owner in s.players(pl) and s.utype_match(u, unit) and s.inloc(u, lc):
                    u.x, u.y = x, y; u.dest = None
                    k += 1
                    if mod and k >= mod:
                        break
            return
        if at in (22, 23, 24, 25):  # Kill/Remove (At)
            k = 0
            for u in list(s.units):
                if u.owner in s.players(pl) and s.utype_match(u, unit) and (at in (22, 24) or s.inloc(u, lc)):
                    s.units.remove(u)
                    if at in (22, 23):
                        s.wr(DEATHS + 4 * u.owner + 48 * u.type, s.rd(DEATHS + 4 * u.owner + 48 * u.type) + 1)
                    k += 1
                    if at in (23, 25) and mod and k >= mod:
                        break
            return
        if at == 46:   # Order
            x, y = s.center(num)
            for u in s.units:
                if u.owner in s.players(pl) and s.utype_match(u, unit) and s.inloc(u, lc):
                    u.dest = (x, y)
            return
        if at == 48:   # Give
            k = 0
            for u in s.units:
                if u.owner in s.players(pl) and s.utype_match(u, unit) and s.inloc(u, lc):
                    u.owner = num; k += 1
                    if mod and k >= mod:
                        break
            return
        if at == 26:   # SetResources
            rt = unit
            for p in s.players(pl):
                for base in ((ORE,) if rt == 0 else (GAS,) if rt == 1 else (ORE, GAS)):
                    ad = base + 4 * p
                    o = s.rd(ad)
                    s.wr(ad, num if mod == 7 else o + num if mod == 8 else max(0, o - num))
            return
        if at == 27:
            for p in s.players(pl):
                o = s.score.get((p, unit), 0)
                s.score[(p, unit)] = num if mod == 7 else o + num if mod == 8 else max(0, o - num)
            return
        if at == 14:
            o = s.rd(TIMER)
            s.wr(TIMER, tm if mod == 7 else o + tm if mod == 8 else max(0, o - tm))
            return
        if at == 1:
            s.victory = True; s.log.append((s.frame, s.rd(CURPL), '<<VICTORY>>')); return
        if at == 2:
            s.defeat = True; s.log.append((s.frame, s.rd(CURPL), '<<DEFEAT>>')); return
        if at == 43:
            for u in s.units:
                if u.owner in s.players(pl) and s.utype_match(u, unit) and s.inloc(u, lc):
                    u.inv = (mod == 4) if mod in (4, 5) else not u.inv
            return
        if at == 38:   # MoveLocation(loc=num, unit, owner, dst=lc)
            for u in s.units:
                if u.owner in s.players(pl) and s.utype_match(u, unit) and s.inloc(u, lc):
                    b = LOC_BASE + 20 * (num - 1)
                    x0, y0, x1, y1 = s.loc(num)
                    hw, hh = abs(x1 - x0) // 2, abs(y1 - y0) // 2
                    s.wr(b, u.x - hw); s.wr(b + 4, u.y - hh); s.wr(b + 8, u.x + hw); s.wr(b + 12, u.y + hh)
                    break
            return
        if at in (49, 50, 51):
            if at == 49:
                for u in s.units:
                    if u.owner in s.players(pl) and s.utype_match(u, unit) and s.inloc(u, lc):
                        u.hp = num
            return
        if at in (0, 3, 4, 7, 10, 12, 13, 15, 16, 17, 28, 29, 30, 31, 32, 47, 54, 55, 56, 57, 5, 6, 11, 27, 42, 52, 53, 58, 59):
            return
        s.unknown(('act', at))

    # ----- CUnit 메모리 동기화 (EUDLoopPlayerUnit / 선택 유닛 읽기용)
    CU0 = 0x59CCA8

    def sync_in(s):
        used = {u.slot for u in s.units if u.slot is not None}
        free = (k for k in range(1700) if k not in used)
        for u in s.units:
            if u.slot is None:
                u.slot = next(free)
            if u.hpr is None:
                u.hpr = s.rd(0x662350 + 4 * u.type)
                if s.rbyte(0x6647B0 + u.type):
                    u.shr = ((s.rd(0x660E00 + 2 * (u.type & ~1)) >> (16 * (u.type & 1))) & 0xFFFF) * 256
        prev = {}
        for p in range(12):
            s.wr(0x6283F8 + 4 * p, 0)
        for u in reversed(s.units):
            a = s.CU0 + 336 * u.slot
            s.wr(a + 8, u.hpr); s.wr(a + 0x60, u.shr)
            s.wr(a + 0x4C, (u.owner & 0xFF) | ((u.order & 0xFF) << 8))
            s.wr(a + 0x58, u.tpos); s.wr(a + 0x64, u.type)
            s.wr(a + 0x28, (u.x & 0xFFFF) | ((u.y & 0xFFFF) << 16))
            s.wr(a + 0xDC, 0x04000000 if u.inv else 0)
            s.wr(a + 0x6C, s.rd(0x6283F8 + 4 * u.owner) if u.owner < 12 else 0)
            if u.owner < 12:
                s.wr(0x6283F8 + 4 * u.owner, a)

    def sync_out(s):
        for u in s.units:
            if u.slot is None:
                continue
            a = s.CU0 + 336 * u.slot
            u.hpr = s.rd(a + 8); u.shr = s.rd(a + 0x60)

    # ----- 한 프레임
    def run_frame(s, limit=3_000_000):
        s.sync_in()
        s._run(limit)
        s.sync_out()
        for u in s.units:
            if u.order in (107, 152):
                pass

    def _run(s, limit):
        t = s.rd(s.root + 4) if s.jumper_next is None else None
        t = s.root
        steps = 0
        while True:
            if t in (0, 0x80000000) or t & 0x80000000:
                break
            steps += 1
            if steps > limit:
                raise RuntimeError('무한 루프 의심 frame %d' % s.frame)
            base = t + 8
            ok = True
            for i in range(16):
                ca = base + 20 * i
                ct = (s.rd(ca + 12) >> 24) & 0xFF
                if ct == 0:
                    break
                if not s.cond(ca):
                    ok = False
                    break
            if ok:
                for i in range(64):
                    aa = base + 320 + 32 * i
                    at = (s.rd(aa + 24) >> 16) & 0xFF
                    if at == 0:
                        break
                    s.act(aa)
            t = s.rd(t + 4)
        s.steps = steps
        s.after()

    def after(s):
        # 시간 / 이동
        s.frame += 1
        if s.frame % FPS_SEC == 0:
            v = s.rd(TIMER)
            if v > 0:
                s.wr(TIMER, v - 1)
        for u in s.units:
            if u.dest:
                dx, dy = u.dest[0] - u.x, u.dest[1] - u.y
                d = max(abs(dx), abs(dy))
                if d <= 8:
                    u.x, u.y = u.dest; u.dest = None
                else:
                    u.x += int(8 * dx / d); u.y += int(8 * dy / d)
