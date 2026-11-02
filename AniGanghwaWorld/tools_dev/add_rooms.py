# -*- coding: utf-8 -*-
"""새 보스방 지형 추가 도구
   기존 보스방(L012/L025/L026) 타일 블록을 빈 공간(검은 바닥)에 복사하고,
   방 안의 시야 유닛(P7 맵 리빌러)·벽 유닛, 새 로케이션을 함께 추가한다.
   사용: python add_rooms.py 입력.chk 출력.chk
"""
import struct, sys

def sections(d):
    s = {}; p = 0; order = []
    while p + 8 <= len(d):
        nm, sz = struct.unpack('<4si', d[p:p+8])
        if sz < 0: break
        s[nm] = bytearray(d[p+8:p+8+sz]); order.append(nm); p += 8 + sz
    return s, order

VOID = 0x29

# (원본 방 로케이션, 새 방 왼쪽 위 타일 x, y, 새 로케이션 번호, 이름)
ROOMS = [
    (25, 130, 2,   145, 'N145 그리드아일랜드'),
    (12, 130, 35,  146, 'N146 천공투기장'),
    (26, 130, 68,  147, 'N147 요크신시티'),
    (25, 130, 101, 148, 'N148 예비방'),
]
EXIT_LOC = 149          # 새 방들 왼쪽 끝 나가기 띠

def main(src, dst):
    d = open(src, 'rb').read()
    s, order = sections(d)
    W = 256
    mt = s[b'MTXM']; tl = s[b'TILE']
    mr = s[b'MRGN']; un = s[b'UNIT']; strx = s[b'STRx']
    def loc(i):
        return struct.unpack_from('<IIII', mr, (i-1)*20)
    # STRx 문자열 추가
    n = struct.unpack_from('<I', strx, 0)[0]
    offs = list(struct.unpack_from('<%dI' % n, strx, 4))
    texts = []
    for o in offs:
        e = strx.index(b'\0', o); texts.append(bytes(strx[o:e]))
    def addstr(t):
        texts.append(t.encode('utf-8')); return len(texts)
    new_units = bytearray()
    for srcL, tx, ty, newL, name in ROOMS:
        l, t, r, b = loc(srcL)
        sx0, sy0 = l // 32 - 1, t // 32 - 1          # 테두리 1칸 포함
        w, h = (r - l) // 32 + 2, (b - t) // 32 + 2
        for yy in range(h):
            for xx in range(w):
                si = (sy0 + yy) * W + sx0 + xx
                di = (ty + yy) * W + tx + xx
                assert struct.unpack_from('<H', mt, di*2)[0] == VOID, ('빈 공간 아님', tx+xx, ty+yy)
        for yy in range(h):
            for xx in range(w):
                si = (sy0 + yy) * W + sx0 + xx
                di = (ty + yy) * W + tx + xx
                struct.pack_into('<H', mt, di*2, struct.unpack_from('<H', mt, si*2)[0])
                struct.pack_into('<H', tl, di*2, struct.unpack_from('<H', tl, si*2)[0])
        dx, dy = (tx - sx0) * 32, (ty - sy0) * 32
        nl, nt, nr, nb = l + dx, t + dy, r + dx, b + dy
        sid = addstr(name)
        struct.pack_into('<IIIIHH', mr, (newL-1)*20, nl, nt, nr, nb, sid, 0)
        # 방 안 유닛 복사 (P7 시야·벽)
        for i in range(len(un) // 36):
            e = bytearray(un[i*36:i*36+36])
            x, y = struct.unpack_from('<HH', e, 4)
            if l <= x <= r and t <= y <= b:
                struct.pack_into('<I', e, 0, 0x7F000000 + len(new_units)//36 + newL*16)   # 새 고유번호
                struct.pack_into('<HH', e, 4, x + dx, y + dy)
                new_units += e
        print('방 L%03d 복사 -> L%03d (%d,%d)-(%d,%d)' % (srcL, newL, nl, nt, nr, nb))
    # 나가기 띠: 새 방들 왼쪽 2칸
    top = loc(ROOMS[0][3])[1]; bot = loc(ROOMS[-1][3])[3]; left = loc(ROOMS[0][3])[0]
    sid = addstr('N149 새방 나가기')
    struct.pack_into('<IIIIHH', mr, (EXIT_LOC-1)*20, left, top, left + 54, bot, sid, 0)
    s[b'UNIT'] = un + new_units
    # STRx 다시 만들기
    n = len(texts); head = 4 + 4*n; data = bytearray(); offs = []
    for t in texts:
        offs.append(head + len(data)); data += t + b'\0'
    s[b'STRx'] = bytearray(struct.pack('<I', n) + struct.pack('<%dI' % n, *offs) + bytes(data))
    out = bytearray()
    for nm in order:
        out += nm + struct.pack('<I', len(s[nm])) + s[nm]
    open(dst, 'wb').write(out)
    print('완료', len(out), 'bytes, 유닛 +%d' % (len(new_units)//36))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
