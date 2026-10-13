"""prep_figures.py - build the two worker figure meshes for WB step.py from the Meshy GLBs (run once, offline).
Blender -b --factory-startup --python prep_figures.py -- <meshy_dir> <assets_dir> [preview_prefix]
Output npz (per figure): V float32 (n,3) metres-free model units, feet at z=0, facing -Y; F int32 (m,3); M int8 (m,)
classes 0 skin, 1 tunic, 2 cloth, 3 hair, 4 jar (pourer only); plus landmark arrays."""
import bpy, bmesh, sys, json, math
import numpy as np
from mathutils import Vector, Matrix
from mathutils.kdtree import KDTree
args = sys.argv[sys.argv.index('--') + 1:]
MD, AD = args[0], args[1]
PREV = args[2] if len(args) > 2 else None
JAR_TILT_DEG = -32.0      # target jar axis angle to horizontal (mouth below the base)
JAR_SCALE = 1.15


def load(glb, cls_path, drop=()):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=glb)
    o = [o for o in bpy.data.objects if o.type == 'MESH'][0]
    me = o.data
    cls = np.load(cls_path).astype(np.int32)
    me.polygons.foreach_set('material_index', np.clip(cls, 0, 31))
    me.update()
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    if drop:
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index in drop], context='FACES')
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    bm.to_mesh(me); bm.free()
    for uv in list(me.uv_layers): me.uv_layers.remove(uv)
    return o


def arrays(o):
    me = o.data
    V = np.empty(len(me.vertices) * 3, np.float64); me.vertices.foreach_get('co', V); V = V.reshape(-1, 3)
    me.calc_loop_triangles()
    F = np.empty(len(me.loop_triangles) * 3, np.int32); me.loop_triangles.foreach_get('vertices', F); F = F.reshape(-1, 3)
    M = np.empty(len(me.loop_triangles), np.int32); me.loop_triangles.foreach_get('material_index', M)
    return V, F, M.astype(np.int8)


def set_verts(o, V):
    o.data.vertices.foreach_set('co', V.astype(np.float32).ravel()); o.data.update()


def decimate(o, faces):
    n = len(o.data.polygons)
    if n <= faces: return
    m = o.modifiers.new('dec', 'DECIMATE'); m.ratio = faces / n
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.modifier_apply(modifier='dec')


def rot(axis, ang):
    return np.array(Matrix.Rotation(ang, 3, Vector(axis)))


report = {}
# ---------------------------------------------------------------- pourer
o = load(f'{MD}/pourer/pourer.glb', f'{MD}/pourer/cls.npy')
me = o.data
V = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', V); V = V.reshape(-1, 3)
PM = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', PM)
vcls = np.full(len(V), -1)
jarv = np.zeros(len(V), bool); armv = np.zeros(len(V), bool); bodyv = np.zeros(len(V), bool)
for p, m in zip(me.polygons, PM):
    vs = list(p.vertices)
    if m == 4: jarv[vs] = True
    elif m == 0: armv[vs] = True
    else: bodyv[vs] = True
armv &= ~jarv; bodyv &= ~jarv
J = V[jarv]
c = J.mean(0)
# jar axis by PCA, oriented toward the mouth (-y)
w_, U = np.linalg.eigh(np.cov((J - c).T)); a = U[:, -1]
if a[1] > 0: a = -a
tilt0 = math.degrees(math.asin(a[2]))
r_ax = np.cross(a, (0, 0, 1)); r_ax /= np.linalg.norm(r_ax)
phi = math.radians(JAR_TILT_DEG - tilt0)            # rotate the axis from tilt0 to target about r_ax
R = rot(r_ax, -phi)
a_new = R @ a
if a_new[2] > a[2]: R = rot(r_ax, phi); a_new = R @ a
def T(P, shift):
    return (P - c) @ (R.T * JAR_SCALE) + c + shift
# push the jar forward (along -y facing) until it clears the torso (body verts in front band)
kd = KDTree(int(bodyv.sum()))
for i, p in enumerate(V[bodyv]): kd.insert(p, i)
kd.balance()
shift = np.zeros(3)
for k in range(60):
    Jn = T(J, shift)
    dmin = min(kd.find(p)[2] for p in Jn[::7])
    if dmin >= 0.02: break
    shift += np.array((0, -0.01, 0))
# hands / forearms follow (linear blend), weight by distance to the ORIGINAL jar surface
kdj = KDTree(len(J))
for i, p in enumerate(J): kdj.insert(p, i)
kdj.balance()
Vn = V.copy()
Vn[jarv] = T(V[jarv], shift)
ai = np.nonzero(armv)[0]
for i in ai:
    d = kdj.find(V[i])[2]
    if d < 0.16 and V[i][1] < 0.12:
        t = min(1.0, max(0.0, (0.16 - d) / 0.14)); w = t * t * (3 - 2 * t)
        Vn[i] = V[i] + w * (T(V[i:i + 1], shift)[0] - V[i])
set_verts(o, Vn)
decimate(o, 24000)
V2, F2, M2 = arrays(o)
z0 = V2[:, 2].min(); feet = V2[V2[:, 2] < z0 + 0.06]
off = np.array((feet[:, 0].mean(), feet[:, 1].mean(), z0))
V2 -= off
# landmarks: jar mouth = jar vertices with the largest projection on the new axis
Jv = V2[np.unique(F2[M2 == 4])]
proj = (Jv - Jv.mean(0)) @ a_new
mouth = Jv[proj > proj.max() - 0.03].mean(0)
report['pourer'] = {'tilt0_deg': tilt0, 'tilt_new_deg': math.degrees(math.asin(a_new[2])), 'shift': shift.tolist(),
                    'height': float(V2[:, 2].max()), 'faces': int(len(F2)), 'mouth': mouth.tolist(), 'axis': a_new.tolist()}
np.savez_compressed(f'{AD}/fig_pourer.npz', V=V2.astype(np.float32), F=F2, M=M2, mouth=mouth, axis=a_new)
if PREV:
    sc = bpy.context.scene
    cols = [(0.58, 0.33, 0.19), (0.33, 0.29, 0.20), (0.37, 0.20, 0.13), (0.05, 0.04, 0.03), (0.0, 0.3, 0.8)]
    o.data.materials.clear()
    for i, cc in enumerate(cols):
        mm = bpy.data.materials.new(f'c{i}'); mm.diffuse_color = (*cc, 1); o.data.materials.append(mm)
    sc.render.engine = 'BLENDER_WORKBENCH'; sc.display.shading.light = 'STUDIO'; sc.display.shading.color_type = 'MATERIAL'
    sc.render.resolution_x = 400; sc.render.resolution_y = 500
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = 2.1
    for name, dd in [('nx', (-1, 0, 0)), ('ny', (0, -1, 0)), ('diag', (0.7, -0.7, 0.55)), ('diag2', (-0.7, -0.7, 0.55))]:
        v = Vector(dd).normalized(); cam.location = v * 5 + Vector((0, 0, 0.8))
        cam.rotation_euler = (-v).to_track_quat('-Z', 'Y').to_euler()
        sc.render.filepath = PREV + f'_pourer_{name}.png'; bpy.ops.render.render(write_still=True)
print('PREP', json.dumps(report))
