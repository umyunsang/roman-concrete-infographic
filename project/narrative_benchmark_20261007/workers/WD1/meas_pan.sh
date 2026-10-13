#!/bin/zsh
# meas_pan.sh <blend> <tag>
D=/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/WD1; cd $D
/Applications/Blender.app/Contents/MacOS/Blender -b $1 --factory-startup --python render_crops.py -- $D/crops $2 jobs_pan2.json 2>&1 | grep -E "rror"
uv run --no-project --with pillow python -I compose.py $D/crops $2 > /dev/null
/Applications/Blender.app/Contents/MacOS/Blender -b $1 --factory-startup --python idmap.py -- $D/crops/$2_jobs_done.json pan2 $D/crops/$2_pan2_id.npz 2>&1 | grep -E "IDMAP|rror"
uv run --no-project --with pillow --with numpy python -I measure_obj.py crops/$2_pan2.png crops/$2_pan2_id.npz R8_pantheon --roof roman_roof --wall roman_stone
