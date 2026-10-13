import bpy, json, numpy as np, math, runpy
from mathutils import Vector
inv=runpy.run_path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/inventory/inventory.py', run_name='inv_mod')
to_pt_np=inv['to_pt_np']
sc=bpy.context.scene; cam=sc.camera; dg=bpy.context.evaluated_depsgraph_get()
fr=[Vector(v) for v in cam.data.view_frame(scene=sc)]  # TR, BR, BL, TL
M=cam.matrix_world.normalized(); O=M.translation; R3=M.to_3x3()
def ray_dir(x,y):
    u=x/1191.0; v=1-y/1684.0
    BL=fr[2]; BR=fr[1]; TL=fr[3]
    loc=BL+(BR-BL)*u+(TL-BL)*v
    return (R3@loc).normalized()
def terrain_hit(x,y):
    d=ray_dir(x,y); o=O.copy()
    for _ in range(30):
        h,loc,nor,fi,ob,m=sc.ray_cast(dg,o,d)
        if not h: return None
        if ob.name=='T_land': return loc
        o=loc+d*1e-3
    return None
# self-check projection
p=terrain_hit(600,900); print('CHK', to_pt_np([tuple(p)])[0] if p else None)
B=json.load(open('blobs_all.json'))
sel=[b for b in B if b['asset'] not in ('landmark_apennines','landmark_vesuvius','water_tiber','water_sea')]
seen=set()
for b in sel:
    key=(b['asset'],round(b['x']/5),round(b['y']/5))
    p=terrain_hit(b['x'],b['y'])
    if p is None: print('BUMP',b['asset'],b['x'],b['y'],'no terrain'); continue
    zs=[]
    for k in range(24):
        a=2*math.pi*k/24
        q=terrain_hit(b['x']+30*math.cos(a), b['y']+30*math.sin(a))
        if q is not None: zs.append(q.z)
    med=float(np.median(zs)); bump=(p.z-med)*10
    print('BUMP',b['asset'],b['x'],b['y'],'area',b['area'],'z %.3f ringmed %.3f bump_pt %.2f'%(p.z,med,bump))
