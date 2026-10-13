"""WD2 harbour + Via Ostiensis sea end (option B of OBJ_PLACE-11: the road ends on land at the shore).

* Via Ostiensis: everything beyond the shore is removed (paver islands beyond the cut, kerb ribbons bisected and
  capped); the road ends in a paved landing (half disc, D7 style) whose outer edge stays >= SHORE_GAP inside the
  coastline. The landing is draped on the current T_land and rebuilt on every run (faces tagged 'wd2_landing').
* L09_portus_lighthouse: rebuilt as the Claudian (Portus) stepped tower with an open fire, on an island platform at
  sea level.
* L09_portus_mole / L12_harbor_pilae: seated in the sea (base 0.04 below the water plane); the pilae are moved into
  the harbour mouth between the lighthouse and the basin, at the foot of the road's landing.
"""
import bpy, bmesh, math
import numpy as np
from mathutils import Vector, Matrix
from wd2_lib import islands, islands_bm, bvh_world, ray_down_z
from harbor_build import build_lighthouse_mesh, SEA_Z, LH

KERB_MIN_FACES = 40
# road frame of the Via Ostiensis sea end, measured on v8_14 (road geometry is owned by WD2, so it is stable):
# origin = road centre line at the coastline, d = seaward axis, n = east.
FRAME_O = np.array([28.592, -83.242]); FRAME_D = np.array([0.3793, -0.9253]); FRAME_N = np.array([0.9253, 0.3793])
SHORE_GAP = 0.45          # landing outer edge -> coastline (world; ~4.5 pt on screen here)
LH_CENTER = (35.0, -93.95)


def frame_st(W):
    rel = W[:, :2] - FRAME_O
    return rel @ FRAME_D, rel @ FRAME_N


def road_arrays(road):
    me = road.data
    assert np.allclose(np.array(road.matrix_world), np.eye(4), atol=1e-6), 'R_via_ostiensis must have an identity transform'
    W = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', W); W = W.reshape(-1, 3)
    return W


def remove_tagged(me, tag):
    a = me.attributes.get(tag)
    if a is None:
        return 0
    vals = np.zeros(len(me.polygons), np.int32); a.data.foreach_get('value', vals)
    if not vals.any():
        return 0
    bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    lay = bm.faces.layers.int.get(tag)
    dead = [f for f in bm.faces if f[lay] == 1]
    bmesh.ops.delete(bm, geom=dead, context='FACES')
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    bm.to_mesh(me); bm.free(); me.update()
    return len(dead)


def road_end_at_shore(road, land_bvh):
    me = road.data
    n_old = remove_tagged(me, 'wd2_landing')
    W = road_arrays(road); s, t = frame_st(W)
    near = (s > -4.0) & (s < -2.6)            # stays on land after the cut, so a re-run sees the same width
    tw, te = float(np.percentile(t[near], 0.5)), float(np.percentile(t[near], 99.5))
    tc = (tw + te) / 2; R = (te - tw) / 2 + 0.12
    # landing centre s_a: walk landwards until the half ring at R + SHORE_GAP is all on land
    s_a = None
    for sa in np.arange(1.0, -6.0, -0.02):
        ok = True
        for th in np.linspace(-math.pi / 2, math.pi / 2, 25):
            for rr in (R + SHORE_GAP, R + SHORE_GAP * 0.5, R):
                p = FRAME_O + FRAME_D * (sa + rr * math.cos(th)) + FRAME_N * (tc + rr * math.sin(th))
                if ray_down_z(land_bvh, p[0], p[1]) is None:
                    ok = False; break
            if not ok:
                break
        if ok:
            s_a = float(sa); break
    if s_a is None:
        raise RuntimeError('road end: no landing position found on land')
    bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    S = np.array([(v.co.x - FRAME_O[0]) * FRAME_D[0] + (v.co.y - FRAME_O[1]) * FRAME_D[1] for v in bm.verts])
    kill = []; n_isl = 0; cut_kerbs = 0
    for fs in islands_bm(bm):
        vs = {v.index for f in fs for v in bm.faces[f].verts}
        smax = max(S[v] for v in vs)
        if len(fs) < KERB_MIN_FACES and smax > s_a + 1e-4:
            kill += fs; n_isl += 1
        elif len(fs) >= KERB_MIN_FACES and smax > s_a + 1e-4:
            cut_kerbs += 1
    bmesh.ops.delete(bm, geom=[bm.faces[f] for f in kill], context='FACES')
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    if cut_kerbs:
        co = Vector((*(FRAME_O + FRAME_D * s_a), 0.0)); no = Vector((FRAME_D[0], FRAME_D[1], 0.0))
        geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
        res = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no, clear_outer=True, dist=1e-5)
        cut_edges = [e for e in res['geom_cut'] if isinstance(e, bmesh.types.BMEdge) and e.is_valid]
        if cut_edges:
            bmesh.ops.holes_fill(bm, edges=cut_edges, sides=0)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    bm.to_mesh(me); bm.free(); me.update()
    # landing height: paver tops sit top_off above the terrain near the road end
    W = road_arrays(road); s, t = frame_st(W)
    paver = np.zeros(len(W), bool)
    for fs in islands(me):
        if len(fs) < KERB_MIN_FACES:
            paver[list({v for f in fs for v in me.polygons[f].vertices})] = True
    band = (s > s_a - 1.6) & (s < s_a - 0.3) & paver
    offs = []
    for p in W[band]:
        z = ray_down_z(land_bvh, p[0], p[1])
        if z is not None:
            offs.append(p[2] - z)
    top_off = float(np.percentile(offs, 75)) if offs else 0.1
    top_off = min(max(top_off, 0.06), 0.16)
    n_new = add_landing(me, land_bvh, s_a, tc, R, top_off)
    W = road_arrays(road); s, _ = frame_st(W)
    return {'landing_centre_s': round(s_a, 3), 'landing_radius': round(R, 3), 'landing_top_above_terrain': round(top_off, 3),
            'removed_paver_islands': n_isl, 'kerbs_cut': cut_kerbs, 'old_landing_faces_removed': n_old,
            'landing_faces': n_new, 'road_max_s': round(float(s.max()), 3)}


def add_landing(me, land_bvh, s_a, tc, R, top_off, segs=12, thick=0.12):
    """half-disc fan (top tris + rim sides + back + bottom = 26 faces < 40 -> paving by the island rule)."""
    bm = bmesh.new(); bm.from_mesh(me)
    lay = bm.faces.layers.int.get('wd2_landing') or bm.faces.layers.int.new('wd2_landing')
    mat = 0
    for i, m in enumerate(me.materials):
        if m and m.name == 'RC.road.selce_basalt':
            mat = i

    def zt(x, y):
        z = ray_down_z(land_bvh, x, y)
        return (z if z is not None else 0.0) + top_off

    c = FRAME_O + FRAME_D * s_a + FRAME_N * tc
    ctop = bm.verts.new((c[0], c[1], zt(*c)))
    rim_top, rim_bot = [], []
    for k in range(segs + 1):
        th = -math.pi / 2 + math.pi * k / segs
        p = c + R * (math.cos(th) * FRAME_D + math.sin(th) * FRAME_N)
        z = zt(*p)
        rim_top.append(bm.verts.new((p[0], p[1], z)))
        rim_bot.append(bm.verts.new((p[0], p[1], z - thick)))
    cbot = bm.verts.new((c[0], c[1], ctop.co.z - thick))
    faces = []
    for k in range(segs):
        faces.append(bm.faces.new((ctop, rim_top[k], rim_top[k + 1])))
        faces.append(bm.faces.new((rim_top[k], rim_bot[k], rim_bot[k + 1], rim_top[k + 1])))
    faces.append(bm.faces.new([rim_top[0], ctop, rim_top[-1], rim_bot[-1], cbot, rim_bot[0]]))
    faces.append(bm.faces.new([cbot] + list(reversed(rim_bot))))
    for f in faces:
        f[lay] = 1; f.material_index = mat; f.smooth = False
    bm.normal_update()
    bm.to_mesh(me); bm.free(); me.update()
    return len(faces)


def build_lighthouse(lh, mats):
    stone, plinth, flame = mats
    me, ztop = build_lighthouse_mesh('L09_portus_lighthouse_wd2', {'stone': 0, 'plinth': 1, 'flame': 2})
    me.materials.clear()
    for m in (stone, plinth, flame):
        me.materials.append(m)
    old = lh.data
    lh.data = me
    if old.users == 0 and old.name != me.name:
        bpy.data.meshes.remove(old)
    lh.location = (LH_CENTER[0], LH_CENTER[1], SEA_Z); lh.rotation_euler = (0, 0, 0); lh.scale = (1, 1, 1)
    return {'top_z_above_sea': round(ztop, 3), 'faces': len(me.polygons), 'centre': LH_CENTER}


def seat_in_sea(o, depth=0.04, loc_xy=None, rot_z=None, scale=None):
    """place o so that its lowest vertex is `depth` below the sea plane."""
    if loc_xy is not None:
        o.location.x, o.location.y = loc_xy
    if rot_z is not None:
        o.rotation_euler = (0, 0, rot_z)
    if scale is not None:
        o.scale = (scale, scale, scale)
    bpy.context.view_layer.update()
    me = o.data
    co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    M = np.array(o.matrix_world); Wz = (np.c_[co, np.ones(len(co))] @ M.T)[:, 2]
    o.location.z += (SEA_Z - depth) - Wz.min()
    bpy.context.view_layer.update()
    return round(float(o.location.z), 4)
