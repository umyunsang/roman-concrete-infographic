#!/bin/zsh
# dev.sh <sections> <tag> <jobs.json> : run step sections on the input, render jobs, compose before/after
W=/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work
D=$W/workers/WD1; cd $D
WD1_SECTIONS=$1 /Applications/Blender.app/Contents/MacOS/Blender -b $W/out/roman_concrete_narrative_v8_14.blend --factory-startup --python step.py -- $D/dev_$2.blend > $D/logs_$2.txt 2>&1
grep -E "Error|rror|Traceback|refus|SystemExit" $D/logs_$2.txt | head -5
python3 -c "
import json; d=json.load(open('$D/dev_$2.report.json')); [print(k, json.dumps(v)[:900]) for k,v in d.items() if k not in ('input','output')]"
if [ -n "$3" ]; then
/Applications/Blender.app/Contents/MacOS/Blender -b $D/dev_$2.blend --factory-startup --python render_crops.py -- $D/crops $2 $3 2>&1 | grep -E "rror"
uv run --no-project --with pillow python -I compose.py $D/crops $2 >/dev/null
uv run --no-project --with pillow python -I -c "
import json
from PIL import Image
for j in json.load(open('$3')):
  n=j['name']
  try: a=Image.open('crops/before_'+n+'.png')
  except FileNotFoundError: continue
  b=Image.open('crops/$2_'+n+'.png')
  c=Image.new('RGB',(a.size[0]+b.size[0]+10,max(a.size[1],b.size[1])),'white'); c.paste(a,(0,0)); c.paste(b,(a.size[0]+10,0)); c.save('crops/cmp_$2_'+n+'.png')
"
fi
