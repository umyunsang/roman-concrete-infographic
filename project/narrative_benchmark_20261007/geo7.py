import bpy, runpy, numpy as np
inv=runpy.run_path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/inventory/inventory.py', run_name='inv_mod')
eval_mesh_arrays=inv['eval_mesh_arrays']; islands=inv['islands']
dg=bpy.context.evaluated_depsgraph_get()
for rn in ['R_via_ostiensis','R_via_appia','R_core_road']:
    ob=bpy.data.objects[rn]; P,mi,E,nf,_=eval_mesh_arrays(ob,dg)
    me=ob.evaluated_get(dg).to_mesh()
    vmat=np.full(len(P),-1)
    for p in me.polygons:
        for v in p.vertices: vmat[v]=p.material_index
    ob.evaluated_get(dg).to_mesh_clear()
    lab=islands(len(P),E)
    mats=[s.material.name for s in ob.material_slots]
    for mi_ in range(len(mats)):
        ext=[]
        for l in np.unique(lab[vmat==mi_]):
            z=P[lab==l,2]; ext.append((z.max()-z.min())*10)
        ext=np.array(ext)
        print('MAT',rn,mats[mi_],'islands',len(ext),'z-extent pt p10 %.2f p50 %.2f p90 %.2f'%(np.percentile(ext,10),np.median(ext),np.percentile(ext,90)))
