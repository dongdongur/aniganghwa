# -*- coding: utf-8 -*-
# =====================================================================
#  애니강화월드 새 버전 - 설정표
#  숫자만 고치면 게임에 반영됩니다. (빌드 다시 하기)
# =====================================================================

# ---------------------------------------------------------------------
#  플레이어 / 로케이션 (원본 맵 배치 그대로. 번호 = 에디터의 L001 ~ L255)
# ---------------------------------------------------------------------
HUMANS = [0, 1, 2, 3]          # P1 ~ P4
BOSS_OWNER = 5                 # P6 : 보스
WAVE_OWNER = 7                 # P8 : 웨이브
ALLY_COMPUTERS = [4, 6]        # P5, P7 : 마을 / NPC (아군 컴퓨터)

FIELD = [8, 9, 10, 11]         # 플레이어별 방어 필드
SPAWN = [17, 19, 21, 23]       # 웨이브 생성 지점
CORNER = [18, 20, 22, 24]      # 웨이브가 도는 경로 끝
LOOP_TOP = [32, 33, 34, 35]    # 경로 끝에 닿으면 다시 위로
SORTIE = [37, 38, 39, 40]      # 출전 발판 (한 번에 1마리)
SELL = [57, 58, 59, 60]        # 판매 발판
GATEWAY_AREA = 3               # 게이트웨이에서 뽑힌 유닛이 나오는 곳
UPGRADE_ZONE = 4               # 강화존 (각 플레이어 오른쪽)
EXIT_ZONE = 45                 # 보스방 나가기
BOSS_AREA = 42                 # 보스방 전체 (출전 1마리 제한 검사용)
SKILL_LOC = 36                 # 보스 스킬 위치 (보스를 따라다님)
TARGET_LOC = 46                # 스킬 대상 위치 (우리 유닛을 따라다님)
ANYWHERE = 64

# ---------------------------------------------------------------------
#  난이도 선택
#   게임 시작 후 P1(방장) 앞에 SELECT 유닛이 생김 (L029).
#   위(L030)로 옮기면 EASY, 아래(L031)로 옮기면 HARD.
#   DIFF_WAIT 초 동안 안 고르면 EASY.
# ---------------------------------------------------------------------
U_SELECT = 45
SELECT_LOC, EASY_LOC, HARD_LOC = 29, 30, 31
DIFF_WAIT = 20
#                 EASY  HARD
WAVE_DEFEAT_LIMIT = [150, 100]     # 필드에 웨이브가 이만큼 쌓이면 패배
BOSS_TIME_LIMIT = 300              # 보스 제한시간 기본 (초) - 스테이지별로 따로 줄 수 있음
BREAK_TIME = 60                    # 보스 클리어 후 다음 보스까지 (초)
START_GAS = 500                    # 시작 가스 (1성 2번 뽑기)

# ---------------------------------------------------------------------
#  유닛 번호
# ---------------------------------------------------------------------
U_RANDOM_DRAW = 83             # 랜덤뽑기 (H UNIT)

# 강화 라인: 등급 순서대로 (1성 D -> C -> B -> A -> S -> S+ -> X)
NORMAL_LINES = {
    "오공":     [65, 107, 115, 77, 78, 58, 17],
    "루피":     [66, 1, 100, 99, 20, 21, 27],
    "나루토":   [67, 120, 117, 54, 55, 51, 102],
    "이치고":   [61, 118, 108, 74, 87, 56, 28],
    "이누야샤": [68, 38, 112, 53, 104, 52, 22],
    "나츠":     [63, 123, 32, 10, 19, 88, 29],
}
# 히든 라인: H -> HX -> HZ
HIDDEN_LINES = {
    "미도리야":   [113, 111, 2],
    "멜리오다스": [114, 37, 50],
    "에렌":       [116, 106, 5],
    "탄지로":     [122, 46, 39],
}

# 강화 비용·확률 (목표 등급 2성 ~ 7성)
GANG_COST = [250, 500, 1000, 2000, 4000, 8000]
GANG_RATE = [100, 80, 60, 40, 20, 10]      # %
PITY_LIMIT = 10                             # 천장: 같은 단계 10회 실패하면 상위 유닛 지급

# 히든 강화: 일반의 같은 단계 대비 강화포인트 x4, 확률 1/2
#  (H->HX 는 3성 단계, HX->HZ 는 4성 단계 기준. 원본 확인 전 임시값)
HIDDEN_STEP_BASE = [1, 2]                   # GANG_COST / GANG_RATE 의 몇 번째 칸을 쓸지
HIDDEN_COST_MUL = 4
HIDDEN_RATE_DIV = 2

# ---------------------------------------------------------------------
#  랜덤뽑기 (0 ~ 9,999 중 하나, 원본 확률 그대로)
# ---------------------------------------------------------------------
RANDOM_TABLE = [
    (0, 1399, 61), (1400, 2799, 63), (2800, 4199, 65),
    (4200, 5599, 66), (5600, 6999, 67), (7000, 8399, 68),
    (8400, 8789, 113), (8790, 9179, 114), (9180, 9569, 116), (9570, 9969, 122),
    (9970, 9977, 7), (9978, 9985, 15), (9986, 9993, 36), (9994, 9999, 96),
]
UNIQUE_UNITS = [7, 15, 36, 96]  # 게임에 1마리만 (이미 있으면 1성으로 대체)

# ---------------------------------------------------------------------
#  판매 (원본 수치)  유닛번호: (미네랄, 가스, 강화포인트)
# ---------------------------------------------------------------------
SELL_TABLE = {}
for _line in NORMAL_LINES.values():
    SELL_TABLE[_line[0]] = (100, 50, 10)    # 1성
    SELL_TABLE[_line[1]] = (150, 75, 50)    # 2성
for _line in HIDDEN_LINES.values():
    SELL_TABLE[_line[0]] = (150, 75, 0)     # 히든 노말

# ---------------------------------------------------------------------
#  킬 보상 (원본 수치)  (킬 수, 미네랄, 가스, 강화포인트)
# ---------------------------------------------------------------------
KILL_REWARDS = [
    (50, 500, 250, 0), (100, 0, 0, 500), (250, 1000, 500, 0), (500, 0, 0, 2000),
    (750, 2500, 1250, 0), (1000, 0, 0, 5000), (1500, 7500, 2500, 0), (2000, 0, 0, 7500),
    (2500, 12000, 4000, 0), (3000, 0, 0, 10000), (4000, 24000, 8000, 0), (5000, 0, 0, 25000),
    (7500, 45000, 15000, 0), (10000, 0, 0, 50000), (12500, 70000, 22500, 0), (15000, 0, 0, 75000),
    (20000, 100000, 30000, 0), (25000, 0, 0, 100000), (30000, 100000, 30000, 100000),
]

# ---------------------------------------------------------------------
#  챕터 / 스테이지 (원본 수치·문구)
#   kind : kill(보스 처치) / survive(마을 지키며 버티기) / escape(도망가기 전에 처치) / count(여러 마리 처치)
#   arena: 전투 지역 (출전 1마리 제한·클리어 후 귀환 기준)   entry: 출전 시 도착 위치
#   exit : 나가기 발판 (None = 못 나감, 클리어하면 자동 귀환)
#   phases: 보스 형태 순서 (죽으면 다음 형태가 같은 위치에 등장)
#   time : 제한시간(초)  phase_time: 형태별 제한시간 (없으면 time 유지)
#   village: 이 지역의 민가(P7)가 전부 부서지면 패배
#   march: 보스·소환 유닛이 공격하러 가는 위치   adds: (유닛, 위치) 비면 다시 생성
#   reward: (미네랄, 가스, 강화포인트)
# ---------------------------------------------------------------------
U_HOUSE = 200          # 민가
U_HOUSE_OWNER = 6      # P7

ROOM_A, ROOM_B, ROOM_C = 12, 25, 26     # 오른쪽 위 보스방 3칸
ROOM_EXIT = 45                          # 보스방 나가기
# 챕터 4 나가기 = 마을 왼쪽 아래(L094). 마신족이 마을(L093)에 있으면 못 나감
ADD_RESPAWN = 120      # 마신족·거인이 다 죽은 뒤 다시 생길 때까지 (틱, 120 = 약 5초)

CHAPTERS = [
    dict(name="Chapter 1", wave=140, first=300,
         intro=["Chapter 1 원 나 블\n* 보스까지 남은시간 : 300초 *\n* 웨이브 패배조건 : 150마리 *\n* 보스 순서 : 루치->사스케->바쿠야 *",
                "Chapter 1 원 나 블\n* 보스까지 남은시간 : 300초 *\n* 웨이브 패배조건 : 100마리 *\n* 보스 순서 : 루치->사스케->바쿠야 *"],
         stages=[
            dict(name="1-1", kind="kill", arena=ROOM_A, entry=ROOM_A, exit=ROOM_EXIT, spawn=ROOM_A,
                 phases=[165, 172], time=300, reward=(500, 250, 125),
                 intro="Chapter 1-1 애니에스로비\n* BOSS 로브 루치 *\n* 승리 조건 : 제한시간 5분내 처치  *\n* 영웅 상성 : 진동형▲ 폭발형▼ *",
                 lines=["Chapter BOSS 《로브 루치》\n『 그 여자는... 땅끝까지 쫓아가 내가 없애겠다. 』",
                        "《로브 루치 레오파드》\n『 고양이 고양이 열매 모델 레오파드 』"],
                 clear="Chapter 1-1 애니에스로비 Clear\n◈ 보상 ◈\nMineral + 500\nGas + 250\n강화포인트 + 125"),
            dict(name="1-2", kind="kill", arena=ROOM_B, entry=ROOM_B, exit=ROOM_EXIT, spawn=ROOM_B,
                 phases=[170], time=300, reward=(1000, 500, 250),
                 intro="Chapter 1-2 종말의 계곡\n* BOSS 우치하 사스케 *\n* 승리 조건 : 제한시간 5분내 처치  *\n* 영웅 상성 : 폭발형▲ 진동형▼ *",
                 lines=["Chapter BOSS 《우치하 사스케》\n『 사륜안이란건 말이야... 우치하의 증표다. 』"],
                 clear="Chapter 1-2 종말의 계곡 Clear\n◈ 보상 ◈\nMineral + 1000\nGas + 500\n강화포인트 + 250"),
            dict(name="1-3", kind="kill", arena=ROOM_C, entry=ROOM_C, exit=ROOM_EXIT, spawn=ROOM_C,
                 phases=[163], time=300, reward=(1500, 750, 500),
                 intro="Chapter 1-3 소울소사이어티\n* BOSS 쿠치키 뱌쿠야 *\n* 승리 조건 : 제한시간 5분내 처치  *\n* 영웅 상성 : 노말형▲ *",
                 lines=["Chapter BOSS 《쿠치키 뱌쿠야》\n『 좋다. 전부 때려눕혀주마!! 』"],
                 clear="Chapter 1-Last 소울소사이어티 Clear\n◈ 보상 ◈\nMineral + 1500\nGas + 750\n강화포인트 + 500"),
         ]),
    dict(name="Chapter 2", wave=141, first=180,
         intro=["Chapter 2 진격의 거인\n* 보스까지 남은시간 : 180초 *\n* 웨이브 패배조건 : 150마리 *\n* 진행 순서 : 수비->탈환->공성 *",
                "Chapter 2 진격의 거인\n* 보스까지 남은시간 : 180초 *\n* 웨이브 패배조건 : 100마리 *\n* 진행 순서 : 수비->탈환->공성 *"],
         stages=[
            dict(name="2-1", kind="survive", arena=56, entry=53, exit=52,
                 extra=[(169, 55), (164, 54)], adds=[(141, 54)], march=53, village=56,
                 time=300, reward=(2000, 1000, 750),
                 intro="Chapter 2-1 월 마리아 수호전\n* BOSS 초대형/갑옷 거인 *\n* 승리 조건 : 5분동안 마을 지키기  *\n* 영웅 상성 : 스플형▲ 폭발형▲ *",
                 lines=["『 녀석이다.......!  거인이다!!!! 』\nBOSS 《초대형 거인》 참전\n『 대피!!! 거인이 온다......!  쳐박는다!!!!』\nBOSS 《갑옷 거인》 참전"],
                 clear="Chapter 2-1 월 마리아 수호전 Clear\n◈ 보상 ◈\nMineral + 2000\nGas + 1000\n강화포인트 + 750"),
            dict(name="2-2", kind="escape", arena=66, check=66, entry=63, exit=None, spawn=63, goal=65,
                 phases=[154], time=300, reward=(3000, 1250, 1000),
                 intro="Chapter 2-2 여성형 거인 탈환전\n* BOSS 여성형 거인 *\n* 승리 조건 : 여성형거인이 숲을 나가기전까지 처치  *\n* 영웅 상성 : 진동형▲ 리바이▲ 폭발형▼ *",
                 lines=["《리바이 병장》\n『 저 녀석이 숲을 빠져 나가기 전에 구해낸다 』\n『 내가 놈을 처리하겠다. 너는 주의를 끌어라! 』"],
                 clear="Chapter 2-2 여성형 거인 탈환전 Clear\n◈ 보상 ◈\nMineral + 3000\nGas + 1250\n강화포인트 + 1000"),
            dict(name="2-3", kind="kill", arena=56, entry=53, exit=52, spawn=67, march=53, village=56,
                 phases=[159], time=300, reward=(5000, 1500, 2000),
                 intro="Chapter 2-3 짐승형 거인 공성전\n* BOSS 짐승형 거인 *\n* 승리 조건 : 마을을 수비하며 원숭이 거인 처치  *\n* 영웅 상성 : 노말형▲ 스플형▲ *",
                 lines=["Chapter 2-3 짐승형 거인 공성전\n『 마을이 파괴되기전까지 짐승형 거인을 처치하자 』"],
                 clear="Chapter 2-Last 진격의거인 Clear\n◈ 보상 ◈\nMineral + 5000\nGas + 1500\n강화포인트 + 2000"),
         ]),
    dict(name="Chapter 3", wave=142, first=180,
         intro=["Chapter 3 원 나 블\n* 보스까지 남은시간 : 180초 *\n* 웨이브 패배조건 : 150마리 *\n* 보스 순서 : 카타쿠리->폐인->우르키오라 *",
                "Chapter 3 원 나 블\n* 보스까지 남은시간 : 180초 *\n* 웨이브 패배조건 : 100마리 *\n* 보스 순서 : 카타쿠리->폐인->우르키오라 *"],
         stages=[
            dict(name="3-1", kind="kill", arena=ROOM_A, entry=ROOM_A, exit=ROOM_EXIT, spawn=ROOM_A,
                 phases=[167], time=300, reward=(10000, 2500, 2000),
                 intro="Chapter 3-1 홀케이크 아일랜드\n* BOSS 카타쿠리 *\n* 승리 조건 : 제한시간 5분내 처치  *\n* 영웅 상성 : 진동형▲ 폭발형▼ *",
                 lines=["Chapter BOSS 《샬롯 카타쿠리》\n『 이것이 선장의 각오인가? 하지만, 내게는 이길 수 없다. 』"],
                 clear="Chapter 3-1 홀케이크 아일랜드 Clear\n◈ 보상 ◈\nMineral + 10000\nGas + 2500\n강화포인트 + 2000"),
            dict(name="3-2", kind="kill", arena=ROOM_B, entry=ROOM_B, exit=ROOM_EXIT, spawn=ROOM_B,
                 phases=[171, 173], time=300, reward=(20000, 5000, 4000),
                 intro="Chapter 3-2 나뭇잎 마을 부수기\n* BOSS 페인 *\n* 승리 조건 : 제한시간 5분내 처치  *\n* 영웅 상성 : 폭발형▲ 진동형▼ *",
                 lines=["Chapter BOSS 《페인》\n『 신 라 천 정 』",
                        "Chapter BOSS 《'천상도' 페인 야히코》\n『 나의 고통은, 네 녀석 이상이다!! 』"],
                 clear="Chapter 3-2 나뭇잎 마을 부수기 Clear\n◈ 보상 ◈\nMineral + 20000\nGas + 5000\n강화포인트 + 4000"),
            dict(name="3-3", kind="kill", arena=ROOM_C, entry=ROOM_C, exit=ROOM_EXIT, spawn=ROOM_C,
                 phases=[155, 174], time=300, phase_time=[300, 240], reward=(30000, 7500, 5000),
                 intro="Chapter 3-3 웨 코 문 드\n* BOSS 우르키오라 *\n* 승리 조건 : 제한시간 5분내 처치  *\n* 영웅 상성 : 이치고▲ 나머지▼ *",
                 lines=["Chapter BOSS 《우르키오라 쉬퍼》\n『 닫아라. 무르씨엘라고 』",
                        "Chapter 3-FINAL 라 스 노 체 스 \n* BOSS 우르키오라 2차 해방 *\n* 승리 조건 : 제한시간 4분내 처치  *\n《우르키오라 쉬퍼》\n『 레슬렉시온 세군다 에타파 』"],
                 clear="Chapter 3-Last 웨코문드 Clear\n◈ 보상 ◈\nMineral + 30000\nGas + 7500\n강화포인트 + 5000"),
         ]),
    dict(name="Chapter 4", wave=136, first=180,
         intro=["Chapter 4 일곱개의 대죄\n* 보스까지 남은시간 : 180초 *\n* 웨이브 패배조건 : 150마리 *\n* 진행 순서 : 핸드릭슨->십계->에스타롯사 *",
                "Chapter 4 일곱개의 대죄\n* 보스까지 남은시간 : 180초 *\n* 웨이브 패배조건 : 100마리 *\n* 진행 순서 : 핸드릭슨->십계->에스타롯사 *"],
         stages=[
            dict(name="4-1", kind="kill", arena=93, entry=93, exit=94, exit_block=136, exit_block_text="마신족이 있어서 나갈 수 없습니다!", spawn=93, march=93, village=93,
                 adds=[(136, 94)], phases=[150], time=300, reward=(40000, 8000, 20000),
                 intro="Chapter 4-1 리오네스 왕국\n* BOSS 마신 핸드릭슨 *\n* 승리 조건 : 마을 수호 + 핸드릭슨 처치  *\n* 챕터4부턴 마신족 있을시 나갈 수 없습니다  *",
                 lines=["Chapter BOSS 《마신 핸드릭슨》\n『 어두운 밤조차 삼키는 칠흑 속으로 사라져라.  널 구해줄 자는 아무도 없다. 』"],
                 clear="Chapter 4-1 리오네스 왕국 Clear\n◈ 보상 ◈\nMineral + 40000\nGas + 8000\n강화포인트 + 20000"),
            dict(name="4-2", kind="count", arena=93, entry=93, exit=94, exit_block=136, exit_block_text="마신족이 있어서 나갈 수 없습니다!", spawn=93, march=93, village=93,
                 adds=[(136, 94)], count=(201, 10, 4), time=300, reward=(50000, 10000, 25000),
                 intro="Chapter 4-2 카멜롯 왕국\n* BOSS 십 계 *\n* 승리 조건 : 마을 수호 + 십계(10) 처치  *\n* 챕터4부턴 마신족 있을시 나갈 수 없습니다 *",
                 lines=["BOSS 《† 십 계 †》 등장! 10명을 모두 쓰러뜨리자"],
                 clear="Chapter 4-2 카멜롯 왕국 Clear\n◈ 보상 ◈\nMineral + 50000\nGas + 10000\n강화포인트 + 25000"),
            dict(name="4-3", kind="kill", arena=93, entry=93, exit=94, exit_block=136, exit_block_text="마신족이 있어서 나갈 수 없습니다!", spawn=93, march=93, village=93,
                 adds=[(136, 94)], phases=[152], time=300, reward=(60000, 15000, 30000),
                 intro="Chapter 4-3 리오네스 왕국 변두리\n* BOSS 에스타롯사 *\n* 승리 조건 : 마을 수호 + 에스타롯사 처치  *\n* 챕터4부턴 마신족 있을시 나갈 수 없습니다 *",
                 lines=["Chapter BOSS 《에스타롯사》\n『 나는 에스타롯사. 자애의 계금을 부여받은자. 』"],
                 clear="Chapter 4-last 에스타롯사 Clear\n◈ 보상 ◈\nMineral + 60000\nGas + 15000\n강화포인트 + 30000"),
         ]),
    dict(name="Chapter 5", wave=137, first=200,
         intro=["Chapter 5 원 나 블\n* 보스까지 남은시간 : 200초 *\n* 웨이브 패배조건 : 150마리 *\n* 보스 순서 : 카이도우->마다라->아이젠 *",
                "Chapter 5 원 나 블\n* 보스까지 남은시간 : 200초 *\n* 웨이브 패배조건 : 100마리 *\n* 보스 순서 : 카이도우->마다라->아이젠 *"],
         stages=[
            dict(name="5-1", kind="kill", arena=ROOM_A, entry=ROOM_A, exit=ROOM_EXIT, spawn=ROOM_A,
                 phases=[148, 147], time=300, reward=(50000, 25000, 30000),
                 intro="Chapter 5-1 와 노 쿠 니\n* BOSS 카이도우(소형) *\n* 승리 조건 : 제한시간 5분내 처치  *\n* 영웅 상성 : 루피 조로▲ 나머지▼ *",
                 lines=["Chapter BOSS 《'사황' 카이도우》\n『 극소수란 말이지... 나랑 싸울 수 있는 녀석들은.... 』",
                        "Chapter BOSS 《'사황' 카이도우 최종전》\n『 하하하하하하!!! 기어 5 (Gear Fifth 5) 』"],
                 clear="Chapter 5-1 와노쿠니 Clear\n◈ 보상 ◈\nMineral + 50000\nGas + 25000\n강화포인트 + 30000"),
            dict(name="5-2", kind="kill", arena=ROOM_B, entry=ROOM_B, exit=ROOM_EXIT, spawn=ROOM_B,
                 phases=[131, 133], time=300, reward=(60000, 30000, 35000),
                 intro="Chapter 5-2 제 4차 닌자대전\n* BOSS 마다라(대형) *\n* 승리 조건 : 제한시간 5분내 처치  *\n* 영웅 상성 : 나루토 사스케▲ 나머지▼ *",
                 lines=["Chapter BOSS 《우치하 마다라》\n『 어느 쪽이 우위인지... 결판을 내보자고!!! 』",
                        "Chapter BOSS 《우치하 마다라 최종전》\n『 나도 신기하게 생각하고있다고. 지금이라면 전부 바꿀 수 있을거같아! 』"],
                 clear="Chapter 5-2 제 4차 닌자대전 Clear\n◈ 보상 ◈\nMineral + 60000\nGas + 30000\n강화포인트 + 35000"),
            dict(name="5-3", kind="kill", arena=ROOM_C, entry=ROOM_C, exit=ROOM_EXIT, spawn=ROOM_C,
                 phases=[135, 132], time=300, reward=(70000, 35000, 40000),
                 intro="Chapter 5-3 현 세\n* BOSS 아이젠(중형) *\n* 승리 조건 : 제한시간 5분내 처치  *\n* 영웅 상성 : 이치고▲ 나머지▼ *",
                 lines=["Chapter BOSS 《아이젠 소스케》\n『 실낱같은 희망으로 얻은 그 여력으로도  』\n『 이몸의 그것에 닿기엔 너무나 멀다는 것을  』",
                        "Chapter BOSS 《아이젠 소스케 최종전》\n『 최후의 월아천충이란... 내 자신이 월아가 되는것이다! 』"],
                 clear="Chapter 5-FINAL 현 세 Clear\n◈ 보상 ◈\nMineral + 70000\nGas + 35000\n강화포인트 + 40000"),
         ]),
]

# 보스 스킬 (원본 주기 기준, 틱 = 약 1/24초)
#   every: 주기  effect: 보스 위치에서 터뜨리는 연출 유닛  attacker: 잠깐 소환해 공격시키는 유닛
#   dur: 공격 유닛 유지 틱  pull: 방 안의 우리 유닛을 보스 앞으로 끌어당김
#   shield: 보스 실드 100% 회복  village: 이 지역 민가를 N채 파괴
#   heal: 보스 체력 100% 회복   hpcut: 방 안 우리 유닛 체력을 N%로   summon: 계속 남는 소환
#   jump: "human"(우리 유닛) / "ally"(주황 아군) 앞으로 순간이동 + 대상 쉴드 0   text: 경고 문구
def SK(every, effect=0, attacker=0, dur=0, pull=False, shield=False, village=0, **kw):
    d = dict(every=every, effect=effect, attacker=attacker, dur=dur, pull=pull, shield=shield, village=village)
    d.update(kw)
    return d

BOSS_SKILLS = {
    165: [SK(120, 47, 65, 12), SK(180, 70)],                         # 루치
    172: [SK(120, 43, 107, 12), SK(180, 70)],                        # 레오파드
    170: [SK(120, 140, 44, 24), SK(200, 72, 79, pull=True), SK(400, 103, 103, 36)],   # 사스케
    163: [SK(180, 142, 47, 24), SK(400, 72, 72, 36)],                # 뱌쿠야
    169: [SK(240, 70, 141, 96)],                                     # 초대형 거인: 거인 소환
    164: [SK(200, 70)],                                              # 갑옷 거인
    154: [SK(200, 44, shield=True)],                                 # 여성형 거인: 실드 회복
    159: [SK(80, 0, 141, 96), SK(360, 70, village=2)],               # 짐승형: 거인 소환, 투척으로 민가 파괴
    167: [SK(180, 141), SK(400, 30), SK(450, 72, 163, 48)],          # 카타쿠리: 미래시(분신)
    171: [SK(360, 72, 142, 72), SK(600, 72)],                        # 페인 육도
    173: [SK(450, 93), SK(500, 13, 54, 24)],                         # 천상도 페인
    155: [SK(360, 84, 52, 24)],                                      # 우르키오라
    174: [SK(200, 93), SK(360, 84, 52, 24), SK(500, 72, 173, 72)],   # 우르키오라 2차
    150: [SK(240, 70, 103, 36)],                                     # 핸드릭슨: 흑염
    201: [SK(300, 44)],                                              # 십계
    152: [SK(360, 72, 201, 120)],                                    # 에스타롯사: 십계 소환
    148: [SK(200, 70, 51, 24), SK(400, 72, 163, 48)],                # 카이도우
    147: [SK(200, 70, 51, 24), SK(400, 72, 163, 48), SK(700, 72)],   # 카이도우 인수형
    131: [SK(200, 53, 0, 0), SK(400, 72, 131, 72)],                  # 마다라: 분신
    133: [SK(200, 74, 0, 0), SK(500, 72, 133, 72)],                  # 마다라 육도
    135: [SK(200, 44, 44, 24), SK(300, 93)],                         # 아이젠
    132: [SK(200, 44, 44, 24), SK(300, 93), SK(800, 39)],            # 아이젠 봉옥
}

GAME_START_TEXT = "게임이 곧 시작됩니다.\n( 좌측 상단 '소환소'에서 유닛을 뽑아주세요 )"
DIFF_TEXT = "\x13\x1f【 난이도 선택 】\n\x13\x04방장(가장 앞 번호 플레이어)은 SELECT 유닛을 \x07위로 옮기면 EASY\x04, \x08아래로 옮기면 HARD\x04, \x10오른쪽으로 옮기면 HELL\x04 입니다.\n\x13\x05(EASY 는 챕터 6까지 / 20초 안에 안 고르면 EASY)"


# =====================================================================
#  챕터 6 ~ 8 + FINAL (드래곤볼) - 원본 문구·수치 기준
#  ※ 원본에서 지렌전은 "추후 준비예정"으로 비어 있어서 새로 설계함
# =====================================================================
def CH_INTRO(title, first, order_label, order, limit=None):
    lim = limit or WAVE_DEFEAT_LIMIT
    return ["%s\n* 보스까지 남은시간 : %d초 *\n* 웨이브 패배조건 : %d마리 *\n* %s : %s *" % (title, first, lim[d], order_label, order)
            for d in (0, 1)]

U_ALLY_HEROES = [127, 126, 119, 168, 121]     # Z 니카 루피, 아수라 나루토, 무월 이치고, 인드라 사스케, END 나츠 (주황 = P5)
U_GOKU_ALLY = 97                              # Z 블루 계왕권 오공 (FINAL 에서 지켜야 하는 손오공)
RING = 136                                    # 힘의대회 무대 / 셀게임장 = 130
RING_EDGE = [138, 140]                        # 무대 양 끝 진흙 (닿으면 장외)

CHAPTERS += [
    dict(name="Chapter 6", wave=134, first=180,
         intro=CH_INTRO("Chapter 6 드래곤볼 DragonBall", 180, "보스 순서", "프리저->셀->마인부우"),
         stages=[
            dict(name="6-1", kind="kill", arena=93, entry=93, exit=94, exit_block=134,
                 exit_block_text="괴인이 있어서 나갈 수 없습니다!", spawn=93,
                 adds=[(134, 94)], allies=[(u, 1) for u in U_ALLY_HEROES], protect=True,
                 phases=[143], time=300, reward=(80000, 40000, 50000),
                 intro="Chapter 6-1 나메크성\n* BOSS 프리저 *\n* 승리 조건 : 유닛들 보호 + 프리저 처치  *\n* 챕터6부턴 괴인이 있을시 나갈 수 없습니다  *\n* 제한시간안에 못잡거나 모든 주황 유닛이 사망시 패배합니다.*",
                 lines=["Chapter BOSS 《프리저》\n『 기다렸구나, 이것이 네놈이 원하던 풀파워다!!! 』"],
                 clear="Chapter 6-1 나메크성 Clear\n◈ 보상 ◈\nMineral + 80000\nGas + 40000\n강화포인트 + 50000"),
            dict(name="6-2", kind="kill", arena=130, entry=130, check=130, exit=None, spawn=130,
                 pre_entry=True, wipe=True,
                 phases=[144, 144, 144], time=300, reward=(80000, 40000, 50000),
                 intro="Chapter 6-2 셀 게임\n* BOSS 셀 *\n* 승리 조건 : 각 플레이어 1명씩 출전해서 셀 퇴치  *\n* 지금부터 시작전까지 1명씩만 출전가능합니다. *\n* 제한시간안에 못잡거나 모두 전멸시 패배합니다. *",
                 lines=["Chapter BOSS 《셀 1단계》[1/3페이지]\n『 자, 어서 셀 게임을 시작해보자고... 』",
                        "Chapter BOSS 《셀 2단계》[2/3페이지]\n『 준비운동은 이정도면 됐겠지? 』",
                        "Chapter BOSS 《셀 3단계》[3/3페이지]\n『 그 몸으로 여기까지 견딜줄이야...!! 놀랍구나!!!!! 』"],
                 clear="Chapter 6-2 셀 게임 Clear\n◈ 보상 ◈\nMineral + 80000\nGas + 40000\n강화포인트 + 50000"),
            dict(name="6-3", kind="kill", arena=ROOM_A, check=BOSS_AREA, follow=True,
                 entry=[ROOM_A, ROOM_B, ROOM_C, 93], phase_spawn=[ROOM_A, ROOM_B, ROOM_C, 93],
                 exit=[ROOM_EXIT, 94],
                 phases=[146, 146, 146, 146], hits={146: 1000}, time=300, reward=(80000, 40000, 50000),
                 intro="Chapter 6-3 계왕성\n* BOSS 마인부우 *\n* 승리 조건 : 마인부우를 쓰러뜨리자  *\n* 특수한 보스이므로 조심해야합니다. *\n* 공격력과 상관없이 타수로만 데미지가 들어갑니다 (형태마다 1000타) *\n* 제한시간안에 못잡을시 패배합니다.*",
                 lines=["Chapter BOSS 《마인부우(선)》[1/4페이지]\n『 초콜릿으로 만들어주마! 』",
                        "Chapter BOSS 《마인부우 (악)》[2/4페이지]\n『 나와라!! 죽여주마!!!!!!!! 』",
                        "Chapter BOSS 《마인부우 (미스틱)》[3/4페이지]\n『 나를 화나게 하면 할수록 네놈은 괴롭게 죽는다. 』",
                        "Chapter BOSS 《마인부우 (시초)》[4/4페이지]\n『 끼아아아아아아아아아!!!!!!!!!!ㅡ  』"],
                 clear="Chapter 6-FINAL 마인부우 Clear\n◈ 보상 ◈\nMineral + 80000\nGas + 40000\n강화포인트 + 50000"),
         ]),
    dict(name="Chapter 7", wave=175, first=180,
         intro=CH_INTRO("Chapter 7 드래곤볼 DragonBall Super ★", 180, "메인보스 순서", "골든프리저->히트->블랙오공"),
         stages=[
            dict(name="7-1", kind="kill", arena=93, entry=93, exit=94, exit_block=134,
                 exit_block_text="괴인이 있어서 나갈 수 없습니다!", spawn=93,
                 adds=[(134, 94)], allies=[(u, 1) for u in U_ALLY_HEROES], protect=True,
                 phases=[143, 138], time=300, reward=(100000, 60000, 80000),
                 intro="Chapter 7-1 부활의 F ★\n* BOSS 골든 프리저 *\n* 승리 조건 : 유닛들 보호 + 골든 프리저 처치  *\n* 챕터7부턴 괴인이 있을시 나갈 수 없습니다  *\n* 제한시간안에 못잡거나 모든 주황 유닛이 사망시 패배합니다.*",
                 lines=["Chapter BOSS 《프리저》 [1/2페이지]\n『 그럼 , 복수를 시작해볼까요?! 』",
                        "Chapter BOSS 《골든 프리저》 [2/2페이지]\n『 자, 이제 죽으시죠! 』"],
                 clear="Chapter 7-1 부활의 F Clear\n◈ 보상 ◈\nMineral + 100000\nGas + 60000\n강화포인트 + 80000"),
            dict(name="7-2", kind="kill", arena=130, entry=130, check=130, exit=None, spawn=130,
                 pre_entry=True, wipe=True, phase_spawn=[130, 130, 130, 130, 130, None],
                 phases=[210, 211, 25, 203, 204, 204], time=540, reward=(80000, 40000, 50000),
                 intro="Chapter 7-2 제 6우주\n* BOSS 히트 *\n* 승리 조건 : 6우주의 대표 출전선수 5명을 이기는것  *\n* 지금부터 시작전까지 1명씩만 출전가능합니다. *\n* 제한시간안에 못잡거나 모두 전멸시 패배합니다. *\n"
                       "제 6우주 출전 명단  제한시간:9분\n1 ROUND 보타모 (독립형)\n2 ROUND 프로스트 (공중형)\n3 ROUND 마겟타 (쉴드형)\n4 ROUND 캬베 (기본형)\n5 ROUND 히트 (리더형)",
                 lines=["Chapter BOSS 《보타모》1ROUND\n『 별거 아니라고 샴파님께 들은대로군. 』",
                        "Chapter BOSS 《프로스트》2ROUND\n『 그럼 무기와 독의 사용은 반칙이 아닌걸로. 』",
                        "Chapter BOSS 《마겟타》3ROUND\n『 포포! 히포포포포포포!~~~~~ 』",
                        "Chapter BOSS 《캬베》4ROUND\n『 얕잡아봐선 곤란합니다! 』",
                        "Chapter BOSS 《살인청부업자히트》[1/2페이지]\n『 제 6우주를 우승시키는것이 나의 일이다!!!....... 』",
                        "Chapter BOSS 《살인청부업자히트》[2/2페이지]\n『 이 일격이 너를 영겁의 시간속에 가두게 될거다...! 』"],
                 clear="Chapter 7-2 제 6우주 Clear\n◈ 보상 ◈\nMineral + 80000\nGas + 40000\n강화포인트 + 50000"),
            dict(name="7-3", kind="kill", arena=ROOM_B, check=BOSS_AREA, follow=True,
                 entry=[ROOM_B, ROOM_A, ROOM_C], phase_spawn=[ROOM_B, ROOM_A, ROOM_C], exit=ROOM_EXIT,
                 phases=[145, 145, 81], hits={145: 1400}, phase_extra={1: [(153, ROOM_A, True)]},
                 time=300, reward=(100000, 50000, 75000),
                 intro="Chapter 7-3 미 래\n* BOSS 블랙오공 *\n* 승리 조건 : 블랙오공을 쓰러뜨리자  *\n* 특수한 보스이므로 조심해야합니다. *\n* 블랙오공은 타수로만 데미지가 들어갑니다 (1400타) *\n* 제한시간안에 못잡을시 패배합니다.*",
                 lines=["Chapter BOSS 《블랙 오공》[1/3페이지]\n『 전투 민족 최강 전사의 힘... 좀 더 보여주시죠! 』",
                        "Chapter BOSS 《자마스 불사신》[2/3페이지]\n『 신에게 주먹을 휘두르는 불안정한 사이어인은... 특히 이 세계에 있어 불필요한 존재입니다. 』",
                        "Chapter BOSS 《합체 자마스》[3/3페이지]\n『 찬양하라... 숭배하라... 이 고고하고 아름다운 불사사신의 몸을 가진 세계 최강의신. 이 자마스를!!! 』"],
                 clear="Chapter 7-FINAL 블랙 오공 Clear\n◈ 보상 ◈\nMineral + 100000\nGas + 50000\n강화포인트 + 75000"),
         ]),
    dict(name="Chapter 8", wave=40, first=200, limit=[120, 80],
         intro=CH_INTRO("Chapter 8 드래곤볼 힘 의 대 회", 200, "보스 순서", "히트->케프라->톳포", [120, 80]),
         stages=[
            dict(name="8", kind="tournament", arena=RING, entry=RING, check=RING, exit=None,
                 pre_entry=True, wipe=True, ringout=RING_EDGE,
                 time=2880, reward=(150000, 75000, 100000),
                 timed=[
                     dict(at=0, unit=204, lines=["Chapter BOSS 《살인청부업자히트》[1/2페이지]\n『 항복을 추천하지. 』",
                                                  "Chapter BOSS 《살인청부업자히트》[2/2페이지]\n『 이 일격이 너를 영겁의 시간속에 가두게 될거다...! 』"],
                          out="《살인청부업자히트》탈락\n출전한 플레이어들의 체력과 쉴드가 100% 회복됩니다"),
                     dict(at=420, unit=158, lines=["Chapter BOSS 《슈퍼사이어인 케프라》[1/2페이지]\n『 좋다 이거야!!.. 내 힘을 확실하게 보여주지!!!!! 』",
                                                    "Chapter BOSS 《슈퍼사이어인 케프라》[2/2페이지]\n『 아직이다..!! 아직 끝나지 않았다고!!!!!!! 』"],
                          out="《슈퍼사이어인 케프라》탈락\n출전한 플레이어들의 체력과 쉴드가 100% 회복됩니다"),
                     dict(at=720, unit=161, lines=["Chapter BOSS 《파괴신 톳포》[1/2페이지]\n『 나의 힘..... 한번 받아내보거라. 』",
                                                    "Chapter BOSS 《파괴신 톳포》[2/2페이지]\n『 제 7우주여....... 사라져라!!!!!!! 』"],
                          out="《파괴신 톳포》탈락\n출전한 플레이어들의 체력과 쉴드가 100% 회복됩니다"),
                 ],
                 intro="Chapter 8 우주 서바이벌 힘의대회\n* BOSS ????? *\n* 승리 조건 : 각 플레이어 1명씩 출전해서 생존게임  *\n* 48분의 타이머 시간동안 보스를 잡으며 살아남기. *\n* 지금부터 미리 대기실에 대표선수 입장해주시길 바랍니다. *\n* 힘의대회 테두리 진흙 필드에 닿을시 퇴장처리됩니다. *",
                 lines=["\x08힘의대회 시작! \x04(히트·케프라·톳포를 모두 탈락시키면 바로 클리어)"],
                 clear="Chapter 8 힘의대회 Clear\n◈ 보상 ◈\nMineral + 150000\nGas + 75000\n강화포인트 + 100000"),
            dict(name="FINAL", kind="kill", arena=RING, entry=RING, check=RING, exit=None, spawn=RING,
                 pre_entry=True, wipe=True, ringout=RING_EDGE,
                 allies=[(U_GOKU_ALLY, 1)], protect_unit=U_GOKU_ALLY,
                 protect_text="손오공이 쓰러졌습니다 - You Defeat",
                 phases=[197, 197, 197], phase_time=[240, 240, 300], time=240, heal_on_phase=True,
                 phase_stats={0: (6000000, 60000, 200), 1: (8000000, 65000, 220), 2: (10000000, 65535, 240)},
                 reward=(200000, 100000, 150000),
                 intro="Chapter FINAL 지 렌\n* 시작전까지 힘의대회 교체 및 재출전이 가능합니다. *\n* '손오공'이 죽을경우 패배하게 됩니다. *\n* 최종 보스 지렌을 각 시간내 쓰러뜨리세요! *",
                 lines=["《 베르무트 》\n\" ( 들리고 있나 지렌...  지렌...... 지렌..............! ) \"\n《 지 렌 》\n\" ( 들리고있다. ) \"\n《 베르무트 》\n\" ( 먼저 손오공을 부숴버리도록해. 잔챙이는 무시해도 좋아. ) \"\nBOSS 《지 렌》 - 1차전 -  (제한시간 4분)",
                        "《 회색의 지렌 》\n『  모든것을 버리지 않고 이정도의 힘을 가지고 있다니. 』\n『 잘도 톳포를 쓰러뜨렸구나. 칭찬해주마! 』\nBOSS 《지 렌》 - 2차전 -  (제한시간 4분)",
                        "《 베르무트 》\n\" ( 힘을 온전할 시간이 끝났다. ) \"\n\" ( 나머진 부탁한다. 지렌. ) \"\nBOSS 《지 렌》 - 최종전 -  (제한시간 5분)"],
                 clear="Chapter FINAL 지렌 Clear\n◈ 보상 ◈\nMineral + 200000\nGas + 100000\n강화포인트 + 150000"),
         ]),
]

BOSS_SKILLS.update({
    143: [SK(180, 44, 8, 24, summon=201), SK(300, 128, jump="ally")],                 # 프리저: 십계 소환, 주황 아군에게 순간이동
    144: [SK(60, 30, 12, 18), SK(300, 128, jump="human"), SK(400, 84, heal=True,
          text="\x13\x08[DANGER] \x04셀이 재생합니다! (체력 100%)")],                  # 셀
    146: [SK(60, 13, 70, 12)],                                                         # 마인부우
    138: [SK(180, 44, 43, 18, summon=201), SK(160, 128, jump="ally")],                 # 골든 프리저
    210: [SK(180, 39, 70, 18)],                                                        # 보타모
    211: [SK(180, 159, 8, 18)],                                                        # 프로스트
    25:  [SK(180, 27, 44, 18)],                                                        # 마겟타
    203: [SK(180, 71, 43, 18)],                                                        # 캬베
    204: [SK(100, 47), SK(200, 128, jump="human"), SK(300, 77, 60, 18)],                # 히트
    145: [SK(75, 47, 175, 24)],                                                        # 블랙 오공
    153: [SK(150, 47, 175, 24)],                                                       # 자마스 불사신 (무적)
    81:  [SK(100, 0, 70, 12), SK(300, 13, pull=True)],                                 # 합체 자마스
    158: [SK(180, 44, 44, 18, summon=175), SK(300, 13, pull=True,
          text="\x13케프라 「 죽 어 버 려 라 ! ! !  」\n\x13\x08[DANGER] ◈ 케프라가 강력한 기술을 시전합니다 ◈ [DANGER]"),
          SK(200, 128, jump="human")],                                                 # 케프라
    161: [SK(180, 0, 70, 18, summon=40), SK(350, 44, hpcut=5,
          text="\x13톳 포 「 제 7우주여... 사라져라 ! ! !  」\n\x13\x08[DANGER] ◈ 톳포가 주변 유닛 소멸 기술을 시전합니다 ◈ [DANGER]"),
          SK(200, 128, jump="human")],                                                 # 톳포
    197: [SK(150, 44, jump="ally"), SK(240, 13, pull=True,
          text="\x13\x08[DANGER] ◈ 지렌의 강력한 일격 ◈ [DANGER]"),
          SK(400, 44, hpcut=10, text="\x13\x08[DANGER] ◈ 지렌이 모든 힘을 개방합니다 ◈ [DANGER]")],   # 지렌
})

VERSION_TEXT = "챕터 1~8 + FINAL"

# =====================================================================
#  새 에피소드 (챕터 9 ~ 11) : 헌터×헌터 / 주술회전 / 원펀맨
#  - 새 보스는 지난 챕터 보스 유닛 칸을 재활용 (챕터 시작 때 이름·체력·쉴드·방어력 변경)
#    units=[(유닛칸, 새 이름, 체력, 쉴드, 방어력)]  ※ 체력 최대 16,777,215 / 쉴드 65,535 / 방어력 255
#  - 새 보스방(지형 추가): L145 그리드아일랜드, L146 천공투기장, L147 요크신시티, L148 예비방, 나가기 L149
#  - 대사는 원작 분위기에 맞춰 새로 쓴 문구 (원작 대사를 그대로 옮기지 않음)
# =====================================================================
ROOM_N1, ROOM_N2, ROOM_N3, ROOM_N4 = 145, 146, 147, 148
ROOM_N_EXIT = 149
ARENA_CELL = 130

def CLEAR_TEXT(title, reward):
    return "%s Clear\n◈ 보상 ◈\nMineral + %d\nGas + %d\n강화포인트 + %d" % ((title,) + tuple(reward))

CHAPTERS += [
    # -----------------------------------------------------------------
    dict(name="Chapter 9", wave=140, first=200, limit=[100, 80],
         units=[(140, "LV.9 키메라 앤트", 250000, 25000, 220),
                (138, "BOSS 레이저", 9000000, 60000, 255),
                (204, "BOSS 히소카", 10000000, 62000, 255),
                (158, "BOSS 클로로 루실루플", 11000000, 64000, 255),
                (201, "환영여단 단원", 800000, 20000, 230),
                (161, "BOSS 메르엠", 12000000, 60000, 255)],
         intro=CH_INTRO("Chapter 9 헌터×헌터 HUNTER×HUNTER", 200, "보스 순서", "레이저->히소카->클로로->[레이드]메르엠", [100, 80]),
         stages=[
            dict(name="9-1", kind="kill", arena=ROOM_N1, entry=ROOM_N1, exit=ROOM_N_EXIT, spawn=ROOM_N1,
                 phases=[138, 138], time=300, reward=(120000, 60000, 100000),
                 intro="Chapter 9-1 그리드 아일랜드\n* BOSS 레이저 *\n* 승리 조건 : 제한시간 5분내 처치  *\n* 필살 서브에 맞으면 체력이 절반이 됩니다. *",
                 lines=["Chapter BOSS 《레이저》\n『 이 섬의 규칙은 내가 정한다. 피구로 승부하자! 』",
                        "Chapter BOSS 《레이저 - 본기》\n『 재밌군... 지금부터 진짜 공을 던져주지! 』"],
                 skills={138: [SK(150, 47, summon=140),
                               SK(200, 13, jump="human", text="\x13\x04레이저 「 받아봐라! 」"),
                               SK(300, 30, hpcut=50, text="\x13\x08[DANGER] ◈ 레이저의 필살 서브 ◈ [DANGER]")]},
                 clear=CLEAR_TEXT("Chapter 9-1 그리드 아일랜드", (120000, 60000, 100000))),
            dict(name="9-2", kind="kill", arena=ROOM_N2, entry=ROOM_N2, check=ROOM_N2, exit=None, spawn=ROOM_N2,
                 pre_entry=True, wipe=True,
                 phases=[204, 204], time=300, reward=(130000, 65000, 110000),
                 intro="Chapter 9-2 천공투기장\n* BOSS 히소카 *\n* 승리 조건 : 각 플레이어 1명씩 출전해서 히소카 퇴치  *\n* 지금부터 시작전까지 1명씩만 출전가능합니다. *\n* 제한시간안에 못잡거나 모두 전멸시 패배합니다. *",
                 lines=["Chapter BOSS 《히소카》\n『 잘 익은 과일들이 왔네... 맛 좀 볼까? 』",
                        "Chapter BOSS 《히소카 - 진심》\n『 좋아, 정말 좋아... 이제 진짜로 놀아줄게♠ 』"],
                 skills={204: [SK(120, 44, pull=True, text="\x13\x04히소카 「 번지 검(번지검)은 고무와 껌의 성질을 모두 가지지♦ 」"),
                               SK(250, 128, jump="human"),
                               SK(400, 77, 60, 18)]},
                 clear=CLEAR_TEXT("Chapter 9-2 천공투기장", (130000, 65000, 110000))),
            dict(name="9-3", kind="kill", arena=ROOM_N3, entry=ROOM_N3, exit=ROOM_N_EXIT, spawn=ROOM_N3,
                 phases=[158], phase_extra={0: [(201, ROOM_N3)] * 4}, guard=(158, 201),
                 exit_block=201, exit_block_text="환영여단이 남아 있어서 나갈 수 없습니다!",
                 time=360, reward=(150000, 75000, 120000),
                 intro="Chapter 9-3 요크신 시티\n* BOSS 클로로 루실루플 + 환영여단 *\n* 승리 조건 : 환영여단 4명 처치 후 클로로 처치  *\n* 단원이 남아 있으면 클로로는 무적입니다. *\n* 제한시간 6분 *",
                 lines=["Chapter BOSS 《클로로 루실루플》\n『 경매장의 물건은 전부 우리가 가져간다. 단원들, 시작해라. 』"],
                 skills={158: [SK(180, 44, 43, 18),
                               SK(300, 13, hpcut=40, text="\x13\x08[DANGER] ◈ 클로로 「 도둑의 극의 - 빼앗은 능력 발동 」 ◈ [DANGER]")],
                         201: [SK(200, 47, 8, 18)]},
                 clear=CLEAR_TEXT("Chapter 9-3 요크신 시티", (150000, 75000, 120000))),
            dict(name="9-R", kind="kill", arena=RING, entry=RING, check=RING, exit=None, spawn=RING,
                 pre_entry=True, wipe=True, heal_on_phase=True,
                 phases=[161, 161, 161],
                 phase_stats={0: (12000000, 60000, 255), 1: (14000000, 65000, 255), 2: (16000000, 65535, 255)},
                 time=300, phase_time=[300, 300, 360], reward=(250000, 120000, 200000),
                 intro="Chapter 9-RAID 동고르 궁전\n* RAID BOSS 메르엠 *\n* 승리 조건 : 3단계 메르엠 처치 (각 단계 제한시간) *\n* 지금부터 시작전까지 1명씩만 출전가능합니다. *\n* 단계가 넘어갈 때 출전 유닛 체력·쉴드 100% 회복 *",
                 lines=["RAID BOSS 《메르엠》 [1/3]\n『 왕에게 이름 따위는 필요 없다. 덤벼라. 』",
                        "RAID BOSS 《메르엠》 [2/3]\n『 ...인간이란 이렇게까지 강해질 수 있는 것인가. 』",
                        "RAID BOSS 《메르엠 - 각성》 [3/3]\n『 여기서부터는 나도 전력을 다하겠다. 』"],
                 skills={161: [SK(150, 44, jump="human"),
                               SK(300, 13, pull=True, text="\x13\x04메르엠 「 도망칠 곳은 없다. 」"),
                               SK(450, 44, hpcut=10, text="\x13\x08[DANGER] ◈ 메르엠의 일격 ◈ [DANGER]"),
                               SK(500, 0, summon=140)]},
                 clear=CLEAR_TEXT("Chapter 9-RAID 메르엠", (250000, 120000, 200000))),
         ]),
    # -----------------------------------------------------------------
    dict(name="Chapter 10", wave=141, first=200, limit=[100, 80],
         units=[(141, "LV.10 저주령", 350000, 35000, 230),
                (143, "BOSS 마히토", 12000000, 62000, 255),
                (144, "BOSS 조고", 12500000, 63000, 255),
                (81, "BOSS 료멘 스쿠나", 13000000, 60000, 255)],
         intro=CH_INTRO("Chapter 10 주술회전 JUJUTSU KAISEN", 200, "보스 순서", "마히토->조고->[레이드]스쿠나", [100, 80]),
         stages=[
            dict(name="10-1", kind="kill", arena=ROOM_A, entry=ROOM_A, exit=ROOM_EXIT, spawn=ROOM_A,
                 phases=[143, 143], time=300, reward=(160000, 80000, 130000),
                 intro="Chapter 10-1 시부야 사변\n* BOSS 마히토 *\n* 승리 조건 : 제한시간 5분내 처치  *\n* 무위전변 : 방 안 우리 유닛 체력 절반 *",
                 lines=["Chapter BOSS 《마히토》\n『 영혼은 모양이 바뀌는 거야. 너희 것도 한번 바꿔볼까? 』",
                        "Chapter BOSS 《마히토 - 편살즉영체》\n『 이제야 나 자신을 알 것 같아! 』"],
                 skills={143: [SK(150, 44, summon=141),
                               SK(300, 30, hpcut=50, text="\x13\x08[DANGER] ◈ 마히토 「 무위전변 」 ◈ [DANGER]"),
                               SK(600, 13, hpcut=20, text="\x13\x08[DANGER] ◈ 영역전개 「 자폐원돈과 」 ◈ [DANGER]")]},
                 clear=CLEAR_TEXT("Chapter 10-1 시부야 사변", (160000, 80000, 130000))),
            dict(name="10-2", kind="kill", arena=ROOM_B, entry=ROOM_B, exit=ROOM_EXIT, spawn=ROOM_B,
                 phases=[144], time=300, reward=(170000, 85000, 140000),
                 intro="Chapter 10-2 시부야 - 화산\n* BOSS 조고 *\n* 승리 조건 : 제한시간 5분내 처치  *\n* 영역전개 시 방 안 유닛 체력 10% *",
                 lines=["Chapter BOSS 《조고》\n『 인간이야말로 가짜다. 우리 저주야말로 진짜 인간이다! 』"],
                 skills={144: [SK(120, 13, 44, 12),
                               SK(300, 30, hpcut=40, text="\x13\x08[DANGER] ◈ 조고 「 극번 『운』 」 ◈ [DANGER]"),
                               SK(600, 13, hpcut=10, text="\x13\x08[DANGER] ◈ 영역전개 「 개관철위산 」 ◈ [DANGER]")]},
                 clear=CLEAR_TEXT("Chapter 10-2 시부야 - 화산", (170000, 85000, 140000))),
            dict(name="10-R", kind="kill", arena=ARENA_CELL, entry=ARENA_CELL, check=ARENA_CELL, exit=None, spawn=ARENA_CELL,
                 pre_entry=True, wipe=True, heal_on_phase=True,
                 phases=[81, 81, 81],
                 phase_stats={0: (13000000, 60000, 255), 1: (15000000, 65000, 255), 2: (16777215, 65535, 255)},
                 time=300, phase_time=[300, 300, 360], reward=(300000, 150000, 250000),
                 intro="Chapter 10-RAID 신주쿠 결전\n* RAID BOSS 료멘 스쿠나 *\n* 승리 조건 : 3단계 스쿠나 처치 (각 단계 제한시간) *\n* 지금부터 시작전까지 1명씩만 출전가능합니다. *\n* 복마어주자 : 경기장 유닛 체력 5% *",
                 lines=["RAID BOSS 《료멘 스쿠나》 [1/3]\n『 분수를 알아라, 애송이들. 』",
                        "RAID BOSS 《료멘 스쿠나》 [2/3]\n『 조금은 즐겁게 해주는군. 』",
                        "RAID BOSS 《료멘 스쿠나 - 완전체》 [3/3]\n『 네 개의 팔, 두 개의 얼굴... 이것이 본래의 나다. 』"],
                 skills={81: [SK(120, 44, jump="human", text="\x13\x04스쿠나 「 해(解) 」"),
                              SK(240, 13, pull=True, text="\x13\x04스쿠나 「 팔(捌) 」"),
                              SK(500, 30, hpcut=5, text="\x13\x08[DANGER] ◈ 영역전개 「 복마어주자 」 ◈ [DANGER]"),
                              SK(700, 0, summon=141)]},
                 clear=CLEAR_TEXT("Chapter 10-RAID 료멘 스쿠나", (300000, 150000, 250000))),
         ]),
    # -----------------------------------------------------------------
    dict(name="Chapter 11", wave=142, first=200, limit=[90, 70],
         units=[(142, "LV.11 괴인협회", 450000, 45000, 240),
                (211, "BOSS 타츠마키", 13000000, 65000, 255),
                (147, "BOSS 괴인왕 오로치", 14000000, 65000, 255),
                (133, "BOSS 보로스", 15500000, 65535, 255),
                (132, "BOSS 가로우", 16500000, 65535, 255)],
         intro=CH_INTRO("Chapter 11 원펀맨 ONE PUNCH MAN", 200, "보스 순서", "타츠마키->오로치->[레이드]보로스->[레이드]가로우", [90, 70]),
         stages=[
            dict(name="11-1", kind="kill", arena=ROOM_C, entry=ROOM_C, exit=ROOM_EXIT, spawn=ROOM_C,
                 phases=[211], time=300, reward=(180000, 90000, 150000),
                 intro="Chapter 11-1 Z시\n* BOSS 전율의 타츠마키 *\n* 승리 조건 : 제한시간 5분내 처치  *\n* 초능력으로 우리 유닛을 끌어당깁니다. *",
                 lines=["Chapter BOSS 《전율의 타츠마키》\n『 S급 2위를 우습게 보지 마! 전부 날려버릴 거야! 』"],
                 skills={211: [SK(120, 44, pull=True, text="\x13\x04타츠마키 「 이리 와! 」"),
                               SK(300, 30, hpcut=40, text="\x13\x08[DANGER] ◈ 타츠마키의 초능력 폭풍 ◈ [DANGER]")]},
                 clear=CLEAR_TEXT("Chapter 11-1 Z시", (180000, 90000, 150000))),
            dict(name="11-2", kind="kill", arena=ROOM_N4, entry=ROOM_N4, exit=ROOM_N_EXIT, spawn=ROOM_N4,
                 phases=[147, 147], time=300, reward=(190000, 95000, 160000),
                 intro="Chapter 11-2 괴인협회 아지트\n* BOSS 괴인왕 오로치 *\n* 승리 조건 : 제한시간 5분내 처치  *\n* 괴인을 계속 불러냅니다. *",
                 lines=["Chapter BOSS 《괴인왕 오로치》\n『 괴인의 왕 앞에 무릎 꿇어라. 』",
                        "Chapter BOSS 《괴인왕 오로치 - 전력》\n『 이 몸의 진짜 모습을 보여주마. 』"],
                 skills={147: [SK(150, 0, summon=142),
                               SK(300, 13, hpcut=30, text="\x13\x08[DANGER] ◈ 오로치의 괴인 포효 ◈ [DANGER]")]},
                 clear=CLEAR_TEXT("Chapter 11-2 괴인협회 아지트", (190000, 95000, 160000))),
            dict(name="11-R1", kind="kill", arena=RING, entry=RING, check=RING, exit=None, spawn=RING,
                 pre_entry=True, wipe=True, heal_on_phase=True,
                 phases=[133, 133], time=300, phase_time=[300, 300], reward=(220000, 110000, 180000),
                 intro="Chapter 11-RAID 우주선 습격\n* RAID BOSS 보로스 *\n* 승리 조건 : 2단계 보로스 처치 *\n* 지금부터 시작전까지 1명씩만 출전가능합니다. *",
                 lines=["RAID BOSS 《보로스》 [1/2]\n『 드디어 나와 겨룰 만한 상대를 찾았군. 』",
                        "RAID BOSS 《보로스 - 메테오릭 버스트》 [2/2]\n『 이 힘을 쓰는 건 처음이다! 』"],
                 skills={133: [SK(150, 44, jump="human"),
                               SK(400, 13, hpcut=5, text="\x13\x08[DANGER] ◈ 보로스 「 붕성포효포 」 ◈ [DANGER]")]},
                 clear=CLEAR_TEXT("Chapter 11-RAID 보로스", (220000, 110000, 180000))),
            dict(name="11-R2", kind="kill", arena=RING, entry=RING, check=RING, exit=None, spawn=RING,
                 pre_entry=True, wipe=True, heal_on_phase=True,
                 phases=[132, 132], time=300, phase_time=[300, 360], reward=(300000, 150000, 300000),
                 intro="Chapter 11-FINAL 괴인 가로우\n* RAID BOSS 가로우 *\n* 승리 조건 : 2단계 가로우 처치 *\n* 지금부터 시작전까지 1명씩만 출전가능합니다. *",
                 lines=["RAID BOSS 《인간괴인 가로우》 [1/2]\n『 히어로가 이기는 이야기는 이제 질렸어. 』",
                        "RAID BOSS 《가로우 - 우주적 공포 모드》 [2/2]\n『 이제 아무도 날 멈출 수 없어. 』"],
                 skills={132: [SK(120, 44, jump="human"),
                               SK(300, 13, pull=True, text="\x13\x04가로우 「 유수암쇄권 」"),
                               SK(600, 30, hpcut=1, text="\x13\x08[DANGER] ◈ 가로우 「 제로 펀치 」 ◈ [DANGER]")]},
                 clear=CLEAR_TEXT("Chapter 11-FINAL 가로우", (300000, 150000, 300000))),
         ]),
]
VERSION_TEXT = "챕터 1~11 + 레이드"
ALL_CLEAR_TEXT = "\x13\x1f모든 챕터 클리어!\n\x13\x04수고하셨습니다. 다음 에피소드는 업데이트에서 이어집니다."

# 테스트용 빠른 진행 (빌드할 때 환경변수 AGW_FAST=1 이면 시간 단축) - 실제 게임에는 영향 없음
import os as _os
if _os.environ.get("AGW_FAST"):
    BREAK_TIME, DIFF_WAIT = 2, 3
    for _ch in CHAPTERS:
        _ch["first"] = 3
        for _st in _ch["stages"]:
            _st["time"] = 40
            if "phase_time" in _st: _st["phase_time"] = [40] * len(_st["phase_time"])
            for _k, _t in enumerate(_st.get("timed", [])): _t["at"] = 2 * _k
            if _os.environ.get("AGW_HITTEST"):
                _st["hits"] = {_u: 50 for _u in _st.get("hits", {})}

# =====================================================================
#  부가 시스템 (원본 기준)  - systems.py 에서 사용
# =====================================================================
# --- 난이도: EASY 는 챕터 6 끝(6-3 마인부우)까지, HARD / HELL 은 끝까지
#   SELECT 를 위(L030) EASY / 아래(L031) HARD / 오른쪽(L152) HELL
HELL_LOC = 152
DIFF_NAMES = ["EASY", "HARD", "HELL"]
WAVE_DEFEAT_LIMIT3 = [150, 100, 80]            # 난이도별 기본 웨이브 패배 마릿수 (챕터 limit 이 있으면 HELL 은 그 값 -20)
DIFF_END_CHAPTER = [6, None, None]             # 이 챕터까지 깨면 승리 (None = 마지막까지)
DIFF_END_TEXT = ["\x13\x1f[EASY] 버전은 여기까지입니다!", "\x13\x1f[HARD] 버전은 여기까지입니다!", "\x13\x1f[HELL] 버전은 여기까지입니다!"]
BOSS_HP_DIFF = [100, 100, 130]                 # 난이도별 보스 체력 %
BOSS_HP_PLAYERS = [60, 75, 90, 100]            # 인원수(1~4인)별 보스 체력 %  (원본에 인원수 난이도가 있었음, 수치는 임시)

# --- 이동 발판 (원본 로케이션)
CONTENT_PAD = [69, 70, 71, 72]                 # 필드의 『 컨텐츠 』 -> 플레이어존
ZONE = [73, 74, 75, 76]                        # 플레이어존 (퓨전·파티레이드·던전 발판이 있는 곳)
ZONE_EXIT = 77                                 # 플레이어존 왼쪽 띠 (Player Zone Move) -> 허브
HUB = 27                                       # 허브 (보상 아이템이 나오는 곳)
HUB_HOME = 28                                  # 허브 -> 내 필드
HUB_SELL = 61                                  # 허브 판매 발판
HUB_ZONE = 86                                  # 허브 -> 내 플레이어존 (퓨전 결과도 여기서 나옴)

# --- 퓨전 조합 (원본 미션 문구 그대로). 재료를 L068(퓨전 띠)에 넣으면 자동 조합
FUSION_AREA = 68
FUSION_LIMIT_ONE = True                        # 같은 결과 유닛은 플레이어별 1개만 보유
U_STONE_TEXT = "초월석"
#  (결과, [(재료, 개수), ...], 강화포인트, 초월석)
FUSIONS = [
    # 퓨전 조합 ☆x7 (Y등급)
    (98,  [(21, 2), (50, 1)], 10000, 0),   # 염왕모드 조로   : 6★루피 x2 / 4☆멜리오다스
    (80,  [(51, 2), (5, 1)],  10000, 0),   # 만화경 사스케   : 6★나루토 x2 / 4☆에렌
    (71,  [(56, 2), (39, 1)], 10000, 0),   # 빙륜환 토시로   : 6★이치고 x2 / 4☆탄지로
    (16,  [(88, 2), (2, 1)],  10000, 0),   # 엘자            : 6★나츠 x2 / 4☆미도리야
    (79,  [(52, 2), (51, 1)], 10000, 0),   # 요괴 셋쇼마루   : 6★이누야샤 x2 / 6★나루토
    (3,   [(58, 2), (56, 1)], 10000, 0),   # 갓블루 베지터   : 6★오공 x2 / 6★이치고
    # 퓨전 조합 ★x8 (Z등급)
    (127, [(27, 2), (98, 1)],  50000, 0),  # 태양신 니카     : 7★루피 x2 / 7☆조로
    (126, [(102, 2), (80, 1)], 50000, 0),  # 육도 아수라     : 7★나루토 x2 / 7☆사스케
    (119, [(28, 2), (71, 1)],  50000, 0),  # 최후의 무월     : 7★이치고 x2 / 7☆토시로
    (121, [(29, 2), (16, 1)],  50000, 0),  # END             : 7★나츠 x2 / 7☆엘자
    (35,  [(22, 2), (79, 1)],  50000, 0),  # 폭쇄아          : 7★이누야샤 x2 / 7☆셋쇼마루
    (97,  [(17, 2), (3, 1)],   50000, 0),  # 블루 계왕권     : 7★오공 x2 / 7☆베지터
    # 퓨전 조합 ★x8 히든
    (11,  [(2, 3)],   50000, 0),           # 올마이트        : 4☆미도리야 x3
    (64,  [(5, 3)],   50000, 0),           # 리바이병장      : 4☆에렌 x3
    (69,  [(50, 3)],  50000, 0),           # 에스카노르      : 4☆멜리오다스 x3
    (76,  [(39, 3)],  50000, 0),           # 젠이츠          : 4☆탄지로 x3
    (75,  [(2, 1), (50, 1), (5, 1), (39, 1)], 50000, 0),   # 고죠 사토루 : 4☆ 1개씩
    (168, [(80, 2), (102, 1)], 50000, 0),  # 사스케(인드라)  : 7☆사스케 x2 / 7★나루토
    (190, [(98, 1), (79, 1)],  50000, 0),  # 키리토          : 7☆조로 / 7☆셋쇼마루
    (91,  [(16, 1), (3, 1)],   50000, 0),  # 메구밍          : 7☆엘자 / 7☆베지터
    (92,  [(71, 1), (80, 1)],  50000, 0),  # 미코토          : 7☆토시로 / 7☆사스케
    (82,  [(28, 1), (17, 1)],  50000, 1),  # 네테로          : 7★이치고 / 7★오공 / 초월석
    (59,  [(27, 1), (29, 1)],  50000, 1),  # 리무루          : 7★루피 / 7★나츠 / 초월석
    (41,  [(102, 1), (22, 1)], 50000, 1),  # 유희            : 7★나루토 / 7★이누야샤 / 초월석
    (48,  [(27, 1), (102, 1), (28, 1)], 50000, 0),   # 세이버   : 7★루피 / 7★나루토 / 7★이치고
    (129, [(29, 1), (22, 1), (17, 1)],  50000, 0),   # 오메가몬 : 7★나츠 / 7★이누야샤 / 7★오공
]

# --- 초월석 (개수로 관리, 게임 중 문구로 안내)
STONE_KILL_REWARDS = {10000: 1, 20000: 1, 30000: 1}      # 킬 보상에 붙는 초월석

# --- 칭호 단계 (titles.py 의 TITLE_TIERS 로 아이디별 단계 지정)
TITLE_NAMES = {1: "브론즈", 2: "실버", 3: "골드", 4: "플래티넘", 5: "다이아몬드", 6: "마스터", 7: "그랜드 마스터",
               8: "챌린저", 9: "레전드", 10: "챔피언", 11: "11단계", 12: "12단계", 13: "13단계", 14: "14단계", 15: "15단계"}
#  칭호혜택 (미네랄, 가스, 강화포인트) - TITLE_BONUS_PERIOD 초마다 지급 (원본 지급 주기 확인 필요)
TITLE_BONUS = {1: (20, 2, 20), 2: (40, 4, 40), 3: (60, 6, 60), 4: (80, 8, 80), 5: (100, 10, 100),
               6: (150, 15, 150), 7: (200, 20, 200), 8: (300, 30, 300), 9: (400, 40, 400), 10: (500, 50, 500),
               11: (600, 60, 600), 12: (700, 70, 700), 13: (800, 80, 800), 14: (900, 90, 900), 15: (1000, 100, 1000)}
TITLE_BONUS_PERIOD = 60
#  프리미엄 (게임 시작 때 1번): 골드↑ 초월석+1, 마스터↑ +1, 챌린저↑ +1 / 건트랩은 사용처 미구현이라 안내만
TITLE_STONE_AT = [3, 6, 8]
#  건트랩 프리미엄: 각 플레이어존 드래곤볼 오른쪽 아래의 건트랩(P7 소유)을 칭호 단계만큼 넘겨줌 -> 드래곤볼을 더 빨리 부숨
#   레전드 +1, 챔피언 +1, 11단계 +1, 12단계 +2, 13단계 +3, 14단계 +4, 15단계 +5 (누적, 최대 8개)
U_GUNTRAP = 209
GUNTRAP_BY_TIER = {9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 6, 15: 7}

# --- 3★ 이하 일괄 판매 / 일괄 강화, BGM, 변환기 : SELECT 유닛을 발판에 올림
BULK_AREA, BULK_SELL_PAD, BULK_UP_PAD = 111, 112, 113
BGM_AREA, BGM_ON_PAD, BGM_OFF_PAD = 43, 150, 151
CONV_AREA, CONV_MIN_PAD, CONV_GAS_PAD = 141, 142, 143
CONVERT_UNLOCK_CHAPTER = 6                     # 변환기가 풀리는 챕터 (원본 "후반 해금", 정확한 챕터 확인 필요)
CONV_MINERAL = (100, 200)                      # 가스 100 -> 미네랄 200
CONV_GAS = (100, 20)                           # 미네랄 100 -> 가스 20
# BGM: sound 폴더의 M번호_조각.ogg (조각 1개 = 약 3.15초). 이 순서대로 돌려가며 재생
BGM_PLAYLIST = list(range(0, 61))
BGM_SEGMENT_TICKS = 75

# --- 드래곤볼 (원본 문구 수치). 각 플레이어존에 1개씩, 잡으면 다음 별
DRAGONBALL_SPOT = [16, 83, 84, 85]
U_DRAGONBALL, U_SUPER_DRAGONBALL = 224, 225
DRAGONBALL_INTERVAL = 60                       # 잡은 뒤 다음 공이 나올 때까지 (초)
DRAGONBALL_POINTS = [1000, 3500, 8000, 16000, 24000, 32000, 50000]
SUPER_DRAGONBALL_POINTS = [75000, 100000, 125000, 150000, 175000, 200000, 300000]

# --- 던전 (뉴비퀘스트): 던전 발판 -> 개인 던전, 악마의 열매·인주력 각 10개 파괴 시 초월석 +1
DUNGEON_PAD = [118, 119, 120, 121]
DUNGEON_ROOM = [116, 105, 106, 117]
DUNGEON_EXIT = 122
U_DEVIL_FRUIT, U_JINCHURIKI = 213, 212
DUNGEON_QUEST = 10

# --- 파티레이드: 레이드 발판 -> L087 (한 번에 1마리), 원본 순서·보상
RAID_PAD = [89, 90, 91, 92]
RAID_ROOM, RAID_EXIT = 87, 88
RAID_OWNER = 7                                 # P8
#  (보스, 같이 나오는 졸개, 보상 문구, (미네랄, 가스, 강화포인트, 초월석))
RAID_CHAIN = [
    (159, 141, "[파티레이드] 짐승거인 토벌 +5000mineral +1000gas", (5000, 1000, 0, 0)),
    (150, 136, "[파티레이드] 마신 핸드릭슨 토벌 +20000mineral +5000gas", (20000, 5000, 0, 0)),
    (201, 136, "[파티레이드] 십계 토벌 +30000mineral +6000gas", (30000, 6000, 0, 0)),
    (152, 136, "[파티레이드] 에스타롯사 토벌 +40000mineral +8000gas", (40000, 8000, 0, 0)),
    (143, 134, "[파티레이드] 프리저 토벌 초 월 석 + 1  강화포인트 + 50000", (0, 0, 50000, 1)),
    (144, 134, "[파티레이드] 셀 토벌 [신화] [히든] 공격력 + 2", (0, 0, 0, 0)),
    (146, 134, "[파티레이드] 마인부우 토벌 [신화] [히든] 공격력 + 3", (0, 0, 0, 0)),
    (138, 175, "[파티레이드] 골든프리저 토벌 [신화] [히든] [스킬]공격력 + 2", (0, 0, 0, 0)),
    (204, 175, "[파티레이드] 히트 토벌 [신화] [히든] [스킬]공격력 + 3", (0, 0, 0, 0)),
    (81, 175, "[파티레이드] 합체자마스 토벌 [신화] [히든] [스킬]공격력 + 5", (0, 0, 0, 0)),
]
RAID_START_DELAY = 30                          # 게임 시작 후 첫 레이드 보스까지 (초)

# --- 웨이브 안내판 (원본 문구)
WAVE_BOARD = "\x13〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓\n\x13WAVE %d : %s\n\x13HP %s SH %s\n\x13〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓"
WAVE_INFO = {140: ("칠무해 (소형)", "60", "6"), 141: ("거인 (대형)", "600", "60"), 142: ("아카츠키 (소형)", "6,000", "600"),
             136: ("마신족 (중형)", "40,000", "4,000"), 137: ("아란칼 (대형)", "80,000", "8,000"), 134: ("괴 인 (소형)", "120,000", "12,000"),
             175: ("외 계 인 (대형)", "160,000", "16,000"), 40: ("파 괴 신 (중형)", "220,000", "22,000")}

# =====================================================================
#  영웅 성장 (원본 조건 기준, 확인 안 되는 부분은 새로 설계)
#   - 모든 조합은 퓨전 띠(L068)에서 (원본 일부는 강화존이었지만 강화존은 7★를 돌려보내서 통일)
# =====================================================================
SKILL_LOC_P = [153, 154, 155, 156]             # 플레이어별 궁극기 범위 (영웅을 따라다님)

# --- 9★ 신화 조합 (그리스 문자 등급). 게임 전체에서 1명만 보유 (원본과 같음)
#  (결과, [(재료, 개수)], 강화포인트, 초월석, 추가조건)
#   추가조건: ("cast", 영웅, n) 그 영웅 궁극기 n번 사용 / ("revive", n) 스바루 사망회귀 n번 / ("raid", 보스) 파티레이드 그 보스 토벌 후
MYTH_COST = 100000
MYTHS = [
    (34,  [(96, 1), (91, 1)], MYTH_COST, 3, ("revive", 100)),          # [λ] 질투의 마녀 사테라 : Z 스바루 + Z 메구밍 (사망회귀 100회)
    (109, [(41, 1), (62, 1), (22, 4)], MYTH_COST, 3, ("cast", 41, 1)),  # [π] 명계의 파라오 아템 : Z 유희 + 오시리스 + 7★이누야샤 x4
    (191, [(127, 1), (98, 2)], MYTH_COST, 5, None),                     # [♬] 프린세스 우타 : Z 니카 + 7☆조로 x2
    (90,  [(69, 1), (29, 3)], MYTH_COST, 3, None),                      # [ν] 멜리오다스 드래곤씬 : Z 에스카노르 + 7★나츠 x3
    (162, [(190, 1), (102, 3)], MYTH_COST, 5, None),                    # [π] 정합기사 앨리스 : Z 키리토 + 7★나루토 x3
    (130, [(75, 1), (36, 1)], MYTH_COST, 3, ("cast", 75, 3)),           # [η] 료멘 스쿠나 : Z 고죠 + Z 카네키 (고죠 궁극기 3회)
    (89,  [(11, 1), (15, 1)], MYTH_COST, 3, ("cast", 11, 5)),           # [ζ] 미도리야 원포올 : Z 올마이트 + Z 사이타마 (올마이트 궁극기 5회)
    (95,  [(97, 1)], MYTH_COST, 3, None),                               # [α] 오공 극의징조 : Z 블루 계왕권 오공
    (192, [(92, 1), (16, 2)], MYTH_COST, 4, None),                      # [Φ] 이와토 스즈메 : Z 미코토 + 7☆엘자 x2
    (93,  [(119, 1), (28, 3)], MYTH_COST, 3, ("cast", 119, 5)),         # [ψ] 이치고 천년혈전 : Z 무월 + 7★이치고 x3 (무월 궁극기 5회)
    (57,  [(71, 1), (16, 1), (98, 1), (80, 1), (79, 1), (3, 1)], MYTH_COST, 5, None),   # [φ] 산의 노인 : 7☆ 6종 1개씩
    (23,  [(64, 1), (7, 1)], MYTH_COST, 3, None),                       # [θ] 종미의 거인 : Z 리바이 + Z 에드워드
    (128, [(3, 2)], MYTH_COST, 5, None),                                # [β] 베지트 블루 : 7☆베지터 x2 (원본 조합 미확인 -> 새로 설계)
    (218, [(129, 1), (17, 3)], MYTH_COST, 5, None),                     # [χ] 오메가몬 X : Z 오메가몬 + 7★오공 x3 (원본 조합 미확인 -> 새로 설계)
    (193, [(95, 1)], 300000, 10, ("raid", 81)),                         # 10★ 무의식의 극의 : [α] 극의징조 + 초월석 10 (파티레이드 합체자마스 토벌 후)
]

# --- Z 각성 (Z + 같은 캐릭터 재료 3 + 초월석 5, 최대 5단계): 단계마다 그 영웅 공격력 업그레이드 +1, 5단계는 쉴드 자동 회복
AWAKEN_MAX = 5
AWAKEN_COST = (50000, 5)                       # (강화포인트, 초월석)
AWAKENS = [
    (127, 27, 3), (121, 29, 3), (59, 28, 3), (35, 22, 3), (126, 102, 3),   # 니카/END/리무루/폭쇄아/아수라 + 7★ x3
    (76, 39, 3), (69, 50, 3),                                              # 젠이츠/에스카노르 + 4☆ 히든 x3
    (218, 0, 0),                                                           # 오메가몬 X : 초월석만 (원본: 초월석 5개씩 진화)
]

# --- 파티레이드 공격력 보상 (원본: [신화] [히든] [스킬] 공격력 +n) = 플레이어 공격력 업그레이드 +n
#   그룹 대표 유닛의 무기 업그레이드 번호를 게임 중에 읽어서 올림
UPGRADE_GROUP = {"신화": 97, "히든": 2, "스킬": 70}
RAID_UPGRADES = {144: [("신화", 2), ("히든", 2)], 146: [("신화", 3), ("히든", 3)],
                 138: [("신화", 2), ("히든", 2), ("스킬", 2)], 204: [("신화", 3), ("히든", 3), ("스킬", 3)],
                 81: [("신화", 5), ("히든", 5), ("스킬", 5)]}

# --- 영웅 궁극기: 영웅을 선택하고 H(홀드)를 누르면 발동. 쿨타임은 본인 화면 왼쪽 위 글줄에 표시
HUD_LINES = 4                                  # 쿨타임을 보여줄 영웅 수 (글줄 0~3)
HERO_SHORT = {121: "나츠", 97: "오공", 64: "리바이", 92: "미코토", 59: "리무루", 129: "오메가몬", 7: "에드워드",
              36: "카네키", 96: "스바루", 34: "사테라", 192: "스즈메", 95: "극의징조", 193: "무의식의 극의", 23: "종미의 거인",
              168: "인드라 사스케", 93: "천년혈전 이치고", 130: "스쿠나", 89: "원포올 미도리야", 90: "드래곤씬 멜리오다스"}
#   (아래 표 설명) 주변에 웨이브가 있고 영웅이 내 필드에 있으면 웨이브 즉사 + 공격 유닛
#   (대사, 공격 유닛, 주변 웨이브 즉사 수, 쿨타임 틱)   공격 유닛 = 잠깐 나타나 공격하는 유닛(원본 스킬 유닛)
SKILL_DUR = 48
HERO_SKILLS = {
    127: ("루피 「 고무고무 바쥬랑 건  【원신총】」", 70, 15, 360),
    126: ("나루토 「 용둔 나선수리검 【仙術】」", 70, 15, 360),
    119: ("이치고 「 무 월 【無月】」", 103, 15, 360),
    121: ("나츠 「 E.N.D 해방 【이그닐의 불꽃】」", 70, 15, 360),
    35:  ("셋쇼마루 「 폭쇄아 【爆碎牙】」", 70, 15, 360),
    97:  ("오공 「 블루 계왕권 20배 【かめはめ波】」", 70, 15, 360),
    11:  ("올마이트 「 유나이티드 스테이츠 오브 스매시  【United States of SMASH】」", 43, 15, 360),
    64:  ("리바이 「 회전 베기 【인류 최강의 병사】」", 70, 15, 360),
    69:  ("에스카노르 「 크루엘 썬【무자비한 태양】」", 13, 15, 360),
    76:  ("젠이츠 「 번개의 호흡 제 1형 벽력일섬 6연  【Thunderclap and Flash】」", 70, 15, 360),
    75:  ("고죠 사토루 「 술식 반전  혁【赫】」", 44, 15, 360),
    168: ("사스케 「 아마테라스 【仙術】」", 103, 15, 360),
    190: ("키리토 「 스타 버스트 스트림  【Star Bust Sterm】」", 70, 15, 360),
    91:  ("메구밍 「 익 스 플 로 전 【대폭발】」", 30, 25, 480),
    92:  ("미코토 「 레일건 【초전자포】」", 43, 15, 360),
    82:  ("네테로 「 백 식 관 음 【제로의 장】」", 72, 15, 360),
    59:  ("리무루 「 폭식자 【벨제뷔트】」", 70, 15, 360),
    41:  ("유희 「 현세로 올라와라! 천공의 신,【오시리스】」", 70, 15, 360),
    48:  ("세이버 「 엑스칼리버 【Excalibur】」", 43, 15, 360),
    129: ("오메가몬 「 그레이 소드 【Grey Sword】」", 70, 15, 360),
    15:  ("사이타마 「 연-속 보통펀치【連速】」", 8, 20, 300),
    7:   ("에드워드 「 연성 【등가교환】」", 70, 15, 360),
    36:  ("카네키 「 혁자 【赫子】」", 44, 15, 360),
    96:  ("스바루 「 사망회귀 【Return by Death】」", 103, 10, 360),
    # 9★ 신화
    34:  ("사테라 「 질투의 그림자 【嫉妬】」", 103, 30, 300),
    109: ("아템 「 나와라! 삼 환 신【오시리스/오벨리스크/라】」", 9, 30, 300),
    191: ("우타 「 토 트 무 지 카  【 U.T.A WORLD 】」", 70, 30, 300),
    90:  ("멜리오다스 「 풀 카운터 【Full Counter】」", 70, 30, 300),
    162: ("앨리스 「 【Enhance Armament】 매섭게 몰아치거라ㅡ 꽃들이여!  」", 70, 30, 300),
    130: ("료멘 스쿠나 「 영역전개 복마어주자 【ふくまみづし】」", 44, 30, 300),
    89:  ("미도리야 「 유나이티드 스테이츠 오브 월드 스매시  【United States of World SMASH】」", 43, 30, 300),
    95:  ("오공 「 극의 징조 【身勝手の極意】」", 70, 30, 300),
    192: ("스즈메 「 문단속 【閉じます】」", 70, 30, 300),
    93:  ("이치고 「 최후의 월아천충 - 내 자신이 월아가 되는것이다!!! 」", 103, 30, 300),
    57:  ("산의 노인 「 아즈라엘 【죽음을 고하는 천사】」", 72, 30, 300),
    23:  ("「 '종미의거인'이 땅울림을 시전합니다.」", 13, 40, 300),
    128: ("베지트 「 빅 뱅 어 택 【Big Bang】」", 70, 30, 300),
    218: ("오메가몬X 「 올 딜리트  【ALL DELETE】」", 70, 40, 300),
    193: ("오공 「 무의식의 극의 완성형 」", 70, 50, 240),
}
SUMMON_ON_SKILL = {41: 62}                     # 유희 궁극기 -> 오시리스의 천공룡 (없으면 1마리 소환, 아템 조합 재료)
U_SUBARU, U_SATELLA, U_ESCANOR = 96, 34, 69
NOON_WINDOW = (62, 72)                         # 에스카노르 정오: 카운트다운 1분 2초 ~ 1분 12초 동안 무적

# --- F10 미션 오브젝트 안내 (원본 강화·퓨전 안내 문구 + 신화 조합)
MISSION_TEXT = (
    "\x1f[2★] \x04강화포인트 250 (100%)  \x1f[3★] \x04500 (80%)  \x1f[4★] \x041,000 (60%)\n"
    "\x1f[5★] \x042,000 (40%)  \x1f[6★] \x044,000 (20%)  \x1f[7★] \x048,000 (10%)\n"
    "\x1f[8★] \x04퓨전 조합 (같은 결과는 1개만)  \x1f[히든] \x04강화포인트 x4, 확률 1/2\n"
    "\x1f[천장] \x04같은 유닛 강화 10회 실패시 상위등급 증정 (히든X)\n"
    "\x07『 퓨전 ☆x7 Y등급 』 \x0410,000point  (재료를 플레이어존 오른쪽 퓨전 띠에)\n"
    "\x04조로=6★루피x2+4☆멜리오다스  사스케=6★나루토x2+4☆에렌  토시로=6★이치고x2+4☆탄지로\n"
    "\x04엘자=6★나츠x2+4☆미도리야  셋쇼마루=6★이누야샤x2+6★나루토  베지터=6★오공x2+6★이치고\n"
    "\x07『 퓨전 ★x8 Z등급 』 \x0450,000point\n"
    "\x04니카=7★루피x2+조로  아수라=7★나루토x2+사스케  무월=7★이치고x2+토시로\n"
    "\x04END=7★나츠x2+엘자  폭쇄아=7★이누야샤x2+셋쇼마루  블루계왕권=7★오공x2+베지터\n"
    "\x07『 히든 Z 』 \x04올마이트/리바이/에스카노르/젠이츠 = 4☆ x3, 고죠 = 4☆ 4종 1개씩\n"
    "\x04키리토=조로+셋쇼마루  메구밍=엘자+베지터  미코토=토시로+사스케  인드라사스케=7☆사스케x2+7★나루토\n"
    "\x04네테로/리무루/유희 = 7★2종+초월석  세이버=7★루피·나루토·이치고  오메가몬=7★나츠·이누야샤·오공\n"
    "\x10『 9★ 신화 』 \x04100,000point + 초월석 (게임에 1명만)\n"
    "\x04사테라=스바루+메구밍(사망회귀100)  아템=유희+오시리스+7★이누야샤x4  우타=니카+조로x2\n"
    "\x04드래곤씬=에스카노르+7★나츠x3  앨리스=키리토+7★나루토x3  스쿠나=고죠+카네키(고죠 궁극기3)\n"
    "\x04원포올=올마이트+사이타마(궁극기5)  극의징조=블루계왕권  스즈메=미코토+엘자x2\n"
    "\x04천년혈전=무월+7★이치고x3(궁극기5)  산의노인=7☆ 6종  종미의거인=리바이+에드워드\n"
    "\x04베지트=베지터x2  오메가몬X=오메가몬+7★오공x3  \x11무의식의극의=극의징조+초월석10(레이드 합체자마스 후)\n"
    "\x1f『 Z 각성 』 \x04Z + 같은 캐릭터 7★(히든은 4☆) x3 + 초월석5 + 50,000point, 최대 5단계"
)

# --- 음성 (sound/staredit/wav 의 원본 음성 파일). 파일 이름만 적으면 됨
#   보스: 등장(형태 변화) 때 모두에게 / 영웅: 궁극기 쓸 때 본인에게
BOSS_VOICE = {165: "BOSSruccivoice1", 172: "BOSSruccivoice2", 170: "BOSSsaskevoice1", 163: "BOSSbyakuyavoice1",
              169: "BOSStitan1", 164: "BOSStitan2", 154: "BOSStitan2", 159: "BOSStitan1",
              167: "BOSSkatakuryvoice1", 171: "BOSSpainvoice1", 173: "BOSSpainvoice2", 155: "BOSSulquivoice1", 174: "BOSSulquivoice3",
              152: "BOSSestarotsavoice1", 148: "BOSSkaidowvoice1", 147: "BOSSkaidow2", 131: "BOSSmadaravoice1", 133: "BOSSmadaravoice2",
              135: "BOSSizenvoice1", 132: "BOSSizenvoice2", 143: "BOSSFFvoice1", 138: "BOSSFFvoice2", 144: "BOSSCCvoice1",
              146: "BOSSBBvoice2", 210: "BOSS6voice1", 211: "BOSS6voice2", 25: "BOSS6voice3", 203: "BOSS6voice4", 204: "BOSS6voice5",
              145: "BOSSBRvoice1", 81: "BOSSBRvoice3", 158: "BOSSkefravoice1", 161: "BOSStotpovoice1", 197: "JIRENvoice0"}
HERO_VOICE = {127: "LUFFY1", 126: "NARUTO1", 119: "ICHIGO1", 121: "5NATSU", 35: "SETSYOMARU0", 97: "OGONG01", 11: "ALLMIGHT1",
              64: "RIBY0", 69: "ESCANOR1", 76: "ZENICH0", 75: "SATORU1", 168: "SASKE11", 190: "KIRITO1", 91: "MAGUMING1",
              92: "MIKOTO1", 82: "NETERO1", 59: "RMRU0", 41: "ATEM0", 48: "SAYBER10", 129: "OMEGA10", 15: "SITAMA1", 7: "EDWARD0",
              36: "KNEKI0", 96: "SBARU1", 34: "SATERA10", 109: "ATEM10", 191: "UTA10", 90: "MELODAS10", 162: "ELICE10",
              130: "SKUNA10", 89: "MIDORIYA10", 95: "OGONG10", 192: "SZME10", 93: "ICHIGO10", 57: "SAN10", 23: "EREN10",
              128: "VEGET10", 218: "OMEGAX10", 193: "OGONG11"}
# ---- 각성 궁극기 / 합동필살기 / 새 영웅 대사 ----
# 각성 궁극기는 기본 스킬과 다른 대사(원본 맵에 들어있던 두 번째 대사 파일)를 씀
ULT2_VOICE = {89: "MIDORIYA11", 90: "MELODAS11", 162: "ELICE11", 93: "ICHIGO11", 57: "SAN11", 128: "VEGET11"}
# 새 영웅 대사: sound/staredit/wav 폴더에 아래 이름의 wav 파일을 넣으면 자동으로 연결됨 (없으면 소리 없이 진행)
#   H 스킬 = 이름.wav / 각성 궁극기 = 이름_U.wav
NEW_VOICE = {180: "RENGOKU", 181: "GIYU", 182: "GON", 183: "GON10", 184: "ITADORI", 185: "MERUEM",
             207: "TANJIRO", 226: "YORIICHI"}
import os as _os
_WAV = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "sound", "staredit", "wav")
for _h, _n in NEW_VOICE.items():
    if _os.path.exists(_os.path.join(_WAV, _n + ".wav")):
        HERO_VOICE[_h] = _n
    if _os.path.exists(_os.path.join(_WAV, _n + "_U.wav")):
        ULT2_VOICE[_h] = _n + "_U"
UPGRADE_SUCCESS_VOICE = "UP1"

# 테스트용 진단 메시지 (확인 끝나면 False)
SHOW_DIAG = True

# =====================================================================
#  새 9★ / 10★ 영웅 (빈 유닛 칸 182~185 사용)
#   stat_from : 능력치(체력·무기·공격속도 등)를 복사해 올 유닛
#   look_from : 생김새(그래픽·초상화·크기·목소리)를 복사해 올 유닛
#   ※ 스타 리마스터는 새 그림을 넣을 수 없어서 기존 영웅 모습을 빌려 씀 (look_from 만 바꾸면 모습 변경)
# =====================================================================
NEW_HEROES = [
    dict(unit=182, tier=9,  name="\x1f[κ] \x04성인 곤 프릭스",       stat_from=95,  look_from=39),
    # 곤 10★ : 타수형(체력 400 = 400대) + 한 방이 아주 센 대신 느린 주먹 (원작: 제약과 서약으로 얻은 일격)
    dict(unit=183, tier=10, name="\x11[Ω] \x04곤 - 제약과 서약",      stat_from=193, look_from=69,
         hp=400, armor=255, weapon=dict(id=107, dmg=36000, bonus=600, factor=1, cooldown=30)),
    dict(unit=184, tier=9,  name="\x1f[ι] \x04이타도리 유지",         stat_from=130, look_from=2),
    # 메르엠 10★ : 만능형 - 공격은 무의식의 극의와 같고, 1초마다 최대 체력의 1% 자가 회복 (원작: 압도적 재생력)
    dict(unit=185, tier=10, name="\x11[Ω] \x04메르엠 - 왕",           stat_from=193, look_from=36,
         regen=1),
]
MYTHS += [
    (182, [(82, 1), (76, 1)], MYTH_COST, 3, None),        # [κ] 성인 곤 : Z 네테로 + Z 젠이츠
    (184, [(11, 1), (75, 1)], MYTH_COST, 3, None),        # [ι] 이타도리 : Z 올마이트 + Z 고죠
    (183, [(182, 1)], 300000, 10, None),                  # 10★ 곤 제약과 서약 : [κ] 성인 곤 + 초월석 10
    (185, [(184, 1), (130, 1)], 300000, 10, None),        # 10★ 메르엠 왕 : [ι] 이타도리 + [η] 스쿠나 + 초월석 10
]
HERO_SKILLS.update({
    182: ("곤 「 잼 켄 그 - 바위 【ジャジャン拳】」", 70, 30, 300),
    184: ("이타도리 「 흑 섬 【黒閃】」", 44, 30, 300),
    183: ("곤 「 제약과 서약 - 성인화 일격 【誓約と制約】」", 72, 50, 240),
    185: ("메르엠 「 왕의 일격 【蟻の王】」", 72, 50, 240),
})
HERO_SHORT.update({182: "성인 곤", 183: "곤(제약과 서약)", 184: "이타도리", 185: "메르엠", 162: "앨리스", 109: "아템",
                   191: "우타", 130: "스쿠나", 57: "산의 노인", 128: "베지트", 218: "오메가몬X"})

# =====================================================================
#  궁극기 각성 (9★·10★ 전용 두 번째 스킬 : P(패트롤) + 원하는 곳 클릭)
#   퓨전 띠에 9★/10★ 영웅을 올리면 강화포인트·초월석을 내고 각성 (영웅마다 1번)
# =====================================================================
ULT_AWAKEN_COST = (200000, 5)        # (강화포인트, 초월석)
ULT2_LOC_P = [158, 159, 160, 161]    # 플레이어별 궁극기2 대상 위치 (게임 중 클릭한 곳으로 옮김)
ULT2_RADIUS = 160                    # 범위 반지름 (픽셀, 32 = 1칸)
ULT2_CD = 1080                       # 쿨타임 (틱, 24 = 1초 -> 45초)
#   각성 궁극기 표 : 실제 애니 필살기 + 연출 + 보스에게 직접 피해
#   kind   : "attack" 범위 안 적(보스 P6·레이드 P8)에게 dmg 를 hits 번 (타수 보스는 1번 = 1타)
#            "heal"   dur 동안 우리 편 전체 체력·쉴드 계속 100% (무한 힐)
#            "seal"   dur 동안 범위 안 보스 행동 봉인 + 피해
#   fx     : 범위 안 여러 지점에서 차례로 터지는 연출 유닛 (원본 보스 스킬 연출 유닛)
#   finale : 마지막에 가운데서 크게 터지는 연출 유닛
#   atk    : dur 동안 소환되어 같이 싸우는 유닛 (0 = 없음)
#   dur    : 지속 틱 (24 = 1초)
def U2(name, kind="attack", dmg=150000, hits=4, fx=(70, 13), finale=72, atk=0, dur=72, self_heal=False):
    return dict(name=name, kind=kind, dmg=dmg, hits=hits, fx=fx, finale=finale, atk=atk, dur=dur, self_heal=self_heal)

ULT2_SKILLS = {
    # --- 9★ (10★ 재료인 극의징조·성인 곤·이타도리·스쿠나는 아래 코드에서 자동 제외)
    89:  U2("미도리야 「 1,000,000% 델라웨어 디트로이트 스매시 【DELAWARE DETROIT SMASH】」", dmg=180000, hits=4, fx=(13, 30), finale=70, atk=43),
    34:  U2("사테라 「 그림자의 포옹 - 질투의 마녀 【嫉妬の魔女・影】」", dmg=160000, hits=5, fx=(103, 103), finale=103, atk=103),
    109: U2("아템 「 신의 일격 - 갓 블레이즈 캐논 【ゴッド・ブレイズ・キャノン】」", dmg=200000, hits=3, fx=(9, 13), finale=70, atk=9),
    191: U2("우타 「 세계의 계속 【世界のつづき】 - 10초 동안 우리 편 무한 회복 」", kind="heal", dmg=0, hits=0, fx=(72, 72), finale=72, dur=240),
    90:  U2("멜리오다스 「 리벤지 카운터 【リベンジカウンター】」", dmg=220000, hits=3, fx=(103, 70), finale=13, atk=0),
    162: U2("앨리스 「 기억 해방술 - 금목서의 검 【Release Recollection】」", dmg=150000, hits=5, fx=(72, 70), finale=72, atk=0),
    192: U2("스즈메 「 요석 봉인 【要石】 - 6초 동안 보스 행동 봉인 」", kind="seal", dmg=80000, hits=3, fx=(94, 72), finale=94, dur=144),
    93:  U2("이치고 「 월아십자충 【月牙十字衝】」", dmg=200000, hits=4, fx=(103, 70), finale=103, atk=0),
    57:  U2("산의 노인 「 만종 - 명계의 종소리 【晩鐘】」", dmg=250000, hits=2, fx=(94, 13), finale=94, atk=0),
    23:  U2("에렌 「 땅울림 - 초대형 거인 행진 【地鳴らし】」", dmg=120000, hits=6, fx=(13, 30), finale=13, atk=0, dur=96),
    128: U2("베지트 「 파이널 카메하메파 【ファイナルかめはめ波】」", dmg=210000, hits=4, fx=(70, 13), finale=70, atk=0),
    218: U2("오메가몬X 「 가루루 캐논 + 그레이 소드 【ガルルキャノン】」", dmg=190000, hits=4, fx=(43, 70), finale=13, atk=0),
    # --- 10★
    193: U2("오공 「 완성 극의 - 은빛 카메하메파 【身勝手の極意・かめはめ波】」", dmg=350000, hits=5, fx=(70, 13), finale=70, atk=0, dur=96),
    183: U2("곤 「 최후의 잼 켄 그 【ジャジャン拳・グー】 - 이걸로 끝나도 좋아 」", dmg=1200000, hits=1, fx=(13, 30), finale=13, atk=0, dur=72),
    185: U2("메르엠 「 왕의 일격 - 원(圓) 흡수 【蟻の王】 - 피해 + 자신 완전 회복 」", dmg=300000, hits=5, fx=(73, 13), finale=94, atk=0, dur=96, self_heal=True),
}

# =====================================================================
#  조합 도감 (빈 공간 R1 에 조합 캐릭터를 하나씩 세워둠, 클릭하면 설명)
#   설명 문구는 tools_dev/make_gallery.py 가 gallery_data.py 로 만들어 줌
# =====================================================================
GALLERY_LOC = 157
TEMP_LOC = 162                       # 유닛을 원하는 좌표에 만들 때 쓰는 임시 위치
GALLERY_OWNER = 11                   # P12 (중립) - 공격하지 않고 클릭만 됨

# =====================================================================
#  타수형 영웅 : 공격력과 상관없이 한 대 맞을 때마다 체력 1 (체력 = 버틸 수 있는 타수)
#   원본에서 체력이 아주 낮게 설정된 미도리야·올마이트·스바루·사테라 라인
#   (쉴드 65535 를 "맞았는지 감지용"으로 씀 -> 한 번에 65535 넘게 맞지 않는 한 1타 = 체력 1)
# =====================================================================
HIT_HEROES = [113, 111, 2, 89, 11, 96, 34, 183]      # 183 = 곤 제약과 서약 (체력 400)
#  타수 보스(마인부우·블랙오공)는 체력을 8,000,000 으로 두고 매 프레임 되돌리며 타수를 셈
#   -> 한 프레임에 아무리 세게 맞아도 1타. 남은 타수는 화면 왼쪽 글줄에 표시
HIT_BOSS_HP = 8000000
HIT_HUD_LINE = 6

# =====================================================================
#  자동강화 패널 (각 플레이어 게이트웨이 아래 건물)
#   버튼 1: 자동강화 ON/OFF   버튼 2: 목표 ▲   버튼 3: 목표 ▼
#   ON 이면 내 필드의 일반 영웅을 목표 ★ 까지 0.5초에 1마리씩 강화존으로 보냄 (강화포인트 있을 때만)
# =====================================================================
U_AUTO_PANEL = 179                    # 패널 건물 (원본의 안 쓰는 칸)
U_AUTO_BTN = [176, 177, 178]          # 버튼을 누르면 잠깐 생기는 표시 유닛 (ON/OFF, ▲, ▼)
AUTO_PANEL_NAME = "\x1f『 자동강화 』"
AUTO_BTN_NAMES = ["\x1f자동강화 ON/OFF", "\x1f목표 ▲", "\x1f목표 ▼"]
AUTO_BTN_ICON = [386, 388, 389]       # 재생 / 빠르게 / 느리게 아이콘
AUTO_BTN_STR = [582, 593, 615]        # 버튼 글자 칸 (영문 클라이언트에선 아래 문구로 바뀜, 한글 클라이언트는 기본 문구)
AUTO_BTN_TEXT = ["q\x01자동강화 ON/OFF (\x03Q\x01)", "w\x01목표 ★ 올리기 (\x03W\x01)", "e\x01목표 ★ 내리기 (\x03E\x01)"]
AUTO_DEFAULT_TARGET = 4
AUTO_PANEL_DY = 80                    # 게이트웨이에서 아래로 (픽셀) - 소환소 방(6x6칸) 안 게이트웨이 바로 밑 2x2칸
AUTO_HUD_LINE = 5

# 10★ 재료가 되는 9★ 은 퓨전 띠에서 10★ 조합만 되도록 궁극기 각성을 뺌 (한 발판에서 두 가지가 겹치지 않게)
#   극의징조(-> 무의식의 극의), 성인 곤(-> 제약과 서약), 이타도리·스쿠나(-> 메르엠)
_MYTH_MATS = {u for _r, _mats, *_x in MYTHS for u, _n in _mats}
for _u in list(ULT2_SKILLS):
    if _u in _MYTH_MATS:
        del ULT2_SKILLS[_u]

# =====================================================================
#  테스트용 채팅 명령어 (CHEAT_ID 아이디만, 게임 채팅에 입력)
#   /스킵  /포인트  /초월석  /자원  /명령어  + 소환 (/극의징조 소환 처럼 뒤에 아무 말 붙여도 됨)
#   배포할 때 끄려면 CHEAT_ON = False
# =====================================================================
CHEAT_ON = True
CHEAT_ID = "sdgh17"
CHEAT_SPAWN = [
    ("/극의징조", 95), ("/올포원", 89), ("/원포올", 89), ("/무의식", 193), ("/성인곤", 182), ("/제약곤", 183),
    ("/이타도리", 184), ("/메르엠", 185), ("/스쿠나", 130), ("/사테라", 34), ("/스바루", 96), ("/니카", 127),
    ("/블루오공", 97), ("/베지트", 128), ("/오메가몬", 129),
]
CHEAT_POINT = 1000000
CHEAT_STONE = 10
CHEAT_RES = 1000000


# =====================================================================
#  귀멸의 칼날 신규 영웅 (빈 유닛 칸 180, 181, 207, 226)
# =====================================================================
NEW_HEROES += [
    dict(unit=180, tier=8,  name="\x1bZ \x04렌고쿠 쿄쥬로",              stat_from=121, look_from=16, gfx=40),   # 그림만 페닉스(검 든 질럿 영웅)
    dict(unit=181, tier=8,  name="\x1bZ \x04토미오카 기유",              stat_from=119, look_from=71, gfx=9),    # 그림만 인페스티드 케리건
    dict(unit=207, tier=9,  name="\x1f[ο] \x04히노카미 카구라 탄지로",    stat_from=95,  look_from=39),
    dict(unit=226, tier=10, name="\x11[Ω] \x04츠기쿠니 요리이치",        stat_from=193, look_from=93),
]
FUSIONS += [
    (180, [(39, 2), (16, 1)], 50000, 0),     # 렌고쿠 : 4☆ 탄지로 x2 + 7☆ 엘자
    (181, [(39, 2), (71, 1)], 50000, 0),     # 기유   : 4☆ 탄지로 x2 + 7☆ 토시로
]
MYTHS += [
    (207, [(180, 1), (181, 1)], MYTH_COST, 3, None),           # [ο] 히노카미 탄지로 : Z 렌고쿠 + Z 기유
    (226, [(207, 1)], 300000, 10, ("inf",)),                   # 10★ 요리이치 : [ο] 탄지로 + 무한성 레이드 클리어
]
HERO_SKILLS.update({
    180: ("렌고쿠 「 염의 호흡 제9형 - 연옥 【煉獄】」", 103, 15, 360),
    181: ("기유 「 물의 호흡 제11형 - 잔잔한 물결 【凪】」", 72, 15, 360),
    207: ("탄지로 「 히노카미 카구라 - 휘휘은광 【輝輝恩光】」", 70, 30, 300),
    226: ("요리이치 「 해의 호흡 - 일륜 【日の呼吸】」", 70, 50, 240),
})
HERO_SHORT.update({180: "렌고쿠", 181: "기유", 207: "히노카미 탄지로", 226: "요리이치"})
ULT2_SKILLS[226] = U2("요리이치 「 해의 호흡 제13형 【日の呼吸・拾参ノ型】」", dmg=400000, hits=5, fx=(103, 70), finale=103, atk=0, dur=96)
for _u in list(ULT2_SKILLS):                     # 10★ 재료가 되는 9★ 은 각성 없음 (다시 적용)
    if _u in {u for _r, _mats, *_x in MYTHS for u, _n in _mats}:
        del ULT2_SKILLS[_u]

# =====================================================================
#  무한성 레이드 이벤트 (6장 클리어 후 상시 개방)
#   플레이어존 왼쪽 아래 발판(L078~081)에 영웅 1명 -> 무한성(L163)
#   상현3 -> 상현2 -> 상현1 -> 무잔 3단계. 무잔까지 잡으면 참가자는 "각성 궁극기" 해금 자격
#   보스는 끝난 1~3장 보스 칸을 재활용 (이름·능력치·무기를 이벤트 때 바꿈)
# =====================================================================
INF_OPEN_CHAPTER = 6                 # 이 챕터(1부터)를 클리어하면 열림
INF_ROOM = 163
INF_SKILL_LOC = 164
INF_PAD = [78, 79, 80, 81]
INF_OWNER = 7                        # P8 (파티레이드와 같은 적 컴퓨터)
INF_SIGN_UNIT = 222
INF_SIGN_NAME = "\x08무 한 성 \x04(입장:1명)"
INF_RETRY = 600                      # 클리어 후 다시 열릴 때까지 (초)
INF_FAIL_RETRY = 120                 # 실패 후 다시 열릴 때까지 (초)
INF_WEAPON_FROM = 89                 # 보스 무기를 복사해 올 무기 (톳포)
#  unit: 재활용 칸   weapon: 전용 무기 번호 (안 쓰는 무기 칸)   time: 제한시간(초)
#  skills: (주기 틱, 연출 유닛, 공격 유닛, 공격 유닛 유지 틱, 방 안 우리 유닛 체력 % (0 = 없음), 경고 문구)
INF_STAGES = [
    dict(unit=165, weapon=52, name="\x08상현 3 \x04아카자", hp=6000000, sh=50000, ar=220, dmg=1500, cd=8, factor=1, time=240,
         reward=(100000, 2),
         intro="\x13\x08【 무한성 1 / 4 】 \x04상현 3 아카자\n\x13\x04『 너도 귀신이 되어라! 그러면 영원히 강해질 수 있다! 』",
         skills=[(96, 13, 44, 24, 0, "\x13\x08술식 전개 \x04- 파괴살 · 난식")]),
    dict(unit=170, weapon=53, name="\x08상현 2 \x04도우마", hp=7000000, sh=55000, ar=230, dmg=1800, cd=12, factor=1, time=240,
         reward=(150000, 2),
         intro="\x13\x08【 무한성 2 / 4 】 \x04상현 2 도우마\n\x13\x04『 너희를 구원해 줄게. 내 안에서 영원히 함께하자. 』",
         skills=[(160, 72, 72, 48, 70, "\x13\x08혈귀술 \x04- 동결 연꽃 \x05(방 안 체력 70%)")]),
    dict(unit=163, weapon=55, name="\x08상현 1 \x04코쿠시보", hp=8000000, sh=60000, ar=240, dmg=2400, cd=15, factor=2, time=240,
         reward=(200000, 3),
         intro="\x13\x08【 무한성 3 / 4 】 \x04상현 1 코쿠시보\n\x13\x04『 달의 호흡... 그 끝을 보여주마. 』",
         skills=[(120, 103, 103, 36, 0, "\x13\x08달의 호흡 \x04- 제16형 월홍 · 편할월")]),
    dict(unit=167, weapon=56, name="\x08귀왕 \x04키부츠지 무잔", hp=8000000, sh=65000, ar=250, dmg=2600, cd=10, factor=2, time=240,
         reward=(0, 0),
         intro="\x13\x11【 무한성 4 / 4 - 1단계 】 \x04키부츠지 무잔\n\x13\x04『 귀살대 따위는 이 몸에게 아무것도 아니다. 』",
         skills=[(100, 70, 44, 36, 0, "\x13\x08무잔 \x04- 촉수 난격")]),
    dict(unit=171, weapon=57, name="\x08귀왕 \x04무잔 - 각성", hp=8000000, sh=65000, ar=250, dmg=3000, cd=10, factor=2, time=240,
         reward=(0, 0),
         intro="\x13\x11【 무한성 4 / 4 - 2단계 】 \x04무잔 각성\n\x13\x04『 이 몸은 천재지변 같은 것이다. 』",
         skills=[(90, 72, 103, 36, 60, "\x13\x08무잔 \x04- 혈귀 세포 폭주 \x05(방 안 체력 60%)")]),
    dict(unit=173, weapon=58, name="\x08귀왕 \x04무잔 - 최종", hp=8000000, sh=65535, ar=255, dmg=3500, cd=10, factor=2, time=300,
         reward=(500000, 5),
         intro="\x13\x11【 무한성 4 / 4 - 최종 】 \x04무잔 최종 형태\n\x13\x04『 해가... 떠오른다... 안 돼...! 』",
         skills=[(80, 13, 70, 36, 0, "\x13\x08무잔 \x04- 최후의 발악"), (240, 72, 72, 48, 50, "\x13\x08무잔 \x04- 육체 팽창 \x05(방 안 체력 50%)")]),
]
INF_CLEAR_TEXT = ("\x13\x11━━━━━━━━━━ 【 무한성 레이드 클리어 】 ━━━━━━━━━━\n"
                  "\x13\x04참가자 전원 \x07강화포인트 +500,000 · 초월석 +5\n"
                  "\x13\x1f이제 참가자는 9★·10★ \x07각성 궁극기\x1f 를 배울 수 있습니다!")


# =====================================================================
#  새 모습 만들기 (기존 그림 + 색 입히기)
#   원본에서 안 쓰는 저그 건물의 이동정보(flingy)·그림묶음(sprite)·그림(image) 칸에
#   다른 유닛의 그림을 복사하고 색 효과를 입혀 새 모습으로 씀
#   from_flingy : 그림을 가져올 모습 (40 = 페닉스 질럿 영웅)
#   slot_flingy : 새 모습을 담을 빈 칸 (23 = 하이브, 24 = 레어 ... 안 쓰는 칸 목록은 README)
#   draw/remap  : 9 + remap 1 주황 불꽃 / 2 초록 불꽃 / 3 파랑 불꽃 / 4 파랑 폭발 ,  16 = 환영(파란 반투명)
# =====================================================================
NEW_LOOKS = []    # ※ 리마스터 고화질 그래픽은 그림을 "그림 번호"로 찾기 때문에 빈 칸에 그림을 복사하는 방식은 화면에 안 나오거나
                  #   지원 안 되는 EUD 로 막힐 위험이 있어 사용 안 함. 대신 아래처럼 기존 모습을 바로 지정.
CHEAT_SPAWN += [("/렌고쿠", 180), ("/기유", 181), ("/탄지로", 207), ("/요리이치", 226)]


# =====================================================================
#  합동 필살기 : 두 영웅이 같은 전투 구역에 적 보스와 함께 있으면 자동 발동 (주인이 달라도 됨)
#   (영웅 A, 영웅 B, 이름, 피해, 타수, 연출 유닛 2개, 마지막 폭발 유닛)
# =====================================================================
COMBO_AREAS = [42, 163, 87, 130, 136, 93, 56, 66]     # 보스방 전체, 무한성, 파티레이드, 셀게임장, 힘의대회, 마을, 2장 마을, 2장 숲
COMBO_LOC = 165                                       # 합동기 대상 위치 (게임 중 보스에게 옮김)
COMBO_RADIUS = 256
COMBO_CD = 1440                                       # 같은 합동기 다시 쓸 때까지 (틱, 60초)
COMBOS = [
    (126, 168, "나루토 × 사스케 「 인 · 양 - 나선수리검 × 인드라의 화살 【陰陽】」", 500000, 4, (70, 103), 13),
    (97, 3,    "오공 × 베지터 「 더블 갓 블루 - 카메하메파 × 파이널 플래시 」", 450000, 4, (70, 13), 70),
    (127, 98,  "루피 × 조로 「 고무고무 킹콩건 × 삼천세계 【三千世界】」", 400000, 4, (13, 72), 13),
    (180, 207, "렌고쿠 × 탄지로 「 염의 호흡 · 연옥 × 히노카미 카구라 【炎 · 日】」", 450000, 4, (103, 103), 103),
    (119, 71,  "이치고 × 토시로 「 월아천충 × 대홍련빙륜환 【月牙 · 氷輪】」", 400000, 4, (103, 72), 72),
    (89, 11,   "미도리야 × 올마이트 「 더블 디트로이트 스매시 【DOUBLE DETROIT SMASH】」", 450000, 4, (13, 30), 70),
    (121, 16,  "나츠 × 엘자 「 화룡의 철권 × 천륜 · 순환의 검 」", 350000, 4, (103, 72), 103),
    (184, 75,  "이타도리 × 고죠 「 흑섬 × 무량공처 【黒閃 · 無量空処】」", 500000, 4, (44, 13), 44),
    (183, 82,  "곤 × 네테로 「 잼 켄 그 × 백식관음 제로의 장 」", 600000, 3, (13, 72), 72),
]

# =====================================================================
#  보스 러시 : 3장 클리어 후 상시. 지금까지 깬 챕터의 보스가 차례로 나오고, 버틴 만큼 보상
#   입장 : 플레이어존 아래 가운데 '보스 러시' 발판 (L166~169) -> 무한성 방을 같이 씀 (둘이 동시에 진행되진 않음)
# =====================================================================
RUSH_OPEN_CHAPTER = 3
RUSH_PAD = [166, 167, 168, 169]
RUSH_SIGN_UNIT = 227
RUSH_SIGN_NAME = "\x1f보스 러시 \x04(입장:1명)"
RUSH_TIME = 90                       # 보스 하나당 제한시간 (초)
RUSH_RETRY = 300                     # 끝난 뒤 다시 열릴 때까지 (초)
RUSH_POINT = 30000                   # 보스 k번째 처치 보상 = k x 이 값
RUSH_STONE_EVERY = 4                 # 이 수만큼 잡을 때마다 초월석 +1
#  (보스 칸, 이 챕터(1부터)를 깨야 등장) - 다른 챕터·레이드·무한성이 재활용하지 않는 보스만
RUSH_ROSTER = [(172, 1), (169, 2), (164, 2), (154, 2), (155, 3), (174, 3), (148, 5), (131, 5), (135, 5),
               (210, 7), (25, 7), (203, 7), (197, 8)]

# =====================================================================
#  현재 목표 안내 (내 화면 왼쪽 글줄)
# =====================================================================
GOAL_HUD_LINE = 7


# ---------------------------------------------------------------------
#  보스 패턴 피하기 (7장 이후 보스 + 무한성 보스)
#   일정 주기마다 우리 영웅 1명 발밑에 스캔 표식 + 미니맵 핑 -> TELE_WARN 틱 뒤 그 자리 폭발
#   폭발 범위(TELE_R 반지름) 안에 남아 있는 우리 유닛은 체력이 cut% 로 떨어짐 (죽지는 않음)
#   표식은 처음 자리에 고정 -> 영웅을 움직여서 빼면 피해 없음. 대상은 플레이어를 돌아가며 고름
# ---------------------------------------------------------------------
TELE_LOC = 170
TELE_R = 96                    # 반지름 3칸
TELE_WARN = 48                 # 약 2초
TELE_MARK = 33                 # 스캐너 스윕 (그림만, 효과 없음)
TELE_BOOM = (13, 30)           # 폭발 연출 유닛
TELE_FROM_CHAPTER = 7
TELE_TEXT = "\x13\x08[ 경 고 ] \x04보스가 큰 기술을 준비합니다! \x11스캔 표식\x04에서 2초 안에 벗어나세요!"


def TELE_RULE(name):
    """스테이지 이름 -> (주기 틱, 맞으면 남는 체력 %). 레이드·FINAL 은 더 자주."""
    if name.endswith(("-R", "-R1", "-R2")) or name == "FINAL":
        return (240, 30)
    if name.startswith(("7", "8")):
        return (360, 50)
    return (300, 30)


INF_TELE = [(300, 40), (270, 40), (240, 30), (240, 30), (210, 30), (180, 20)]   # 무한성 6단계
