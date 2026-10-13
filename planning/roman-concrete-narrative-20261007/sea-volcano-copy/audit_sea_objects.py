"""Read-only visible sea-model inventory and original face-geometry export."""
import json,runpy,hashlib
from pathlib import Path
import bpy
import numpy as np

OUT=Path('/Users/um-yunsang/.planning/roman-concrete-narrative-20261007/sea-volcano-copy')
ROOT=Path('/Users/um-yunsang/Documents/로마콘크리트_3D/narrative_benchmark_20261007')
H=runpy.run_path(str(ROOT/'scripts/integrate_assets.py'),run_name='helpers')
names=['L09_portus_lighthouse','L09_portus_mole','L12_harbor_pilae','NB_marine_breakwater']
records={};arrays={};visible=[]
for ob in bpy.data.objects:
 if ob.type!='MESH' or ob.hide_render or not any(not c.hide_render for c in ob.users_collection):continue
 if not ob.name.startswith(('L0','L1','NB_','S_lab')):continue
 bbox=H['screen_bbox'](ob)
 if bbox[3]>1380 and bbox[1]>1250:
  visible.append({'name':ob.name,'bbox':bbox,'materials':[x.name if x else None for x in ob.data.materials]})
for name in names:
 ob=bpy.data.objects[name];m=ob.data
 v=np.empty(len(m.vertices)*3);m.vertices.foreach_get('co',v);v=v.reshape(-1,3)
 starts=np.empty(len(m.polygons),dtype=np.int32);m.polygons.foreach_get('loop_start',starts)
 totals=np.empty(len(m.polygons),dtype=np.int32);m.polygons.foreach_get('loop_total',totals)
 loops=np.empty(len(m.loops),dtype=np.int32);m.loops.foreach_get('vertex_index',loops)
 c=np.array([p.center[:] for p in m.polygons]);n=np.array([p.normal[:] for p in m.polygons]);areas=np.array([p.area for p in m.polygons])
 matrix=np.array(ob.matrix_world);world=v@matrix[:3,:3].T+matrix[:3,3]
 records[name]={'vertices':len(v),'polygons':len(c),'local_min':v.min(0).tolist(),'local_max':v.max(0).tolist(),
  'world_min':world.min(0).tolist(),'world_max':world.max(0).tolist(),'matrix_world':matrix.tolist(),
  'screen_bbox':H['screen_bbox'](ob),'geometry_sha256':H['mesh_fingerprint'](m),
  'materials':[x.name if x else None for x in m.materials],
  'current_material_face_counts':{mat.name:sum(p.material_index==i for p in m.polygons) for i,mat in enumerate(m.materials)}}
 arrays.update({name+'_vertices':v,name+'_starts':starts,name+'_totals':totals,name+'_loops':loops,name+'_centers':c,name+'_normals':n,name+'_areas':areas,name+'_matrix_world':matrix})
result={'source':bpy.data.filepath,'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
 'visible_sea_side_models':sorted(visible,key=lambda d:d['bbox'][0]),'selected_objects':records,
 'method':'Fresh background open, pure geometry/property reads; no material/index/mesh/transform/visibility/save/render/UI writes.'}
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'sea-object-geometry.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
np.savez_compressed(OUT/'sea-object-geometry.npz',**arrays)
print(json.dumps(result,ensure_ascii=False))
