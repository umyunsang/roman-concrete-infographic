import bpy, runpy, numpy as np
from mathutils import Vector
inv=runpy.run_path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/inventory/inventory.py', run_name='inv_mod')
eval_mesh_arrays=inv['eval_mesh_arrays']
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def stack(x,y,skip):
    out=[]; o=Vector((x,y,40))
    for _ in range(60):
        h,loc,nor,fi,ob,m=sc.ray_cast(dg,o,Vector((0,0,-1)))
        if not h: break
        if ob.name!=skip: out.append((ob.name,round(loc.z,3)))
        o=loc+Vector((0,0,-1e-4))
    return out
trees="T_cypress,T_pine.004,T_pine.022,T_pine.001,T_pine.002,T_pine.003,T_pine.011,T_pine.013,T_pine.017,T_pine.018,T_pine.019,T_pine,T_pine.007,T_pine.008,T_pine.009,T_pine.010,T_pine.014,T_pine.015,T_pine.016,T_pine.020,T_pine.021".split(',')
for tn in trees:
    ob=bpy.data.objects[tn]; P,mi,_,_,_=eval_mesh_arrays(ob,dg)
    mats=[s.material.name if s.material else '' for s in ob.material_slots]
    me=ob.evaluated_get(dg).to_mesh(); tv=set()
    for poly in me.polygons:
        if 'trunk' in mats[poly.material_index]: tv.update(poly.vertices)
    ob.evaluated_get(dg).to_mesh_clear()
    if tv:
        T=P[sorted(tv)]; ring=T[T[:,2]<=T[:,2].min()+0.02]; c=ring.mean(0); r=np.linalg.norm(ring[:,:2]-c[:2],axis=1).max()
        pts=[c[:2]]+[c[:2]+r*1.3*np.array([np.cos(a),np.sin(a)]) for a in np.linspace(0,2*np.pi,8,endpoint=False)]
    else:
        c=P[P[:,2]<=P[:,2].min()+0.05].mean(0); pts=[c[:2]]
    zmax=P[:,2].max(); zmin=P[:,2].min()
    tops=[]
    for q in pts:
        s=stack(q[0],q[1],tn)
        tops.append(s[0] if s else None)
    # topmost covering surface at trunk center
    s0=stack(pts[0][0],pts[0][1],tn)
    cover=[x for x in s0 if x[1]>zmin]
    vis_base=max([zmin]+[x[1] for x in cover])
    print('VH',tn,'zmin %.3f zmax %.3f'%(zmin,zmax),'stack@center',s0[:3],'covering-above',cover[:3],'h_full %.2f h_visible %.2f'%((zmax-zmin)*10,(zmax-vis_base)*10),'burial_pt %.2f'%((vis_base-zmin)*10))
