"""Read-only face assignment builder for the existing v7 heritage/tree meshes.

Ownership: COL_ruined; visible T_pine/T_cypress copies; explicit heritage list
below; NB_marine_breakwater. Never saves, changes geometry, or creates materials.
The root owns material application and production rendering. Names of roles are
graphic surface roles, not archaeological identifications of real materials.
"""
import numpy as np

PALETTE = {
    'roman_stone': '#D3BE9E',
    'colosseum_wall': '#CDA477',
    'colosseum_interior': '#B89D78',
    'arena_earth': '#B5A07B',
    'roman_roof': '#A88565',
    'roman_plinth': '#B5A68B',
    'foliage': '#75865C',
    'foliage_light': '#8D9A70',
    'trunk': '#8D6C49',
}

HERITAGE = {
    'L03_forum_temple': {'plinth': .13, 'cap': .78},
    'L03_forum_vesta': {'plinth': .13, 'cap': .655},
    'L04_palatine': {'plinth': .17},
    'L04_palatine_arch': {},
    'L05_aqua_claudia': {'plinth': .10},
    'L08_pompeii': {'plinth': .10},
    'L09_portus_lighthouse': {'plinth': .09},
    'L09_portus_mole': {'plinth': .13},
    'L11_privernum_wall': {'plinth': .11},
    'L12_harbor_pilae': {'plinth': .10},
    'NB_marine_breakwater': {'plinth': .18},
    'NB_roman_breakwater': {'plinth': .18},
}

def _visible(ob):
    return (ob.type == 'MESH' and not ob.hide_render
            and any(not col.hide_render for col in ob.users_collection))

def _geometry(ob):
    m = ob.data
    v = np.empty(len(m.vertices) * 3, dtype=np.float64)
    m.vertices.foreach_get('co', v)
    mat = np.array(ob.matrix_world, dtype=np.float64)
    vertices = v.reshape(-1, 3) @ mat[:3, :3].T + mat[:3, 3]
    c = np.empty(len(m.polygons) * 3, dtype=np.float64)
    n = np.empty(len(m.polygons) * 3, dtype=np.float64)
    m.polygons.foreach_get('center', c)
    m.polygons.foreach_get('normal', n)
    centers = c.reshape(-1, 3) @ mat[:3, :3].T + mat[:3, 3]
    normals = n.reshape(-1, 3) @ np.linalg.inv(mat[:3, :3])
    normals /= np.maximum(np.linalg.norm(normals, axis=1)[:, None], 1e-12)
    return vertices, centers, normals

def _components(mesh):
    parent = list(range(len(mesh.vertices)))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for edge in mesh.edges:
        a, b = (find(int(v)) for v in edge.vertices)
        if a != b:
            parent[b] = a
    groups = {}
    for i in range(len(parent)):
        groups.setdefault(find(i), []).append(i)
    return list(groups.values())

def _indices(mask):
    return np.flatnonzero(mask).astype(int).tolist()

def _tree(ob):
    vertices, centers, normals = _geometry(ob)
    components = _components(ob.data)
    base_z = float(vertices[:, 2].min())
    top_z = float(vertices[:, 2].max())
    height = top_z - base_z
    labels = np.full(len(vertices), 'foliage', dtype=object)
    woody, crown = [], []
    for i, component in enumerate(components):
        p = vertices[component]
        span = p.max(axis=0) - p.min(axis=0)
        # Actual pine mesh has one narrow, connected pole/branch component and
        # seven separate ellipsoid crown lobes. Cypress has only a continuous
        # tapered foliage mesh; no trunk is invented for it.
        narrow_tall = span[2] > max(span[0], span[1]) * 3.0
        near_bottom = p[:, 2].min() <= base_z + height * .08
        if len(components) > 1 and narrow_tall and near_bottom:
            woody.append(i)
            labels[component] = 'trunk'
        else:
            crown.append((i, float(p[:, 2].mean())))
    # Whole existing crown lobes receive the lighter leaf shade. This avoids
    # painting arbitrary height bands through a connected trunk or roof.
    if len(crown) >= 4:
        for i, _ in sorted(crown, key=lambda x: x[1], reverse=True)[:2]:
            labels[components[i]] = 'foliage_light'
    faces = {'trunk': [], 'foliage_light': []}
    for polygon in ob.data.polygons:
        role = labels[int(polygon.vertices[0])]
        if role in faces:
            faces[role].append(int(polygon.index))
    faces = {role: values for role, values in faces.items() if values}
    return {
        'default': 'foliage', 'faces': faces,
        'notes': {
            'classification': 'Disconnected existing mesh components, world-space bbox aspect and height.',
            'connected_components': len(components),
            'woody_components': woody,
            'no_invented_trunk': not bool(woody),
            'lighter_crowns': 2 if len(crown) >= 4 else 0,
            'geometry_unchanged': True,
        },
    }

def _colosseum(ob):
    vertices, centers, normals = _geometry(ob)
    if len(ob.data.polygons) != 197806:
        raise ValueError('COL_ruined topology drift: audited v7 has 197806 polygons')
    xy_center = (vertices[:, :2].min(axis=0) + vertices[:, :2].max(axis=0)) * .5
    centered = vertices[:, :2] - xy_center
    values, axes = np.linalg.eigh(np.cov(centered.T))
    axes = axes[:, np.argsort(values)[::-1]]
    radii = np.max(np.abs(centered @ axes), axis=0)
    uv = (centers[:, :2] - xy_center) @ axes / radii
    radius = np.sqrt(np.sum(uv * uv, axis=1))
    radial = centers[:, :2] - xy_center
    radial /= np.maximum(np.linalg.norm(radial, axis=1)[:, None], 1e-12)
    inward_normal = np.sum(normals[:, :2] * radial, axis=1) < -.12
    upward_surface = normals[:, 2] > .28
    zmin, zmax = float(vertices[:, 2].min()), float(vertices[:, 2].max())
    # Inner seating/terrace surfaces and inward-facing existing walls. The
    # outer arcade keeps the hero stone color. No new seating is generated.
    interior = (radius < .83) & (upward_surface | inward_normal)
    # Only already-existing low, upward-facing central surfaces. The mesh has
    # ruins/hypogeum, so no arena disk, filled sand plane, or roof is inferred.
    arena = ((radius < .43) & (normals[:, 2] > .60)
             & (centers[:, 2] < zmin + (zmax - zmin) * .16))
    interior &= ~arena
    return {
        'default': 'colosseum_wall',
        'faces': {
            'colosseum_interior': _indices(interior),
            'arena_earth': _indices(arena),
        },
        'notes': {
            'classification': 'World-space principal ellipse radius + face orientation; low central existing upfaces only.',
            'ellipse_center_xy': xy_center.tolist(),
            'ellipse_radii': radii.tolist(),
            'z_range': [zmin, zmax],
            'arena_limit_z': zmin + (zmax - zmin) * .16,
            'archaeological_claim': 'Graphic surface separation only; no claim that all low central surfaces are historical sand.',
            'no_added_arena_fill': True,
            'geometry_unchanged': True,
        },
    }

def _heritage(ob, settings):
    vertices, centers, normals = _geometry(ob)
    zmin, zmax = float(vertices[:, 2].min()), float(vertices[:, 2].max())
    height = max(zmax - zmin, 1e-12)
    h = (centers[:, 2] - zmin) / height
    faces = {}
    if 'plinth' in settings:
        faces['roman_plinth'] = _indices(h < settings['plinth'])
    if 'cap' in settings:
        # The two forum meshes visibly contain dome/cap geometry. This warm
        # cap shade is not a claim of tiles or any new roof construction.
        faces['roman_roof'] = _indices(h > settings['cap'])
    faces = {role: values for role, values in faces.items() if values}
    return {
        'default': 'roman_stone', 'faces': faces,
        'notes': {
            'classification': 'Existing geometric lower base and, for two forum temples only, existing upper cap.',
            'normalized_height_thresholds': dict(settings),
            'z_range': [zmin, zmax],
            'roof_claim': 'Existing dome/cap color only' if 'cap' in settings else 'No roof inferred on this ruin.',
            'geometry_unchanged': True,
        },
    }

def build_assignments(bpy):
    """Return object -> default role + nonoverlapping per-role polygon indices."""
    result = {}
    for ob in sorted(bpy.data.objects, key=lambda item: item.name):
        if not _visible(ob):
            continue
        if ob.name.startswith(('T_pine', 'T_cypress')):
            result[ob.name] = _tree(ob)
        elif ob.name == 'COL_ruined':
            result[ob.name] = _colosseum(ob)
        elif ob.name in HERITAGE:
            result[ob.name] = _heritage(ob, HERITAGE[ob.name])
    for name, entry in result.items():
        all_faces = [i for ids in entry['faces'].values() for i in ids]
        if len(all_faces) != len(set(all_faces)):
            raise ValueError('Overlapping role assignments: ' + name)
        if all_faces and (min(all_faces) < 0 or max(all_faces) >= len(bpy.data.objects[name].data.polygons)):
            raise ValueError('Invalid polygon index: ' + name)
    return result

def summarize(assignments):
    counts = {}
    for entry in assignments.values():
        for role, indices in entry['faces'].items():
            counts[role] = counts.get(role, 0) + len(indices)
    return {'objects': len(assignments), 'explicit_face_counts': counts,
            'tree_objects': sum(n.startswith(('T_pine', 'T_cypress')) for n in assignments),
            'heritage_objects': sum(n in HERITAGE for n in assignments),
            'colosseum_objects': int('COL_ruined' in assignments)}
