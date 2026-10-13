import bpy, runpy, json, sys, numpy as np, math
from mathutils import Vector
inv=runpy.run_path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/inventory/inventory.py', run_name='inv_mod')
to_pt_np=inv['to_pt_np']
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
roadset=set(n for n in bpy.data.objects.keys() if n.startswith('R_') or n.startswith('R1_road') or n=='R4_bridge_west_bed')
def hits(x,y,z0=40.0):
    out=[]; o=Vector((x,y,z0))
    for _ in range(40):
        h,loc,nor,fi,ob,m=sc.ray_cast(dg,o,Vector((0,0,-1)))
        if not h: break
        out.append((ob.name,loc.z)); o=loc+Vector((0,0,-1e-4))
    return out
def road_at(x,y,rn):
    hs=hits(x,y); rz=[z for n,z in hs if n==rn]
    other=[(n,z) for n,z in hs if n not in roadset and not n.startswith('W_water')]
    return (max(rz) if rz else None, min(rz) if rz else None, other[0] if other else (None,None), hs)
rd=json.load(open('roads.json'))
out={}
for rn in ['R_via_ostiensis','R_via_appia','R_core_road']:
    ob=bpy.data.objects[rn]; ev=ob.evaluated_get(dg); me=ev.to_mesh(); mw=ob.matrix_world
    C=np.array([tuple(mw@p.center) for p in me.polygons if (mw.to_3x3()@p.normal).z>0.7]); ev.to_mesh_clear()
    uv=to_pt_np(C)
    if rn=='R_core_road':
        keep=((uv[:,0]>=840.9)&(uv[:,0]<=964.9)&(uv[:,1]>=864.4)&(uv[:,1]<=982.4))|((uv[:,0]>=588.2)&(uv[:,0]<=816.8)&(uv[:,1]>=963.9)&(uv[:,1]<=1026.4))
        C=C[keep]; uv=uv[keep]
    # centerline-ish samples: subsample
    idx=np.arange(0,len(C),max(1,len(C)//160))
    res=[]
    for i in idx:
        p=C[i]
        nb=C[np.linalg.norm(C[:,:2]-p[:2],axis=1)<1.2]
        if len(nb)<5: continue
        u,s,vt=np.linalg.svd(nb[:,:2]-nb[:,:2].mean(0)); t=vt[0]; nrm=np.array([-t[1],t[0]])
        for sgn in (1,-1):
            q=p[:2].copy(); last=None
            for k in range(200):
                q=q+sgn*nrm*0.01
                top,bot,oth,hs=road_at(q[0],q[1],rn)
                if top is None: break
                last=(q.copy(),top,bot,oth)
            if last is None: continue
            qo=q+sgn*nrm*0.03
            hs=hits(qo[0],qo[1]); tz=[z for n,z in hs if n=='T_land']; first=[n for n,z in hs if not n.startswith('W_water')]
            q_in,top,bot,oth=last
            outside=first[0] if first else None
            terr=max(tz) if tz else None
            # what is just outside the edge (first non-wave hit)
            o_first=[(n,z) for n,z in hs if not n.startswith('W_water')]
            ofz=o_first[0][1] if o_first else None
            vis=(top-ofz)*10 if ofz is not None else None
            gap=(bot-ofz)*10 if ofz is not None else None
            e=to_pt_np([[q_in[0],q_in[1],top]])[0]
            res.append(dict(u=float(e[0]),v=float(e[1]),side=sgn,outside=o_first[0][0] if o_first else None,vis_pt=vis,gap_pt=gap,thick_pt=(top-bot)*10))
    out[rn]=res
    for side in (1,-1):
        L=[r for r in res if r['side']==side and r['vis_pt'] is not None]
        if not L: continue
        vis=np.array([r['vis_pt'] for r in L]); gp=np.array([r['gap_pt'] for r in L])
        outs={}
        for r in L: outs[r['outside']]=outs.get(r['outside'],0)+1
        print('EDGE',rn,'side',side,'n',len(L),'outside',outs,'visible side height pt p50 %.2f p90 %.2f max %.2f'%(np.median(vis),np.percentile(vis,90),vis.max()),'gap-under-edge pt p50 %.2f p90 %.2f max %.2f'%(np.median(gp),np.percentile(gp,90),gp.max()),'thick p50 %.2f'%np.median([r['thick_pt'] for r in L]))
json.dump(out,open('edges.json','w'))
