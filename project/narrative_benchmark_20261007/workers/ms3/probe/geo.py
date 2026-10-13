import bpy, sys, json, bmesh
import numpy as np
from mathutils import Vector
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts, Terrain, need
OUT = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/ms3/probe/geo.npz'
S = Screen(); O = bpy.data.objects
ms = need('MS3_core34_to_5'); me = ms.data
co = np.empty(len(me.vertices)*3); me.vertices.foreach_get('co', co); co = co.reshape(-1,3)
mi = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi)
print('local bbox', co.min(0).round(4), co.max(0).round(4))
slots = [s.material.name for s in ms.material_slots]
for k, n in enumerate(slots):
    vs = set()
    for p in me.polygons:
        if p.material_index == k: vs.update(p.vertices)
    vs = np.array(sorted(vs))
    if len(vs)==0: print(n, 'none'); continue
    c = co[vs]
    print('mat', k, n, 'nverts', len(vs), 'faces', int((mi==k).sum()), 'bbox', c.min(0).round(4), c.max(0).round(4), 'mean', c.mean(0).round(4))
# arrow tip: farthest arrow vertex along principal horizontal axis
k = slots.index('RC.v12_1.direction_arrow')
vs = sorted({v for p in me.polygons if p.material_index == k for v in p.vertices}); A = co[vs]
ctr = A[:, :2].mean(0); U, s_, Vt = np.linalg.svd(A[:, :2]-ctr); ax = Vt[0]
proj = (A[:, :2]-ctr) @ ax
print('arrow principal axis (local)', ax.round(4), 'extent', proj.min().round(4), proj.max().round(4))
# width profile along axis to identify tip (narrow end = tip)
for lo, hi in ((proj.min(), proj.min()+0.1*(proj.max()-proj.min())), (proj.max()-0.1*(proj.max()-proj.min()), proj.max())):
    m = (proj>=lo)&(proj<=hi); perp = (A[m, :2]-ctr) @ np.array((-ax[1], ax[0]))
    print('  end', round(float(lo),3), round(float(hi),3), 'n', int(m.sum()), 'perp width', round(float(perp.max()-perp.min()),4))
# world
M = np.array(ms.matrix_world)
Wa = (np.c_[A, np.ones(len(A))] @ M.T)[:, :3]
print('arrow world bbox', Wa.min(0).round(3), Wa.max(0).round(3))
wax = np.array(ms.matrix_world.to_3x3() @ Vector((ax[0], ax[1], 0)))[:2]; wax /= np.linalg.norm(wax)
print('arrow world axis', wax.round(4), 'heading deg', np.degrees(np.arctan2(wax[1], wax[0])).round(2))
# column base
land = need('T_land'); TER = Terrain(land)
Wall = (np.c_[co, np.ones(len(co))] @ M.T)[:, :3]
zmin = Wall[:, 2].min(); low = Wall[Wall[:, 2] < zmin + 0.03]
rel = np.array([p[2]-TER.z(p[0], p[1]) for p in Wall[Wall[:, 2] < zmin + 0.6][::5]])
print('world zmin', round(zmin,4), 'low verts', len(low))
print('plinth-bottom-ish verts rel to terrain: min/med/max', rel.min().round(3), np.median(rel).round(3), rel.max().round(3))
# plinth material verts
k2 = slots.index('RC.v12.roman_plinth')
vs2 = sorted({v for p in me.polygons if p.material_index == k2 for v in p.vertices}); Pl = Wall[vs2]
print('plinth world bbox', Pl.min(0).round(3), Pl.max(0).round(3))
# terrain around footprint
fx = np.linspace(Pl[:,0].min(), Pl[:,0].max(), 7); fy = np.linspace(Pl[:,1].min(), Pl[:,1].max(), 7)
tz = np.array([[TER.z(x, y) for x in fx] for y in fy]); print('terrain under plinth bbox min/max', tz.min().round(3), tz.max().round(3))
# the plinth bottom vs terrain per vertex
bot = Pl[Pl[:, 2] < Pl[:, 2].min() + 0.05]
rb = np.array([p[2]-TER.z(p[0], p[1]) for p in bot]); print('plinth bottom verts rel terrain', len(bot), rb.min().round(3), np.median(rb).round(3), rb.max().round(3))
# plinth top
print('plinth top z', Pl[:, 2].max().round(3), 'top rel terrain at centre', round(Pl[:,2].max() - TER.z(*Pl[:, :2].mean(0)), 3))
print('origin', ms.matrix_world.translation[:], 'terrain at origin', TER.z(ms.matrix_world.translation.x, ms.matrix_world.translation.y))
# roads: islands
res = {}
for rn in ('R_core_road', 'R_via_appia'):
    r = need(rn); bm = bmesh.new(); bm.from_mesh(r.data); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    seen=set(); isl=[]
    for f in bm.faces:
        if f.index in seen: continue
        st=[f]; seen.add(f.index); vs=set(); nf=0
        while st:
            a=st.pop(); nf+=1; vs.update(v.index for v in a.verts)
            for e in a.edges:
                for g in e.link_faces:
                    if g.index not in seen: seen.add(g.index); st.append(g)
        isl.append((sorted(vs), nf))
    bm.free()
    WV = world_verts(r); PV = S.project(WV)
    cen = []; kerb = []
    for vs, nf in isl:
        c = PV[vs].mean(0)
        if nf < 40:
            if 560 < c[0] < 1100 and 780 < c[1] < 1080: cen.append([*WV[vs].mean(0), *c, nf])
        else:
            m = (PV[vs,0] > 560) & (PV[vs,0] < 1100) & (PV[vs,1] > 780) & (PV[vs,1] < 1080)
            if m.any(): kerb.append(np.c_[WV[vs][m], PV[vs][m]])
    res[rn+'_pav'] = np.array(cen); res[rn+'_kerb'] = np.concatenate(kerb) if kerb else np.zeros((0,5))
    print(rn, 'pavers in roi', len(cen), 'kerb pts', len(res[rn+'_kerb']), 'islands', len(isl))
for n in ('R1_road5_bed', 'R1_road_landing5'):
    W = world_verts(need(n)); res[n] = np.c_[W, S.project(W)]
res['ms3_world'] = Wall; res['ms3_pt'] = S.project(Wall)
res['ms3_arrow_world'] = Wa
np.savez(OUT, **res)
