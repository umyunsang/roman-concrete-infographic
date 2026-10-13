"""WD2 probe: Via Ostiensis islands (pavers / kerbs / beds), over-sea status, screen positions."""
import bpy, bmesh, sys, json
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts, bvh_of, need

out = sys.argv[sys.argv.index('--') + 1]
S = Screen()
land_bvh, _ = bvh_of([need('T_land')])
sea_bvh, _ = bvh_of([need('L10_sea')])


def down(b, p):
    h = b.ray_cast(Vector((p[0], p[1], 50)), Vector((0, 0, -1)))
    return h[0].z if h[0] else None


def islands(me):
    bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    seen = set(); outl = []
    for f in bm.faces:
        if f.index in seen: continue
        st = [f]; seen.add(f.index); fs = []
        while st:
            a = st.pop(); fs.append(a.index)
            for e in a.edges:
                for g in e.link_faces:
                    if g.index not in seen: seen.add(g.index); st.append(g)
        outl.append(sorted(fs))
    bm.free(); return outl

rep = {}
for name in ['R_via_ostiensis', 'R_roadgeo_ostiensis_junction_fill']:
    o = need(name); me = o.data; W = world_verts(o)
    mi = np.zeros(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi)
    isl = []
    for fs in islands(me):
        vs = sorted({v for f in fs for v in me.polygons[f].vertices})
        P = W[vs]; c = P.mean(0)
        lz = down(land_bvh, c); sz = down(sea_bvh, c)
        sp = S.project(P)
        isl.append({'nf': len(fs), 'nv': len(vs), 'mat': int(np.bincount(mi[fs]).argmax()), 'c': c.round(3).tolist(),
                    'zmin': round(P[:, 2].min(), 3), 'zmax': round(P[:, 2].max(), 3),
                    'wmin': P.min(0).round(3).tolist(), 'wmax': P.max(0).round(3).tolist(),
                    'land_z': None if lz is None else round(lz, 3), 'sea_z': None if sz is None else round(sz, 3),
                    'pt': [round(sp[:, 0].min(), 1), round(sp[:, 0].max(), 1), round(sp[:, 1].min(), 1), round(sp[:, 1].max(), 1)],
                    'faces': fs if len(fs) < 60 else None})
    rep[name] = isl
# coastline in screen: for x in 0..620, first y (from top) where camera ray hits sea before land
land_obj = need('T_land'); sea_obj = need('L10_sea')
bvh, owner = bvh_of([land_obj, sea_obj])
coast = []
for x in np.arange(0, 640, 1.0):
    prev = None
    for y in np.arange(1300, 1684, 0.5):
        o, d = S.ray((x, y)); loc, nor, fi, dist = bvh.ray_cast(o, d)
        cur = owner[fi] if fi is not None else None
        if prev == 'T_land' and cur == 'L10_sea':
            coast.append([float(x), float(y)]); break
        prev = cur
rep['coast'] = coast
json.dump(rep, open(out, 'w'))
print('WROTE', out)
