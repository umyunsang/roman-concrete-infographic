import bpy, sys, runpy, json, numpy as np
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
argv=sys.argv[sys.argv.index('--')+1:]
sc=bpy.context.scene; cam=sc.camera; O=bpy.data.objects
def to_pt(p):
    v=world_to_camera_view(sc,cam,p); return (v.x*1191,(1-v.y)*1684)
for o in O:
    if o.type!='MESH' or o.hide_render: continue
    cols=[c.name for c in o.users_collection]
    if not any(k in o.name for k in ('R_','R3_','R4_','COL','road','Road','piazza','R1_','R2_')) and '35_FIELDS_ROADS' not in cols: continue
    idx=np.linspace(0,len(o.data.vertices)-1,min(3000,len(o.data.vertices))).astype(int)
    P=np.array([to_pt(o.matrix_world@o.data.vertices[i].co) for i in idx])
    b=[round(P[:,0].min()),round(P[:,0].max()),round(P[:,1].min()),round(P[:,1].max())]
    if b[0]<950 and b[1]>250 and b[2]<1100 and b[3]>450:
        print('OBJ',o.name,cols,b,len(o.data.polygons),[s.material.name for s in o.material_slots if s.material][:3])
if argv and argv[0]=='render':
    for n in argv[1].split(','):
        O[n].hide_render=True
    H=runpy.run_path(str(Path(bpy.data.filepath).parents[1]/'scripts/integrate_assets.py'),run_name='helpers')
    H['render_two_pass'](Path(argv[2]))
