"""WD2: Roman stepped lighthouse (Portus/Claudius type) + stone causeway (mole) under the Via Ostiensis.
All geometry is rebuilt from scratch on every run (idempotent)."""
import bpy, bmesh, math
import numpy as np
from mathutils import Vector, Matrix
from wd2_lib import box_bm, cyl_bm, mesh_from_bm, boolean_diff, append_mesh, material_copy, set_mat_color

SEA_Z = -0.70

# tier sizes (world units) -- top/bottom = D4/T1 = 0.34, each tier steps in >= 0.35 a side
LH = dict(P=3.5, H0=0.42,              # island platform (square) height above the sea
          T1=2.9, H1=2.35, T2=2.2, H2=2.0, T3=1.5, H3=1.65, D4=0.8, H4=1.0,
          CORN=0.08, CORN_H=0.12, BOWL_D=0.9, BOWL_H=0.2, FLAME_H=0.8)


def _arch_cutter(bm, cx, cy, z0, w, h, depth, axis):
    """an arched opening cutter (box + half cylinder) centred on (cx, cy), facing along axis 'x' or 'y'."""
    r = w / 2
    hb = h - r
    if axis == 'y':
        box_bm(bm, cx - r, cx + r, cy - depth, cy + depth, z0, z0 + hb)
        segs = 12
        # half-cylinder along y
        ring = []
        for side in (-depth, depth):
            pts = [bm.verts.new((cx + r * math.cos(math.pi * i / segs), cy + side, z0 + hb + r * math.sin(math.pi * i / segs))) for i in range(segs + 1)]
            ring.append(pts)
        for i in range(segs):
            bm.faces.new((ring[0][i], ring[0][i + 1], ring[1][i + 1], ring[1][i]))
        bm.faces.new(list(reversed(ring[0])))
        bm.faces.new(ring[1])
    else:
        box_bm(bm, cx - depth, cx + depth, cy - r, cy + r, z0, z0 + hb)
        segs = 12
        ring = []
        for side in (-depth, depth):
            pts = [bm.verts.new((cx + side, cy + r * math.cos(math.pi * i / segs), z0 + hb + r * math.sin(math.pi * i / segs))) for i in range(segs + 1)]
            ring.append(pts)
        for i in range(segs):
            bm.faces.new((ring[0][i], ring[0][i + 1], ring[1][i + 1], ring[1][i]))
        bm.faces.new(ring[0])
        bm.faces.new(list(reversed(ring[1])))


def _tier(name, half, z0, h, openings, bevel=0.05):
    """square tier with arched openings cut on its -y / +x faces. openings: list of (face, u, z, w, hgt)."""
    bm = bmesh.new()
    box_bm(bm, -half, half, -half, half, z0, z0 + h, mat=0, bevel=bevel, segs=2)
    me = mesh_from_bm(name + '_body', bm); bm.free()
    if not openings:
        return me
    cb = bmesh.new()
    for face, u, zc, w, hh in openings:
        d = 0.16
        if face == '-y':
            _arch_cutter(cb, u, -half, zc, w, hh, d, 'y')
        elif face == '+x':
            _arch_cutter(cb, half, u, zc, w, hh, d, 'x')
        elif face == '+y':
            _arch_cutter(cb, u, half, zc, w, hh, d, 'y')
        elif face == '-x':
            _arch_cutter(cb, -half, u, zc, w, hh, d, 'x')
    cme = mesh_from_bm(name + '_cut', cb); cb.free()
    out = boolean_diff(me, cme)
    bpy.data.meshes.remove(me)
    return out


def _cyl_tier(name, r, z0, h, n_open=4, ow=0.26, oh=0.48):
    bm = bmesh.new()
    cyl_bm(bm, 0, 0, r, z0, z0 + h, mat=0, segs=32)
    me = mesh_from_bm(name + '_body', bm); bm.free()
    cb = bmesh.new()
    for k in range(n_open):
        a = math.pi / 4 + k * math.pi / 2           # openings face the diagonals -> two face the camera
        cx, cy = r * math.cos(a), r * math.sin(a)
        # rotate a y-facing cutter about z by (a - 90deg)
        tmp = bmesh.new(); _arch_cutter(tmp, 0, 0, z0 + 0.3, ow, oh, 0.3, 'y')
        rot = Matrix.Rotation(a - math.pi / 2, 4, 'Z')
        bmesh.ops.transform(tmp, matrix=Matrix.Translation((cx, cy, 0)) @ rot, verts=tmp.verts)
        tme = bpy.data.meshes.new('_tmp'); tmp.to_mesh(tme); tmp.free()
        append_mesh(cb, tme); bpy.data.meshes.remove(tme)
    cme = mesh_from_bm(name + '_cut', cb); cb.free()
    out = boolean_diff(me, cme)
    bpy.data.meshes.remove(me)
    return out


def _flame(bm, z0, h, mat):
    """three-tongue flame: tapered, slightly bulged cones."""
    def tongue(cx, cy, r, hh, lean):
        segs = 14; rings = 7
        prev = None; verts_rings = []
        for k in range(rings + 1):
            t = k / rings
            rad = r * math.sin(math.pi * (0.15 + 0.85 * t)) * (1 - t) ** 0.35 if k < rings else 0
            z = z0 + hh * t
            ox, oy = lean[0] * t * t, lean[1] * t * t
            if k == rings:
                verts_rings.append([bm.verts.new((cx + ox, cy + oy, z))])
            else:
                verts_rings.append([bm.verts.new((cx + ox + rad * math.cos(2 * math.pi * i / segs),
                                                  cy + oy + rad * math.sin(2 * math.pi * i / segs), z)) for i in range(segs)])
        for k in range(rings):
            a, b = verts_rings[k], verts_rings[k + 1]
            for i in range(segs):
                j = (i + 1) % segs
                if len(b) == 1:
                    f = bm.faces.new((a[i], a[j], b[0]))
                else:
                    f = bm.faces.new((a[i], a[j], b[j], b[i]))
                f.material_index = mat; f.smooth = True
        f = bm.faces.new(list(reversed(verts_rings[0]))); f.material_index = mat
    tongue(0, 0, 0.27, h, (0.03, -0.03))
    tongue(0.15, -0.09, 0.15, h * 0.66, (0.08, -0.05))
    tongue(-0.13, 0.09, 0.14, h * 0.58, (-0.07, 0.04))
    tongue(0.04, 0.16, 0.12, h * 0.5, (0.02, 0.07))


def build_lighthouse_mesh(mesh_name, mats):
    """mats: dict stone, plinth, flame -> material slot index. Local origin = tower axis at sea level."""
    p = LH
    parts = []
    bm = bmesh.new()
    # island platform (into the water) + one plinth step
    box_bm(bm, -p['P'] / 2, p['P'] / 2, -p['P'] / 2, p['P'] / 2, -0.10, p['H0'], mat=mats['plinth'], bevel=0.07, segs=2)
    s1 = p['T1'] / 2 + 0.2
    box_bm(bm, -s1, s1, -s1, s1, p['H0'] - 0.01, p['H0'] + 0.14, mat=mats['plinth'], bevel=0.04, segs=2)
    z = p['H0'] + 0.14
    tiers = [(p['T1'], p['H1'], [('-y', 0.0, 0.0, 0.56, 0.98), ('-y', 0.0, 1.4, 0.28, 0.52), ('+x', -0.5, 1.0, 0.28, 0.52), ('+x', 0.5, 1.0, 0.28, 0.52)]),
             (p['T2'], p['H2'], [('-y', 0.0, 0.68, 0.28, 0.52), ('+x', 0.0, 0.68, 0.28, 0.52)]),
             (p['T3'], p['H3'], [('-y', 0.0, 0.55, 0.24, 0.46), ('+x', 0.0, 0.55, 0.24, 0.46)])]
    for k, (T, H, ops) in enumerate(tiers):
        ops_abs = [(f, u, z + zz, w, hh) for f, u, zz, w, hh in ops]
        me = _tier(f'_wd2_lh_t{k}', T / 2, z, H, ops_abs)
        append_mesh(bm, me, mat_map={0: mats['stone']}); bpy.data.meshes.remove(me)
        # cornice (plinth stone) at the top of the tier
        c = T / 2 + p['CORN']
        box_bm(bm, -c, c, -c, c, z + H - 0.02, z + H + p['CORN_H'], mat=mats['plinth'], bevel=0.035, segs=2)
        z += H + p['CORN_H']
    # cylinder tier with four arched fire-chamber openings
    me = _cyl_tier('_wd2_lh_t3', p['D4'] / 2, z, p['H4'], ow=0.2, oh=0.42)
    append_mesh(bm, me, mat_map={0: mats['stone']}); bpy.data.meshes.remove(me)
    z += p['H4']
    cyl_bm(bm, 0, 0, p['D4'] / 2 + 0.07, z - 0.02, z + 0.09, mat=mats['plinth'], segs=32)
    z += 0.09
    # open fire bowl (brazier) + flame
    cyl_bm(bm, 0, 0, p['BOWL_D'] / 2 * 0.62, z - 0.01, z + p['BOWL_H'] * 0.45, mat=mats['plinth'], segs=24)
    cyl_bm(bm, 0, 0, p['BOWL_D'] / 2 * 0.80, z + p['BOWL_H'] * 0.45, z + p['BOWL_H'], mat=mats['plinth'], segs=24,
           r_top=p['BOWL_D'] / 2)
    _flame(bm, z + p['BOWL_H'] * 0.55, p['FLAME_H'], mats['flame'])
    me = mesh_from_bm(mesh_name, bm); bm.free()
    for poly in me.polygons:
        if poly.material_index != mats['flame']:
            poly.use_smooth = False
    return me, z + p['BOWL_H'] * 0.55 + p['FLAME_H']


def causeway_bm(bm, left, right, top_l, top_r, bottom_z, mat, batter=0.12):
    """solid strip between two edge polylines (world/local XY), top following top_l/top_r, sloped (battered) sides."""
    n = len(left)
    L = [np.array(p, float) for p in left]; R = [np.array(p, float) for p in right]
    vt_l, vt_r, vb_l, vb_r = [], [], [], []
    for i in range(n):
        a, b = L[i], R[i]
        out = (a - b) / max(np.linalg.norm(a - b), 1e-6)
        vt_l.append(bm.verts.new((a[0], a[1], top_l[i])))
        vt_r.append(bm.verts.new((b[0], b[1], top_r[i])))
        vb_l.append(bm.verts.new((a[0] + out[0] * batter, a[1] + out[1] * batter, bottom_z)))
        vb_r.append(bm.verts.new((b[0] - out[0] * batter, b[1] - out[1] * batter, bottom_z)))
    fs = []
    for i in range(n - 1):
        fs.append(bm.faces.new((vt_l[i], vt_r[i], vt_r[i + 1], vt_l[i + 1])))          # top
        fs.append(bm.faces.new((vb_l[i], vt_l[i], vt_l[i + 1], vb_l[i + 1])))          # left side
        fs.append(bm.faces.new((vt_r[i], vb_r[i], vb_r[i + 1], vt_r[i + 1])))          # right side
        fs.append(bm.faces.new((vb_r[i], vb_l[i], vb_l[i + 1], vb_r[i + 1])))          # bottom
    fs.append(bm.faces.new((vt_l[0], vb_l[0], vb_r[0], vt_r[0])))
    fs.append(bm.faces.new((vt_r[-1], vb_r[-1], vb_l[-1], vt_l[-1])))
    for f in fs:
        f.material_index = mat
    return fs
