"""Root-owned, scoped v5 -> v6 composition edit. Never touches the source map."""
import json, runpy, hashlib
from pathlib import Path
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
P = json.loads((ROOT / 'copy/composition_v10.json').read_text())
h = runpy.run_path(str(ROOT / 'scripts/integrate_assets.py'), run_name='helpers')
source = (ROOT / P['sourceScene']).resolve()
output = (ROOT / P['outputScene']).resolve()
assert Path(bpy.data.filepath).resolve() == source
source_hash = h['sha256_file'](source)
original_hash = h['sha256_file'](h['SOURCE'])
states = {o.name: o.hide_viewport for o in bpy.data.objects}

def snap():
    result = h['source_fingerprints'](list(bpy.data.objects))
    for name, item in result.items():
        item['hide_viewport'] = states[name]
        if 'camera_data' in item:
            item['camera_data'].pop('session_uid', None)
    return result

for ob in bpy.data.objects:
    ob.hide_viewport = False
bpy.context.view_layer.update()
before = snap()
scene_before = h['scene_fingerprint'](bpy.context.scene)
report = {'input': str(source), 'output': str(output), 'input_sha256': source_hash,
          'original_source_sha256': original_hash, 'operations': [], 'before': before}

def mesh_children(ob):
    return ([ob] if ob.type == 'MESH' else []) + [c for c in ob.children_recursive if c.type == 'MESH']

def group_points(ob):
    return np.concatenate([h['world_coords'](c) for c in mesh_children(ob)])

def box(ob):
    uv = h['project_pts'](group_points(ob))
    return [float(uv[:,0].min()), float(uv[:,1].min()), float(uv[:,0].max()), float(uv[:,1].max())]

def translate_screen(ob, du, dv):
    origin = np.array(ob.matrix_world.translation)
    uv = h['project_pts'](origin.reshape(1,3))[0]
    delta = h['pts_to_world']([uv + [du,dv]], origin[2])[0] - origin
    # XY translation preserves the object's height above the map.
    ob.location.x += float(delta[0]); ob.location.y += float(delta[1])
    bpy.context.view_layer.update()

def translate_overlay(ob, du, dv):
    """Move baked overlay geometry in the camera plane, retaining its depth and pixel size."""
    scene = bpy.context.scene; cam = scene.camera
    pts = group_points(ob)
    inverse = np.linalg.inv(np.array(cam.matrix_world))
    view = pts @ inverse[:3,:3].T + inverse[:3,3]
    tr,br,bl,tl = [np.array(c) for c in cam.data.view_frame(scene=scene)]
    ratio = float(view[:,2].mean()/tr[2]) if cam.data.type!='ORTHO' else 1.
    delta_cam = np.array([du/1191*(tr[0]-bl[0])*ratio,
                          -dv/1684*(tr[1]-bl[1])*ratio,0.])
    ob.location += Vector(np.array(cam.matrix_world)[:3,:3] @ delta_cam)
    bpy.context.view_layer.update()

terrain = bpy.data.objects['T_land']
ev = terrain.evaluated_get(bpy.context.evaluated_depsgraph_get())
tmp = ev.to_mesh()
terrain_bvh = BVHTree.FromPolygons([terrain.matrix_world @ v.co for v in tmp.vertices],
                                  [tuple(f.vertices) for f in tmp.polygons], all_triangles=False)
ev.to_mesh_clear()

def ground(x,y):
    co, _, _, _ = terrain_bvh.ray_cast(Vector((float(x),float(y),100)), Vector((0,0,-1)), 200)
    return float(co.z) if co is not None else None

def fit_group(ob, target):
    start = box(ob)
    # The ground level is set from evaluated vertices rather than an arbitrary mesh origin.
    ob.location.z -= float(group_points(ob)[:,2].min())
    for _ in range(5):
        bpy.context.view_layer.update()
        got = box(ob)
        ratio = min((target[2]-target[0])/(got[2]-got[0]), (target[3]-target[1])/(got[3]-got[1]))
        ob.scale *= ratio
        bpy.context.view_layer.update()
        ob.location.z -= float(group_points(ob)[:,2].min())
        bpy.context.view_layer.update()
        got = box(ob)
        translate_screen(ob, (target[0]+target[2]-got[0]-got[2])/2, target[3]-got[3])
    report['operations'].append({'name': ob.name, 'action': 'fit projected group preserving rotation',
                                 'before_bbox': start, 'target_bbox': target, 'after_bbox': box(ob)})

def conform_low_band(ob, preserve_top=False):
    """Stretch only the lowest vertices down onto the unchanged terrain after clearing it."""
    old_box = box(ob)
    pts = h['world_coords'](ob)
    assert len(pts) == len(ob.data.vertices) and len(ob.modifiers) == 0
    zlo, zhi = float(pts[:,2].min()), float(pts[:,2].max())
    ids = np.flatnonzero(pts[:,2] <= zlo + max(.02,(zhi-zlo)*.005))
    def targets():
        current = h['world_coords'](ob)
        heights = [ground(*current[i,:2]) for i in ids]
        assert all(z is not None for z in heights), (ob.name, 'base outside land')
        return current, np.array(heights)+.02
    current, zs = targets()
    rise = max(0.,float((zs-current[ids,2]).max()))
    ob.location.z += rise
    bpy.context.view_layer.update()
    if preserve_top:
        # Compensate the projection change from raising the frame, keeping its headline alignment.
        translate_screen(ob, 0, old_box[1]-box(ob)[1])
        current, zs = targets()
        extra = max(0.,float((zs-current[ids,2]).max()))
        ob.location.z += extra
        bpy.context.view_layer.update()
    current, zs = targets()
    ob.data = ob.data.copy()
    inv = ob.matrix_world.inverted()
    for i,z in zip(ids,zs):
        v = current[i].copy(); v[2] = z
        ob.data.vertices[int(i)].co = inv @ Vector(v)
    ob.data.update(); bpy.context.view_layer.update()
    updated = h['world_coords'](ob)
    gaps = [updated[i,2]-ground(*updated[i,:2]) for i in ids]
    # Float32 mesh coordinates are evaluated through scaled transforms; allow 0.1 mm.
    assert max(abs(g-.02) for g in gaps) < 1e-4, (ob.name,min(gaps),max(gaps))
    report['operations'].append({'name':ob.name,'action':'ground-conform lowest mesh band',
        'bottom_vertices':len(ids),'initial_rise':rise,'after_bbox':box(ob),
        'bottom_ground_gap_min_max':[min(gaps),max(gaps)],
        'note':'Only a copied local mesh in v6 is edited; terrain and canonical GLB stay intact.'})

def resolve_ground_faces(ob):
    """Conform wide bottom triangles too, not only their corners on a curved terrain."""
    added = 0; counts = []
    for round_number in range(4):
        pts = h['world_coords'](ob)
        ob_bvh = BVHTree.FromPolygons([Vector(p) for p in pts],
                         [tuple(f.vertices) for f in ob.data.polygons],all_triangles=False)
        pairs = terrain_bvh.overlap(ob_bvh)
        counts.append(len(pairs))
        if not pairs: break
        face_ids = sorted({b for a,b in pairs})
        bm = bmesh.new();bm.from_mesh(ob.data);bm.faces.ensure_lookup_table()
        edges = {e for i in face_ids for e in bm.faces[i].edges}
        count_before = len(bm.verts)
        bmesh.ops.subdivide_edges(bm,edges=list(edges),cuts=16 if round_number==0 else 3,
                                 use_grid_fill=True)
        inv = ob.matrix_world.inverted()
        for v in bm.verts:
            wp = ob.matrix_world @ v.co; z = ground(wp.x,wp.y)
            if z is not None and wp.z < z+.02:
                wp.z = z+.02; v.co = inv @ wp
        added += len(bm.verts)-count_before
        bm.to_mesh(ob.data);bm.free();ob.data.update();bpy.context.view_layer.update()
    else:
        raise RuntimeError((ob.name,'unresolved bottom-face terrain crossings',counts))
    report['operations'].append({'name':ob.name,'action':'subdivide crossing bottom surfaces and conform to terrain',
          'initial_to_final_crossing_pairs':counts,'added_base_vertices':added,'after_bbox':box(ob)})

# Modern building stays enlarged. Contact corrections retain its screen alignment.
conform_low_band(bpy.data.objects['NB_modern_building'], preserve_top=True)
resolve_ground_faces(bpy.data.objects['NB_modern_building'])
fit_group(bpy.data.objects['NB_lime_clast_specimen'], P['models']['clastBox'])
conform_low_band(bpy.data.objects['NB_lime_clast_specimen'])
resolve_ground_faces(bpy.data.objects['NB_lime_clast_specimen'])
fit_group(bpy.data.objects['NB_core4_sequence'], P['models']['crackSequenceBox'])
fit_group(bpy.data.objects['S_lab_island'], P['models']['laboratoryBox'])
conform_low_band(bpy.data.objects['S_lab_island'], preserve_top=True)
fit_group(bpy.data.objects['C5_researchers'], P['models']['ruinObservationBox'])
conform_low_band(bpy.data.objects['C5_researchers'], preserve_top=True)

# Relocate the obstructing trees to measured land points, planting each base on the surface.
for name, uv in P['newTreeOrigins'].items():
    ob = bpy.data.objects[name]; old_box = box(ob)
    new = h['pts_to_world']([uv],0)[0]
    z = ground(*new[:2]); assert z is not None, (name, uv, 'outside land')
    old_min = float(h['world_coords'](ob)[:,2].min())
    ob.location.x = float(new[0]); ob.location.y = float(new[1])
    bpy.context.view_layer.update()
    pts = h['world_coords'](ob)
    feet = pts[pts[:,2] <= pts[:,2].min()+.04]
    heights = [ground(*v[:2]) for v in feet]
    assert all(v is not None for v in heights), (name, 'tree base outside land')
    ob.location.z += max(float(g-v[2]) for g,v in zip(heights,feet))+.01
    bpy.context.view_layer.update()
    report['operations'].append({'name':name,'action':'move tree and plant on terrain',
         'target_origin_uv':uv,'before_bbox':old_box,'after_bbox':box(ob)})

# Clear disconnected field pieces only inside the explicitly scoped plazas and explanation zones.
field = bpy.data.objects['F_centuriatio']
assert not field.modifiers and len(field.data.vertices) == 42012
pts = h['world_coords'](field)
parents = list(range(len(pts)))
def find(a):
    while parents[a] != a:
        parents[a] = parents[parents[a]]; a = parents[a]
    return a
def union(a,b):
    a,b = find(a),find(b)
    if a != b: parents[b] = a
for edge in field.data.edges: union(*edge.vertices)
groups = {}
for i in range(len(pts)): groups.setdefault(find(i),[]).append(i)
modern = group_points(bpy.data.objects['NB_modern_building'])
plaza_lo, plaza_hi = modern[:,:2].min(0)-1.5, modern[:,:2].max(0)+1.5
delete_ids = set(); chosen=[]
for ids in groups.values():
    p = pts[ids]; uv = h['project_pts'](p)
    bb = [uv[:,0].min(),uv[:,1].min(),uv[:,0].max(),uv[:,1].max()]
    plaza = np.all(p[:,:2].min(0)<plaza_hi) and np.all(p[:,:2].max(0)>plaza_lo)
    zones = [i for i,z in enumerate(P['fieldClearZones']) if h['bbox_overlap'](bb,z)]
    if plaza or zones:
        delete_ids.update(ids); chosen.append({'vertices':len(ids),'bbox':list(map(float,bb)),
            'modern_plaza':bool(plaza),'zones':zones})
field.data = field.data.copy()
bm = bmesh.new(); bm.from_mesh(field.data); bm.verts.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[bm.verts[i] for i in sorted(delete_ids)],context='VERTS')
bm.to_mesh(field.data); bm.free(); field.data.update()
report['field_clear'] = {'original_vertices':len(pts),'removed_vertices':len(delete_ids),
    'remaining_vertices':len(field.data.vertices),'component_count':len(chosen),
    'components':chosen,'zones':P['fieldClearZones'],'plaza_xy':[plaza_lo.tolist(),plaza_hi.tolist()]}

marine = bpy.data.objects['NB_marine_breakwater']
marine.location += Vector(P['marine']['deltaWorld']); bpy.context.view_layer.update()
report['operations'].append({'name':marine.name,'action':'shoreward and partly below water',
    'delta_world':P['marine']['deltaWorld'],'after_bbox':box(marine),
    'note':'No seabed exists in the illustration; placement is shoreline embedding, not a seabed claim.'})
for name in P['hideOldLeaders']:
    bpy.data.objects[name].hide_render = True
for name,dy in [('S_core2_badge',-12),('S_core2_underline',-14)]:
    translate_overlay(bpy.data.objects[name],0,dy)
    report['operations'].append({'name':name,'action':'align badge or rule with larger native typography',
        'screen_delta_y':dy,'after_bbox':box(bpy.data.objects[name])})

after = snap()
changed = {name:[key for key in before[name] if before[name][key] != after[name][key]]
           for name in before if before[name] != after[name]}
allowed = set(P['newTreeOrigins']) | set(P['hideOldLeaders']) | {
 'NB_modern_building','NB_lime_clast_specimen','NB_core4_sequence','S_lab_island','C5_researchers',
 'F_centuriatio','NB_marine_breakwater','S_core2_badge','S_core2_underline'}
for name in ['NB_lime_clast_specimen','NB_core4_sequence']:
    allowed.update(o.name for o in bpy.data.objects[name].children_recursive)
assert set(changed) <= allowed, set(changed)-allowed
for name,keys in changed.items():
    permitted = {'matrix_world','matrix_basis'}
    if name in {'NB_modern_building','NB_lime_clast_specimen','S_lab_island','C5_researchers','F_centuriatio'}:
        permitted.add('mesh_sha256')
    if name in P['hideOldLeaders']: permitted.add('hide_render')
    assert set(keys) <= permitted, (name,keys)
report['changed_objects'] = changed
report['allowed_object_names'] = sorted(allowed)
report['after'] = after
for ob in bpy.data.objects: ob.hide_viewport = states[ob.name]
bpy.context.view_layer.update()
assert scene_before == h['scene_fingerprint'](bpy.context.scene)
assert h['sha256_file'](source) == source_hash
assert h['sha256_file'](h['SOURCE']) == original_hash
bpy.ops.wm.save_as_mainfile(filepath=str(output))
report['render_passes'] = h['render_two_pass'](ROOT/'renders/narrative_v6.png')
report['scene_preserved'] = True
(ROOT/'out/poster-composition-v6.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('COMPOSITION_V6_COMPLETE',json.dumps({'file':str(output),'changes':changed,
    'field_removed_vertices':len(delete_ids),'render_passes':report['render_passes']},ensure_ascii=False))
