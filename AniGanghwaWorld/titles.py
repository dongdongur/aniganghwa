# -*- coding: utf-8 -*-
# 개별칭호 목록
#
# (배틀넷 아이디, 칭호 문구) 를 한 줄씩 추가하면 됩니다.
# 아이디는 대소문자까지 정확히 같아야 합니다.
#
# 색상 코드 (문구 안에 그대로 넣기)
#   \x08 빨강   \x11 주황   \x03 노랑   \x07 초록
#   \x1f 청록   \x0e 하늘   \x10 보라   \x04 흰색   \x05 회색
#
# 예) 무지개 호날두
#   ("sdgh17", "\x08《\x11호\x03날\x07두\x08》"),

from eudplib import (
    Db,
    EUDFunc,
    EUDIf,
    EUDEndIf,
    EUDReturn,
    f_strcmp,
    f_printAll,
    EUDLoopPlayer,
)

# 칭호 단계 (카페 인증 후 패치 때 추가)  (배틀넷 아이디, 단계 1~15)
#  1 브론즈 2 실버 3 골드 4 플래티넘 5 다이아몬드 6 마스터 7 그랜드마스터 8 챌린저 9 레전드 10 챔피언 11~15 단계
#  단계별 혜택(주기적 자원)과 프리미엄(초월석)은 config.py 의 TITLE_BONUS / TITLE_STONE_AT
TITLE_TIERS = [
    ("sdgh17", 15),
]

INDIVIDUAL_TITLES = [
    ("sdgh17", "\x08《\x11호\x03날\x07두\x08》"),
]

_PLAYER_NAME_BASE = 0x57EEEB  # 플레이어 이름 (36바이트 간격)


@EUDFunc
def GetIndividualTitle(player):
    """개별칭호 대상이면 목록 번호(1부터), 아니면 0"""
    for i, (bnet_id, _title) in enumerate(INDIVIDUAL_TITLES):
        name_db = Db(bnet_id.encode("utf-8") + b"\0")
        if EUDIf()(f_strcmp(_PLAYER_NAME_BASE + 36 * player, name_db) == 0):
            EUDReturn(i + 1)
        EUDEndIf()
    EUDReturn(0)


def ShowTitles():
    """게임 시작 때 개별칭호 보유자 입장 메시지"""
    for player in EUDLoopPlayer("Human"):
        for i, (bnet_id, title) in enumerate(INDIVIDUAL_TITLES):
            if EUDIf()(GetIndividualTitle(player) == i + 1):
                f_printAll("\x13" + title + " \x04" + bnet_id + " \x04님이 입장했습니다!")
            EUDEndIf()


@EUDFunc
def GetTitleTier(player):
    """칭호 단계 (없으면 0)"""
    for bnet_id, tier in TITLE_TIERS:
        name_db = Db(bnet_id.encode("utf-8") + b"\0")
        if EUDIf()(f_strcmp(_PLAYER_NAME_BASE + 36 * player, name_db) == 0):
            EUDReturn(tier)
        EUDEndIf()
    EUDReturn(0)
