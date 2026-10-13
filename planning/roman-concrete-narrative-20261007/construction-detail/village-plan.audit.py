import bpy,runpy,json,numpy as np
from pathlib import Path
R=Path('/Users/um-yunsang/Documents/로마콘크리트_3D/narrative_benchmark_20261007')
O=Path('/Users/um-yunsang/.planning/roman-concrete-narrative-20261007/construction-detail')
H=runpy.run_path(str(R/'scripts/integrate_assets.py'),run_name='helpers')
rows=[]
for o in bpy.data.objects:
 if o.type!='MESH' or o.hide_render:continue
 b=H['screen_bbox'](o)
 if b[2]>=70 and b[0]<=1120 and b[3]>=340 and b[1]<=1380:
  rows.append({'name':o.name,'bbox':b,'parent':o.parent.name if o.parent else None,'polygons':len(o.data.polygons),'materials':[m.get('semantic_role') for m in o.data.materials]})
o=bpy.data.objects['COL_ruined'];m=o.data;wp=H['world_coords'](o);p=H['project_pts'](wp)
np.savez_compressed(O/'village-plan.hero.npz',points=p,worldz=wp[:,2],starts=np.array([q.loop_start for q in m.polygons]),totals=np.array([q.loop_total for q in m.polygons]),loops=np.array([l.vertex_index for l in m.loops]))
(O/'village-plan.inventory.json').write_text(json.dumps({'source':str(Path(bpy.data.filepath)),'sha256':H['sha256_file'](bpy.data.filepath),'objects':rows},ensure_ascii=False,indent=2)+'\n')
print('inventory',len(rows));print([r for r in rows if r['name'].startswith(('C3','C4','NB_lime','NB_calcium','NB_detail','L02_tiber','COL_'))])
