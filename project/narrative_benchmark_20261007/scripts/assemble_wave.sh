#!/bin/zsh
# Chain worker step.py files in order onto an input blend, then render the two passes.
# usage: assemble_wave.sh <in.blend> <out_tag> <worker>...   e.g. assemble_wave.sh out/v8_14.blend v8_15 WE WD1 WD2 WB WC WA WM
set -euo pipefail
W=/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work
B=/Applications/Blender.app/Contents/MacOS/Blender
IN=$1; TAG=$2; shift 2
C=$W/chain/$TAG; mkdir -p $C
cur=$IN; i=0
for wk in "$@"; do
  i=$((i+1)); nxt=$C/$(printf '%02d' $i)_$wk.blend
  echo "[$i] $wk: $cur -> $nxt"
  $B -b $cur --factory-startup --python $W/workers/$wk/step.py -- $nxt > $C/$(printf '%02d' $i)_$wk.log 2>&1 || { echo "FAIL $wk"; tail -30 $C/$(printf '%02d' $i)_$wk.log; exit 1; }
  grep -qE "Saved|saved" $C/$(printf '%02d' $i)_$wk.log || { echo "NOSAVE $wk"; tail -30 $C/$(printf '%02d' $i)_$wk.log; exit 1; }
  cur=$nxt
done
OUT=$W/out/roman_concrete_narrative_$TAG.blend
[[ -e $OUT ]] && { echo "refusing to overwrite $OUT"; exit 1; }
cp $cur $OUT
cd $W && $B -b $OUT --factory-startup --python scripts/render_tag.py -- $TAG > $C/render.log 2>&1
grep RENDER $C/render.log | cut -c1-200
echo "OUT $OUT"
