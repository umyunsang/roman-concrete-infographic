"""Import selected Meshy GLBs into a new Roman concrete draft; preserve source scene.

Default operation is a dry run. --save-draft explicitly writes only the new draft.
Run in background Blender after opening canonical roman_concrete_map.blend.
Manifest: {"expected_source_sha256": "...", "text_zones_path": "...",
 "hide_objects": [], "assets":
 [{"id": "modern_building", "path": "model.glb", "bbox": [x0,y0,x1,y1],
   "replace_objects": ["C1_pozzolana_quarry"], "ground_z": 0,
   "rotation_z_degrees": 0, "grayscale": 0.72, "shadow_pass": "map"}]}
An asset may instead use "reuse_object_prefixes": ["D4_"] with no path.
Only render-visible MESH objects from the original source are copied. A hidden
merged fit proxy controls separate new gray groups, preserving original contrast.
No regeneration of terrain, roads, water, trees, camera, or central arena occurs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

PROJECT = Path('/Users/um-yunsang/Documents/로마콘크리트_3D')
SOURCE = PROJECT / 'roman_concrete_map.blend'
DRAFT_ROOT = PROJECT / 'narrative_benchmark_20261007'
FRAME_W, FRAME_H = 1191.0, 1684.0
CORE_NAMES = ['C1_pozzolana_quarry', 'C2_hot_mixing', 'C3_arch_building',
              'C4_crack_repair', 'C5_researchers']
ORIGINAL_D4_SEQUENCE = [f'D4_{part}{i}' for part, count in
                        [('cube', 3), ('crack', 3), ('drop', 3), ('lime', 2), ('arrow', 2)]
                        for i in range(count)]
ALLOWED_HIDE = set(CORE_NAMES + ['L09_portus_mole'] + ORIGINAL_D4_SEQUENCE)
OVERLAY_COLLECTIONS = {'80_SHAPES', '81_NOSHADOW', '85_HEADER'}


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def json_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':')).encode()).hexdigest()


def mesh_fingerprint(mesh):
    h = hashlib.sha256()
    for label, collection, field, width, dtype in [
        ('vertices', mesh.vertices, 'co', 3, np.float32),
        ('edges', mesh.edges, 'vertices', 2, np.int32),
        ('loops', mesh.loops, 'vertex_index', 1, np.int32),
        ('poly_start', mesh.polygons, 'loop_start', 1, np.int32),
        ('poly_total', mesh.polygons, 'loop_total', 1, np.int32),
    ]:
        values = np.empty(len(collection) * width, dtype=dtype)
        collection.foreach_get(field, values)
        h.update(label.encode())
        h.update(str(len(collection)).encode())
        h.update(values.tobytes())
    return h.hexdigest()


def scalar_rna(obj):
    values = {}
    for prop in obj.bl_rna.properties:
        if prop.identifier in {'rna_type', 'name'} or prop.type in {'POINTER', 'COLLECTION'}:
            continue
        try:
            val = getattr(obj, prop.identifier)
            if getattr(prop, 'is_array', False):
                val = list(val)
            if isinstance(val, (str, int, float, bool, list)):
                values[prop.identifier] = val
        except (AttributeError, TypeError, RuntimeError):
            continue
    return values


def source_fingerprints(objects):
    bpy.context.view_layer.update()
    result = {}
    for ob in objects:
        r = {'name': ob.name, 'type': ob.type,
             'matrix_world': [list(row) for row in ob.matrix_world],
             'matrix_basis': [list(row) for row in ob.matrix_basis],
             'parent': ob.parent.name if ob.parent else None,
             'collections': sorted(c.name for c in ob.users_collection),
             'color': list(ob.color), 'hide_render': ob.hide_render,
             'hide_viewport': ob.hide_viewport,
             'modifiers': [scalar_rna(m) for m in ob.modifiers],
             'constraints': [scalar_rna(c) for c in ob.constraints]}
        if ob.type == 'MESH':
            r['mesh_sha256'] = mesh_fingerprint(ob.data)
            r['materials'] = [m.name if m else None for m in ob.data.materials]
        elif ob.type == 'CAMERA':
            r['camera_data'] = scalar_rna(ob.data)
        elif ob.type == 'FONT':
            r['body'] = ob.data.body
        result[ob.name] = r
    return result


def scene_fingerprint(scene):
    return {'camera': scene.camera.name if scene.camera else None,
            'render': {n: getattr(scene.render, n) for n in
                       ['engine', 'resolution_x', 'resolution_y', 'resolution_percentage',
                        'pixel_aspect_x', 'pixel_aspect_y', 'film_transparent', 'use_border']},
            'collections': {c.name: {'hide_render': c.hide_render,
                                    'hide_viewport': c.hide_viewport}
                            for c in bpy.data.collections}}


def project_pts(points, scene=None):
    scene = scene or bpy.context.scene
    bpy.context.view_layer.update()
    cam = scene.camera
    tr, br, bl, tl = [np.array(c) for c in cam.data.view_frame(scene=scene)]
    inv = np.linalg.inv(np.array(cam.matrix_world))
    pc = points @ inv[:3, :3].T + inv[:3, 3]
    if cam.data.type == 'ORTHO':
        x, y = pc[:, 0], pc[:, 1]
    else:
        scale = tr[2] / pc[:, 2]
        x, y = pc[:, 0] * scale, pc[:, 1] * scale
    return np.stack([(x - bl[0]) / (tr[0] - bl[0]) * FRAME_W,
                     (tr[1] - y) / (tr[1] - bl[1]) * FRAME_H], 1)


def pts_to_world(uv, height=0.0, scene=None):
    scene = scene or bpy.context.scene
    bpy.context.view_layer.update()
    cam = scene.camera
    matrix = np.array(cam.matrix_world)
    tr, br, bl, tl = [np.array(c) for c in cam.data.view_frame(scene=scene)]
    uv = np.asarray(uv, dtype=np.float64).reshape(-1, 2)
    top = tl + (tr - tl) * uv[:, 0:1] / FRAME_W
    bot = bl + (br - bl) * uv[:, 0:1] / FRAME_W
    frame = top + (bot - top) * uv[:, 1:2] / FRAME_H
    point = frame @ matrix[:3, :3].T + matrix[:3, 3]
    direction = (np.broadcast_to(matrix[:3, :3] @ np.array([0, 0, -1.0]), point.shape)
                 if cam.data.type == 'ORTHO' else point - matrix[:3, 3])
    return point + direction * ((height - point[:, 2:3]) / direction[:, 2:3])


def world_coords(ob):
    evaluated = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        values = np.empty(len(mesh.vertices) * 3, dtype=np.float64)
        mesh.vertices.foreach_get('co', values)
        matrix = np.array(ob.matrix_world)
        return values.reshape(-1, 3) @ matrix[:3, :3].T + matrix[:3, 3]
    finally:
        evaluated.to_mesh_clear()


def screen_bbox(ob):
    uv = project_pts(world_coords(ob))
    return [float(uv[:, 0].min()), float(uv[:, 1].min()),
            float(uv[:, 0].max()), float(uv[:, 1].max())]


def bbox_overlap(a, b, pad=0.0):
    return (a[0] < b[2] + pad and a[2] > b[0] - pad and
            a[1] < b[3] + pad and a[3] > b[1] - pad)


def fit_projected_bbox(ob, target, ground_z=0.0, rotation_z_degrees=0.0):
    """Uniform fit, bottom-aligned, no terrain or camera changes."""
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (0, 0, math.radians(rotation_z_degrees))
    center = (target[0] + target[2]) / 2
    ob.location = tuple(pts_to_world([[center, target[3]]], ground_z)[0])
    for _ in range(8):
        bpy.context.view_layer.update()
        got = screen_bbox(ob)
        ratio = min((target[2] - target[0]) / (got[2] - got[0]),
                    (target[3] - target[1]) / (got[3] - got[1]))
        ob.scale *= ratio
        bpy.context.view_layer.update()
        got = screen_bbox(ob)
        u, v = (got[0] + got[2]) / 2, got[3]
        shift = pts_to_world([[center, target[3]]], ground_z)[0]
        shift -= pts_to_world([[u, v]], ground_z)[0]
        ob.location.x += float(shift[0])
        ob.location.y += float(shift[1])
    got = screen_bbox(ob)
    eps = 0.5
    if got[0] < target[0] - eps or got[1] < target[1] - eps or got[2] > target[2] + eps or got[3] > target[3] + eps:
        raise RuntimeError(f'{ob.name}: fit exceeded target: {got} vs {target}')
    return got


def get_new_collection(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def import_glb(asset):
    path = Path(asset['path']).expanduser().resolve()
    if not path.is_file() or path.suffix.lower() not in {'.glb', '.gltf'}:
        raise ValueError(f'Local GLB/GLTF required: {path}')
    name = asset.get('object_name', 'NB_' + asset['id'])
    if bpy.data.objects.get(name):
        raise ValueError(f'New object name already exists: {name}')
    prior = set(bpy.data.objects)
    old_materials, old_images = set(bpy.data.materials), set(bpy.data.images)
    bpy.ops.import_scene.gltf(filepath=str(path))
    imported = set(bpy.data.objects) - prior
    meshes = [o for o in imported if o.type == 'MESH']
    if not meshes:
        raise RuntimeError(f'GLB contained no meshes: {path}')
    bpy.context.view_layer.update()
    bm = bmesh.new()
    try:
        for ob in meshes:
            ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
            tmp = ev.to_mesh().copy()
            ev.to_mesh_clear()
            tmp.transform(ob.matrix_world)
            bm.from_mesh(tmp)
            bpy.data.meshes.remove(tmp)
        mesh = bpy.data.meshes.new(name)
        bm.to_mesh(mesh)
    finally:
        bm.free()
    mesh.materials.clear()
    for layer in list(mesh.uv_layers):
        mesh.uv_layers.remove(layer)
    for attr in list(mesh.color_attributes):
        mesh.color_attributes.remove(attr)
    values = np.empty(len(mesh.vertices) * 3, dtype=np.float64)
    mesh.vertices.foreach_get('co', values)
    points = values.reshape(-1, 3)
    minimum, maximum = points.min(0), points.max(0)
    points -= [(minimum[0] + maximum[0]) / 2,
               (minimum[1] + maximum[1]) / 2, minimum[2]]
    mesh.vertices.foreach_set('co', points.ravel())
    mesh.update()
    proportions = asset.get('model_proportions', [1, 1, 1])
    if len(proportions) != 3 or any(float(s) <= 0 for s in proportions):
        raise ValueError('Model proportions require three positive values')
    mesh.transform(Matrix.Diagonal([float(s) for s in proportions] + [1]))
    for ob in imported:
        bpy.data.objects.remove(ob, do_unlink=True)
    for mat in set(bpy.data.materials) - old_materials:
        if mat.users == 0:
            bpy.data.materials.remove(mat)
    for im in set(bpy.data.images) - old_images:
        if im.users == 0:
            bpy.data.images.remove(im)
    ob = bpy.data.objects.new(name, mesh)
    shadow = asset.get('shadow_pass', 'map')
    if shadow not in {'map', 'overlay'}:
        raise ValueError('shadow_pass must be map or overlay')
    collection = '46_NARRATIVE_ASSETS' if shadow == 'map' else '81_NOSHADOW'
    get_new_collection(collection).objects.link(ob)
    gray = float(asset.get('grayscale', 0.72))
    if not 0.0 <= gray <= 1.0:
        raise ValueError('grayscale must be 0 through 1')
    ob.color = (gray, gray, gray, 1.0)
    ob['narrative_meshy_task_id'] = asset.get('source_task_id', '')
    ob['narrative_model_sha256'] = sha256_file(path)
    ob['narrative_source_file'] = str(path)
    return ob


def reuse_source_meshes(asset, source_objects):
    """Copy source geometry by original gray, plus a temporary merged fit proxy."""
    prefixes = asset['reuse_object_prefixes']
    if not isinstance(prefixes, list) or not prefixes or any(p != 'D4_' for p in prefixes):
        raise ValueError('This reuse lane only permits reuse_object_prefixes: ["D4_"]')
    meshes = [ob for ob in source_objects if ob.type == 'MESH'
              and ob.name.startswith(tuple(prefixes)) and not ob.hide_render
              and any(not c.hide_render for c in ob.users_collection)]
    if not meshes:
        raise RuntimeError('No render-visible original source meshes match reuse prefixes')
    root_name = asset.get('object_name', 'NB_' + asset['id'])
    name = root_name + '_FIT_PROXY'
    if bpy.data.objects.get(root_name) or bpy.data.objects.get(name):
        raise ValueError(f'New object name already exists: {name}')
    bpy.context.view_layer.update()
    bm = bmesh.new()
    gray_groups = {}
    try:
        for source_ob in meshes:
            evaluated = source_ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
            temporary = evaluated.to_mesh().copy()
            evaluated.to_mesh_clear()
            temporary.transform(source_ob.matrix_world)
            bm.from_mesh(temporary)
            rgba = tuple(source_ob.color)
            if rgba not in gray_groups:
                gray_groups[rgba] = {'bm': bmesh.new(), 'sources': []}
            gray_groups[rgba]['bm'].from_mesh(temporary)
            gray_groups[rgba]['sources'].append(source_ob.name)
            bpy.data.meshes.remove(temporary)
        mesh = bpy.data.meshes.new(name)
        bm.to_mesh(mesh)
    finally:
        bm.free()
    mesh.materials.clear()
    coords = np.empty(len(mesh.vertices) * 3, dtype=np.float64)
    mesh.vertices.foreach_get('co', coords)
    points = coords.reshape(-1, 3)
    minimum, maximum = points.min(0), points.max(0)
    offset = np.array([(minimum[0] + maximum[0]) / 2,
                       (minimum[1] + maximum[1]) / 2, minimum[2]])
    points -= offset
    mesh.vertices.foreach_set('co', points.ravel())
    mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    shadow = asset.get('shadow_pass', 'overlay')
    if shadow not in {'map', 'overlay'}:
        raise ValueError('shadow_pass must be map or overlay')
    collection = get_new_collection('81_NOSHADOW' if shadow == 'overlay' else '46_NARRATIVE_ASSETS')
    collection.objects.link(ob)
    ob.hide_render = True
    # The dependency graph must update this temporary fit object's matrix.
    # It is never rendered and is removed before the draft is saved.
    ob.hide_viewport = False
    copy_names = []
    for index, (rgba, group) in enumerate(gray_groups.items()):
        group_name = root_name + f'_GRAY{index:02}'
        if bpy.data.objects.get(group_name):
            raise ValueError(f'New copy group name already exists: {group_name}')
        group_mesh = bpy.data.meshes.new(group_name)
        try:
            group['bm'].to_mesh(group_mesh)
        finally:
            group['bm'].free()
        group_mesh.materials.clear()
        group_coords = np.empty(len(group_mesh.vertices) * 3, dtype=np.float64)
        group_mesh.vertices.foreach_get('co', group_coords)
        group_points = group_coords.reshape(-1, 3) - offset
        group_mesh.vertices.foreach_set('co', group_points.ravel())
        group_mesh.update()
        copy = bpy.data.objects.new(group_name, group_mesh)
        collection.objects.link(copy)
        copy.color = rgba
        copy['narrative_reused_source_objects'] = json.dumps(sorted(group['sources']))
        copy_names.append(copy.name)
    ob['narrative_reuse_group_names'] = json.dumps(copy_names)
    ob['narrative_reuse_root_name'] = root_name
    reused = sorted(meshes, key=lambda o: o.name)
    ob['narrative_reused_source_objects'] = json.dumps([o.name for o in reused])
    ob['narrative_meshy_task_id'] = ''
    ob['narrative_model_sha256'] = json_hash([
        {'name': o.name, 'mesh_sha256': mesh_fingerprint(o.data),
         'matrix_world': [list(row) for row in o.matrix_world]} for o in reused])
    ob['narrative_source_file'] = str(SOURCE)
    return ob


def add_reused_lime_inclusions(body, source_objects):
    """Embed copies of existing D2 lime shapes in a Meshy schematic specimen.

    Meshy supplies the solid matrix. These are illustrative, visible inclusions,
    not a scan of a historical specimen. No original mesh is modified.
    """
    source_by_name = {ob.name: ob for ob in source_objects}
    coords = np.array([v.co[:] for v in body.data.vertices])
    low, high = coords.min(0), coords.max(0)
    size = high - low
    tree = BVHTree.FromPolygons([v.co for v in body.data.vertices],
                               [p.vertices[:] for p in body.data.polygons])
    specifications = [('front', .21, .68, .14), ('front', .41, .30, .22),
                      ('front', .73, .54, .10), ('front', .62, .82, .18),
                      ('right', .23, .25, .13), ('right', .71, .67, .19)]
    result = []
    for index, (side, across, height, relative_diameter) in enumerate(specifications):
        diameter = float(min(size) * relative_diameter)
        source = source_by_name[f'D2_lime{index:02}']
        if side == 'front':
            origin = Vector((low[0] + size[0] * across,
                             low[1] - size[1], low[2] + size[2] * height))
            direction = Vector((0, 1, 0))
        else:
            origin = Vector((high[0] + size[0], low[1] + size[1] * across,
                             low[2] + size[2] * height))
            direction = Vector((-1, 0, 0))
        hit, normal, face, distance = tree.ray_cast(origin, direction)
        if hit is None:
            raise RuntimeError(f'Lime inclusion ray missed solid matrix: {side}/{index}')
        if normal.dot(direction) > 0:
            normal.negate()
        evaluated = source.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh().copy()
        evaluated.to_mesh_clear()
        mesh.transform(source.matrix_world)
        values = np.array([v.co[:] for v in mesh.vertices])
        minimum, maximum = values.min(0), values.max(0)
        values = (values - (minimum + maximum) / 2) / max(maximum - minimum)
        mesh.vertices.foreach_set('co', values.ravel())
        mesh.update()
        mesh.materials.clear()
        ob = bpy.data.objects.new(f'{body.name}_LIME{index:02}', mesh)
        body.users_collection[0].objects.link(ob)
        ob.parent = body
        ob.matrix_parent_inverse = Matrix.Identity(4)
        ob.location = hit - normal * (diameter * .18)
        ob.scale = (diameter,) * 3
        ob.color = (1, 1, 1, 1)
        ob['narrative_reused_source_object'] = source.name
        ob['narrative_schematic_inclusion'] = True
        result.append(ob)
    bpy.context.view_layer.update()
    return result


def finalize_reuse_groups(proxy):
    """Apply fitted proxy transform to new gray-group copies, then remove proxy."""
    root = bpy.data.objects.new(proxy['narrative_reuse_root_name'], None)
    root.empty_display_type = 'PLAIN_AXES'
    proxy.users_collection[0].objects.link(root)
    root.matrix_world = proxy.matrix_world.copy()
    group_names = json.loads(proxy['narrative_reuse_group_names'])
    for name in group_names:
        copy = bpy.data.objects[name]
        copy.parent = root
        copy.matrix_parent_inverse = Matrix.Identity(4)
        copy.matrix_basis = Matrix.Identity(4)
    for key in ['narrative_reuse_group_names', 'narrative_reused_source_objects',
                'narrative_meshy_task_id', 'narrative_model_sha256', 'narrative_source_file']:
        root[key] = proxy[key]
    proxy_mesh = proxy.data
    bpy.data.objects.remove(proxy, do_unlink=True)
    bpy.data.meshes.remove(proxy_mesh)
    bpy.context.view_layer.update()
    return root


def assert_source_preserved(before, after, allowed_visibility, original_scene):
    changed = []
    for name, expected in before.items():
        actual = after.get(name)
        if actual is None:
            changed.append(name + ': missing')
            continue
        expected, actual = dict(expected), dict(actual)
        if name in allowed_visibility:
            for key in ['hide_render', 'hide_viewport']:
                expected.pop(key, None)
                actual.pop(key, None)
        if expected != actual:
            changed.append(name)
    now_scene = scene_fingerprint(bpy.context.scene)
    # New collections are permitted; all original collection flags remain exact.
    for name, expected in original_scene['collections'].items():
        if now_scene['collections'].get(name) != expected:
            changed.append('collection:' + name)
    if now_scene['camera'] != original_scene['camera'] or now_scene['render'] != original_scene['render']:
        changed.append('camera/render settings')
    if changed:
        raise RuntimeError('Source preservation check failed: ' + ', '.join(changed))


def render_two_pass(output, resolution_percentage=48):
    """Render map plus overlay without changing persistent source settings."""
    scene, render = bpy.context.scene, bpy.context.scene.render
    shading = scene.display.shading
    saved_collections = {c.name: c.hide_render for c in bpy.data.collections}
    saved_render = {n: getattr(render, n) for n in
                    ['filepath', 'use_border', 'resolution_percentage', 'film_transparent']}
    saved_shadows = shading.show_shadows
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    map_png = output.with_name(output.stem + '_map_pass.png')
    overlay_png = output.with_name(output.stem + '_overlay_pass.png')
    try:
        render.use_border = False
        render.resolution_percentage = resolution_percentage
        for c in bpy.data.collections:
            c.hide_render = saved_collections[c.name] or c.name in OVERLAY_COLLECTIONS
        render.film_transparent = False
        shading.show_shadows = True
        render.filepath = str(map_png)
        bpy.ops.render.render(write_still=True)
        for c in bpy.data.collections:
            c.hide_render = saved_collections[c.name] or c.name not in OVERLAY_COLLECTIONS | {'Collection'}
        render.film_transparent = True
        shading.show_shadows = False
        render.filepath = str(overlay_png)
        bpy.ops.render.render(write_still=True)
    finally:
        for c in bpy.data.collections:
            c.hide_render = saved_collections[c.name]
        for name, value in saved_render.items():
            setattr(render, name, value)
        shading.show_shadows = saved_shadows
    return {'map_pass': str(map_png), 'overlay_pass': str(overlay_png),
            'compose_note': 'Alpha-composite these passes, then current Figma RGBA text overlay.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest')
    parser.add_argument('--output', default=str(DRAFT_ROOT / 'out/roman_concrete_narrative.blend'))
    parser.add_argument('--report', default=str(DRAFT_ROOT / 'out/integration-report.json'))
    parser.add_argument('--audit-only', action='store_true')
    parser.add_argument('--save-draft', action='store_true')
    parser.add_argument('--render-passes')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    if Path(bpy.data.filepath).resolve() != SOURCE.resolve():
        raise RuntimeError('Open canonical main source, not an unconfirmed A/B candidate.')
    output = Path(args.output).resolve()
    if not output.is_relative_to(DRAFT_ROOT.resolve()) or output == SOURCE.resolve():
        raise RuntimeError('Draft output must remain under narrative_benchmark_20261007.')
    manifest = json.loads(Path(args.manifest).read_text()) if args.manifest else {'assets': []}
    source_hash = sha256_file(SOURCE)
    if manifest.get('expected_source_sha256', source_hash) != source_hash:
        raise RuntimeError('Canonical source changed; refresh approval/manifest against current source.')
    source_objects = list(bpy.data.objects)
    before, scene_before = source_fingerprints(source_objects), scene_fingerprint(bpy.context.scene)
    site_names = ['L09_portus_lighthouse', 'L09_portus_mole', 'L12_harbor_pilae',
                  'L11_privernum_wall', 'L08_pompeii_site', 'S_lab_island', 'COL_ruined']
    anchors = {n: screen_bbox(bpy.data.objects[n]) for n in CORE_NAMES + site_names
               if bpy.data.objects.get(n) and bpy.data.objects[n].type == 'MESH'}
    anchor_world = {}
    for name in anchors:
        ob = bpy.data.objects[name]
        coords = world_coords(ob)
        anchor_world[name] = {'world_min': coords.min(0).tolist(),
                              'world_max': coords.max(0).tolist(),
                              'location': list(ob.location),
                              'rotation_euler_degrees': [math.degrees(x) for x in ob.rotation_euler]}
    zones_path = Path(manifest.get('text_zones_path', PROJECT / 'loop/figma_texts.json'))
    zones = json.loads(zones_path.read_text())
    report = {'source': str(SOURCE), 'source_sha256': source_hash,
              'source_snapshot_sha256': json_hash(before), 'anchors': anchors,
              'anchor_world': anchor_world,
              'assets': [], 'dry_run': not args.save_draft, 'audit_only': args.audit_only}
    allowed_visibility = set()
    if not args.audit_only:
        for asset in manifest.get('assets', []):
            replacements = set(asset.get('replace_objects', []))
            if not replacements <= ALLOWED_HIDE or not replacements <= set(before):
                raise RuntimeError('Only named CORE scenes, harbor mole, or superseded D4 sequence may be hidden.')
            if asset.get('reuse_object_prefixes'):
                if asset.get('path'):
                    raise ValueError('Specify a GLB path or reuse_object_prefixes, never both')
                ob = reuse_source_meshes(asset, source_objects)
            else:
                ob = import_glb(asset)
            got = fit_projected_bbox(ob, asset['bbox'], asset.get('ground_z', 0.0),
                                     asset.get('rotation_z_degrees', 0.0))
            inclusions = []
            if asset.get('reuse_lime_inclusions'):
                if asset.get('reuse_object_prefixes'):
                    raise ValueError('Lime inclusions require a Meshy solid matrix')
                inclusions = add_reused_lime_inclusions(ob, source_objects)
                boxes = [got] + [screen_bbox(o) for o in inclusions]
                got = [min(b[0] for b in boxes), min(b[1] for b in boxes),
                       max(b[2] for b in boxes), max(b[3] for b in boxes)]
                target = asset['bbox']
                if got[0] < target[0]-.5 or got[1] < target[1]-.5 or got[2] > target[2]+.5 or got[3] > target[3]+.5:
                    raise RuntimeError('Illustrative lime inclusions exceed model target')
            if min(got[:2]) < 8 or got[2] > FRAME_W - 8 or got[3] > FRAME_H - 8:
                raise RuntimeError(f'{ob.name}: outside safe page bounds')
            collisions = [z['id'] for z in zones if bbox_overlap(got, z['b'], 2.0)]
            if collisions:
                raise RuntimeError(f'{ob.name}: intersects text zones {collisions}')
            if 'COL_ruined' in anchors and bbox_overlap(got, anchors['COL_ruined'], 2.0):
                raise RuntimeError(f'{ob.name}: projected overlap with protected central Colosseum')
            ob.data.calc_loop_triangles()
            triangles = len(ob.data.loop_triangles)
            for inclusion in inclusions:
                inclusion.data.calc_loop_triangles()
                triangles += len(inclusion.data.loop_triangles)
            if triangles > 500_000:
                raise RuntimeError(f'{ob.name}: {triangles} triangles; reduce imported model before integration')
            for name in replacements:
                bpy.data.objects[name].hide_render = True
                bpy.data.objects[name].hide_viewport = True
            allowed_visibility |= replacements
            final_ob = finalize_reuse_groups(ob) if ob.get('narrative_reuse_group_names') else ob
            copy_names = json.loads(final_ob.get('narrative_reuse_group_names', '[]'))
            if copy_names:
                copy_bboxes, copy_triangles = [], 0
                for name in copy_names:
                    copy = bpy.data.objects[name]
                    copy.data.calc_loop_triangles()
                    copy_triangles += len(copy.data.loop_triangles)
                    copy_bboxes.append(screen_bbox(copy))
                copy_union = [min(b[0] for b in copy_bboxes), min(b[1] for b in copy_bboxes),
                              max(b[2] for b in copy_bboxes), max(b[3] for b in copy_bboxes)]
                if max(abs(a - b) for a, b in zip(copy_union, got)) > 0.25:
                    raise RuntimeError('Copied gray groups do not match fitted proxy bbox')
                if copy_triangles != triangles:
                    raise RuntimeError('Visible copied group triangles differ from proxy')
                triangles, got = copy_triangles, copy_union
            report['assets'].append({'id': asset['id'], 'object': final_ob.name,
                                     'projected_bbox': got, 'triangles': triangles,
                                     'hidden_originals': sorted(replacements),
                                     'source_model_sha256': final_ob['narrative_model_sha256'],
                                     'reused_source_objects': json.loads(final_ob.get('narrative_reused_source_objects', '[]')),
                                     'visible_gray_copy_groups': copy_names,
                                     'illustrative_lime_inclusions': [
                                         {'object': o.name, 'reused_from': o['narrative_reused_source_object'],
                                          'projected_bbox': screen_bbox(o)} for o in inclusions],
                                     'temporary_fit_proxy_removed': bool(copy_names)})
        hide_only = set(manifest.get('hide_objects', []))
        if not hide_only <= ALLOWED_HIDE or not hide_only <= set(before):
            raise RuntimeError('hide_objects may only name CORE scenes, harbor mole, or superseded D4 sequence.')
        for name in hide_only:
            bpy.data.objects[name].hide_render = True
            bpy.data.objects[name].hide_viewport = True
        allowed_visibility |= hide_only
    after = source_fingerprints(source_objects)
    assert_source_preserved(before, after, allowed_visibility, scene_before)
    if args.render_passes and not args.audit_only:
        passes_path = Path(args.render_passes).resolve()
        if not passes_path.is_relative_to(DRAFT_ROOT.resolve()):
            raise RuntimeError('Render output must remain under draft folder.')
        report['render_passes'] = render_two_pass(passes_path)
        assert_source_preserved(before, source_fingerprints(source_objects), allowed_visibility, scene_before)
    if args.save_draft and not args.audit_only:
        if output.exists():
            raise RuntimeError('Draft output already exists; use a new versioned filename.')
        output.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(output), check_existing=False)
        report['saved_draft'] = str(output)
    if sha256_file(SOURCE) != source_hash:
        raise RuntimeError('Canonical source bytes changed during integration')
    report['source_preserved'] = True
    report['original_geometry_transforms_preserved'] = True
    report['allowed_visibility_changes'] = sorted(allowed_visibility)
    report['source_object_count'] = len(source_objects)
    report['source_object_names'] = sorted(before)
    report['saved_source_snapshot_sha256'] = json_hash(source_fingerprints(source_objects))
    report['saved_scene_fingerprint'] = scene_fingerprint(bpy.context.scene)
    report_path = Path(args.report).resolve()
    if not report_path.is_relative_to(DRAFT_ROOT.resolve()):
        raise RuntimeError('Report output must remain under draft folder.')
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print('NARRATIVE_INTEGRATION', json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
