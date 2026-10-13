import bpy, runpy, json, numpy as np
from mathutils import Vector
from mathutils.kdtree import KDTree
inv=runpy.run_path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/inventory/inventory.py', run_name='inv_mod')
to_pt_np=inv['to_pt_np']; eval_mesh_arrays=inv['eval_mesh_arrays']
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
E=json.load(open('edges.json'))
for rn in ['R_via_ostiensis','R_via_appia','R_core_road']:
    P,_,_,_,_=eval_mesh_arrays(bpy.data.objects[rn],dg)
    uvP=to_pt_np(P)
    rows=E[rn]
    out=[]
    for r in rows:
        if r['vis_pt'] is None: continue
        d=np.hypot(uvP[:,0]-r['u'],uvP[:,1]-r['v'])
        # vertices whose screen pos within 1.5pt horizontally-ish of edge point AND z within 0.3
        sel=d<2.0
        if sel.sum()<2: continue
        zz=P[sel,2]; h=(zz.max()-zz.min())*10
        out.append((r['outside'],r['vis_pt'],h,r['u'],r['v'],r['side']))
    for o in ('T_land','L10_sea'):
        L=[x for x in out if x[0]==o]
        if not L: continue
        vis=np.array([x[1] for x in L]); h=np.array([x[2] for x in L])
        exc=vis-0.94
        print('E2',rn,o,'n',len(L),'vis p50 %.2f p90 %.2f max %.2f'%(np.median(vis),np.percentile(vis,90),vis.max()),'mesh local z-extent p50 %.2f'%np.median(h),
              'excess(vis-0.94) >0.5pt: %d/%d'%((exc>0.5).sum(),len(L)),'>1.5: %d'%((exc>1.5).sum()))
        fl=[x for x in L if x[1]-x[2]>0.5]
        print('   true-gap (vis-extent)>0.5pt: %d/%d'%(len(fl),len(L)), 'max gap %.2f'%max([x[1]-x[2] for x in L]), 'locs', sorted([(round(x[3]),round(x[4]),round(x[1]-x[2],2)) for x in fl],key=lambda t:t[1])[:40:3])
        big=sorted([x for x in L if x[1]-0.94>1.5],key=lambda x:-x[1])[:10]
        print('   top', [(round(x[3],1),round(x[4],1),round(x[1],2),x[5]) for x in big])
