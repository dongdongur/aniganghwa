# -*- coding: utf-8 -*-
"""조합 도감 방 + 새 9★/10★ 유닛 이름 + 궁극기2 위치를 base 맵(chk)에 추가하는 도구
   사용: python add_gallery.py 입력.chk 출력.chk
   - 보스방B(L025) 바닥을 빈 공간 R1 에 복사 -> L157 조합 도감
   - 조합 캐릭터(퓨전·신화·10★)를 P12(중립)로 한 줄씩 세움, P1~P4 시야 유닛
   - 유닛 182~185 이름(UNIx) 지정, L158~161 궁극기2 대상 위치
"""
import struct, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import config as C

VOID = 0x29
SRC_ROOM, TX, TY = 25, 82, 150           # 복사할 방, 붙일 왼쪽 위 타일


def sections(d):
    s = {}; p = 0; order = []
    while p + 8 <= len(d):
        nm, sz = struct.unpack('<4si', d[p:p + 8])
        if sz < 0: break
        s[nm] = bytearray(d[p + 8:p + 8 + sz]); order.append(nm); p += 8 + sz
    return s, order


def gallery_rows():
    y = [r for r, *_ in C.FUSIONS[:6]]
    z = [r for r, *_ in C.FUSIONS[6:]]
    m9 = [m[0] for m in C.MYTHS if m[2] < 300000]
    m10 = [m[0] for m in C.MYTHS if m[2] >= 300000]
    rows = [y]
    for k in range(0, len(z), 7): rows.append(z[k:k + 7])
    for k in range(0, len(m9), 8): rows.append(m9[k:k + 8])
    rows.append(m10)
    return rows


def main(src, dst):
    d = open(src, 'rb').read()
    s, order = sections(d)
    W = 256
    mt, tl, mr, un, strx, unix = s[b'MTXM'], s[b'TILE'], s[b'MRGN'], s[b'UNIT'], s[b'STRx'], s[b'UNIx']
    n = struct.unpack_from('<I', strx, 0)[0]
    offs = list(struct.unpack_from('<%dI' % n, strx, 4))
    texts = [bytes(strx[o:strx.index(b'\0', o)]) for o in offs]

    def addstr(t):
        texts.append(t.encode('utf-8')); return len(texts)

    def loc(i):
        return struct.unpack_from('<IIII', mr, (i - 1) * 20)
    # 1) 바닥 복사
    l, t, r, b = loc(SRC_ROOM)
    sx0, sy0 = l // 32 - 1, t // 32 - 1
    w, h = (r - l) // 32 + 2, (b - t) // 32 + 2
    for yy in range(h):
        for xx in range(w):
            di = (TY + yy) * W + TX + xx
            assert struct.unpack_from('<H', mt, di * 2)[0] == VOID, ('빈 공간 아님', TX + xx, TY + yy)
    for yy in range(h):
        for xx in range(w):
            si = (sy0 + yy) * W + sx0 + xx; di = (TY + yy) * W + TX + xx
            struct.pack_into('<H', mt, di * 2, struct.unpack_from('<H', mt, si * 2)[0])
            struct.pack_into('<H', tl, di * 2, struct.unpack_from('<H', tl, si * 2)[0])
    dx, dy = (TX - sx0) * 32, (TY - sy0) * 32
    gl, gt, gr, gb = l + dx, t + dy, r + dx, b + dy
    struct.pack_into('<IIIIHH', mr, (C.GALLERY_LOC - 1) * 20, gl, gt, gr, gb, addstr('N157 조합 도감'), 0)
    for k, L in enumerate(C.ULT2_LOC_P):
        struct.pack_into('<IIIIHH', mr, (L - 1) * 20, 0, 0, 2 * C.ULT2_RADIUS, 2 * C.ULT2_RADIUS,
                         addstr('N%d P%d 궁극기2 대상' % (L, k + 1)), 0)
    # 1-2) 무한성 레이드 방 : 보스방C(L026) 바닥을 빈 공간 R2 에 복사
    l2, t2, r2, b2 = loc(26)
    sx2, sy2 = l2 // 32 - 1, t2 // 32 - 1
    w2, h2 = (r2 - l2) // 32 + 2, (b2 - t2) // 32 + 2
    ITX, ITY = 86, 218
    for yy in range(h2):
        for xx in range(w2):
            di = (ITY + yy) * W + ITX + xx
            assert struct.unpack_from('<H', mt, di * 2)[0] == VOID, ('무한성 자리 빈 공간 아님', ITX + xx, ITY + yy)
    for yy in range(h2):
        for xx in range(w2):
            si = (sy2 + yy) * W + sx2 + xx; di = (ITY + yy) * W + ITX + xx
            struct.pack_into('<H', mt, di * 2, struct.unpack_from('<H', mt, si * 2)[0])
            struct.pack_into('<H', tl, di * 2, struct.unpack_from('<H', tl, si * 2)[0])
    ddx, ddy = (ITX - sx2) * 32, (ITY - sy2) * 32
    il, it, ir, ib = l2 + ddx, t2 + ddy, r2 + ddx, b2 + ddy
    struct.pack_into('<IIIIHH', mr, (C.INF_ROOM - 1) * 20, il, it, ir, ib, addstr('N163 무한성'), 0)
    struct.pack_into('<IIIIHH', mr, (C.INF_SKILL_LOC - 1) * 20, 0, 0, 128, 128, addstr('N164 무한성 보스 스킬'), 0)
    struct.pack_into('<IIIIHH', mr, (C.TELE_LOC - 1) * 20, 0, 0, 2 * C.TELE_R, 2 * C.TELE_R, addstr('N170 보스 패턴 표식'), 0)
    struct.pack_into('<IIIIHH', mr, (C.COMBO_LOC - 1) * 20, 0, 0, 2 * C.COMBO_RADIUS, 2 * C.COMBO_RADIUS, addstr('N165 합동기 대상'), 0)
    for k, L in enumerate(C.RUSH_PAD):
        struct.pack_into('<IIIIHH', mr, (L - 1) * 20, 1536, 928 + 1024 * k, 1696, 1024 + 1024 * k,
                         addstr('N%d P%d 보스 러시 발판' % (L, k + 1)), 0)
    unix[C.RUSH_SIGN_UNIT] = 0
    struct.pack_into('<H', unix, 3192 + 2 * C.RUSH_SIGN_UNIT, addstr(C.RUSH_SIGN_NAME))
    unix[C.INF_SIGN_UNIT] = 0
    struct.pack_into('<H', unix, 3192 + 2 * C.INF_SIGN_UNIT, addstr(C.INF_SIGN_NAME))
    # 2) 새 영웅 이름 / 기본값 (UNIx)
    for hdef in C.NEW_HEROES:
        u, sf = hdef['unit'], hdef['stat_from']
        unix[u] = 0                                                 # 사용자 설정 사용
        struct.pack_into('<I', unix, 228 + 4 * u, struct.unpack_from('<I', unix, 228 + 4 * sf)[0])
        struct.pack_into('<H', unix, 1140 + 2 * u, struct.unpack_from('<H', unix, 1140 + 2 * sf)[0])
        unix[1596 + u] = unix[1596 + sf]
        for base in (1824, 2280, 2736):
            struct.pack_into('<H', unix, base + 2 * u, struct.unpack_from('<H', unix, base + 2 * sf)[0])
        struct.pack_into('<H', unix, 3192 + 2 * u, addstr(hdef['name']))
    # 2-2) 자동강화 패널·버튼 표시 유닛 이름
    for u, nm in [(C.U_AUTO_PANEL, C.AUTO_PANEL_NAME)] + list(zip(C.U_AUTO_BTN, C.AUTO_BTN_NAMES)):
        unix[u] = 0
        struct.pack_into('<H', unix, 3192 + 2 * u, addstr(nm))
    struct.pack_into('<IIIIHH', mr, (C.TEMP_LOC - 1) * 20, 0, 0, 32, 32, addstr('N%d 임시(유닛 생성용)' % C.TEMP_LOC), 0)
    # 3) 도감 유닛은 게임 시작 때 트리거로 만듦 (수치 적용 뒤라 모습·체력이 맞게 나옴). 여기선 시야만.
    rows = gallery_rows()
    new = bytearray(); serial = 0x7E000000

    def put(unit, owner, x, y):
        nonlocal serial
        e = bytearray(36)
        struct.pack_into('<IHHHHHHBBBBIHHII', e, 0, serial, x, y, unit, 0, 0x1F, 0x3F, owner, 100, 100, 100, 0, 0, 0, 0, 0)
        serial += 1; new.extend(e)
    iw, ih = gr - gl, gb - gt
    for p in range(4):                                             # 시야 (맵 리빌러)
        for fy in (0.25, 0.75):
            put(101, p, (gl + gr) // 2, int(gt + ih * fy))
            put(101, p, (il + ir) // 2, int(it + (ib - it) * fy))
    s[b'UNIT'] = un + new
    nn = len(texts); head = 4 + 4 * nn; data = bytearray(); offs = []
    for t_ in texts:
        offs.append(head + len(data)); data += t_ + b'\0'
    s[b'STRx'] = bytearray(struct.pack('<I', nn) + struct.pack('<%dI' % nn, *offs) + bytes(data))
    out = bytearray()
    for nm in order:
        out += nm + struct.pack('<I', len(s[nm])) + s[nm]
    open(dst, 'wb').write(out)
    print('도감 L%d (%d,%d)-(%d,%d), 시야 8개' % (C.GALLERY_LOC, gl, gt, gr, gb))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])


def gallery_positions(gl, gt, gr, gb):
    """도감 칸마다 (유닛, x, y)"""
    rows = gallery_rows(); out = []
    iw, ih = gr - gl, gb - gt
    for ri, row in enumerate(rows):
        y = gt + 48 + ri * (ih - 96) // (len(rows) - 1)
        for ci, u in enumerate(row):
            out.append((u, gl + (ci + 1) * iw // (len(row) + 1), y))
    return out
