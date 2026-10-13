import bpy, sys
import numpy as np
from mathutils import Vector
W='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work'
sys.path.insert(0, W+'/workers/layout')
from common import Screen, world_verts, bvh_of, map_visible_objects
S=Screen()
tower=[o for o in bpy.data.objects if o.name.startswith('D3_') and not o.name.startswith('D3_press') and o.type=='MESH']
print('tower objs', [o.name for o in tower])
bvh, owner = bvh_of(tower)
def hit(pt, b=bvh, own=owner):
    o,d = S.ray(pt); h = b.ray_cast(o, d)
    return (own[h[2]], h[3]) if h[0] is not None else (None, None)
for y in (1232.0, 1258.5, 1287.0, 1308.0):
    xs = np.arange(330, 290, -0.05)
    for x in xs:
        n,_ = hit((x,y))
        if n: print('row', y, 'silhouette x', round(x,2), n); break
mv = map_visible_objects()
bvhm, ownm = bvh_of(mv)
print('n map objs', len(mv))
from collections import Counter
for c in [(198.0,1497.0),(197.5,1496.1)]:
    cnt=Counter(); 
    for dx in np.arange(-3,3.01,0.25):
        for dy in np.arange(-3,3.01,0.25):
            if dx*dx+dy*dy<=9:
                n,_=hit((c[0]+dx,c[1]+dy), bvhm, ownm); cnt[n]+=1
    print('around', c, cnt.most_common())
# min dist to sea
def mind(c, name='L10_sea'):
    best=99
    for dx in np.arange(-4,4.01,0.05):
        for dy in np.arange(-4,4.01,0.05):
            r=np.hypot(dx,dy)
            if r<best:
                n,_=hit((c[0]+dx,c[1]+dy), bvhm, ownm)
                if n==name: best=r
    return best
print('sea dist from 198,1497:', round(mind((198.0,1497.0)),3), 'from 197.5,1496.1:', round(mind((197.5,1496.1)),3))
for p in ['H_lime','H_ash','H_stones','H_mold','H_books','H_research','H_colosseum','H_gate']:
    o=bpy.data.objects[p]
    print(p, 'pt per world', round(1/S.world_per_pt(np.array(o.matrix_world.translation)),3), 'pt per local', round(o.scale[0]/S.world_per_pt(np.array(o.matrix_world.translation)),3), 'pt', np.round(S.to_pt(o.matrix_world.translation),2))
