"""Inspect downloaded village sources in an unsaved factory scene only."""
import bpy,runpy,numpy as np,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path('/Users/um-yunsang/Documents/로마콘크리트_3D/narrative_benchmark_20261007')
OUT=Path(__file__).resolve().parent
P=runpy.run_path(str(OUT/'village_parts.py'))
H=runpy.run_path(str(ROOT/'scripts/integrate_assets.py'),run_name='audit_helpers')
assert not bpy.data.filepath,'Use factory startup; do not load production blend.'
models=[];report={}
for name,key in [('NB_village_house','roman_low_house'),('NB_village_market','roman_market_shade'),('NB_village_citizens','roman_ordinary_citizens')]:
 src=ROOT/'models/village_v15'/(key+'.glb');digest=hashlib.sha256(src.read_bytes()).hexdigest()
 ob=H['import_glb']({'path':str(src),'id':key,'object_name':name,'grayscale':.72});models.append(ob);me=ob.data
 v=np.empty(len(me.vertices)*3);c=np.empty(len(me.polygons)*3);n=np.empty(len(me.polygons)*3)
 me.vertices.foreach_get('co',v);me.polygons.foreach_get('center',c);me.polygons.foreach_get('normal',n);v=v.reshape(-1,3);c=c.reshape(-1,3);n=n.reshape(-1,3)
 tri=np.asarray([list(p.vertices)for p in me.polygons],dtype=np.int32)
 np.savez_compressed(OUT/(name+'_local_geometry.npz'),vertices=v,centers=c,normals=n,triangles=tri)
 report[name]={'path':str(src),'source_sha256':digest,'vertices':len(v),'faces':len(c),'local_bbox':[v.min(0).tolist(),v.max(0).tolist()],'geometry_hash':H['mesh_fingerprint'](me)}
assign=P['build_assignments'](bpy);corrections=P['build_correction_masks'](bpy)
assert all(H['mesh_fingerprint'](o.data)==report[o.name]['geometry_hash']for o in models)
def lin(h):
 x=int(h,16)/255;return x/12.92 if x<=.04045 else((x+.055)/1.055)**2.4
for ob in models:
 e=assign[ob.name];roles=[e['default']]+list(e['faces']);ob.data.materials.clear()
 for r in roles:
  h=P['PALETTE'][r].lstrip('#');m=bpy.data.materials.new('AUDIT_'+r);m.diffuse_color=tuple(lin(h[i:i+2])for i in(0,2,4))+(1,);ob.data.materials.append(m)
 for p in ob.data.polygons:p.material_index=0
 for i,r in enumerate(roles[1:],1):
  for j in e['faces'][r]:ob.data.polygons[j].material_index=i
for ob in bpy.data.objects:
 if ob not in models:ob.hide_render=True
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.color_type='MATERIAL';scene.display.shading.light='STUDIO';scene.display.shading.background_type='WORLD';scene.display.shading.background_color=(1,1,1);scene.world.color=(1,1,1);scene.render.film_transparent=False
scene.render.resolution_x=600;scene.render.resolution_y=600;scene.render.resolution_percentage=100;scene.render.use_border=False
camdata=bpy.data.cameras.new('AUDIT_village_camera');cam=bpy.data.objects.new('AUDIT_village_camera',camdata);scene.collection.objects.link(cam);cam.hide_render=False;camdata.type='ORTHO';scene.camera=cam
for ob in models:
 for m in models:m.hide_render=m is not ob
 a=np.load(OUT/(ob.name+'_local_geometry.npz'));v=a['vertices'];lo=v.min(0);hi=v.max(0);center=Vector((lo+hi)/2);scale=float(np.max(hi-lo));camdata.ortho_scale=scale*1.45
 for i,d in enumerate([(2.8,-4,2.8),(-3.5,3,2.5),(0,-4,1.0)]):
  cam.location=center+Vector(d)*scale;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();scene.render.filepath=str(OUT/(ob.name+'_parts_view'+str(i)+'.png'));bpy.ops.render.render(write_still=True)
for ob in models:
 e=report[ob.name];assert H['mesh_fingerprint'](ob.data)==e['geometry_hash'];assert hashlib.sha256(Path(e['path']).read_bytes()).hexdigest()==e['source_sha256']
(OUT/'village-parts-audit.json').write_text(json.dumps({'factory_scene_only':True,'source_glbs_preserved':True,'models':report,'helper_pure':True,'assignments':{n:e['notes']for n,e in assign.items()},'correction_masks':corrections},ensure_ascii=False,indent=2)+'\n')
print('VILLAGE_PART_COUNTS',json.dumps({n:e['notes']for n,e in assign.items()},separators=(',',':')))
print('CORRECTION_COUNTS',json.dumps({n:{k:{j:q[j]for j in ['face_count','bbox','vertex_mean']}for k,q in e.items()}for n,e in corrections.items()},separators=(',',':')))
