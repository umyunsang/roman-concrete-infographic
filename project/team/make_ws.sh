#!/bin/bash
# 워커 작업 공간 만들기: ./make_ws.sh <이름> [원본 .blend]
# 본 프로젝트(~/Documents/로마콘크리트_3D)는 건드리지 않고 team/ws_<이름>/ 에 필요한 것만 복사, 스크립트의 ROOT 경로를 바꿈.
set -e
SRC="$HOME/Documents/로마콘크리트_3D"
WS="$SRC/team/ws_$1"
BLEND="${2:-$SRC/roman_concrete_map.blend}"
rm -rf "$WS"; mkdir -p "$WS"/{assets,sketch_v2,ref/svg,loop,renders,out}
cp "$BLEND" "$WS/roman_concrete_map.blend"
cp -R "$SRC/scripts" "$WS/scripts"
find "$SRC/assets" -maxdepth 1 -type f \( -name '*.json' -o -name '*.npz' \) -exec cp {} "$WS/assets/" \;
cp -R "$SRC/assets/peaks" "$WS/assets/peaks"
cp "$SRC/sketch_v2/text_zones.json" "$WS/sketch_v2/"
cp "$SRC/ref/svg/water.json" "$WS/ref/svg/"
cp "$SRC/loop/figma_texts.json" "$WS/loop/"
grep -rl "/Users/um-yunsang/Documents/로마콘크리트_3D/" "$WS/scripts" | while read f; do
  sed -i '' "s#/Users/um-yunsang/Documents/로마콘크리트_3D/#$WS/#g" "$f"
done
echo "ws ready: $WS"
