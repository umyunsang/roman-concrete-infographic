import bpy, runpy, numpy as np
inv=runpy.run_path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/inventory/inventory.py', run_name='inv_mod')
eval_mesh_arrays=inv['eval_mesh_arrays']; to_pt_np=inv['to_pt_np']
dg=bpy.context.evaluated_depsgraph_get()
for pref in ['MS3_','MS2_','MS1_','C5_researchers','L08_pompeii_site','D3_','L11_privernum']:
    obs=[o for o in bpy.data.objects if o.name.startswith(pref) and o.type=='MESH' and not o.hide_render]
    if not obs: continue
    Ps=np.vstack([eval_mesh_arrays(o,dg)[0] for o in obs])
    print('H',pref,[o.name for o in obs][:6],'zmin %.3f zmax %.3f h_pt %.1f'%(Ps[:,2].min(),Ps[:,2].max(),(Ps[:,2].max()-Ps[:,2].min())*10), 'screen box', np.round([to_pt_np(Ps)[:,0].min(),to_pt_np(Ps)[:,0].max(),to_pt_np(Ps)[:,1].min(),to_pt_np(Ps)[:,1].max()],1).tolist())
