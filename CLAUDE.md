# 애니강화월드 새 버전 — 작업 인수인계 (Claude 용)

스타크래프트 리마스터 EUD 맵 "[EUD]애니강화월드"를 eudplib(파이썬)으로 처음부터 다시 만든 프로젝트.
원본 1~8장 + FINAL 재현, 새 9~11장(헌터헌터·주술회전·원펀맨), 각종 시스템 추가.

## 사용자
- 호칭은 항상 "동동아". 한국어, 짧고 명확하게, 마침표 뒤 한 칸 띄움.
- 배틀넷 아이디 sdgh17 (치트 명령어 허용 아이디).
- 게임을 잘 앎. 의미 없는 기능(운 요소, 한 판에 못 모으는 보상)은 싫어함. 중복 트리거 금지.
- 스킬 기획 원칙: 궁극기는 보스용 공격기(실제 애니 필살기 이름 + 멋진 이펙트), 힐 캐릭은 지속시간 무한힐. 웨이브 즉사형은 금지.
- 실제 게임 테스트는 사용자가 함. 스크린샷으로 피드백 옴.

## 처음 세션 시작할 때
```
bash setup.sh                       # eudplib 0.81 설치, 고정 경로 연결, StormLib 빌드
python3 /home/claude/proj2/build.py # -> AniGanghwaWorld/out/AniGanghwaWorld_new.scx
```
- 위치(로케이션)·유닛 이름·방 복사 등 지형/CHK 를 바꿨으면 기본 맵부터 다시 만든 뒤 빌드:
```
cd /home/claude/proj2
python3 AniGanghwaWorld/tools_dev/add_gallery.py base.chk base_g.chk
python3 /home/claude/tools/mpqput.py base_before_gallery.scx base_g.chk AniGanghwaWorld/base/base_map.scx
python3 build.py
```

## 검증 (에뮬레이터) — 빌드 후 반드시 덤프부터 새로!
```
cd /home/claude/tools
AGW_FAST=1 python3 runemu.py              # emu_dump.pkl 갱신 (안 하면 옛 빌드로 테스트됨! AGW_FAST=1 = 시간 단축, 없으면 한 판 1시간)
DIFF=31 KD=4 python3 drive.py 2400 > /tmp/run.txt   # HARD 전체 판 (약 10분, <<VICTORY>> 확인)
#  DIFF: 난이도, KD: 처치 지연, ALLP=1: 4인
python3 tests/test_inf.py   # 무한성 / test_tele: 보스 패턴 피하기 / test_cr: 합동기·보스러시
python3 tests/test_u2.py    # 각성 궁극기 / test_hit: 타수 영웅·보스 / test_cheat: 치트 / test_new: 새 영웅
```
- 메모리 쓰기 점검: 테스트 스크립트 2번째 줄에 `import wlog` 넣으면 쓴 페이지를 /tmp/wpages_*.pkl 로 기록.
  허용 영역 = 원본도 쓰던 곳, CUnit(0x59CCA8~0x6283E8), 점수/데스, 로케이션 0x58DC60, 글줄 0x640B58~,
  버튼셋 0x5187E8, 요구조건 0x514178, 툴팁 포인터 0x6D5A30(둘 다 실게임 확인됨). 그 외 = 튕김 위험.

## 파일 구조
- `build.py` 빌드 진입점 (sounds → datinit → game 순서, game 이 systems·extras 를 불러옴)
- `AniGanghwaWorld/config.py` 모든 수치·기획 데이터 (챕터/보스/스킬/영웅/이벤트). 대부분 수정은 여기서.
- `game.py` 챕터·스테이지 진행, 보스 스킬(boss_skills), 타수 보스, /스킵
- `systems.py` 강화·조합·신화·영웅 스킬(H=홀드)·각성 궁극기(P=패트롤+클릭)·HUD·BGM·대사
- `extras.py` 새 영웅 데이터 복사, 자동강화 건물, 도감, 치트, 무한성, 합동필살기, 보스러시, 목표 HUD, 보스 패턴 피하기(tele_*)
- `datinit.py / eudfix_data.py / datinit_data.py` 원본 dat 값, 버튼셋·요구조건·툴팁 재배치
- `gallery_data.py` 도감 설명 (tools_dev/make_gallery.py 로 생성)
- `sounds.py` sound 폴더 wav/ogg 를 맵에 넣음. 영웅 대사 = sound/staredit/wav/<HERO_VOICE>.wav
- `tools_dev/add_gallery.py` CHK 편집 (방 복사, 로케이션 157~170, 유닛 이름)
- `README.txt` 단계별 전체 변경 기록 (1단계~), 사용자에게 주는 설명서 겸용
- `tools/` 에뮬레이터(emu.py), 봇(drive.py), dat 기본값(datmodel.py, eud_editor_data), mpqput.py

## 꼭 지킬 것 (실수했던 것들)
- 리마스터 EUD 에뮬레이터: 지원 안 하는 메모리 쓰기 = 맵 실행 불가/튕김. 그림 데이터(images/sprites/flingy 그래픽) 쓰기 금지.
  HD 는 이미지 번호로 그림을 찾아서 GRP 복사 방식 새 모습은 안 보임 → 새 모습은 units.dat 그림 칸(0x6644F8+u)만.
- dat 의 Add/Sub 쓰기는 한 번만 적용 (두 번 적용 버그 있었음).
- `f_dwread(a) + f_dwread(b)` 처럼 같은 함수 두 번을 한 식에 쓰면 반환 변수가 겹쳐 값이 깨짐 → 따로 변수에 읽기.
- 함수 안에서 모듈 EUDVariable 에 `<<`/`+=` 하면 global 선언 필요 (UnboundLocalError).
- 루프 펼치기 남발 금지: chk 22MB 대. 반복 연출은 변수 기반 공용 틱으로.
- 카운트다운 남은 시간은 메모리 대신 조건(CountdownTimer) 빼고-되돌리기 방식으로 읽음.
- /스킵 처럼 클리어를 부르는 곳은 현재 번호를 따로 복사(g_now)해서 연쇄 클리어 방지.
- 타수 보스: HP 8,000,000 으로 두고 매 프레임 복구, 맞은 횟수만 감소. 타수 영웅: 쉴드 65535 감시값.
- 극의징조(95) 는 각성 궁극기 없음 (10★ 조합 재료 전용). 10★ 에 각성기.

## 주요 주소
units.dat 필드 = tools/eud_editor_data/Offset.txt. 버튼셋 0x5187E8(12B/유닛), 요구조건 0x514178 + 인덱스 0x660A70,
로케이션 0x58DC60(20B), CUnit 0x59CCA8+336k(+0x08 HP, +0x28 위치, +0x4C 주인, +0x4D 명령, +0x58 명령 목표,
+0x60 쉴드, +0x64 종류, +0x6C 다음 유닛, +0xDC 상태 무적 0x04000000), 첫 유닛 0x6283F8, 선택 0x6284B8,
이름 0x57EEEB+36p, 채팅 0x640B60(218B x 11줄). 명령 Hold 107, Patrol 152.

## 진행 상태 (2026-11-02)
- 10-1단계 전달 완료 (안전 점검, 렌고쿠=피닉스/기유=감염된 케리건 모습, 각성기 두 번째 대사, 합동기 대사).
- 진행 중: 보스 패턴 피하기 (7장 이후 보스 + 무한성). config TELE_*, INF_TELE, extras.tele_start/tele_tick,
  로케이션 170. 에뮬 검증 후 11단계로 전달 예정.
- 새 영웅 8명 대사: config NEW_VOICE 이름으로 wav 를 넣으면 자동 연결. 파일 자체는 아직 없음
  (클라우드 작업 공간은 일반 사이트에서 파일을 내려받을 수 없음 → 사용자가 파일 제공).
- 남은 아이디어: 4인 동시 발판 쉴드 파괴, 도전 모드(조건부 보스러시), 각성 게이지.
- 지형 다듬기는 화면을 못 보니 사용자 스크린샷 받아서 진행.
