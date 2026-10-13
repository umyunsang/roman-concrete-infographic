import bpy, bmesh, sys, numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/WD1')
import wd1lib as L
S = L.Screen()
o = bpy.data.objects['COL_ruined']; me = o.data
sx, sy, sz = o.matrix_world.to_scale()
bvh, owner, fidx = L.bvh_of(L.map_visible_objects())
offs = L.disk(8)
Wv = L.world_verts(o); P = S.project(Wv)
bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table()
for nm, box in {'west': (378, 402, 845, 866), 'east': (744, 770, 900, 932)}.items():
    g = L.ray_grid(S, box, 8, bvh, owner, fidx)
    m = g['hit'] == g['names'].index('COL_ruined')
    resid = m & ~L.dilate(L.erode(m, offs), offs)
    resid[:8, :] = resid[-8:, :] = False; resid[:, :8] = resid[:, -8:] = False
    for ys, xs in L.label(resid):
        ln = L.comp_len_pt(ys, xs, 8)
        if ln < 2: continue
        fs = sorted({int(f) for f in g['face'][ys, xs] if f >= 0})
        print('==', nm, 'len', round(ln, 2), 'faces', len(fs), 'at', round(box[0] + xs.mean() / 8, 1), round(box[2] + ys.mean() / 8, 1))
        vs = sorted({v.index for f in fs for v in bm.faces[f].verts})
        for f in fs:
            F = bm.faces[f]
            print('  f', f, 'area_w %.4f' % (F.calc_area() * sx * sy), 'nv', len(F.verts), 'verts', [v.index for v in F.verts],
                  'pt', [tuple(P[v.index].round(1)) for v in F.verts])
        # vertex degree and distance to neighbour mean
        for vi in vs:
            v = bm.verts[vi]
            nbr = [e.other_vert(v).index for e in v.link_edges]
            mean = Wv[nbr].mean(0)
            print('   v', vi, 'pt', P[vi].round(1), 'deg', len(nbr), 'dev %.3f' % np.linalg.norm(Wv[vi] - mean), 'faces', len(v.link_faces), 'boundary', any(e.is_boundary for e in v.link_edges))
