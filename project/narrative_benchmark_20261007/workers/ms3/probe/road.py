import bpy, sys, bmesh, json
import numpy as np
from mathutils import Vector
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts, Terrain, need
S = Screen(); land = need('T_land'); TER = Terrain(land)
def ground(pt):
    o, d = S.ray(np.array(pt, float)); h = TER.bvh.ray_cast(o, d)[0]; return np.array((h.x, h.y))
WP = [(560, 1010), (640, 1003), (700, 994), (760, 989), (800, 983), (835, 972), (860, 955), (880, 932), (900, 908), (920, 888), (936, 876)]
G = np.array([ground(p) for p in WP])
def densify(P, n):
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1); s = np.r_[0, np.cumsum(seg)]; u = np.linspace(0, s[-1], n)
    return np.stack([np.interp(u, s, P[:, 0]), np.interp(u, s, P[:, 1])], 1)
C = densify(G, 800)
def tangents(C):
    T = np.gradient(C, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]; return T, np.stack([-T[:, 1], T[:, 0]], 1)
T, N = tangents(C); s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(C, axis=0), axis=1))]
r = need('R_core_road'); bm = bmesh.new(); bm.from_mesh(r.data); bm.faces.ensure_lookup_table()
seen = set(); isl = []
for f in bm.faces:
    if f.index in seen: continue
    st = [f]; seen.add(f.index); vs = set(); nf = 0
    while st:
        a = st.pop(); nf += 1; vs.update(v.index for v in a.verts)
        for e in a.edges:
            for g in e.link_faces:
                if g.index not in seen: seen.add(g.index); st.append(g)
    isl.append((sorted(vs), nf))
bm.free()
WV = world_verts(r)
pav = [(vs, nf) for vs, nf in isl if nf < 40]; kerbs = [(vs, nf) for vs, nf in isl if nf >= 40]
PC = np.array([WV[vs, :2].mean(0) for vs, _ in pav])
def param(P):
    d = np.linalg.norm(P[:, None, :] - C[None, :, :], axis=2); i = d.argmin(1)
    return i, np.einsum('ij,ij->i', P - C[i], N[i])
near = np.linalg.norm(PC - np.array((31.86, -4.99)), axis=1) < 40
PCn = PC[near]; idx, lat = param(PCn)
ok = np.abs(lat) < 4
print('pavers near', len(PCn), 'within 4 of guide', ok.sum())
off = np.full(len(C), np.nan); hw = np.full(len(C), np.nan)
for k in range(len(C)):
    m = ok & (np.abs(idx - k) <= 6)
    if m.sum() >= 5: off[k] = (lat[m].max() + lat[m].min()) / 2; hw[k] = (lat[m].max() - lat[m].min()) / 2
good = ~np.isnan(off)
print('centre offset range', np.nanmin(off).round(3), np.nanmax(off).round(3), 'paver-centroid half-width p10/50/90', np.nanpercentile(hw, [10, 50, 90]).round(3))
xk = np.arange(len(C)); off = np.interp(xk, xk[good], off[good])
Kg = np.exp(-0.5 * (np.arange(-30, 31) / 10.0) ** 2); Kg /= Kg.sum(); off = np.convolve(np.pad(off, 30, mode='edge'), Kg, 'valid')
C2 = C + N * off[:, None]; C2 = densify(C2, 800); T2, N2 = tangents(C2); s2 = np.r_[0, np.cumsum(np.linalg.norm(np.diff(C2, axis=0), axis=1))]
# kerb lateral positions relative to C2
KV = np.concatenate([WV[vs, :2] for vs, _ in kerbs]); KV = KV[np.linalg.norm(KV - np.array((31.86, -4.99)), axis=1) < 40]
d = np.linalg.norm(KV[:, None, :] - C2[None, ::2, :], axis=2); ik = d.argmin(1) * 2
kl = np.einsum('ij,ij->i', KV - C2[ik], N2[ik])
print('kerb lateral |l| percentiles', np.percentile(np.abs(kl), [1, 10, 50, 90, 99]).round(3))
# per-side kerb inner/outer along s
for side in (1, -1):
    m = np.sign(kl) == side
    print('side', side, 'kerb |l| min/max', np.abs(kl[m]).min().round(3), np.abs(kl[m]).max().round(3))
# paver vertex lateral extents (not centroids)
PVall = np.concatenate([WV[vs, :2] for (vs, _), n_ in zip(pav, near) if n_])
d = np.linalg.norm(PVall[:, None, :] - C2[None, ::2, :], axis=2); ip = d.argmin(1) * 2
pl = np.einsum('ij,ij->i', PVall - C2[ip], N2[ip])
print('paver vertex lateral p1/p99', np.percentile(pl[np.abs(pl) < 4], [0.5, 1, 99, 99.5]).round(3))
# MS3 current relation
ms = need('MS3_core34_to_5'); o = np.array(ms.matrix_world.translation[:2])
i0 = np.linalg.norm(C2 - o, axis=1).argmin(); l0 = (o - C2[i0]) @ N2[i0]
head_road = np.degrees(np.arctan2(T2[i0, 1], T2[i0, 0]))
print('MS3 origin', o.round(3), 's0', s2[i0].round(3), 'l0', round(float(l0), 3), 'road heading', round(float(head_road), 2), 'MS3 rotz', round(np.degrees(ms.rotation_euler.z), 2))
# plinth footprint lateral extents
W = world_verts(ms); co = np.empty(len(ms.data.vertices)*3); ms.data.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
mi = np.empty(len(ms.data.polygons), np.int32); ms.data.polygons.foreach_get('material_index', mi)
pv = sorted({v for p in ms.data.polygons if p.material_index == 1 for v in p.vertices})
F = W[pv, :2]; fl = (F - C2[i0]) @ N2[i0]; fs = (F - C2[i0]) @ T2[i0]
print('plinth lateral range', fl.min().round(3), fl.max().round(3), 'along range', fs.min().round(3), fs.max().round(3))
cv = sorted({v for p in ms.data.polygons if p.material_index == 0 for v in p.vertices})
Cc = W[cv, :2]; cl = (Cc - C2[i0]) @ N2[i0]
print('column lateral range', cl.min().round(3), cl.max().round(3))
np.savez('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/ms3/probe/road.npz', C2=C2, s2=s2, T2=T2, N2=N2, G=G, KV=KV, kl=kl, PCn=PCn,
         C2pt=S.project(np.c_[C2, [TER.z(x, y) for x, y in C2]]))
