import bpy, runpy, json, sys, numpy as np, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
inv=runpy.run_path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/inventory/inventory.py', run_name='inv_mod')
to_pt_np=inv['to_pt_np']; eval_mesh_arrays=inv['eval_mesh_arrays']
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
OUT={}
def vpt(p,dz):
    a=to_pt_np([p, (p[0],p[1],p[2]-dz)]); return float(np.linalg.norm(a[0]-a[1]))
VS=vpt((0,0,0),1.0)
OUT['vscale_pt_per_unit']=VS
def ray_other(p, d, selfnames, maxhops=20):
    o=Vector(p); dist=0.0
    for _ in range(maxhops):
        hit,loc,nor,fi,ob,mat=sc.ray_cast(dg,o,Vector(d))
        if not hit: return None,None,None
        dd=(loc-Vector(p)).length
        if ob.name in selfnames:
            o=loc+Vector(d)*1e-4; continue
        return ob.name, dd, tuple(nor)
    return None,None,None
def kind(n):
    if n is None: return 'none'
    if n=='T_land': return 'terrain'
    if n.startswith('F_'): return 'field'
    if n in ('L10_sea','L02_tiber'): return 'water'
    if n.startswith('W_water'): return 'wave'
    if n.startswith('R_') or n.startswith('R1_road') or n.startswith('R4_bridge'): return 'road'
    if n.startswith('B_pons'): return 'bridge'
    return 'other:'+n
trees=sys.argv[sys.argv.index('--')+1].split(',')
res={}
for tn in trees:
    ob=bpy.data.objects[tn]
    P,mi,edges,nf,tris=eval_mesh_arrays(ob,dg)
    zmin=P[:,2].min(); zmax=P[:,2].max()
    dz=0.5/VS
    sel=np.where(P[:,2]<=zmin+dz)[0]
    if len(sel)<8: sel=np.argsort(P[:,2])[:8]
    S=P[sel]
    gaps=[];sup=[];bur=[]
    for p in S:
        n,d,nor=ray_other(p+np.array([0,0,1e-4]),(0,0,-1),{tn})
        gaps.append(d*VS if d is not None else None); sup.append(kind(n))
        nu,du,_=ray_other(p,(0,0,1),{tn})
        bur.append((kind(nu), du*VS if du is not None else None))
    # trunk material faces
    mats=[s.material.name if s.material else None for s in ob.material_slots]
    me=ob.evaluated_get(dg).to_mesh()
    trunk_idx=[i for i,m in enumerate(mats) if m and 'trunk' in m]
    tv=set()
    for poly in me.polygons:
        if poly.material_index in trunk_idx: tv.update(poly.vertices)
    ob.evaluated_get(dg).to_mesh_clear()
    tv=sorted(tv)
    axis=None
    if len(tv)>=6:
        T=P[tv]; c=T.mean(0); u,s,vt=np.linalg.svd(T-c); ax=vt[0]; ax=ax if ax[2]>0 else -ax
        axis=math.degrees(math.acos(min(1,abs(ax[2]))))
    zcol=np.array(ob.matrix_world)[:3,2]; tilt_obj=math.degrees(math.acos(zcol[2]/np.linalg.norm(zcol)))
    # base center & COM
    com=P.mean(0)
    base=S.mean(0)
    # gap of trunk base center
    uvb=to_pt_np([base])[0]; uvt=to_pt_np([[base[0],base[1],zmax]])[0]
    # field edge distance if support is field
    fe=None
    fields=[k for k in sup if k=='field']
    ninfo=None
    hitn,hd,_=ray_other(base+np.array([0,0,1e-3]),(0,0,-1),{tn})
    if hitn and hitn.startswith('F_'):
        fo=bpy.data.objects[hitn]; FP,_,_,_,_=eval_mesh_arrays(fo,dg)
        # convex hull in XY, distance from base to hull boundary (world) -> pt via horizontal projection
        from scipy.spatial import ConvexHull
        h=ConvexHull(FP[:,:2]); poly=FP[h.vertices,:2]
        best=1e9; bp=None
        for i in range(len(poly)):
            a=poly[i]; b=poly[(i+1)%len(poly)]; ab=b-a; t=np.clip(np.dot(base[:2]-a,ab)/np.dot(ab,ab),0,1); q=a+t*ab
            dd=np.linalg.norm(base[:2]-q)
            if dd<best: best=dd; bp=q
        qq=to_pt_np([base,[bp[0],bp[1],base[2]]])
        fe={'field':hitn,'dist_world':float(best),'dist_pt':float(np.linalg.norm(qq[0]-qq[1]))}
    res[tn]={'n_samples':int(len(S)),'zmin':float(zmin),'zmax':float(zmax),'h_pt':float((zmax-zmin)*VS),
             'gap_pt_max':max([g for g in gaps if g is not None], default=None),'gap_pt_min':min([g for g in gaps if g is not None], default=None),
             'support_kinds':{k:sup.count(k) for k in set(sup)},
             'burial':[(k,round(d,2) if d else None) for k,d in bur][:3]+[('maxd',max([d for k,d in bur if d is not None and k!='none'],default=None))],
             'trunk_axis_tilt_deg':axis,'obj_z_tilt_deg':tilt_obj,
             'base_pt':[float(x) for x in uvb],'top_pt':[float(x) for x in uvt],'base_center_support':kind(hitn),'base_center_gap_pt':(hd*VS if hd is not None else None),'field_edge':fe}
    print('TREE',tn,json.dumps(res[tn]))
json.dump(res,open(sys.argv[sys.argv.index('--')+2],'w'),indent=1)
