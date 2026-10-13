import bpy, numpy as np, json
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=sc.camera; O=bpy.data.objects
def to_pt(p):
    v=world_to_camera_view(sc,cam,p); return (v.x*1191,(1-v.y)*1684)
def hexof(c): return '#%02X%02X%02X'%tuple(round(255*((x*12.92) if x<=0.0031308 else (1.055*x**(1/2.4)-0.055))) for x in c[:3])
def box(o):
    if o.type!='MESH' or not o.data.vertices: return None
    mw=o.matrix_world; idx=np.linspace(0,len(o.data.vertices)-1,min(4000,len(o.data.vertices))).astype(int)
    P=np.array([to_pt(mw@o.data.vertices[i].co) for i in idx]); return [round(P[:,0].min()),round(P[:,0].max()),round(P[:,1].min()),round(P[:,1].max())]
want=lambda n: any(k in n for k in ('L03_','D3_','S_sect','NB_core4','R1_calcium','R1_water','tree','Tree','TREE','pine','cypress','NB_modern','C3_','C2_','NB_core'))
for o in sorted(O,key=lambda o:o.name):
    if o.type!='MESH' or o.hide_render: continue
    b=box(o)
    if want(o.name) or (b and b[0]<566 and b[1]>408 and b[2]<1475 and b[3]>1350) or (b and b[0]<135 and b[1]>68 and b[2]<1035 and b[3]>965) or (b and b[0]<410 and b[1]>258 and b[2]<1345 and b[3]>1185):
        mats=sorted({s.material.name+' '+hexof(s.material.diffuse_color) for s in o.material_slots if s.material})
        print('OBJ',o.name,'|',[c.name for c in o.users_collection],'|',b,'|',len(o.data.polygons),'|',mats)
for m in bpy.data.materials:
    if any(k in m.name for k in ('roof','stone','plinth','foliage','concrete','paper','land','ground','specimen','sect','road','crack','calcium','water','heal')):
        print('MAT',m.name,hexof(m.diffuse_color),m.users)
print('TLAND',[s.material.name for s in O['T_land'].material_slots])
