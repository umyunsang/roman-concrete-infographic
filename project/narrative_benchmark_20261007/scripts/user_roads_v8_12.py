"""v8.12: user request — roads around the Colosseum must not be hidden.

- South road: the travertine podium's outer lip lay over the road's upper half (x 550-775pt). Its outer edge is pulled
  in per angle so it stays 4pt clear of the road.
- North-west road (CORE 1 -> 2): about 85pt of it ran behind the Colosseum's tall north-west wall. It is re-laid
  between the Pantheon and the wall top. The Pantheon moves 30pt left and 14pt up to open that corridor (its label
  moves in Figma).
Run: blender -b out/roman_concrete_narrative_v8_11.blend --factory-startup --python scripts/user_roads_v8_12.py -- <test|final> [test_prefix]
"""
import bpy, bmesh, math, json, sys, runpy
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'out/roman_concrete_narrative_v8_11.blend'
OUT = ROOT / 'out/roman_concrete_narrative_v8_12.blend'
argv = sys.argv[sys.argv.index('--') + 1:]
MODE = argv[0]
assert Path(bpy.data.filepath).resolve() == SRC.resolve()
W_PT, H_PT = 1191, 1684
sc = bpy.context.scene; cam = sc.camera; O = bpy.data.objects
report = {}

def to_pt(p):
    v = world_to_camera_view(sc, cam, p); return np.array((v.x * W_PT, (1 - v.y) * H_PT))
frame = [cam.matrix_world @ v for v in cam.data.view_frame(scene=sc)]
origin = cam.matrix_world.translation
def ray(pt):
    u, v = pt[0] / W_PT, 1 - pt[1] / H_PT
    tr, br, bl, tl = frame
    return origin, ((bl + (br - bl) * u + (tl - bl) * v) - origin).normalized()
dg = bpy.context.evaluated_depsgraph_get()
def bvh_of(objs):
    verts, polys = [], []
    for o in objs:
        ev = o.evaluated_get(dg); me = ev.to_mesh(); mw = o.matrix_world; b = len(verts)
        verts += [mw @ v.co for v in me.vertices]; polys += [[b + i for i in p.vertices] for p in me.polygons]
        ev.to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys)
TERRAIN = bvh_of([O['T_land']])
def tz(x, y):
    h = TERRAIN.ray_cast(Vector((x, y, 500)), Vector((0, 0, -1)))[0]; return h.z if h else 0.0
def ground(pt):
    h = TERRAIN.ray_cast(*ray(pt))[0]; assert h is not None, pt; return h
def world_per_pt(p):
    r = cam.matrix_world.col[0].xyz.normalized()
    return 1.0 / np.linalg.norm(to_pt(p + r) - to_pt(p))
def screen_box(o, step=1):
    mw = o.matrix_world; P = np.array([to_pt(mw @ o.data.vertices[i].co) for i in range(0, len(o.data.vertices), step)])
    return [round(float(v), 1) for v in (P[:, 0].min(), P[:, 0].max(), P[:, 1].min(), P[:, 1].max())]
def occluded(road, blockers):
    """road vertices whose camera ray hits a blocker first, as screen points."""
    B = bvh_of(blockers); mw = road.matrix_world; hidden = []
    for v in road.data.vertices:
        p = mw @ v.co; d = p - origin; L = d.length
        if B.ray_cast(origin, d.normalized(), L - 0.05)[0] is not None: hidden.append(to_pt(p))
    return np.array(hidden)

# 1. Pantheon 30pt left / 14pt up (keeps 5pt+ from the CORE 1 milestone, opens a corridor above the wall)
pan = O['R8_pantheon']
before_box = screen_box(pan, 7)
pw = np.array([pan.matrix_world @ v.co for v in pan.data.vertices[::7]])
base = Vector(((pw[:, 0].min() + pw[:, 0].max()) / 2, (pw[:, 1].min() + pw[:, 1].max()) / 2, pw[:, 2].min()))
o_, d_ = ray(to_pt(base) + np.array((-30.0, -14.0))); t = (base.z - o_.z) / d_.z; nb = o_ + d_ * t
delta = nb - base; delta.z = tz(nb.x, nb.y) - tz(base.x, base.y)
pan.matrix_world.translation += delta
bpy.context.view_layer.update()
report['pantheon_box'] = [before_box, screen_box(pan, 7)]

# 2. NW road re-laid along a new screen centreline (vertices keep arc position and lateral offset)
road = O['R_core_road']
if road.data.users > 1: road.data = road.data.copy()
mw = road.matrix_world; inv = mw.inverted()
OLD = np.array([(300, 658), (320, 652), (340, 642.5), (360, 635), (380, 627), (400, 619), (420, 610), (440, 599.5),
                (460, 583), (480, 565), (500, 544), (520, 527.5), (540, 516.5)], float)
NEW = np.array([(300, 658), (320, 651), (340, 630), (360, 605), (380, 582), (400, 565), (420, 556), (440, 554),
                (460, 549), (480, 539), (500, 528), (520, 521), (540, 516.5)], float)
def densify(P, n=400):
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1); s = np.concatenate([[0], np.cumsum(seg)])
    u = np.linspace(0, s[-1], n); return np.stack([np.interp(u, s, P[:, 0]), np.interp(u, s, P[:, 1])], 1), u
def smooth(P, it=3):
    for _ in range(it):   # Chaikin, ends fixed
        Q = [P[0]]
        for a, b in zip(P[:-1], P[1:]): Q += [0.75 * a + 0.25 * b, 0.25 * a + 0.75 * b]
        Q.append(P[-1]); P = np.array(Q)
    return P
Co, so = densify(smooth(OLD)); Cn, sn = densify(smooth(NEW))
def frame_at(C, i):
    a, b = C[max(i - 1, 0)], C[min(i + 1, len(C) - 1)]; t = (b - a) / np.linalg.norm(b - a); return t, np.array((-t[1], t[0]))
moved = 0
for v in road.data.vertices:
    w = mw @ v.co; q = to_pt(w)
    if not (295 < q[0] < 545 and 480 < q[1] < 700): continue
    i = int(np.argmin(np.linalg.norm(Co - q, axis=1)))
    if i in (0, len(Co) - 1): continue
    t0, n0 = frame_at(Co, i); d = q - Co[i]
    lat, lon = float(d @ n0), float(d @ t0)
    if abs(lat) > 40: continue
    j = int(round(so[i] / so[-1] * (len(Cn) - 1)))
    t1, n1 = frame_at(Cn, j); q2 = Cn[j] + n1 * lat + t1 * lon
    h = w.z - tz(w.x, w.y); g = ground(q2)
    v.co = inv @ Vector((g.x, g.y, tz(g.x, g.y) + h)); moved += 1
road.data.update(); bpy.context.view_layer.update()
report['nw_road_vertices_moved'] = moved

# 3. podium outer lip pulled in per angle, 4pt clear of the roads (vertex order per angle: inner, outer top, outer lip)
pod = O['R3_colosseum_podium']
if pod.data.users > 1: pod.data = pod.data.copy()
pm = pod.matrix_world; pinv = pm.inverted()
ROADS = bvh_of([road, O['R_via_appia']])
V = pod.data.vertices; N = len(V) // 3
ri = np.array([(pm @ V[3 * k].co)[:] for k in range(N)]); ro = np.array([(pm @ V[3 * k + 1].co)[:] for k in range(N)])
rl = np.array([(pm @ V[3 * k + 2].co)[:] for k in range(N)])
def clear(x, y):
    p = Vector((x, y, tz(x, y) + 0.05)); hit = ROADS.find_nearest(p)[0]
    if hit is None: return True
    return math.hypot(hit.x - x, hit.y - y) > 4 * world_per_pt(p)
T = np.ones(N)
for k in range(N):
    for t in np.linspace(1.0, 0.45, 56):
        x, y = ri[k, :2] + t * (rl[k, :2] - ri[k, :2])
        if clear(x, y): T[k] = t; break
    else: T[k] = 0.45
Ts = T.copy()
for _ in range(6):   # smooth envelope that never pushes the lip back over a road
    K = np.exp(-0.5 * (np.arange(-6, 7) / 2.5) ** 2); K /= K.sum()
    Ts = np.minimum(T, np.convolve(np.concatenate([Ts[-6:], Ts, Ts[:6]]), K, 'valid'))
for k in range(N):
    if Ts[k] > 0.999: continue
    for idx, src in ((3 * k + 1, ro[k]), (3 * k + 2, rl[k])):
        x, y = ri[k, :2] + Ts[k] * (src[:2] - ri[k, :2])
        hgt = src[2] - tz(src[0], src[1])
        V[idx].co = pinv @ Vector((x, y, tz(x, y) + hgt))
pod.data.update(); bpy.context.view_layer.update()
report['podium_angles_clipped'] = int((Ts < 0.999).sum()); report['podium_t_min'] = round(float(Ts.min()), 3)

# 4. check: no road vertex hidden by the Colosseum, its podium or the Pantheon
hid = occluded(road, [O['COL_ruined'], pod, pan])
report['road_vertices_hidden'] = len(hid)
if len(hid): report['hidden_box'] = [round(float(v)) for v in (hid[:, 0].min(), hid[:, 0].max(), hid[:, 1].min(), hid[:, 1].max())]
P = np.array([to_pt(mw @ v.co) for v in road.data.vertices])
for x0 in range(340, 560, 20):
    s = (P[:, 0] >= x0) & (P[:, 0] < x0 + 20) & (P[:, 1] < 700) & (P[:, 1] > 480)
    if s.sum(): report[f'nw_band_x{x0}'] = [round(float(P[s, 1].min())), round(float(P[s, 1].max()))]

print('REPORT ' + json.dumps(report, ensure_ascii=False))
H = runpy.run_path(str(ROOT / 'scripts/integrate_assets.py'), run_name='helpers')
if MODE == 'test':
    print('RENDER ' + json.dumps(H['render_two_pass'](Path(argv[1]).with_suffix('.png'))))
else:
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT), copy=False)
    r = H['render_two_pass'](ROOT / 'renders/narrative_v8_12_roads.png'); report['render'] = r
    (ROOT / 'out/v8_12-user-roads-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('RENDER ' + json.dumps(r))
