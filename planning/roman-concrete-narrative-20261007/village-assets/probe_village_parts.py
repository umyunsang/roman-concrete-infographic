import bpy,numpy as np,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parent
scene=bpy.context.scene;scene.render.resolution_x=scene.render.resolution_y=600
camdata=bpy.data.cameras.new('probe');cam=bpy.data.objects.new('probe',camdata);scene.collection.objects.link(cam);camdata.type='ORTHO';scene.camera=cam
points={
'NB_village_house':[(280,391),(260,350),(310,440),(310,416),(178,420),(408,462),(428,482),(224,190),(296,300)],
'NB_village_market':[(178,324),(210,346),(225,348),(226,399),(261,400),(396,349),(400,326),(345,378),(328,271),(329,290),(311,319),(351,331),(328,397),(343,401),(483,418),(117,414)],
'NB_village_citizens':[(240,135),(247,162),(364,144),(357,150),(360,140),(403,278),(411,294),(407,316),(399,263),(392,247),(347,239),(328,233),(255,230),(241,267),(211,288)],
}
report={}
for name in points:
 a=np.load(OUT/(name+'_local_geometry.npz'));v=a['vertices'];tri=a['triangles'];lo=v.min(0);hi=v.max(0);center=Vector((lo+hi)/2);scale=float(np.max(hi-lo));camdata.ortho_scale=scale*1.45;cam.location=center+Vector((0,-4,1))*scale;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();tr,br,bl,tl=cam.data.view_frame(scene=scene);direction=cam.matrix_world.to_3x3()@Vector((0,0,-1));bvh=BVHTree.FromPolygons([Vector(p)for p in v],tri,all_triangles=True)
 hits=[]
 for px,py in points[name]:
  lp=tl+(tr-tl)*(px/600)+(bl-tl)*(py/600);origin=cam.matrix_world@lp;pos,norm,face,dist=bvh.ray_cast(origin,direction)
  hits.append({'pixel':[px,py],'local':list(pos)if pos else None,'face':face})
 report[name]=hits;print('PROBES',name,json.dumps(hits,separators=(',',':')))
 if name=='NB_village_citizens':
  for label,m in [('left_head', (v[:,0]<0)&(v[:,2]>1.58)),('right_neck',(v[:,0]>0)&(v[:,2]>1.55))]:
   vv=v[m];print('REGION',label,len(vv),[vv.min(0).tolist(),vv.max(0).tolist()])
(OUT/'village-ray-probes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
