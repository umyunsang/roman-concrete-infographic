"""Read-only original-polygon masks for the existing D2_lime_kiln v9 mesh."""
import numpy as np

PALETTE = {
    'kiln_shell': '#D3BE9E',
    'kiln_foundation': '#9C9B89',
    'kiln_interior': '#6E6253',
    'kiln_smoke': '#A7AAA3',
}
EXPECTED = (4442, 6494)

def select_arrays(centers, normals):
    c = np.asarray(centers, dtype=np.float64)
    n = np.asarray(normals, dtype=np.float64)
    z = c[:, 2]
    labels = np.full(len(c), 'kiln_shell', dtype=object)
    labels[z < .400] = 'kiln_foundation'
    radius = np.linalg.norm(c[:, :2], axis=1)
    inward = np.sum(c[:, :2] * n[:, :2], axis=1) / np.maximum(radius, 1e-8)
    # Actual concave chamber walls and underside of its arched roof.
    cavity = (radius < 2.80) & (c[:, 1] < 1.35) & (z > .420) & (z < 3.50)
    cavity &= (inward < -.300) | (n[:, 2] < -.400)
    labels[cavity] = 'kiln_interior'
    # Existing raised curling plume; measured local z separates it from shell.
    labels[z > 4.800] = 'kiln_smoke'
    return {
        'default': 'kiln_shell',
        'faces': {role: np.flatnonzero(labels == role).astype(int).tolist()
                  for role in PALETTE if role != 'kiln_shell' and np.any(labels == role)},
        'notes': 'Existing D2_lime_kiln only: domed masonry shell, lowest foundation platform, concave chamber/arched interior, and raised curling smoke-shaped geometry. Interior selection uses inward-facing local normals and bounded chamber coordinates, not a rectangular front patch. Plume attribution is based on the existing shape above the vent; no new fire or geometry is added.',
    }

def build_assignments(bpy):
    obj = bpy.data.objects.get('D2_lime_kiln')
    if obj is None or obj.type != 'MESH':
        raise ValueError('Expected D2_lime_kiln source mesh is missing')
    mesh = obj.data
    if (len(mesh.vertices), len(mesh.polygons)) != EXPECTED:
        raise ValueError('D2_lime_kiln topology counts differ from source v9')
    centers = np.asarray([tuple(poly.center) for poly in mesh.polygons], dtype=np.float64)
    normals = np.asarray([tuple(poly.normal) for poly in mesh.polygons], dtype=np.float64)
    return {'D2_lime_kiln': select_arrays(centers, normals)}
