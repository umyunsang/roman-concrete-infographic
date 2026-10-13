import bpy,json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
scene=bpy.context.scene
cd=bpy.data.cameras.new('parts_audit_camera');cam=bpy.data.objects.new('parts_audit_camera',cd);scene.collection.objects.link(cam);scene.camera=cam;cd.type='ORTHO'
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.display.shading.color_type='OBJECT';scene.display.shading.background_type='VIEWPORT';scene.display.shading.background_color=(.94,.93,.91)
for name in ['C2_hot_mixing','C5_researchers','L08_pompeii_site']:
 o=bpy.data.objects[name]
 for q in bpy.data.objects:q.hide_render=q!=o
 o.color=(.6,.6,.6,1)
 bounds=[[min(v.co[k] for v in o.data.vertices) for k in range(3)],[max(v.co[k] for v in o.data.vertices) for k in range(3)]]
 ctr=Vector(tuple((bounds[0][k]+bounds[1][k])/2 for k in range(3)));center=o.matrix_world@ctr
 cd.ortho_scale=max(o.dimensions)*1.24
 for label,direction in [('top',(0,0,1)),('front',(0,-1,.25)),('back',(0,1,.25))]:
  cam.location=o.matrix_world@(ctr+Vector(direction)*5);cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
  scene.render.filepath=str(OUT/(name+'-'+label+'.png'));bpy.ops.render.render(write_still=True)
 print(name,bounds)
