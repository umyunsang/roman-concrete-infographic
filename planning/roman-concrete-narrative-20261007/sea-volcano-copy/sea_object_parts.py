"""Read-only, source-polygon part assignments for four v8 seaside models.

No geometry creation, object writes, material writes, render, or save.
Coordinates are original local mesh coordinates, measured against source v8.
"""
import numpy as np

PALETTE = {
    'sea_stone': '#D3BE9E',
    'sea_base': '#9C9B89',
    'sea_deck': '#C5AD87',
    'sea_cap': '#A47F5E',
    'sea_recess': '#6E817E',
    'sea_concrete': '#B5B0A0',
}

EXPECTED = {
    'L09_portus_lighthouse': (4928, 6779),
    'L09_portus_mole': (4265, 5489),
    'L12_harbor_pilae': (4172, 5389),
    'NB_marine_breakwater': (20539, 17330),
}

NOTES = {
    'L09_portus_lighthouse': 'Warm stone walls; lowest foot is sea_base. The existing summit/conical roof and balcony top faces are sea_cap. Small inset shaft-window faces use sea_recess, bounded by measured recess depth, window heights and face area to exclude broad outer walls. Lantern body remains stone.',
    'L09_portus_mole': 'Raised quay wall body remains warm stone. Low vertical/underside foundation faces use sea_base; actual upward-facing recessed floor and perimeter walking surface use sea_deck; the elevated corner-block top uses sea_cap. Irregular debris remains stone.',
    'L12_harbor_pilae': 'Six existing pier/pillar forms: stone side walls, sea_base below the slab-top elevation, sea_deck on actual upward slab faces, sea_cap on upward upper-pillar cap faces. Lower ornamental panels retain the stone default.',
    'NB_marine_breakwater': 'Existing low slab and two block-wall segments only: concrete wall body, base underside/lowest sides, deck on slab top, cap on upward wall tops. No separate exposed aggregate geometry was identified; no aggregate mask is invented.',
}


def select_arrays(name, centers, normals, areas):
    c = np.asarray(centers, dtype=np.float64)
    n = np.asarray(normals, dtype=np.float64)
    a = np.asarray(areas, dtype=np.float64)
    z, nz = c[:, 2], n[:, 2]
    labels = np.full(len(c), 'sea_stone', dtype=object)
    if name == 'L09_portus_lighthouse':
        labels[z < .050] = 'sea_base'
        labels[(z > 1.610) | ((z > 1.345) & (z < 1.430) & (nz > .55))] = 'sea_cap'
        # Inset original shaft windows, not their carved stone frames.
        bands = ((.430, .525), (.565, .655), (.715, .815), (.895, 1.005), (1.085, 1.215))
        heights = np.zeros(len(c), dtype=bool)
        for lo, hi in bands:
            heights |= (z > lo) & (z < hi)
        front = (abs(c[:, 0]) < .026) & (c[:, 1] > -.044) & (c[:, 1] < -.012)
        rear = (abs(c[:, 0]) < .026) & (c[:, 1] > .192) & (c[:, 1] < .232)
        sides = (abs(c[:, 1] - .095) < .028) & (abs(c[:, 0]) > .103) & (abs(c[:, 0]) < .142)
        labels[heights & (front | rear | sides) & (a < .0035)] = 'sea_recess'
        default = 'sea_stone'
    elif name == 'L09_portus_mole':
        labels[(z < .230) & (nz < .65)] = 'sea_base'
        labels[(nz > .65) & (((z > .025) & (z < .510)) | ((z > .790) & (z < 1.610)))] = 'sea_deck'
        labels[(nz > .65) & (z > 2.300)] = 'sea_cap'
        default = 'sea_stone'
    elif name == 'L12_harbor_pilae':
        labels[z < .350] = 'sea_base'
        labels[(nz > .65) & (z >= .350) & (z < .750)] = 'sea_deck'
        labels[(nz > .65) & (z > 2.700)] = 'sea_cap'
        default = 'sea_stone'
    elif name == 'NB_marine_breakwater':
        labels[:] = 'sea_concrete'
        labels[z < .055] = 'sea_base'
        labels[(nz > .65) & (z > .055) & (z < .105)] = 'sea_deck'
        labels[(nz > .65) & (z > .180)] = 'sea_cap'
        default = 'sea_concrete'
    else:
        raise KeyError(name)
    return {
        'default': default,
        'faces': {role: np.flatnonzero(labels == role).astype(int).tolist()
                  for role in PALETTE if role != default and np.any(labels == role)},
        'notes': NOTES[name],
    }


def build_assignments(bpy):
    result = {}
    for name, expected in EXPECTED.items():
        obj = bpy.data.objects.get(name)
        if obj is None or obj.type != 'MESH':
            raise ValueError('Missing expected source mesh: ' + name)
        mesh = obj.data
        actual = (len(mesh.vertices), len(mesh.polygons))
        if actual != expected:
            raise ValueError('Source topology count mismatch for %s: %s != %s' % (name, actual, expected))
        centers = np.asarray([tuple(poly.center) for poly in mesh.polygons], dtype=np.float64)
        normals = np.asarray([tuple(poly.normal) for poly in mesh.polygons], dtype=np.float64)
        areas = np.asarray([poly.area for poly in mesh.polygons], dtype=np.float64)
        result[name] = select_arrays(name, centers, normals, areas)
    return result
