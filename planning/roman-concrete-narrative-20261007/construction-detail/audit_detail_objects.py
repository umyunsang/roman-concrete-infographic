import bpy,runpy,json,hashlib
from pathlib import Path
import numpy as np
P=Path('/Users/um-yunsang/.planning/roman-concrete-narrative-20261007/construction-detail')
R=Path('/Users/um-yunsang/Documents/로마콘크리트_3D/narrative_benchmark_20261007')
H=runpy.run_path(str(R/'scripts/integrate_assets.py'),run_name='helpers')
visible=[];details={};arrays={};candidates={}
for ob in bpy.data.objects:
 vis=not ob.hide_render and any(not col.hide_render for col in ob.users_collection)
 if ob.type=='MESH' and vis:
  box=H['screen_bbox'](ob)
  visible.append({'name':ob.name,'parent':ob.parent.name if ob.parent else None,'bbox':box,'vertices':len(ob.data.vertices),'polygons':len(ob.data.polygons)})
  if (box[0]<430 and box[2]>240 and box[1]>1000 and box[3]<1385) or (box[0]<210 and box[1]>600 and box[3]<800):
   candidates[ob.name]=box
 if ob.name.startswith(('D1_','D2_','D3_','D4_','L_D1','L_D2','L_D3','L_D4')) or ob.name in candidates or ob.name in ['C2_hot_mixing','L03_forum_temple','L03_forum_vesta','L02_tiber','COL_ruined'] or ob.name.startswith(('S_lead','S_sect','NB_core4_sequence','NB_lime_clast_specimen')):
  rec={'type':ob.type,'hide_render':ob.hide_render,'hide_viewport':ob.hide_viewport,'collections':[x.name for x in ob.users_collection],
       'parent':ob.parent.name if ob.parent else None,'children':[x.name for x in ob.children],'matrix_world':[list(row) for row in ob.matrix_world],'color':list(ob.color)}
  if ob.type=='MESH':
   m=ob.data;rec.update({'bbox':H['screen_bbox'](ob),'vertices':len(m.vertices),'polygons':len(m.polygons),'geometrySHA':H['mesh_fingerprint'](m),'materials':[{'name':mat.name if mat else None,'diffuse':list(mat.diffuse_color) if mat else None,'faces':sum(p.material_index==i for p in m.polygons)} for i,mat in enumerate(m.materials)]})
   v=np.array([list(x.co) for x in m.vertices]);starts=np.array([p.loop_start for p in m.polygons]);totals=np.array([p.loop_total for p in m.polygons]);loops=np.array([l.vertex_index for l in m.loops]);c=np.array([list(p.center) for p in m.polygons]);n=np.array([list(p.normal) for p in m.polygons]);a=np.array([p.area for p in m.polygons]);mi=np.array([p.material_index for p in m.polygons]);world=v@np.array(ob.matrix_world)[:3,:3].T+np.array(ob.matrix_world)[:3,3]
   rec.update({'local_min':v.min(0).tolist(),'local_max':v.max(0).tolist(),'world_min':world.min(0).tolist(),'world_max':world.max(0).tolist()})
   for key,val in [('vertices',v),('starts',starts),('totals',totals),('loops',loops),('centers',c),('normals',n),('areas',a),('material_indices',mi),('world',world),('projected',H['project_pts'](world))]:arrays[ob.name+'_'+key]=val
  elif ob.type=='FONT':
   rec['body']=ob.data.body;rec['bbox']=H['screen_bbox'](ob)
  elif ob.type=='CURVE':
   rec['bbox']=H['screen_bbox'](ob);rec['splines']=[{'type':s.type,'points':[list(p.co) for p in s.points]} for s in ob.data.splines];rec['materials']=[m.name if m else None for m in ob.data.materials]
  details[ob.name]=rec
report={'source':bpy.data.filepath,'sourceSHA':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'visible_meshes':visible,'details':details,'hearth_candidates':candidates}
(P/'detail-object-inventory.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');np.savez_compressed(P/'detail-object-geometry.npz',**arrays)
print(json.dumps({'visible':len(visible),'details':len(details),'hearth_candidates':candidates,'detail_roots':{n:r for n,r in details.items() if r['type']=='EMPTY'}},ensure_ascii=False))
