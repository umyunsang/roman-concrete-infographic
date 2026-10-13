import bpy, runpy, json, numpy as np, math
from mathutils import Vector
inv=runpy.run_path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/inventory/inventory.py', run_name='inv_mod')
to_pt_np=inv['to_pt_np']; eval_mesh_arrays=inv['eval_mesh_arrays']
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=sc.camera; fr=[Vector(v) for v in cam.data.view_frame(scene=sc)]; M=cam.matrix_world.normalized(); O=M.translation; R3=M.to_3x3()
def ray_dir(x,y):
    u=x/1191.0; v=1-y/1684.0; loc=fr[2]+(fr[1]-fr[2])*u+(fr[3]-fr[2])*v; return (R3@loc).normalized()
def cam_hit(x,y):
    h,loc,nor,fi,ob,m=sc.ray_cast(dg,O,ray_dir(x,y)); return (ob.name,loc) if h else (None,None)
def top(x,y):
    h,loc,nor,fi,ob,m=sc.ray_cast(dg,Vector((x,y,40)),Vector((0,0,-1))); return (ob.name,loc.z) if h else (None,None)
spots={'ost_a':(330,1095),'ost_b':(250,1215),'ost_c':(180,1320),'ost_d':(375,1040),'core_se_a':(925,920),'core_se_b':(940,903),'appia_a':(868,985),'appia_b':(1078,950),'appia_mid':(1000,962),'se2_a':(790,990),'se2_mid':(700,1010),'se2_b':(640,1018)}
roads={'ost':'R_via_ostiensis','core':'R_core_road','appia':'R_via_appia','se2':'R_core_road'}
for k,(x,y) in spots.items():
    rn=roads[k.split('_')[0]]
    ob,p=cam_hit(x,y)
    # find road point near screen spot: search small screen neighborhood
    found=None
    for dx in np.linspace(-8,8,17):
        for dy in np.linspace(-8,8,17):
            ob,p=cam_hit(x+dx,y+dy)
            if ob==rn: found=p; break
        if found: break
    if not found: print('XS',k,'no road'); continue
    # road direction via nearby top face centers
    P,_,_,_,_=eval_mesh_arrays(bpy.data.objects[rn],dg)
    nb=P[np.linalg.norm(P[:,:2]-np.array(found[:2]),axis=1)<1.0]
    u,s,vt=np.linalg.svd(nb[:,:2]-nb[:,:2].mean(0)); t=vt[0]; n=np.array([-t[1],t[0]])
    # choose n pointing to the near side (camera side: world (+1,-1))
    if np.dot(n,[1,-1])<0: n=-n
    prof=[]
    for s_ in np.linspace(-1.5,1.5,301):
        q=np.array(found[:2])+n*s_
        o,z=top(q[0],q[1]); prof.append((s_,o,z))
    # near edge: last s where object==rn going outward (+)
    rs=[p_ for p_ in prof if p_[1]==rn]
    if not rs: print('XS',k,'no profile'); continue
    s_edge=max(p_[0] for p_ in rs)
    road_top_near=max(p_[2] for p_ in rs if p_[0]>=s_edge-0.25)
    out=[p_ for p_ in prof if p_[0]>s_edge and p_[0]<=s_edge+0.25]
    outs={}
    for p_ in out: outs[p_[1]]=outs.get(p_[1],0)+1
    tz=[p_[2] for p_ in out if p_[1]=='T_land']
    width=(s_edge-min(p_[0] for p_ in rs))
    print('XS',k,'road width %.2f world'%width,'near-edge road top %.3f'%road_top_near,'outside objs',outs,'terrain just outside min %.3f max %.3f'%(min(tz),max(tz)) if tz else '', 'step pt %.2f'%((road_top_near-min(tz[:5]))*10) if tz else '')
