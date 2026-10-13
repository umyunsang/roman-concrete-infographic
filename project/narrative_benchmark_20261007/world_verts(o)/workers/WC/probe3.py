import bpy, sys, json
import numpy as np
from mathutils import Vector
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts, Terrain
np.set_printoptions(precision=3, suppress=True, linewidth=220)
S=Screen(); O=bpy.data.objects
land=O['T_land']; T=Terrain(land)
print('T_land colls', [c.name for c in land.users_collection])
for (x,y) in [(45.156,-38.003),(50.018,-33.141),(54.881,-28.278),(43.4,-39.8),(46.9,-36.2)]:
    print('terrain at cube', x,y, T.z(x,y))
# D1 local geometry
for n in ['D1_concrete','D1_seawater','D1_tank_floor','D1_tank_wall0','D1_tank_wall1','D1_tank_wall2','D1_tank_wall3']:
    o=O[n]; lv=np.array([v.co for v in o.data.vertices])
    print(n,'loc',np.array(o.location),'local mesh min',lv.min(0),'max',lv.max(0),'mods',[(m.type, getattr(m,'width',None), getattr(m,'segments',None)) for m in o.modifiers])
# crystals: base & tip in D1_material local
par=O['D1_material']; Mi=par.matrix_world.inverted()
for i in range(26):
    o=O[f'D1_crystal{i:02d}']; lv=np.array([v.co for v in o.data.vertices])
    W=world_verts(o); P=S.project(W)
    L=np.array([(Mi@Vector(w))[:] for w in W])
    # tip = vertex farthest from centroid of others
    c=L.mean(0); d=np.linalg.norm(L-c,axis=1); tip=L[np.argmax(d)]
    base=L[np.argsort(d)[:]].mean(0)
    print(o.name,'nv',len(lv),'loc',np.array(o.location),'tip',tip,'cent',c,'pt x %.1f-%.1f y %.1f-%.1f'%(P[:,0].min(),P[:,0].max(),P[:,1].min(),P[:,1].max()))
print('crystal00 verts local', np.array([v.co for v in O['D1_crystal00'].data.vertices]))
print('crystal00 faces', [list(p.vertices) for p in O['D1_crystal00'].data.polygons])
# around core1
for n in ['MS1_core1_to_2','NB_modern_building','R1_frame_rust','R3_frame_crack_col','R3_frame_crack_col2']:
    o=O[n]; W=world_verts(o); P=S.project(W)
    print(n,'pt x %.1f-%.1f y %.1f-%.1f'%(P[:,0].min(),P[:,0].max(),P[:,1].min(),P[:,1].max()),'world',W.min(0),W.max(0))
nb=O['NB_modern_building']; W=world_verts(nb)
zmin=W[:,2].min(); low=W[W[:,2]<zmin+0.05]
print('building zmin',zmin,'n low verts',len(low),'low xy range',low[:,:2].min(0),low[:,:2].max(0))
print('terrain under building corners', [round(T.z(x,y),3) for x,y in [(low[:,0].min(),low[:,1].min()),(low[:,0].max(),low[:,1].min()),(low[:,0].min(),low[:,1].max()),(low[:,0].max(),low[:,1].max())]])
print('pt per world at building', 1/S.world_per_pt(Vector(W.mean(0))))
# objects whose screen bbox near building region 690-900 x 340-570
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or len(o.data.vertices)==0: continue
    if o.name.startswith(('NB_modern','R1_frame','R3_frame')): continue
    W=world_verts(o)
    if len(W)>200000: continue
    P=S.project(W)
    x0,x1,y0,y1=P[:,0].min(),P[:,0].max(),P[:,1].min(),P[:,1].max()
    if x1>680 and x0<900 and y1>340 and y0<580 and (x1-x0)<600:
        print('NEAR1', o.name, [c.name for c in o.users_collection], 'pt %.1f-%.1f %.1f-%.1f'%(x0,x1,y0,y1))
