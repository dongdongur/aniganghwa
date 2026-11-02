#!/bin/bash
# 새 클라우드 세션에서 한 번 실행: 의존성 설치 + 작업 경로 연결
# 사용: bash setup.sh   (저장소 루트에서)
set -e
R="$(cd "$(dirname "$0")" && pwd)"
pip install --break-system-packages -q "eudplib==0.81.0" || pip install --break-system-packages -q eudplib
# 코드들이 쓰는 고정 경로를 저장소로 연결
mkdir -p /home/claude
ln -sfn "$R" /home/claude/proj2
ln -sfn "$R/tools" /home/claude/tools
mkdir -p "/home/claude/g_EUD-Editor-3/EUD Editor 3"
ln -sfn "$R/tools/eud_editor_data" "/home/claude/g_EUD-Editor-3/EUD Editor 3/Data"
# StormLib (scx 안의 chk 교체용 mpqput.py 가 사용)
if [ ! -f /home/claude/StormLib/build/libstorm.so ]; then
  git clone -q https://github.com/ladislav-zezula/StormLib.git /home/claude/StormLib
  git -C /home/claude/StormLib checkout -q 116135c27e8c0dcf8ea0a0c549a6d737ce10fc73
  cmake -S /home/claude/StormLib -B /home/claude/StormLib/build -DBUILD_SHARED_LIBS=ON >/dev/null
  make -C /home/claude/StormLib/build -j8 >/dev/null
fi
echo "OK. 빌드: python3 /home/claude/proj2/build.py  -> AniGanghwaWorld/out/AniGanghwaWorld_new.scx"
