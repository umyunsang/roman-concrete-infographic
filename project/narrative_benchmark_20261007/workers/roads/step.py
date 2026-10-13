"""Road colouring step: Roman basalt paving (selce) + light limestone kerbs (umbones / crepidines).

Run: Blender -b <in.blend> --factory-startup --python step.py -- <out.blend> [test_prefix]
  - opens any input blend, applies only this step's material changes, saves to <out.blend>
  - with test_prefix: also renders the two passes (<prefix>_map_pass.png, <prefix>_overlay_pass.png) and writes
    <prefix>_samples.json (screen points of visible paver / kerb / landing / bridge / milestone-plate faces) for
    measure.py.
Idempotent: materials are found-or-created by name and every target mesh gets the same two slots and the same
per-face indices on every run.

Split rule (works on v8_11 and on any re-laid stretch built from the same parts):
  each road mesh is many loose parts. A part with fewer than 40 faces is paving (paver boxes have 5 faces, cut
  pieces 1-4, the thin bed strips under the paving near the landings 4-5); a part with 40 or more faces is a kerb
  ribbon (every kerb ribbon in v8_11 has 222-448 faces, except two 40/45-face kerb ends of the Via Ostiensis at the
  harbour crossing, which is why the bound is "< 40" and not "<= 40").
"""
import bpy, bmesh, sys, json, runpy, math
from pathlib import Path
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

HERE = Path(__file__).resolve().parent
ROOT = next((p for p in [HERE, *HERE.parents] if (p / 'scripts/integrate_assets.py').exists()), HERE.parents[1])   # nb_work
PROTECTED = [ROOT / 'out/roman_concrete_narrative_v8_11.blend']
W_PT, H_PT = 1191, 1684

ROADS = ['R_core_road', 'R_via_appia', 'R_via_ostiensis']
LANDINGS = ['R1_road_landing1', 'R1_road_landing5']      # landing discs at the two dead ends -> paving
BEDS = ['R4_bridge_west_bed', 'R1_road5_bed']           # flat fills standing in for removed pavers -> paving
BRIDGES = ['B_pons1', 'B_pons2']                         # deck top -> paving, masonry -> limestone
PARAPETS = ['B_pons1_parapet0', 'B_pons1_parapet1', 'B_pons2_parapet0', 'B_pons2_parapet1']   # -> limestone
KERB_MIN_FACES = 40

MAT_PAVE = 'RC.road.selce_basalt'
MAT_KERB = 'RC.road.umbo_limestone'
# Material (diffuse) colours, sRGB hex. Chosen from the measured render response of this scene's Workbench studio
# light (see report.json "calibration"): paver tops render ~L* 67 (Oklch C 0.011), kerb tops ~L* 79 (C 0.029).
PAVE_HEX = '#A9A69F'
KERB_HEX = '#C7BEAA'


def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_lin(h):
    return tuple(srgb_to_lin(int(h[i:i + 2], 16) / 255) for i in (1, 3, 5))


def need(name):
    o = bpy.data.objects.get(name)
    if o is None:
        raise RuntimeError(f'roads step: object {name!r} not found in {bpy.data.filepath}')
    if o.type != 'MESH':
        raise RuntimeError(f'roads step: object {name!r} is {o.type}, expected MESH')
    return o


def get_material(name, hex_, template):
    m = bpy.data.materials.get(name)
    if m is None:
        m = template.copy() if template else bpy.data.materials.new(name)
        m.name = name
    lin = hex_lin(hex_)
    m.diffuse_color = (*lin, 1.0)
    if m.use_nodes and m.node_tree:
        for n in m.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED':
                n.inputs['Base Color'].default_value = (*lin, 1.0)
    return m


def own_mesh(o):
    if o.data.users > 1:
        o.data = o.data.copy()
    return o.data


def islands(me):
    bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    seen = set(); out = []
    for f in bm.faces:
        if f.index in seen: continue
        st = [f]; seen.add(f.index); fs = []
        while st:
            a = st.pop(); fs.append(a.index)
            for e in a.edges:
                for g in e.link_faces:
                    if g.index not in seen: seen.add(g.index); st.append(g)
        out.append(sorted(fs))
    bm.free()
    return out


def set_slots(o, idx, pave, kerb):
    me = own_mesh(o)
    for s in o.material_slots:
        if s.link == 'OBJECT':
            raise RuntimeError(f'roads step: {o.name} has an object-linked material slot; refusing to guess')
    me.materials.clear(); me.materials.append(pave); me.materials.append(kerb)
    assert len(idx) == len(me.polygons)
    me.polygons.foreach_set('material_index', np.asarray(idx, dtype=np.int32))
    me.update()


def classify_road(o):
    me = o.data; idx = np.zeros(len(me.polygons), np.int32); n_pave = n_kerb = 0; kerb_sizes = []
    for fs in islands(me):
        if len(fs) >= KERB_MIN_FACES:
            idx[fs] = 1; n_kerb += 1; kerb_sizes.append(len(fs))
        else:
            n_pave += 1
    return idx, {'paving_parts': n_pave, 'kerb_parts': n_kerb, 'kerb_part_faces': sorted(kerb_sizes),
                 'paving_faces': int((idx == 0).sum()), 'kerb_faces': int((idx == 1).sum())}


def bridge_deck_faces(o):
    """deck = the loose part that spans the whole bridge (largest horizontal extent); its upward faces are the roadway."""
    me = o.data; mw = o.matrix_world; R = mw.to_3x3()
    W = np.array([(mw @ v.co)[:] for v in me.vertices])
    best = None
    for fs in islands(me):
        vs = sorted({vi for f in fs for vi in me.polygons[f].vertices}); e = W[vs].max(0) - W[vs].min(0)
        if best is None or max(e[0], e[1]) > best[0]: best = (max(e[0], e[1]), fs)
    return [f for f in best[1] if (R @ me.polygons[f].normal).normalized().z > 0.5]


def apply():
    for n in ROADS + LANDINGS + BEDS + BRIDGES + PARAPETS:
        need(n)
    template = need('R_core_road').material_slots[0].material if need('R_core_road').material_slots else None
    if template is not None and template.name in (MAT_PAVE, MAT_KERB):
        template = bpy.data.materials.get('RC.v12.base_road_foundation')
    pave = get_material(MAT_PAVE, PAVE_HEX, template)
    kerb = get_material(MAT_KERB, KERB_HEX, template)
    rep = {'materials': {MAT_PAVE: PAVE_HEX, MAT_KERB: KERB_HEX}, 'objects': {}}
    for n in ROADS:
        o = need(n); idx, info = classify_road(o); set_slots(o, idx, pave, kerb); rep['objects'][n] = info
    for n in LANDINGS + BEDS:
        o = need(n); set_slots(o, np.zeros(len(o.data.polygons), np.int32), pave, kerb)
        rep['objects'][n] = {'all': MAT_PAVE, 'faces': len(o.data.polygons)}
    for n in BRIDGES:
        o = need(n); deck = bridge_deck_faces(o); idx = np.ones(len(o.data.polygons), np.int32); idx[deck] = 0
        set_slots(o, idx, pave, kerb); rep['objects'][n] = {'deck_top_faces_paving': len(deck), 'masonry_faces_limestone': int(idx.sum())}
    for n in PARAPETS:
        o = need(n); set_slots(o, np.ones(len(o.data.polygons), np.int32), pave, kerb)
        rep['objects'][n] = {'all': MAT_KERB, 'faces': len(o.data.polygons)}
    left = [o.name for o in bpy.data.objects if o.name in ROADS + LANDINGS + BEDS + BRIDGES + PARAPETS
            and any(s.material and s.material.name == 'RC.v12.base_road_foundation' for s in o.material_slots)]
    if left:
        raise RuntimeError(f'roads step: still on the old road material: {left}')
    rep['old_material_still_used_by'] = sorted(o.name for o in bpy.data.objects
                                               if any(s.material and s.material.name == 'RC.v12.base_road_foundation' for s in o.material_slots))
    return rep


# ---------------------------------------------------------------- verification samples (test mode only)
def export_samples(path):
    sc = bpy.context.scene; cam = sc.camera; dg = bpy.context.evaluated_depsgraph_get()
    ortho = cam.data.type == 'ORTHO'; cz = cam.matrix_world.col[2].xyz.normalized(); co = cam.matrix_world.translation

    def to_pt(p):
        v = world_to_camera_view(sc, cam, p); return (v.x * W_PT, (1 - v.y) * H_PT)

    def visible(o, p):
        if ortho:
            orig = p + cz * 1000.0; d = -cz; L = 1000.0
        else:
            d = p - co; L = d.length; d = d.normalized(); orig = co
        hit, loc, nor, fi, obj, _ = sc.ray_cast(dg, orig, d)
        return hit and obj is not None and obj.original == o and (loc - orig).length > L - 0.05

    out = {}
    def add(cat, o, p, extra=None):
        if visible(o, p):
            x, y = to_pt(p); out.setdefault(cat, []).append([round(x, 2), round(y, 2), o.name] + (extra or []))

    def face_points(o, f, inner=(0.0,)):
        mw = o.matrix_world; R = mw.to_3x3(); nrm = (R @ f.normal).normalized()
        c = mw @ f.center; pts = []
        for t in inner:
            if t == 0: pts.append(c)
            else:
                for vi in f.vertices: pts.append(c + ((mw @ o.data.vertices[vi].co) - c) * t)
        lift = Vector((0, 0, 0.003)) if abs(nrm.z) > 0.7 else nrm * 0.003   # some kerb ribbons have flipped normals
        return [p + lift for p in pts], nrm

    for n in ROADS:
        o = need(n); me = o.data; mw = o.matrix_world; R = mw.to_3x3()
        for k, fs in enumerate(islands(me)):
            if len(fs) >= KERB_MIN_FACES:
                for f in fs:
                    P = me.polygons[f]
                    if abs((R @ P.normal).normalized().z) > 0.7:
                        pts, _ = face_points(o, P); add('kerb', o, pts[0], [k])
            else:
                top = max(fs, key=lambda f: abs((R @ me.polygons[f].normal).normalized().z))
                P = me.polygons[top]
                if abs((R @ P.normal).normalized().z) > 0.7 and P.area > 0.05:
                    pts, _ = face_points(o, P); add('paver', o, pts[0], [k, len(fs)])
    for n in LANDINGS + BEDS:
        o = need(n)
        for P in o.data.polygons:
            pts, nrm = face_points(o, P, (0.0, 0.35, 0.7))
            if abs(nrm.z) > 0.7:
                for p in pts: add('landing' if n in LANDINGS else 'bed', o, p)
    for n in BRIDGES:
        o = need(n); deck = set(bridge_deck_faces(o))
        for P in o.data.polygons:
            pts, nrm = face_points(o, P, (0.0, 0.5))
            for p in pts: add('bridge_deck' if P.index in deck else 'bridge_masonry', o, p)
    for n in PARAPETS:
        o = need(n)
        for P in o.data.polygons:
            pts, nrm = face_points(o, P, (0.0, 0.5))
            for p in pts: add('parapet', o, p)
    for o in bpy.data.objects:
        if o.type != 'MESH' or not o.name.startswith('MS'): continue
        slots = [s.material.name if s.material else '' for s in o.material_slots]
        if 'RC.v12_1.direction_arrow' not in slots: continue
        mi = slots.index('RC.v12_1.direction_arrow'); mw = o.matrix_world; R = mw.to_3x3()
        for P in o.data.polygons:
            if P.material_index != mi: continue
            c = mw @ P.center; nrm = (R @ P.normal).normalized()
            view = (c - co).normalized() if not ortho else -cz
            if nrm.dot(view) < -0.2: add('plate', o, c + nrm * 0.003)
    Path(path).write_text(json.dumps(out))
    return {k: len(v) for k, v in out.items()}


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    if not argv:
        raise SystemExit('usage: blender -b in.blend --factory-startup --python step.py -- out.blend [test_prefix]')
    out = Path(argv[0]).resolve(); src = Path(bpy.data.filepath).resolve()
    if out == src or any(out == p.resolve() for p in PROTECTED):
        raise SystemExit(f'roads step: refusing to overwrite {out}')
    rep = apply()
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(out), copy=True)
    rep['input'] = str(src); rep['output'] = str(out)
    if len(argv) > 1:
        prefix = Path(argv[1]).resolve()
        H = runpy.run_path(str(ROOT / 'scripts/integrate_assets.py'), run_name='helpers')
        rep['render'] = H['render_two_pass'](prefix.with_suffix('.png'))
        rep['samples'] = export_samples(prefix.parent / (prefix.name + '_samples.json'))
    print('ROADS_STEP ' + json.dumps(rep, ensure_ascii=False))


if __name__ == '__main__':
    main()
