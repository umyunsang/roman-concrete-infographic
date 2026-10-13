import bpy,runpy,json
from pathlib import Path
import numpy as np
P=Path(__file__).parent;R=Path('/Users/um-yunsang/Documents/로마콘크리트_3D/narrative_benchmark_20261007');H=runpy.run_path(str(R/'scripts/integrate_assets.py'),run_name='helpers')
names=['L03_forum_vesta','L03_forum_temple','L02_tiber','COL_ruined'];a={};records={}
for name in names:
 o=bpy.data.objects[name];m=o.data
 a[name+'_projected']=H['project_pts'](H['world_coords'](o));a[name+'_starts']=np.array([p.loop_start for p in m.polygons]);a[name+'_totals']=np.array([p.loop_total for p in m.polygons]);a[name+'_loops']=np.array([l.vertex_index for l in m.loops]);records[name]={'bbox':H['screen_bbox'](o),'geometrySHA':H['mesh_fingerprint'](m),'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'vertices':len(m.vertices),'polygons':len(m.polygons)}
np.savez_compressed(P/'v10-temple-placement-geometry.npz',**a);(P/'v10-temple-placement-geometry.json').write_text(json.dumps(records,indent=2)+'\n');print('V10_TEMPLE_EXPORT_COMPLETE')
