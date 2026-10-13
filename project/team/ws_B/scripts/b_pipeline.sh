#!/bin/bash
# 워커 B 전체 재생성 사슬: (선택) 물체 → 발자국 → 시스템 python3(산괴·높이장·삼각분할) → Blender(땅·길·밭·나무·물·도형·조명·감사·렌더)
# 사용: scripts/b_pipeline.sh [objects]   — objects 주면 peaks_place·palatine_proc 먼저
set -e
WS=/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_B
B=/Applications/Blender.app/Contents/MacOS/Blender
RUN=/Users/um-yunsang/Documents/로마콘크리트_3D/team/bg_run.py
SP=/private/tmp/claude-501/-Users-um-yunsang/e6101edd-22a2-4787-95db-be2ff209cf5a/scratchpad
cd $WS
if [ "$1" = "objects" ]; then
  $B -b roman_concrete_map.blend --python $RUN -- $WS peaks_place.py palatine_proc.py b_sea_ground.py b_lab_rock.py b_kiln_smoke.py b_vesta_roof.py b_vesuvius_clean.py b_c1_quarry.py b_d2_cutaway.py b_shade_set.py 2>&1 | grep -E "STEP|FAIL|Error" || true
fi
$B -b roman_concrete_map.blend --python $RUN -- $WS update_footprints.py 2>&1 | grep -E "FAIL|footprints" || true
python3 scripts/assets/b_polys_patch.py
python3 scripts/assets/range_dem.py $SP/dem11
python3 scripts/assets/terrain_hf.py $SP/dem
python3 scripts/assets/land_tri.py
python3 scripts/assets/water_tri.py
$B -b roman_concrete_map.blend --python $RUN -- $WS terrain.py terrain_mesh2.py b_merge_peaks.py b_lab_rock.py aqueduct.py fill_plains.py bridge.py water.py overlay_shapes.py b_rm_ground.py b_shade_set.py b_look.py audit_v7.py b_audit_extra.py render_final.py 2>&1 | grep -E "FAIL|Error|Traceback|합계|글 배경|배경 |프레임 밖|겹침|final|trees|chevrons|tris|EXTRA" || true
