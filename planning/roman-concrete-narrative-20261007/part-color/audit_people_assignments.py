import bpy,runpy,json,math
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
roles={'skin':'#C99C78','linen':'#DED1AF','cloth':'#9C5C43','toolwood':'#8D6C49','toolmetal':'#526873','basin':'#B9976F','mixture':'#8B6950','raw_lime':'#FFF4DD','raw_ash':'#A4876D','roman_stone':'#D3BE9E'}
a=runpy.run_path(str(OUT/'process_people_parts.py'))['build_assignments'](bpy)
def linear(hex):
 vals=[int(hex[i:i+2],16)/255 for i in (1,3,5)];return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals)+(1,)
scene=bpy.context.scene
original_camera=scene.camera
cd=bpy.data.cameras.new('parts_audit_camera');cam=bpy.data.objects.new('parts_audit_camera',cd);scene.collection.objects.link(cam);scene.camera=cam;cd.type='ORTHO'
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.display.shading.color_type='MATERIAL';scene.display.shading.background_type='VIEWPORT';scene.display.shading.background_color=linear('#F2EFE4')[:3]
scene.view_settings.exposure=0
report={}
for name,record in a.items():
 o=bpy.data.objects[name]
 for q in bpy.data.objects:q.hide_render=q!=o
 matnames=[record['default']]+list(record['faces']);o.data.materials.clear()
 for key in matnames:
  m=bpy.data.materials.new(name+'_'+key);m.diffuse_color=linear(roles[key]);o.data.materials.append(m)
 for poly in o.data.polygons:poly.material_index=0
 for key,ids in record['faces'].items():
  for i in ids:o.data.polygons[i].material_index=matnames.index(key)
 bounds=[[min(v.co[k] for v in o.data.vertices) for k in range(3)],[max(v.co[k] for v in o.data.vertices) for k in range(3)]]
 ctr=Vector(tuple((bounds[0][k]+bounds[1][k])/2 for k in range(3)));center=o.matrix_world@ctr;cd.ortho_scale=max(o.dimensions)*1.3
 for label,direction in [('front',(0,-1,.4)),('back',(0,1,.4)),('top',(0,0,1))]:
  cam.location=o.matrix_world@(ctr+Vector(direction)*5);cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
  scene.render.filepath=str(OUT/(name+'-parts-'+label+'.png'));bpy.ops.render.render(write_still=True)
 report[name]={'faces':len(o.data.polygons),'default_faces':len(o.data.polygons)-sum(len(ids) for ids in record['faces'].values()),'role_counts':{key:len(ids) for key,ids in record['faces'].items()},'notes':record['notes']}
(OUT/'process-people-parts-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('PROCESS_PEOPLE_PARTS',json.dumps(report))
