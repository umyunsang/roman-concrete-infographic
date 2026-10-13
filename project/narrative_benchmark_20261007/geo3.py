import bpy, runpy, json, sys, numpy as np, math
from mathutils import Vector
inv=runpy.run_path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/inventory/inventory.py', run_name='inv_mod')
to_pt_np=inv['to_pt_np']; eval_mesh_arrays=inv['eval_mesh_arrays']; islands=inv['islands']
dg=bpy.context.evaluated_depsgraph_get()
FP,fmi,fe,_,_=eval_mesh_arrays(bpy.data.objects['F_centuriatio'],dg)
lab=islands(len(FP),fe)
def hull2d(pts):
    pts=sorted(set(map(tuple,np.round(pts,6))))
    def cross(o,a,b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo=[];up=[]
    for p in pts:
        while len(lo)>=2 and cross(lo[-2],lo[-1],p)<=0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up)>=2 and cross(up[-2],up[-1],p)<=0: up.pop()
        up.append(p)
    return np.array(lo[:-1]+up[:-1])
def inpoly(pt,poly):
    s=None
    for i in range(len(poly)):
        a=poly[i]; b=poly[(i+1)%len(poly)]
        c=(b[0]-a[0])*(pt[1]-a[1])-(b[1]-a[1])*(pt[0]-a[0])
        if s is None: s=c>=0
        elif (c>=0)!=s: return False
    return True
# island hulls (only large islands = plates; small = stakes etc.)
ul=np.unique(lab)
hulls={}
for l in ul:
    pts=FP[lab==l]
    if len(pts)<4: continue
    ext=pts[:,:2].max(0)-pts[:,:2].min(0)
    if ext.max()<0.6: continue
    hulls[l]=(hull2d(pts[:,:2]), pts[:,2].max(), ext)
print('field islands',len(ul),'plates',len(hulls))
trees="T_cypress,T_pine.004,T_pine.022,T_pine.001,T_pine.002,T_pine.003,T_pine.011,T_pine.013,T_pine.017,T_pine.018,T_pine.019,T_pine,T_pine.007,T_pine.008,T_pine.009,T_pine.010,T_pine.014,T_pine.015,T_pine.016,T_pine.020,T_pine.021".split(',')
for tn in trees:
    ob=bpy.data.objects[tn]; P,mi,_,_,_=eval_mesh_arrays(ob,dg)
    mats=[s.material.name if s.material else '' for s in ob.material_slots]
    tr=np.isin(mi,[i for i,m in enumerate(mats) if 'trunk' in m])
    me=ob.evaluated_get(dg).to_mesh(); tv=set()
    for poly in me.polygons:
        if 'trunk' in mats[poly.material_index]: tv.update(poly.vertices)
    ob.evaluated_get(dg).to_mesh_clear()
    if tv:
        T=P[sorted(tv)]; base=T[T[:,2]<=T[:,2].min()+0.02].mean(0); rad=np.linalg.norm(T[T[:,2]<=T[:,2].min()+0.02][:,:2]-base[:2],axis=1).max()
    else:
        u,s,vt=np.linalg.svd(P-P.mean(0)); ax=vt[0]*np.sign(vt[0][2]); print(tn,'spindle axis tilt deg',math.degrees(math.acos(abs(ax[2]))))
        base=P[P[:,2]<=P[:,2].min()+0.05].mean(0); rad=0.0
    best=None
    for l,(h,zt,ext) in hulls.items():
        inside=inpoly(base[:2],h)
        # distance to hull boundary
        dmin=1e9; q=None
        for i in range(len(h)):
            a=h[i]; b=h[(i+1)%len(h)]; ab=b-a; t=np.clip(np.dot(base[:2]-a,ab)/np.dot(ab,ab),0,1); qq=a+t*ab; d=np.linalg.norm(base[:2]-qq)
            if d<dmin: dmin=d; q=qq
        sd=-dmin if inside else dmin  # negative = inside
        if best is None or sd<best[0]: best=(sd,l,q,zt,ext)
    sd,l,q,zt,ext=best
    pp=to_pt_np([base,[q[0],q[1],base[2]]]); dpt=float(np.linalg.norm(pp[0]-pp[1]))
    # screen distance from trunk silhouette edge (radius) ~ subtract rad projected
    print('TF',tn,'base_pt',np.round(to_pt_np([base])[0],1).tolist(),'nearest plate',int(l),'ext',np.round(ext,2).tolist(),'inside' if sd<0 else 'outside','edge_dist_world %.3f'%abs(sd),'edge_dist_pt %.2f'%dpt,'trunk_r_world %.3f'%rad,'plate_top_z %.3f base_z %.3f'%(zt,base[2]))
