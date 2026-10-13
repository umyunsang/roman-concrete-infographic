import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
scene=bpy.context.scene
results={}
for name,pixels in {
'C5_researchers':{'head_left':(235,433),'head_foreground':(424,480),'head_rear':(480,393),'torso_rear':(477,444),'leg_rear':(478,535),'head_right':(780,544),'hand_foreground':(450,532)},
'C2_hot_mixing':{'arm_left_lower':(252,393),'arm_right_lower':(601,409),'hand_right_upper':(735,330),'robe_patch':(612,509)},
'L08_pompeii_site':{'scaffold_pile':(326,427),'brace_upper':(823,440),'brace_lower':(791,566)}
}.items():
 o=bpy.data.objects[name];coords=[v.co for v in o.data.vertices];lo=[min(v[k] for v in coords) for k in range(3)];hi=[max(v[k] for v in coords) for k in range(3)];ctr=Vector(tuple((lo[k]+hi[k])/2 for k in range(3)));center=o.matrix_world@ctr;campos=o.matrix_world@(ctr+Vector((0,-1,.4))*5);q=(center-campos).to_track_quat('-Z','Y');scale=max(o.dimensions)*1.3;inv=o.matrix_world.inverted();bvh=BVHTree.FromPolygons(coords,[list(p.vertices) for p in o.data.polygons],all_triangles=False)
 results[name]={}
 for label,(px,py) in pixels.items():
  worldorigin=campos+q@Vector(((px/1000-.5)*scale,(.5-py/1000)*scale,0));worlddir=q@Vector((0,0,-1));origin=inv@worldorigin;direction=(inv.to_3x3()@worlddir).normalized();hit,norm,poly,dist=bvh.ray_cast(origin,direction)
  results[name][label]={'pixel':[px,py],'local':list(hit) if hit else None,'face':poly}
Path(__file__).with_name('people-pixel-probes.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results))
