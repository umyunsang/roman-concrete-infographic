"""tland_diff.py - where and how much T_land changed between two blends (read-only).
Blender -b <after.blend> --factory-startup --python tland_diff.py -- <before.blend> <out.json>
Reads the before T_land vertex positions with bpy.data.libraries.load (link-free copy of the mesh datablock)."""
import bpy, sys, json
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'layout'))
from common import Screen, world_verts
argv = sys.argv[sys.argv.index('--') + 1:]
before, out = Path(argv[0]), Path(argv[1])
S = Screen()
land = bpy.data.objects['T_land']; A = world_verts(land)
with bpy.data.libraries.load(str(before), link=False) as (src, dst):
    dst.meshes = [land.data.name]
mb = dst.meshes[0]
co = np.empty(len(mb.vertices) * 3); mb.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
M = np.array(land.matrix_world); Bw = (np.c_[co, np.ones(len(co))] @ M.T)[:, :3]
assert Bw.shape == A.shape
dz = A[:, 2] - Bw[:, 2]; dxy = np.abs(A[:, :2] - Bw[:, :2]).max()
ch = np.nonzero(np.abs(dz) > 1e-6)[0]
P = S.project(Bw[ch])
res = {'vertices': len(A), 'changed': int(len(ch)), 'raised': int((dz > 1e-6).sum()), 'max_xy_shift': float(dxy),
       'max_drop': round(float(-dz.min()), 3), 'mean_drop_changed': round(float(-dz[ch].mean()), 3) if len(ch) else 0}
boxes = {'A_core_south': (480, 760, 960, 1080), 'B_ostiensis': (40, 460, 960, 1480), 'B_landing1': (460, 620, 460, 580),
         'B_landing5': (840, 1010, 820, 980)}
inbox = np.zeros(len(ch), bool)
for k, (x0, x1, y0, y1) in boxes.items():
    m = (P[:, 0] >= x0) & (P[:, 0] <= x1) & (P[:, 1] >= y0) & (P[:, 1] <= y1); inbox |= m
    if m.any():
        res[k] = {'changed': int(m.sum()), 'screen_box': [round(float(v), 1) for v in (P[m, 0].min(), P[m, 0].max(), P[m, 1].min(), P[m, 1].max())],
                  'max_drop': round(float(-dz[ch][m].min()), 3)}
res['changed_outside_the_four_boxes'] = int((~inbox).sum())
for n in ['R3_colosseum_podium', 'COL_ruined', 'MS3_core34_to_5', 'MS1_core1_to_2', 'MS2_core2_to_34']:
    o = bpy.data.objects.get(n)
    if o is None:
        continue
    Wo = world_verts(o)[:, :2][::7]
    d = np.sqrt(((Bw[ch][:, None, :2] - Wo[None]) ** 2).sum(-1)).min() if len(ch) else None
    res[f'min_xy_distance_changed_vertex_to_{n}'] = round(float(d), 2) if d is not None else None
out.write_text(json.dumps(res, indent=1)); print('TLAND', json.dumps(res))
