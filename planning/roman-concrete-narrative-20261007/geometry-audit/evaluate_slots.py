"""Evaluate candidate point displacements without mutating any Blender object."""
exec((__import__('pathlib').Path('/Users/um-yunsang/.planning/roman-concrete-narrative-20261007/geometry-audit/audit_scene.py')).read_text())

def ground_z(x,y,name='T_land'):
    co,normal,index,distance=bvh(name).ray_cast(Vector((x,y,100)),Vector((0,0,-1)),200)
    return float(co.z) if co is not None else None

def displaced(name,du=0,dv=0,dz=0,align=None):
    item=cache[name];points=item['pts'];origin=np.array(item['info']['world_origin'])
    uv=helper.project_pts(origin.reshape(1,3))[0]
    a=helper.pts_to_world([uv],origin[2])[0]
    b=helper.pts_to_world([uv+[du,dv]],origin[2])[0]
    delta=b-a;delta[2]+=dz
    if align=='land':
        z=ground_z(origin[0]+delta[0],origin[1]+delta[1])
        if z is not None:delta[2]=z+.02-origin[2]
    points=points+delta
    uv2=helper.project_pts(points)
    lo=points[:,2].min();hi=points[:,2].max()
    bottom=points[points[:,2]<=lo+max(.02,(hi-lo)*.005)]
    gaps=[];land_count=0;sea_count=0
    step=max(1,len(bottom)//200)
    for p in bottom[::step][:201]:
        land=ground_z(p[0],p[1]);sea=ground_z(p[0],p[1],'L10_sea')
        if land is not None:land_count+=1;gaps.append(float(p[2]-land))
        if sea is not None:sea_count+=1
    result={'name':name,'du_dv_dz':[du,dv,dz],'delta_world':delta.tolist(),
            'new_origin':(origin+delta).tolist(),'new_bbox':[float(uv2[:,0].min()),float(uv2[:,1].min()),float(uv2[:,0].max()),float(uv2[:,1].max())],
            'bottom_sample_land_count':land_count,'bottom_sample_sea_count':sea_count,
            'land_gap_min_max':[min(gaps),max(gaps)] if gaps else None}
    return result

slots=[]
for du,dv in [(0,0),(0,-10),(10,0),(-10,0),(20,0),(-20,0),(0,15),(0,-20)]:
    slots.append(displaced('NB_lime_clast_specimen',du,dv,align='land'))
for dv in [0,-20,-30,-40,-50,-60]:
    slots.append(displaced('NB_marine_breakwater',0,dv,-.62))
for name in ['T_pine.011','T_pine.013','T_pine.017','T_pine.018','T_pine.019']:
    for du,dv in [(105,35),(145,10),(170,45),(-5,85),(25,95)]:
        slots.append(displaced(name,du,dv,align='land'))
for dz in [.6,.95,.98]:
    slots.append(displaced('NB_modern_building',0,0,dz))
(ROOT/'candidate_slots.json').write_text(json.dumps(slots,ensure_ascii=False,indent=2))
for x in slots: print('CANDIDATE',x['name'],x['du_dv_dz'],[round(v,3) for v in x['delta_world']],
                      [round(v,1) for v in x['new_bbox']],x['land_gap_min_max'],x['bottom_sample_land_count'],x['bottom_sample_sea_count'])
