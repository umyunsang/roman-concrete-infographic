import bpy, numpy as np
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=sc.camera; O=bpy.data.objects
frame=[cam.matrix_world@v for v in cam.data.view_frame(scene=sc)]; origin=cam.matrix_world.translation
def ray(pt):
    u,v=pt[0]/1191,1-pt[1]/1684; tr,br,bl,tl=frame
    return origin,((bl+(br-bl)*u+(tl-bl)*v)-origin).normalized()
o=O['NB_core4_sequence_GRAY03']; mw=o.matrix_world
bvh=BVHTree.FromPolygons([mw@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
cls={}
for y in range(1170,1252,2):
    row=''
    for x in range(620,846,2):
        h,n,i,d=bvh.ray_cast(*ray((x,y)))
        if h is None: row+='.'
        else:
            k=(round(n.x,1),round(n.y,1),round(n.z,1)); cls.setdefault(k,len(cls)); row+='ABCDEFGHIJ'[cls[k]%10]
    print('%4d %s'%(y,row))
print(cls)
