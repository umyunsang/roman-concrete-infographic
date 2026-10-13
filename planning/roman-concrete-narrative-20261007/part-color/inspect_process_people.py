import bpy,json,math
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
scene=bpy.context.scene
records=[]
for name in ['C2_hot_mixing','C5_researchers','L08_pompeii_site']:
 o=bpy.data.objects[name]
 for z in bpy.data.objects:z.hide_render=z!=o
 coords=[o.matrix_world @ v.co for v in o.data.vertices]
 mn=Vector(tuple(min(v[k] for v in coords) for k in range(3)));mx=Vector(tuple(max(v[k] for v in coords) for k in range(3)));ctr=(mn+mx)/2
 # Original camera direction to preserve the actual poster viewing orientation.
 d=scene.camera.rotation_euler.to_quaternion() @ Vector((0,0,1))
 cd=bpy.data.cameras.new(name+'_audit');cam=bpy.data.objects.new(name+'_audit',cd);scene.collection.objects.link(cam)
 cam.location=ctr+d*max(mx-mn)*3;cam.rotation_euler=scene.camera.rotation_euler.copy();cd.type='ORTHO';cd.ortho_scale=max(mx-mn)*1.40;scene.camera=cam
 scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
 scene.display.shading.color_type='OBJECT';o.color=(.6,.6,.6,1);scene.display.shading.background_type='VIEWPORT';scene.display.shading.background_color=(.94,.93,.91)
 scene.render.filepath=str(OUT/(name+'-audit.png'));bpy.ops.render.render(write_still=True)
 # Components computed by edge connectivity on base mesh, not altering geometry.
 n=len(o.data.vertices);parent=list(range(n))
 def find(a):
  while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
  return a
 for e in o.data.edges:
  a,b=map(find,e.vertices)
  if a!=b:parent[b]=a
 verts={}
 for v in o.data.vertices:verts.setdefault(find(v.index),[]).append(v.index)
 faces={}
 for poly in o.data.polygons:faces.setdefault(find(poly.vertices[0]),[]).append(poly.index)
 comps=[]
 for root,ids in verts.items():
  xs=[o.data.vertices[i].co for i in ids];lo=[min(v[k] for v in xs) for k in range(3)];hi=[max(v[k] for v in xs) for k in range(3)]
  comps.append({'root':root,'vertex_count':len(ids),'face_count':len(faces.get(root,[])),'lo':lo,'hi':hi,'face_indices':faces.get(root,[])})
 rec={'name':name,'vertex_count':n,'face_count':len(o.data.polygons),'matrix_world':[list(r) for r in o.matrix_world],'local_bounds':[[min(v.co[k] for v in o.data.vertices) for k in range(3)],[max(v.co[k] for v in o.data.vertices) for k in range(3)]],'components':sorted(comps,key=lambda c:-c['face_count'])}
 records.append(rec)
(OUT/'process-components.json').write_text(json.dumps(records))
print('PROCESS_AUDIT_DONE',json.dumps([{'name':r['name'],'vertices':r['vertex_count'],'faces':r['face_count'],'components':len(r['components']),'largest':[(c['face_count'],c['lo'],c['hi']) for c in r['components'][:10]]} for r in records]))
