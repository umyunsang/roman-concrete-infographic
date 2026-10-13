import bpy, numpy as np
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=sc.camera; O=bpy.data.objects
def P(o):
    mw=o.matrix_world; idx=np.arange(0,len(o.data.vertices),max(1,len(o.data.vertices)//60000))
    return np.array([(lambda v:(v.x*1191,(1-v.y)*1684))(world_to_camera_view(sc,cam,mw@o.data.vertices[i].co)) for i in idx])
C=P(O['COL_ruined']); D=P(O['R3_colosseum_podium'])
for x0 in range(340,560,10):
    s=(C[:,0]>=x0)&(C[:,0]<x0+10); t=(D[:,0]>=x0)&(D[:,0]<x0+10)
    print('x%d COL ymin %s  POD ymin %s'%(x0, '%.0f'%C[s,1].min() if s.sum() else '-', '%.0f'%D[t,1].min() if t.sum() else '-'))
for n in ('L03_forum_temple','R8_pantheon','B_pons1','R1_road_landing1','MS1_core1_to_2'):
    if n in O and not O[n].hide_render:
        Q=P(O[n]); print(n,[round(v) for v in (Q[:,0].min(),Q[:,0].max(),Q[:,1].min(),Q[:,1].max())])
