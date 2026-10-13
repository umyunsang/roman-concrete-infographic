import bpy, runpy, json, numpy as np
inv=runpy.run_path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/inventory/inventory.py', run_name='inv_mod')
eval_mesh_arrays=inv['eval_mesh_arrays']
dg=bpy.context.evaluated_depsgraph_get()
E=json.load(open('edges2.json'))
for rn in ['R_via_ostiensis','R_via_appia','R_core_road']:
    P,_,_,_,_=eval_mesh_arrays(bpy.data.objects[rn],dg)
    out=[]
    for r in E[rn]:
        if r['vis_pt'] is None or r['near']<0.3: continue
        d=np.hypot(P[:,0]-r['qx'],P[:,1]-r['qy']); sel=d<0.12
        if sel.sum()<2: continue
        ext=(r['top']-P[sel,2].min())*10
        out.append((r['outside'],r['vis_pt'],ext,r['u'],r['v']))
    for o in ('T_land','L10_sea'):
        L=[x for x in out if x[0]==o]
        if not L: continue
        vis=np.array([x[1] for x in L]); ext=np.array([x[2] for x in L]); g=vis-ext
        print('NEAR',rn,o,'n',len(L),'visible side pt p50 %.2f p90 %.2f max %.2f'%(np.median(vis),np.percentile(vis,90),vis.max()),'own side extent p50 %.2f'%np.median(ext),
              'gap(vis-ext) p50 %.2f p90 %.2f max %.2f; n>0.5: %d'%(np.median(g),np.percentile(g,90),g.max(),(g>0.5).sum()),
              'vis-0.94>0.5: %d'%((vis-0.94>0.5).sum()))
        print('   locs gap>0.5', sorted([(round(x[3]),round(x[4]),round(x[1]-x[2],2)) for x in L if x[1]-x[2]>0.5],key=lambda t:t[1])[::2][:25])
