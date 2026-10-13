"""Pure assignment masks for the two inspected Meshy vault base meshes.

The generated construction asset did NOT provide distinguishable timber
centering or an unfinished rubble crown. Do not label its nested masonry arch
as wood. Root may adapt the preserved Meshy base and add explicit timber/rubble
geometry separately. These masks color only actually existing base surfaces.

Coordinates are mesh-local after H.import_glb has baked glTF transforms and
centered the bottom. Placement/rotation/scale of the object do not change masks.
No mesh, material, object, scene, or file is mutated by build_assignments.
"""
import numpy as np

PALETTE = {
    'construction_stone': '#D3BE9E',
    'construction_mortar': '#B5AD97',
    'construction_brick_facing': '#B58A69',
    'construction_base': '#B5A68B',
    # This token is offered for root's explicit new support geometry only.
    # No original generated-base face is assigned this role.
    'construction_wood': '#8D6C49',
}

def _geometry(ob):
    mesh = ob.data
    v = np.empty(len(mesh.vertices) * 3, dtype=np.float64)
    c = np.empty(len(mesh.polygons) * 3, dtype=np.float64)
    n = np.empty(len(mesh.polygons) * 3, dtype=np.float64)
    mesh.vertices.foreach_get('co', v)
    mesh.polygons.foreach_get('center', c)
    mesh.polygons.foreach_get('normal', n)
    return v.reshape(-1, 3), c.reshape(-1, 3), n.reshape(-1, 3)

def _indices(mask):
    return np.flatnonzero(mask).astype(int).tolist()

def _build_construction(ob):
    vertices, centers, normals = _geometry(ob)
    lo, hi = vertices.min(axis=0), vertices.max(axis=0)
    span = hi - lo
    h = (centers[:, 2] - lo[2]) / max(span[2], 1e-12)
    # Existing large curved barrel shell and its soffit. The flat front arch
    # ring and the closed rear wall retain the masonry stone role.
    shell = (h > .39) & (np.abs(normals[:, 1]) < .60)
    # Existing low floor/ledge/base surfaces, not a new plinth or walkway.
    max_z = np.fromiter((vertices[list(p.vertices), 2].max() for p in ob.data.polygons), dtype=float)
    base = (max_z < lo[2] + span[2] * .065) & ~shell
    return {'default': 'construction_stone',
            'faces': {'construction_mortar': _indices(shell),
                      'construction_base': _indices(base)},
            'notes': {
                'actual_mesh': 'Fully covered short barrel vault, closed rear wall, nested block-jointed masonry arch, small bucket.',
                'actual_timber_centering_present': False,
                'actual_unfinished_rubble_crown_present': False,
                'generated_prompt_mismatch': 'Timber/unfinished stage was not generated; material color alone must not imply it exists.',
                'root_adaptation': 'Explicit timber support and a partial vault cutaway may be added by root; original GLB preserved.',
                'local_bbox': [lo.tolist(), hi.tolist()],
                'visible_open_end_axis': 'negative local Y',
                'source_face_count': 18179,
                'current_face_count': len(ob.data.polygons),
                'wood_faces_on_generated_base': 0,
                'classification': 'Existing curved shell by height/orientation, low base, remaining masonry.',
                'material_scope': 'Graphic separation of visible geometry; exposed large rubble inclusions are not claimed.',
            }}

def _build_complete(ob):
    vertices, centers, normals = _geometry(ob)
    lo, hi = vertices.min(axis=0), vertices.max(axis=0)
    span = hi - lo
    h = (centers[:, 2] - lo[2]) / max(span[2], 1e-12)
    x = (centers[:, 0] - lo[0]) / max(span[0], 1e-12)
    # The generated base has a roof segment ending near local x=+0.06 and
    # a real cutaway between this segment and the positive-X terminal arch.
    # Color the existing exposed roof cutoff/end, not invented aggregate.
    cutoff = (x > .505) & (x < .553) & (h > .49)
    # Thin negative-X arch-facing surface (not the whole pier or sidewall).
    facing = (x < .045) & (normals[:, 0] < -.55) & (h > .13)
    facing &= ~cutoff
    max_z = np.fromiter((vertices[list(p.vertices), 2].max() for p in ob.data.polygons), dtype=float)
    base = (max_z < lo[2] + span[2] * .065) & ~cutoff & ~facing
    return {'default': 'construction_stone',
            'faces': {'construction_mortar': _indices(cutoff),
                      'construction_brick_facing': _indices(facing),
                      'construction_base': _indices(base)},
            'notes': {
                'actual_mesh': 'Long-axis-X vaulted corridor/arcade fragment with three side openings and a real open roof cutaway.',
                'actual_exposed_rubble_aggregate_present': False,
                'cutoff_material': 'Existing exposed cutoff receives a quieter core tone; no inclusions are added by this helper.',
                'facing_material': 'Existing thin arch end face only; not a claim of a historical building-specific brick composition.',
                'local_bbox': [lo.tolist(), hi.tolist()],
                'long_axis': 'local X',
                'source_face_count': 19731,
                'current_face_count': len(ob.data.polygons),
                'classification': 'Actual roof cutoff, thin terminal facing, low existing pier foot, remaining masonry.',
            }}

def build_assignments(bpy):
    result = {}
    for name, builder in [('NB_vault_construction', _build_construction),
                          ('NB_vault_complete', _build_complete)]:
        ob = bpy.data.objects.get(name)
        if ob is None or ob.type != 'MESH':
            continue
        entry = builder(ob)
        entry['faces'] = {role: ids for role, ids in entry['faces'].items() if ids}
        all_faces = [i for ids in entry['faces'].values() for i in ids]
        if len(all_faces) != len(set(all_faces)):
            raise ValueError('Overlapping construction part masks: ' + name)
        if all_faces and (min(all_faces) < 0 or max(all_faces) >= len(ob.data.polygons)):
            raise ValueError('Invalid construction polygon index: ' + name)
        entry['notes']['explicit_face_counts'] = {r: len(ids) for r, ids in entry['faces'].items()}
        entry['notes']['default_face_count'] = len(ob.data.polygons) - len(all_faces)
        result[name] = entry
    return result
