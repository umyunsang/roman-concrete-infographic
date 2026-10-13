# 워커 작업 규칙 (로마 콘크리트 A2 포스터 · Blender 지도 고도화)

## 너의 역할
너는 워커다. 감독(혹독한 비평가)이 내준 비평을 고쳐 **지도 렌더**를 고도화한다. 감독은 여러 워커의 결과를 이름을 가린 채 나란히 놓고 비교해 AAA가 아니면 다시 돌려보낸다. 기준은 `team/RUBRIC.md`.

## 절대 규칙
1. **자기 작업 공간만** 고친다: `team/ws_<이름>/` (아래 WS). 본 프로젝트 `~/Documents/로마콘크리트_3D/` 의 다른 파일, 다른 워커 공간, Figma는 **건드리지 않는다**.
2. **GUI Blender·Blender MCP 도구(mcp__blender__*) 사용 금지.** Blender는 백그라운드로만:
   `/Applications/Blender.app/Contents/MacOS/Blender -b $WS/roman_concrete_map.blend --python /Users/um-yunsang/Documents/로마콘크리트_3D/team/bg_run.py -- $WS <스크립트1.py> [스크립트2.py ...]`
   (스크립트는 `$WS/scripts/assets/`에서 찾음. 실패하면 저장 안 함. 한 번에 백그라운드 Blender 하나만.)
3. Meshy·Sketchfab·Comfy 등 **크레딧·외부 다운로드 금지.** 새 형태는 절차 제작(bmesh·수식)으로.
4. **색 금지** — 회색 단계만(Workbench 색 방식 OBJECT, `ob.color=(g,g,g,1)`). 글자 넣기 금지(글은 Figma가 맡음).
5. **글 자리 고정**: 글 상자 `$WS/loop/figma_texts.json`, 글 오버레이 `team/text_overlay_2x.png`. 물체가 글을 가리면 안 됨.
6. 무거운 메시 금지(물체 하나 50만 삼각형 이하, 장면 250만 이하). 메모리 16GB 기기.
7. 끝낼 때 감사 **0**: 글↔물체 0, 글 배경 복잡 0, 프레임 밖 0 (`audit_v7.py` 출력).

## 장면 구조 (요약)
- 카메라 `CAM_iso`: 원근 2점 투시, 화면 pt 1191×1684(A2). 좌표 변환 `asset_utils.py`(Blender 텍스트): `pt_to_world(u,v,h)`, `pts_to_world`, `project_pts`, `screen_bbox`, `rise_per_unit`.
- 컬렉션: 20_LANDMARK(COL_ruined 콜로세움) · 30_TERRAIN(T_land 땅, L10_sea, L02_tiber, W_water_marks) · 35_FIELDS_ROADS(F_centuriatio 밭, R_core_road CORE 흐름 길, R_via_appia, R_via_ostiensis, B_pons1/2 다리) · 40_REGION(봉우리 L01_*, 수도교 L05_aqua_claudia, 베수비오 L07, 폼페이 L08_*, 항구 L09_*, 프리베르눔 L11, 실험실 S_lab_island, 가마 D2_lime_kiln, 팔라티노 L04_palatine, 신전 L03_*) · 45_CORE_SCENES(C1~C5 작업 장면) · 50_DETAIL_MODEL(D1~D4 원리 모형) · 60_TREES · 80_SHAPES/81_NOSHADOW/85_HEADER(카메라 앞 도형·헤더, 그림자 없는 2번째 패스).
- 스크립트(`$WS/scripts/assets/`):
  - 시스템 python3로: `terrain_polys.py`(바다·강 다각형) → `land_tri.py`·`water_tri.py`(삼각분할) → `terrain_hf.py /private/tmp/claude-501/-Users-um-yunsang/e6101edd-22a2-4787-95db-be2ff209cf5a/scratchpad/dem`(땅 높이장; 물체 발자국 `assets/object_footprints.json` 사용)
  - 백그라운드 Blender로: `terrain.py`(수면) · `terrain_mesh2.py`(땅) · `aqueduct.py` · `fill_plains.py`(길·밭·나무) · `bridge.py` · `water.py`(물결) · `overlay_shapes.py`(번호·밑줄·핀·지시선·연표) · `header3d.py` · `detail_models.py` · `peaks_place.py` · `update_footprints.py` · `audit_v7.py` · `render_final.py`(2패스 합성 → `$WS/renders/v7_map_2x.png`)
  - 땅을 바꿨으면 시스템 python3 단계 → `terrain.py terrain_mesh2.py aqueduct.py fill_plains.py bridge.py water.py overlay_shapes.py audit_v7.py render_final.py`. 밭·길만이면 `fill_plains.py bridge.py water.py audit_v7.py render_final.py`.
  - 새 스크립트를 만들어도 됨(같은 폴더). 물체를 옮기면 `update_footprints.py` 후 `terrain_hf.py`부터 다시.
- 확인: `$WS/renders/v7_map_2x.png`(2382×3367, 1pt=2px)를 PIL로 잘라 Read로 본다. 포스터 합성: `python3 /Users/um-yunsang/Documents/로마콘크리트_3D/team/compose.py $WS/renders/v7_map_2x.png $WS/out/poster_2x.png` (→ `poster_2x_1x.png`도 생김).

## 디자인 도구·근거 (참고해서 고칠 것)
- `~/.claude/skills/color-expert/SKILL.md`: 명도 대비·APCA(글 바탕 명도), 회색 단계 위계.
- `~/.claude/plugins/` 의 diagram-design(액소노메트릭·분해도 문법), Li & Agrawala SIGGRAPH 2007 절개도 규칙(축 정렬 절단·계단식 절개·단면만 어둡게) → DETAIL 모형.
- Lu et al. CHI 2020: 고리형 흐름의 기본은 시계 방향 → 우리 ①→⑤(반시계)엔 **명시적 방향 신호** 필요(길 위 셰브런 포장·이정표 등, 글 아님).
- Harrison CHI 2015: 첫인상 500ms — 명도 위계와 초점이 먼저 읽혀야.

## 끝낼 때 낼 것 (`$WS/out/`)
1. `poster_2x.png` (+ `poster_2x_1x.png`) — compose.py로 합성
2. `NOTES.md` — 비평 항목별로 무엇을 어떻게 고쳤는지(스크립트·수치), 감사 출력 마지막 줄, 남은 한계
3. 마지막 응답은 짧게: 고친 항목 목록, 감사 결과, 산출물 경로.
