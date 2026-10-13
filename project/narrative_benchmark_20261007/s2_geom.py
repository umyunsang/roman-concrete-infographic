import bpy, json, math, runpy, sys, time
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
T0 = time.time()
BASE = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/'
INV = BASE + 'nb_work/workers/inventory/inventory.py'
INVJ = BASE + 'nb_work/review_loop/obj_r11/inventory.json'
OUT = BASE + 'opb2/'
g = runpy.run_path(INV)
to_pt_np = g['to_pt_np']; eval_mesh_arrays = g['eval_mesh_arrays']; render_visible = g['render_visible']; in_overlay = g['in_overlay']
sc = bpy.context.scene; cam = sc.camera
camloc = Vector(cam.matrix_world.translation)
dg = bpy.context.evaluated_depsgraph_get()
inv = json.load(open(INVJ))
obj_assets = {}
for a in inv['assets']:
    for n in a['objects']:
        obj_assets.setdefault(n, []).append(a['id'])
objbox = {o['name']: o['bbox_projected_unclipped_pt'] for o in inv['objects']}

vis = sorted([o for o in bpy.data.objects if render_visible(o)], key=lambda o: o.name)
mapobjs = [o for o in vis if not in_overlay(o)]
# --- evaluated geometry + BVH for map objects
GEO = {}
TREES = {}
AABB = {}
for o in mapobjs:
    ev = o.evaluated_get(dg)
    me = ev.to_mesh()
    M = o.matrix_world
    verts = [M @ v.co for v in me.vertices]
    polys = [tuple(p.vertices) for p in me.polygons]
    mats = [p.material_index for p in me.polygons]
    matnames = [s.material.name if s.material else None for s in o.material_slots]
    normals = [(M.to_3x3() @ p.normal).normalized() for p in me.polygons]
    centers = [M @ p.center for p in me.polygons]
    areas = [p.area for p in me.polygons]
    ev.to_mesh_clear()
    if not polys:
        continue
    TREES[o.name] = BVHTree.FromPolygons(verts, polys)
    P = np.array([tuple(v) for v in verts])
    GEO[o.name] = dict(P=P, polys=polys, mats=np.array(mats), matnames=matnames,
                       normals=np.array([tuple(n) for n in normals]), centers=np.array([tuple(c) for c in centers]),
                       areas=np.array(areas))
    AABB[o.name] = (P.min(0), P.max(0))
print('BVH built', len(TREES), round(time.time() - T0, 1))

def kz(p):
    """pt per world unit vertical at p"""
    uv = to_pt_np(np.array([p, np.array(p) + np.array([0, 0, 1.0])]))
    return float(np.linalg.norm(uv[1] - uv[0]))

def cast(origin, d, maxdist=1e5, skip=(), only=None, cand=None):
    """nearest hit over render-visible map objects; returns (name, loc, normal, dist) or None"""
    origin = Vector(origin); d = Vector(d).normalized()
    best = None
    names = cand if cand is not None else TREES.keys()
    for n in names:
        if n in skip: continue
        if only is not None and n not in only: continue
        h = TREES[n].ray_cast(origin, d, maxdist)
        if h[0] is not None and (best is None or h[3] < best[3]):
            best = (n, h[0], h[1], h[3])
    return best

def cand_xy(p, pad=0.5):
    return [n for n, (lo, hi) in AABB.items() if lo[0] - pad <= p[0] <= hi[0] + pad and lo[1] - pad <= p[1] <= hi[1] + pad]

def cand_screen(pt, pad=1.0):
    out = []
    for n in TREES:
        b = objbox.get(n)
        if b and b[0] - pad <= pt[0] <= b[1] + pad and b[2] - pad <= pt[1] <= b[3] + pad:
            out.append(n)
    return out

def asset_of(n):
    return obj_assets.get(n, ['?'])

MINE = {
 'landmark_colosseum': ['COL_ruined', 'R3_colosseum_podium', 'R4_arena_skin'],
 'landmark_pantheon': ['R8_pantheon'],
 'bridge_north': ['B_pons1', 'B_pons1_parapet0', 'B_pons1_parapet1'],
 'bridge_south': ['B_pons2', 'B_pons2_parapet0', 'B_pons2_parapet1', 'R4_bridge_west_bed'],
 'milestone_1_to_2': ['MS1_core1_to_2'],
 'milestone_2_to_34': ['MS2_core2_to_34'],
 'milestone_34_to_5': ['MS3_core34_to_5'],
}
ROADS = ['R_core_road', 'R1_road_landing1', 'R1_road_landing5', 'R1_road5_bed', 'R_via_appia', 'R_via_ostiensis', 'R_roadgeo_ostiensis_junction_fill']
res = {'assets': {}}
# ---------------- A. base samples, support, burial, height
for aid, names in MINE.items():
    A = {'objects': {}}
    own = set(names)
    allP = np.concatenate([GEO[n]['P'] for n in names])
    ztop = float(allP[:, 2].max())
    for n in names:
        G = GEO[n]; P = G['P']
        zmin = float(P[:, 2].min())
        k = kz(P[np.argmin(P[:, 2])])
        band = 0.5 / k
        idx = np.where(P[:, 2] <= zmin + band)[0]
        if len(idx) < 8:
            idx = np.argsort(P[:, 2])[:8]
        # thin out very large sample sets
        if len(idx) > 400:
            idx = idx[np.linspace(0, len(idx) - 1, 400).astype(int)]
        samples = []
        for i in idx:
            p = Vector(P[i])
            c = cand_xy(p)
            dn = cast(p + Vector((0, 0, 1e-3)), (0, 0, -1), 1e4, skip=own, cand=c)
            up = cast(p - Vector((0, 0, 1e-3)), (0, 0, 1), max(ztop - zmin, 1.0), skip=own, cand=c)
            s = {'p': list(P[i]), 'pt': to_pt_np(P[i])[0].tolist()}
            if dn:
                gdist = dn[3] - 1e-3
                q = np.array(p) - np.array([0, 0, max(gdist, 0)])
                s['down'] = [dn[0], gdist, float(np.linalg.norm(to_pt_np(np.array([P[i], q]))[0] - to_pt_np(np.array([P[i], q]))[1])) * (1 if gdist >= 0 else -1), list(dn[2])]
            if up:
                udist = up[3] - 1e-3
                q = np.array(p) + np.array([0, 0, udist])
                s['up'] = [up[0], udist, float(np.linalg.norm(to_pt_np(np.array([P[i], q]))[0] - to_pt_np(np.array([P[i], q]))[1]))]
            samples.append(s)
        # surface-area weighted centroid
        cen = (G['centers'] * G['areas'][:, None]).sum(0) / G['areas'].sum()
        A['objects'][n] = {'zmin': zmin, 'zmax': float(P[:, 2].max()), 'kz': k, 'n_samples': len(samples), 'samples': samples,
                           'centroid': cen.tolist(), 'tilt_matrix_deg': math.degrees((bpy.data.objects[n].matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized().angle(Vector((0, 0, 1))))}
    res['assets'][aid] = A
print('A done', round(time.time() - T0, 1))

# ---------------- milestone parts: plate/pillar/plinth analysis
camR = Vector(cam.matrix_world.col[0][:3]).normalized()
for aid in ['milestone_1_to_2', 'milestone_2_to_34', 'milestone_34_to_5']:
    n = MINE[aid][0]; G = GEO[n]
    mn = G['matnames']
    def faces_of(key):
        return np.where(np.isin(G['mats'], [i for i, m in enumerate(mn) if m and key in m]))[0]
    fa, fs, fp = faces_of('direction_arrow'), faces_of('milestone_stone'), faces_of('roman_plinth')
    def verts_of(fi):
        vi = sorted({v for f in fi for v in G['polys'][f]})
        return G['P'][vi]
    Pa, Ps, Pp = verts_of(fa), verts_of(fs), verts_of(fp)
    ca = Pa.mean(0)
    U, S, Vt = np.linalg.svd(Pa - ca, full_matrices=False)
    ax1, ax2, nrm = Vt[0], Vt[1], Vt[2]
    vcam = np.array(camloc) - ca; vcam /= np.linalg.norm(vcam)
    f = abs(float(nrm @ vcam))
    t1 = (Pa - ca) @ ax1; t2 = (Pa - ca) @ ax2
    L = float(t1.max() - t1.min())
    # width profile near both ends
    def width_at(lo, hi):
        sel = (t1 >= lo) & (t1 <= hi)
        return float(t2[sel].max() - t2[sel].min()) if sel.sum() > 2 else 0.0
    tmin, tmax = t1.min(), t1.max()
    prof = [width_at(tmin + L * a, tmin + L * (a + 0.05)) for a in np.arange(0, 1.0, 0.05)]
    # tip: end whose extreme 5% width is smallest relative to 15-25% inward
    tipsign = 1 if prof[-1] < prof[0] else -1
    tipv = Pa[np.argmax(t1 * tipsign)]
    tailv = Pa[np.argmin(t1 * tipsign)]
    uvt = to_pt_np(np.array([tipv, tailv]))
    Lp = float(np.linalg.norm(uvt[0] - uvt[1]))
    kr = float(np.linalg.norm(to_pt_np(np.array([ca, ca + np.array(camR)]))[1] - to_pt_np(np.array([ca, ca + np.array(camR)]))[0]))
    Lt = L * kr
    # pillar axis tilt: centroids of z slices
    zs = np.linspace(Ps[:, 2].min(), Ps[:, 2].max(), 12)
    cs = []
    for z0, z1 in zip(zs[:-1], zs[1:]):
        sel = (Ps[:, 2] >= z0) & (Ps[:, 2] < z1)
        if sel.sum() > 20:
            cs.append(np.r_[Ps[sel, :2].mean(0), (z0 + z1) / 2])
    cs = np.array(cs)
    A_ = np.c_[cs[:, 2], np.ones(len(cs))]
    bx = np.linalg.lstsq(A_, cs[:, 0], rcond=None)[0][0]; by = np.linalg.lstsq(A_, cs[:, 1], rcond=None)[0][0]
    pill_tilt = math.degrees(math.atan(math.hypot(bx, by)))
    # self occlusion: sample arrow faces facing camera, ray toward camera
    occ_self = occ_other = tot = 0.0
    tip_occ = None
    others_hit = {}
    pillar_tree = BVHTree.FromPolygons([Vector(v) for v in G['P']], [G['polys'][i] for i in np.r_[fs, fp]])
    for fi in fa:
        c = G['centers'][fi]; nn = G['normals'][fi]
        v = np.array(camloc) - c; v /= np.linalg.norm(v)
        if nn @ v <= 0.05:
            continue
        ar = G['areas'][fi]; tot += ar
        o = Vector(c) + Vector(v) * 1e-3
        h1 = pillar_tree.ray_cast(o, Vector(v))
        if h1[0] is not None:
            occ_self += ar; continue
        h2 = cast(o, v, skip={n}, cand=cand_screen(to_pt_np(c)[0]))
        if h2:
            occ_other += ar; others_hit[h2[0]] = others_hit.get(h2[0], 0) + ar
    # tip visibility (slightly inside the tip)
    tipin = tipv - (tipv - ca) * 0.02
    v = np.array(camloc) - tipin; v /= np.linalg.norm(v)
    ht = pillar_tree.ray_cast(Vector(tipin) + Vector(v) * 1e-3, Vector(v))
    ho = cast(Vector(tipin) + Vector(v) * 1e-3, v, skip={n}, cand=cand_screen(to_pt_np(tipin)[0]))
    tip_occ = {'by_pillar': ht[0] is not None, 'by_other': ho[0] if ho else None}
    # plinth footprint (bottom verts) and height
    zb = Pp[:, 2].min()
    foot = Pp[Pp[:, 2] <= zb + 0.02]
    res['assets'][aid]['ms'] = {
        'plate_normal': nrm.tolist(), 'f_cos': f, 'plate_len_world': L, 'Lp_pt': Lp, 'Lt_pt': Lt, 'Lp_over_Lt': Lp / Lt,
        'width_profile': prof, 'tip_world': tipv.tolist(), 'tip_pt': uvt[0].tolist(), 'tail_pt': uvt[1].tolist(),
        'self_occ_frac': occ_self / tot if tot else None, 'other_occ_frac': occ_other / tot if tot else None, 'others_hit': others_hit,
        'tip_occ': tip_occ, 'pillar_axis_tilt_deg': pill_tilt, 'pillar_slices': cs.tolist(),
        'plinth_foot_world': foot.tolist(), 'plinth_foot_pt': to_pt_np(foot).tolist(),
        'arrow_dir_world': (tipv - tailv).tolist(), 'n_arrow_faces': int(len(fa)), 'n_stone': int(len(fs)), 'n_plinth': int(len(fp)),
    }
print('MS done', round(time.time() - T0, 1))

# ---------------- road vertex occlusion by each non-road object (ray toward camera)
road_occ = {}
road_occ_pts = {}
for rn in ROADS:
    if rn not in GEO: continue
    P = GEO[rn]['P']
    uv = to_pt_np(P)
    for i in range(len(P)):
        p = P[i]
        v = np.array(camloc) - p; v /= np.linalg.norm(v)
        c = [n for n in cand_screen(uv[i], 0.5) if n not in ROADS]
        if not c: continue
        h = cast(Vector(p) + Vector(v) * 2e-3, v, skip=set(ROADS), cand=c)
        if h:
            road_occ[(rn, h[0])] = road_occ.get((rn, h[0]), 0) + 1
            road_occ_pts.setdefault(h[0], []).append([rn] + uv[i].tolist())
res['road_occlusion'] = {f'{a}|{b}': c for (a, b), c in road_occ.items()}
res['road_occ_pts'] = {k: v for k, v in road_occ_pts.items() if not k.startswith('T_land')}
print('road occ done', round(time.time() - T0, 1))

# ---------------- BVH overlaps (07)
def screen_box_of(names):
    bs = [objbox[n] for n in names if objbox.get(n)]
    return [min(b[0] for b in bs), max(b[1] for b in bs), min(b[2] for b in bs), max(b[3] for b in bs)]
MINE_ALL = dict(MINE)
MINE_ALL['road_core'] = ['R_core_road', 'R1_road_landing1']
ovl = {}
for aid, names in MINE_ALL.items():
    for n in names:
        b = objbox[n]
        for m in TREES:
            if m in names: continue
            bm = objbox.get(m)
            if not bm: continue
            if bm[0] > b[1] + 5 or bm[1] < b[0] - 5 or bm[2] > b[3] + 5 or bm[3] < b[2] - 5: continue
            # world AABB check
            la, ha = AABB[n]; lb, hb = AABB[m]
            if (la > hb + 0.01).any() or (lb > ha + 0.01).any(): continue
            pairs = TREES[n].overlap(TREES[m])
            if not pairs: continue
            # depth: verts of n's overlapping polys inside m
            pis = sorted({p[0] for p in pairs})
            vids = sorted({v for pi in pis for v in GEO[n]['polys'][pi]})
            dmax = 0.0; dpt = 0.0
            for vi in vids[:3000]:
                p = Vector(GEO[n]['P'][vi])
                loc, nor, ix, dist = TREES[m].find_nearest(p)
                if loc is None: continue
                if (p - loc).dot(nor) < 0:
                    if dist > dmax:
                        dmax = dist
                        dpt = float(np.linalg.norm(to_pt_np(np.array([tuple(p), tuple(loc)]))[0] - to_pt_np(np.array([tuple(p), tuple(loc)]))[1]))
            # visibility of overlap: centers of n-polys in pairs, ray to camera; visible if first hit is n or m or none
            vis_n = 0; tested = 0
            cpts = []
            for pi in pis[:600]:
                c = GEO[n]['centers'][pi]
                v = np.array(camloc) - c; v /= np.linalg.norm(v)
                h = cast(Vector(c) + Vector(v) * 2e-3, v, skip={n}, cand=cand_screen(to_pt_np(c)[0]))
                tested += 1
                if (h is None) or (h[0] == m and h[3] < 0.05):
                    vis_n += 1
                    cpts.append(to_pt_np(c)[0].tolist())
            ovl[f'{n}|{m}'] = {'pairs': len(pairs), 'depth_world': dmax, 'depth_pt_screen': dpt, 'depth_pt_kz': dmax * kz(GEO[n]['P'][vids[0]]),
                                 'vis_centers': vis_n, 'tested': tested, 'assets_m': asset_of(m), 'vis_pts_sample': cpts[:30]}
res['overlaps'] = ovl
print('overlap done', round(time.time() - T0, 1))

# ---------------- export projected triangles for masks
tri_export = {}
for n in ['R_core_road', 'R1_road_landing1', 'R1_road_landing5', 'R1_road5_bed', 'R_via_appia', 'R_via_ostiensis', 'R_roadgeo_ostiensis_junction_fill',
          'L02_tiber', 'L10_sea', 'B_pons1', 'B_pons2', 'R4_bridge_west_bed', 'R3_colosseum_podium', 'COL_ruined', 'R8_pantheon',
          'MS1_core1_to_2', 'MS2_core2_to_34', 'MS3_core34_to_5', 'T_cypress', 'B_pons1_parapet0', 'B_pons1_parapet1', 'B_pons2_parapet0', 'B_pons2_parapet1']:
    G = GEO[n]
    uv = to_pt_np(G['P'])
    tris = []
    for poly in G['polys']:
        for j in range(1, len(poly) - 1):
            tris.append((poly[0], poly[j], poly[j + 1]))
    np.save(OUT + f'tri_{n}.npy', uv[np.array(tris)].astype(np.float32))
    np.save(OUT + f'trimat_{n}.npy', np.repeat(G['mats'], [len(p) - 2 for p in G['polys']]).astype(np.int16))
    np.save(OUT + f'triz_{n}.npy', G['P'][np.array(tris)][:, :, 2].mean(1).astype(np.float32))
    tri_export[n] = {'matnames': G['matnames'], 'n': len(tris)}
res['tri_export'] = tri_export
# heights h_A
for aid, names in MINE.items():
    allP = np.concatenate([GEO[n]['P'] for n in names])
    res['assets'][aid]['zmin_all'] = float(allP[:, 2].min()); res['assets'][aid]['zmax_all'] = float(allP[:, 2].max())
for n in ['T_cypress', 'T_pine.004', 'C2_hot_mixing', 'D2_lime_kiln', 'NB_modern_building', 'L05_aqua_claudia']:
    P = GEO[n]['P']; res.setdefault('others', {})[n] = {'zmin': float(P[:, 2].min()), 'zmax': float(P[:, 2].max()), 'min': P.min(0).tolist(), 'max': P.max(0).tolist()}
res['camloc'] = list(camloc)
json.dump(res, open(OUT + 's2_geom.json', 'w'))
print('ALL DONE', round(time.time() - T0, 1))
