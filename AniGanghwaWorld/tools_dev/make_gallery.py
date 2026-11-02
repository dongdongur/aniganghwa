# -*- coding: utf-8 -*-
"""조합 도감 설명 문구(gallery_data.py) 만들기
   사용: python make_gallery.py <EUD Editor 3 의 Data 폴더> <base_map 에서 꺼낸 chk>
   (스타 기본 dat 값 + 맵 유닛 설정 + datinit_data 를 합쳐 실제 수치를 계산)
"""
import sys, os, re, struct
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.join(HERE, '..')
sys.path.insert(0, PROJ); sys.path.insert(0, HERE)
import config as C
from datinit_data import WRITES
ED, CHK = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(HERE, '검증도구'))
import datmodel as M
M.ED = ED
from mapinfo import Chk

c = Chk(CHK)
m = M.load_defaults(M.Mem())
# 맵 유닛 설정(UNIx) 반영
o, n = c.sec[b'UNIx']; U = c.d[o:o + n]
for u in range(228):
    if U[u] == 0:
        m.wd(0x662350 + 4 * u, struct.unpack_from('<I', U, 228 + 4 * u)[0])
        m.wb(0x660E00 + 2 * u, U[1140 + 2 * u:1142 + 2 * u])
        m.wb(0x65FEC8 + u, U[1596 + u:1597 + u])
for wpn in range(130):
    m.wb(0x656EB0 + 2 * wpn, U[3648 + 2 * wpn:3650 + 2 * wpn])
    m.wb(0x657678 + 2 * wpn, U[3908 + 2 * wpn:3910 + 2 * wpn])
for a, mod, v in WRITES:
    old = m.rd(a); m.wd(a, v if mod == 7 else (old + v if mod == 8 else old - v))

def clean(s): return re.sub(r'[\x00-\x1f]', '', s).strip()
def name(u):
    for h in C.NEW_HEROES:
        if h['unit'] == u: return clean(h['name'])
    return clean(c.uname(u))
STAT = {h['unit']: h['stat_from'] for h in C.NEW_HEROES}
DTYPE = {0: '독립형', 1: '폭발형', 2: '진동형', 3: '노말형', 4: '방어무시'}
SPLASH = {2: '원형 스플', 3: '적군 스플', 24: '공중 스플'}

def perf(u):
    s = STAT.get(u, u)
    hp = m.rd(0x662350 + 4 * s) // 256; sh = m.r(0x660E00 + 2 * s, 2); ar = m.r(0x65FEC8 + s, 1)
    w = m.r(0x6636B8 + s, 1)
    if w >= 130:
        w = m.r(0x6616E0 + s, 1)
    if w >= 130:
        return '체력 %s / 쉴드 %s / 방어 %d' % (format(hp, ','), format(sh, ','), ar), '공격 없음'
    dmg = m.r(0x656EB0 + 2 * w, 2); bon = m.r(0x657678 + 2 * w, 2); cd = m.r(0x656FB8 + w, 1)
    fac = m.r(0x6564E0 + w, 1)
    nh = {h['unit']: h for h in C.NEW_HEROES}.get(u, {})
    if 'hp' in nh: hp = nh['hp']
    if 'armor' in nh: ar = nh['armor']
    if 'weapon' in nh:
        ww = nh['weapon']; dmg, bon, cd, fac = ww['dmg'], ww['bonus'], ww['cooldown'], ww['factor']
    rng = m.rd(0x657470 + 4 * w); dt = m.r(0x657258 + w, 1); ex = m.r(0x6566F8 + w, 1)
    atk = DTYPE.get(dt, '?')
    if ex in SPLASH: atk += ' · ' + SPLASH[ex]
    hits = (' x%d' % fac) if fac > 1 else ''
    if u in C.HIT_HEROES:
        hpline = '\x11타수형 \x04체력 %s = %s대 버팀 (공격력 상관없이 1대에 1)' % (format(hp, ','), format(hp, ','))
    else:
        hpline = '체력 %s / 쉴드 %s / 방어 %d' % (format(hp, ','), format(sh, ','), ar)
    pf = hpline + '\n\x13공격력 %s%s (+%d/업) / 공속 %.2f초 / 사거리 %d칸' % (
        format(dmg, ','), hits, bon, cd / 24, max(1, rng // 32))
    return pf, atk

def recipe(u):
    for r, mats, cost, st in C.FUSIONS:
        if r == u:
            t = ' + '.join('%s x%d' % (name(a), k) if k > 1 else name(a) for a, k in mats)
            return t + '\n\x13강화포인트 %s%s' % (format(cost, ','), (' + 초월석 %d' % st) if st else '')
    for r, mats, cost, st, ex in C.MYTHS:
        if r == u:
            t = ' + '.join('%s x%d' % (name(a), k) if k > 1 else name(a) for a, k in mats)
            t += '\n\x13강화포인트 %s + 초월석 %d' % (format(cost, ','), st)
            if ex and ex[0] == 'cast': t += ' / %s 궁극기 %d회 사용 후' % (name(ex[1]), ex[2])
            if ex and ex[0] == 'revive': t += ' / 사망회귀 %d회 후' % ex[1]
            if ex and ex[0] == 'raid': t += ' / 파티레이드 %s 토벌 후' % name(ex[1])
            if ex and ex[0] == 'inf': t += ' / 무한성 레이드 클리어 후'
            return t
    return '-'

def tier(u):
    if u in [r for r, *_ in C.FUSIONS[:6]]: return '\x0e7☆ (Y)'
    if u in [r for r, *_ in C.FUSIONS]: return '\x1b8★ (Z)'
    for r, mats, cost, *_ in C.MYTHS:
        if r == u: return '\x1110★' if cost >= 300000 else '\x1f9★ 신화'
    return ''

out = {}
for row in __import__('add_gallery').gallery_rows():
    for u in row:
        pf, atk = perf(u)
        txt = '\x13\x1f━━━━━━━ 조합 도감 ━━━━━━━\n\x13%s \x04%s\n' % (tier(u), name(u))
        txt += '\x13\x07[조합] \x04%s\n' % recipe(u)
        txt += '\x13\x07[공격형태] \x04%s\n' % atk
        txt += '\x13\x07[성능] \x04%s\n' % pf
        nh = {h['unit']: h for h in C.NEW_HEROES}.get(u, {})
        if nh.get('regen'):
            txt += '\x13\x07[특성] \x04자가 회복 : 1초마다 최대 체력의 %d%%\n' % nh['regen']
        if u in C.HERO_SKILLS:
            sk = C.HERO_SKILLS[u]
            txt += '\x13\x07[궁극기 H] \x04%s \x05(쿨 %d초, 웨이브 %d마리 즉사)\n' % (clean(sk[0]), sk[3] // 24, sk[2])
        if u in C.ULT2_SKILLS:
            d = C.ULT2_SKILLS[u]
            if d['kind'] == 'heal':
                eff = '%d초 동안 우리 편 전체 무한 회복' % (d['dur'] // 24)
            elif d['kind'] == 'seal':
                eff = '%d초 보스 봉인 + %s x%d 피해' % (d['dur'] // 24, format(d['dmg'], ','), d['hits'])
            else:
                eff = '범위 피해 %s x%d' % (format(d['dmg'], ','), d['hits'])
            txt += '\x13\x07[각성 궁극기 P] \x04%s\n\x13\x05  └ %s / 쿨 %d초\n\x13\x05  └ 각성: 무한성 레이드 클리어 + %s P + 초월석 %d\n' % (
                clean(d['name']), eff, C.ULT2_CD // 24, format(C.ULT_AWAKEN_COST[0], ','), C.ULT_AWAKEN_COST[1])
        out[u] = txt.rstrip('\n')
with open(os.path.join(PROJ, 'gallery_data.py'), 'w', encoding='utf-8') as f:
    f.write('# -*- coding: utf-8 -*-\n# 조합 도감 설명 (tools_dev/make_gallery.py 가 자동 생성)\nGALLERY_TEXT = {\n')
    for u, t in out.items():
        f.write('    %d: %r,\n' % (u, t))
    f.write('}\n')
print('도감 문구', len(out))
