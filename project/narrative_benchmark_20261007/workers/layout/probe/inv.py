import bpy, numpy as np
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=sc.camera; O=bpy.data.objects
print('RES', sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage, sc.render.engine, sc.display.shading.light, sc.display.shading.color_type)
def to_pt(p):
    v=world_to_camera_view(sc,cam,p); return (v.x*1191,(1-v.y)*1684)
dg=bpy.context.evaluated_depsgraph_get()
rows=[]
for o in O:
    if o.type!='MESH' : continue
    vis = not o.hide_render and all(not c.hide_render for c in o.users_collection)
    mw=o.matrix_world; V=o.data.vertices; n=len(V)
    if n==0: continue
    step=max(1,n//3000)
    P=np.array([to_pt(mw@V[i].co) for i in range(0,n,step)])
    x0,x1,y0,y1=P[:,0].min(),P[:,0].max(),P[:,1].min(),P[:,1].max()
    # near colosseum region
    if x1<200 or x0>950 or y1<400 or y0>1150: continue
    rows.append((o.name,[c.name for c in o.users_collection],vis,n,round(x0),round(x1),round(y0),round(y1), o.data.users, o.parent.name if o.parent else None, len(o.modifiers)))
for r in sorted(rows,key=lambda r:r[6]): print('OBJ',r)
