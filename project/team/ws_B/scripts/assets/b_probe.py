import bpy, numpy as np
U = bpy.data.texts['asset_utils.py'].as_module()
for uv in [(300,700),(600,1000),(1000,400),(600,1500),(560,496),(962,862),(372,1140)]:
    w = U.pts_to_world(np.array([uv],float),0.0)[0]
    w2 = w.copy(); w2[0]+=1.0
    w3 = w.copy(); w3[1]+=1.0
    q = U.project_pts(np.array([w,w2,w3]))
    print('uv',uv,'world',w.round(2),'pt per +x',np.round(q[1]-q[0],2),'pt per +y',np.round(q[2]-q[0],2),'rise',round(float(U.rise_per_unit(np.array([uv],float))[0]),2))
for n in ('L04_palatine','COL_ruined','L01_gennaro','L01_corno_grande','T_land','L10_sea'):
    o = bpy.data.objects[n]; print(n, [round(x,1) for x in U.screen_bbox(o,4)], 'dims', [round(x,2) for x in o.dimensions], 'loc', [round(x,2) for x in o.location])
