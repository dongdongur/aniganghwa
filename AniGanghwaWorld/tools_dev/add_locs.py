# -*- coding: utf-8 -*-
"""로케이션 추가/수정 도구:  python add_locs.py 입력.chk 출력.chk
   LOCS 목록의 (번호, 이름, 왼, 위, 오른, 아래) 를 MRGN 에 기록한다 (픽셀 단위)."""
import struct, sys
LOCS = [
    (150, 'N150 BGM 켜기', 192, 5440, 448, 5700),
    (151, 'N151 BGM 끄기', 192, 5900, 448, 6016),
    (152, 'N152 난이도 HELL', 7216, 2720, 7400, 2912),
    (153, 'N153 P1 궁극기 범위', 0, 0, 448, 448),
    (154, 'N154 P2 궁극기 범위', 0, 0, 448, 448),
    (155, 'N155 P3 궁극기 범위', 0, 0, 448, 448),
    (156, 'N156 P4 궁극기 범위', 0, 0, 448, 448),
]
def sections(d):
    s = {}; p = 0; order = []
    while p + 8 <= len(d):
        nm, sz = struct.unpack('<4si', d[p:p+8])
        if sz < 0: break
        s[nm] = bytearray(d[p+8:p+8+sz]); order.append(nm); p += 8 + sz
    return s, order
def main(src, dst):
    s, order = sections(open(src, 'rb').read())
    mr = s[b'MRGN']; strx = s[b'STRx']
    n = struct.unpack_from('<I', strx, 0)[0]
    offs = struct.unpack_from('<%dI' % n, strx, 4)
    texts = [bytes(strx[o:strx.index(b'\0', o)]) for o in offs]
    for num, name, l, t, r, b in LOCS:
        texts.append(name.encode('utf-8'))
        struct.pack_into('<IIIIHH', mr, (num-1)*20, l, t, r, b, len(texts), 0)
        print('L%03d %s' % (num, name))
    n = len(texts); head = 4 + 4*n; data = bytearray(); o2 = []
    for t in texts:
        o2.append(head + len(data)); data += t + b'\0'
    s[b'STRx'] = bytearray(struct.pack('<I', n) + struct.pack('<%dI' % n, *o2) + bytes(data))
    out = bytearray()
    for nm in order: out += nm + struct.pack('<I', len(s[nm])) + s[nm]
    open(dst, 'wb').write(out)
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
