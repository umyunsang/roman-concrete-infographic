#!/bin/zsh
# usage: cycle.sh <tag>   (step on v8_14 -> WC_test.blend, renders/<tag>, assets_<tag>, crops, grain+saliency measures)
set -e
W=/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work
D=$W/workers/WC; B=/Applications/Blender.app/Contents/MacOS/Blender; T=$1
$B -b $W/out/roman_concrete_narrative_v8_14.blend --factory-startup --python $D/step.py -- $D/WC_test.blend $D/renders/$T 2>&1 | grep -E "^WC|Error|Traceback|File \"" | grep -v "render {" || true
$B -b $D/WC_test.blend --factory-startup --python $W/workers/inventory/render_assets.py -- $D/assets_$T --only detail_core3_lime_specimen,detail_core4_three_cubes,support_core5_lab,detail_d1_seawater,core1_modern_building --no-selftest 2>&1 | grep -E "RENDER_ASSETS|Error|Traceback" || true
cd $D/meas
uv run -q --no-project --with pillow python -I compose.py compose ../renders/$T ../renders/${T}_map2x.png
uv run -q --no-project --with pillow python -I crops.py ../renders/${T}_map2x.png $T
uv run -q --no-project --with pillow --with numpy --with scipy python -I sal.py ../renders/${T}_map2x.png ../assets_$T/assets_index.json
