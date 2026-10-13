"""Temporary native-camera yaw comparison only. Never saves the loaded blend."""
import bpy,runpy,numpy as np,math,json,hashlib
from pathlib import Path
ROOT=Path('/Users/um-yunsang/Documents/로마콘크리트_3D/narrative_benchmark_20261007')
OUT=Path(__file__).resolve().parent
SOURCE=ROOT/'out/roman_concrete_narrative_v11.blend'
EXPECTED='f58d958eee5db375a76779f337681be96f8b7b6f0f0d4ba562f7d9aa3f79f528'
assert Path(bpy.data.filepath).resolve()==SOURCE
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
H=runpy.run_path(str(ROOT/'scripts/integrate_assets.py'),run_name='read_helpers')
scene=bpy.context.scene;ob=bpy.data.objects['NB_worker_pair']
camera_before=list(scene.camera.matrix_world)
original_basis=ob.matrix_basis.copy();original_yaw=ob.rotation_euler.z
original_geometry=H['mesh_fingerprint'](ob.data)
original_all={o.name:H['mesh_fingerprint'](o.data)for o in bpy.data.objects if o.type=='MESH'}
def points():
 return np.concatenate([H['world_coords'](o)for o in [ob]+list(ob.children_recursive)if o.type=='MESH'])
def bbox():
 uv=H['project_pts'](points());return [float(uv[:,0].min()),float(uv[:,1].min()),float(uv[:,0].max()),float(uv[:,1].max())]
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.color_type='MATERIAL'
for c in bpy.data.collections:
 if c.name in H['OVERLAY_COLLECTIONS']:c.hide_render=True
scene.render.film_transparent=False;scene.display.shading.show_shadows=True
scene.render.resolution_x=3573;scene.render.resolution_y=5052;scene.render.resolution_percentage=100
scene.render.use_border=True;scene.render.use_crop_to_border=True
scene.render.border_min_x=550/1191;scene.render.border_max_x=710/1191
scene.render.border_min_y=1-1020/1684;scene.render.border_max_y=1-890/1684
scene.render.image_settings.file_format='PNG'
rows=[]
for label,delta in [('plus30',30),('plus55',55),('minus35',-35)]:
 ob.matrix_basis=original_basis.copy();ob.rotation_euler.z=original_yaw+math.radians(delta);bpy.context.view_layer.update()
 start_box=bbox();ratio=min(1,(685-557)/(start_box[2]-start_box[0]),(1008-902)/(start_box[3]-start_box[1]));ob.scale*=ratio;bpy.context.view_layer.update()
 # The parent anchor and original Z bottom remain fixed. No screen translation
 # or production foot/road changes; fitted candidates only shrink uniformly.
 b=bbox();p=points();low=p[:,2].min();feet=p[p[:,2]<low+.15];footuv=H['project_pts'](feet)
 origin=np.asarray(ob.matrix_world.translation);front=np.asarray(ob.matrix_world@__import__('mathutils').Vector((0,-1,0)));d=H['project_pts']([front,origin]);direction=(d[0]-d[1]).tolist()
 png=OUT/('pair_yaw_'+label+'_native.png');scene.render.filepath=str(png);bpy.ops.render.render(write_still=True)
 row={'label':label,'delta_degrees':delta,'absolute_yaw_degrees':math.degrees(ob.rotation_euler.z),'uniform_scale_ratio':ratio,'bbox':b,'world_location':list(ob.location),'world_scale':list(ob.scale),'foot_min_z':float(low),'feet_screen_bbox':[float(footuv[:,0].min()),float(footuv[:,1].min()),float(footuv[:,0].max()),float(footuv[:,1].max())],'screen_forward_vector':direction,'png':str(png)}
 rows.append(row);print('CANDIDATE',json.dumps(row,separators=(',',':')))
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
assert original_geometry==H['mesh_fingerprint'](ob.data)
assert original_all=={o.name:H['mesh_fingerprint'](o.data)for o in bpy.data.objects if o.type=='MESH'}
assert camera_before==list(scene.camera.matrix_world)
(OUT/'pair-yaw-candidates.json').write_text(json.dumps({'source_sha256':EXPECTED,'source_yaw_degrees':math.degrees(original_yaw),'native_camera_preserved':True,'all_mesh_geometry_preserved':True,'production_bytes_preserved':True,'candidates':rows},ensure_ascii=False,indent=2)+'\n')
print('READ_ONLY_SOURCE_GEOMETRY_CAMERA_PASS',EXPECTED)
