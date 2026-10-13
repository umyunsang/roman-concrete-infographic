import bpy, sys, math
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'layout'))
from common import Screen, world_verts, map_visible_objects, bvh_of

def mesh_arrays(o):
    me = o.data
    W = world_verts(o)
    ls = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('loop_start', ls)
    lt = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('loop_total', lt)
    lv = np.empty(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', lv)
    E = np.empty(len(me.edges) * 2, np.int32); me.edges.foreach_get('vertices', E)
    return W, ls, lt, lv, E.reshape(-1, 2)

def vert_islands(nv, E):
    parent = np.arange(nv)
    def find(a):
        r = a
        while parent[r] != r: r = parent[r]
        while parent[a] != r:
            parent[a], a = r, parent[a]
        return r
    for a, b in E:
        ra, rb = find(a), find(b)
        if ra != rb: parent[ra] = rb
    roots = np.array([find(i) for i in range(nv)])
    _, lab = np.unique(roots, return_inverse=True)
    return lab

def face_islands(o):
    W, ls, lt, lv, E = mesh_arrays(o)
    lab = vert_islands(len(W), E)
    flab = lab[lv[ls]] if len(ls) else np.zeros(0, int)
    return W, lab, flab, ls, lt, lv

class Land:
    def __init__(self, name='T_land'):
        self.bvh, _ = bvh_of([bpy.data.objects[name]])
    def z(self, x, y, top=50.0):
        h = self.bvh.ray_cast(Vector((x, y, top)), Vector((0, 0, -1)))[0]
        return h.z if h else float('nan')
    def zs(self, XY):
        return np.array([self.z(x, y) for x, y in XY])
