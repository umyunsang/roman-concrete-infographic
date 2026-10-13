"""Pure, read-only face assignment builder for the existing L07_vesuvius.

Audited source: roman_concrete_narrative_v8.blend, 59014 vertices / 116849 faces.
No geometry, object transforms, camera, visibility, materials, or files are
changed by build_assignments. Root owns final material application and render.
The colors separate existing geometric surfaces; they do not identify geology
or assert vegetation, ash, lava, or a historical eruption on those surfaces.
"""
import numpy as np

PALETTE = {
    'volcano_body': '#B6B19C',
    'volcano_crater': '#7C7364',
    'volcano_rock': '#A7957C',
    'volcano_low_slope': '#AAA68F',
}

def _geometry(ob):
    m = ob.data
    mat = np.array(ob.matrix_world, dtype=np.float64)
    a = np.empty(len(m.vertices) * 3, dtype=np.float64)
    c = np.empty(len(m.polygons) * 3, dtype=np.float64)
    n = np.empty(len(m.polygons) * 3, dtype=np.float64)
    m.vertices.foreach_get('co', a)
    m.polygons.foreach_get('center', c)
    m.polygons.foreach_get('normal', n)
    vertices = a.reshape(-1, 3) @ mat[:3, :3].T + mat[:3, 3]
    centers = c.reshape(-1, 3) @ mat[:3, :3].T + mat[:3, 3]
    normals = n.reshape(-1, 3) @ np.linalg.inv(mat[:3, :3])
    normals /= np.maximum(np.linalg.norm(normals, axis=1)[:, None], 1e-12)
    return vertices, centers, normals

def _indices(mask):
    return np.flatnonzero(mask).astype(int).tolist()

def build_assignments(bpy):
    ob = bpy.data.objects.get('L07_vesuvius')
    if ob is None or ob.type != 'MESH' or ob.hide_render:
        return {}
    if not any(not c.hide_render for c in ob.users_collection):
        return {}
    if (len(ob.data.vertices), len(ob.data.polygons)) != (59014, 116849):
        raise ValueError('L07_vesuvius topology differs from the inspected v8 mesh')
    vertices, centers, normals = _geometry(ob)
    lo, hi = vertices.min(axis=0), vertices.max(axis=0)
    height = float(hi[2] - lo[2])
    h = (centers[:, 2] - lo[2]) / height
    top = vertices[vertices[:, 2] > lo[2] + height * .80]
    # Existing high ring's mean XY is more faithful to the asymmetric opening
    # than the whole cone's footprint center (the lower cone is not symmetric).
    opening_center = top[:, :2].mean(axis=0)
    delta = centers[:, :2] - opening_center
    radius = np.linalg.norm(delta, axis=1)
    radial_direction = delta / np.maximum(radius[:, None], 1e-12)
    outward_normal = np.sum(normals[:, :2] * radial_direction, axis=1)
    # Existing concave high bowl, including its upward-facing lower interior.
    # Restrict by opening radius, height, and orientation so the outer cone
    # does not become a dark cylindrical cap. No separate crater is generated.
    crater = ((h > .58) & (radius < 3.40)
              & ((outward_normal < .12) | (radius < 2.00)))
    # Warm neutral cap/rim is limited to already-existing high rocky surfaces.
    rim = (h > .89) & (radius < 4.60) & ~crater
    # Close neutral earth at the low region avoids an artificial green belt.
    # Much of the low scan lies below the existing terrain; it remains there.
    low_slope = (h < .24) & ~crater & ~rim
    faces = {
        'volcano_crater': _indices(crater),
        'volcano_rock': _indices(rim),
        'volcano_low_slope': _indices(low_slope),
    }
    selected = [i for ids in faces.values() for i in ids]
    if len(selected) != len(set(selected)):
        raise ValueError('Overlapping volcano surface masks')
    return {ob.name: {
        'default': 'volcano_body',
        'faces': faces,
        'notes': {
            'classification': 'Existing upper concavity/rim, broad outer slopes, and low existing scan surfaces.',
            'world_bbox': [lo.tolist(), hi.tolist()],
            'opening_center_xy': opening_center.tolist(),
            'polygon_count': len(ob.data.polygons),
            'explicit_face_counts': {role: len(ids) for role, ids in faces.items()},
            'default_face_count': len(ob.data.polygons) - len(selected),
            'color_rationale': {
                'volcano_body': 'Brighter gray earth than candidate #A5A18D to retain the Colosseum/CORE hierarchy.',
                'volcano_crater': 'Muted dark earth restricted to the existing small upper interior; no red/lava.',
                'volcano_rock': 'Warm, low-chroma upper rim harmonizes with the Roman stone map without matching its hero saturation.',
                'volcano_low_slope': 'Close neutral earth rather than green #7E8967; separates the low foot without implying added vegetation or a dominant belt.',
            },
            'no_eruption_lava_vegetation_claim': True,
            'geometry_camera_placement_unchanged': True,
        },
    }}
