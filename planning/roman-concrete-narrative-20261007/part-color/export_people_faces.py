import bpy,json
from pathlib import Path
OUT=Path(__file__).resolve().parent
rows={}
for name in ['C2_hot_mixing','C5_researchers','L08_pompeii_site']:
 o=bpy.data.objects[name]
 rows[name]=[{'i':p.index,'center':list(p.center),'normal':list(p.normal),'area':p.area,'lo':[min(o.data.vertices[j].co[k] for j in p.vertices) for k in range(3)],'hi':[max(o.data.vertices[j].co[k] for j in p.vertices) for k in range(3)]} for p in o.data.polygons]
(OUT/'process-face-metrics.json').write_text(json.dumps(rows))
print({n:len(v) for n,v in rows.items()})
