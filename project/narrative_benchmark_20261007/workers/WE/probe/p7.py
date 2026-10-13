import bpy, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from welib import *
from common import overlay_objects
S = Screen(); L = Land()
out = Path(sys.argv[sys.argv.index('--') + 1])
zones = {'hill': (38, 78, -42, -2), 'privn': (40, 66, 0, 22), 'bench': (8, 38, 32, 62)}
res = {}
for n, (x0, x1, y0, y1) in zones.items():
    xs = np.arange(x0, x1 + 1e-6, 0.25); ys = np.arange(y0, y1 + 1e-6, 0.25)
    Z = np.array([[L.z(x, y) for x in xs] for y in ys])
    res[n + '_Z'] = Z; res[n + '_ext'] = np.array([x0, x1, y0, y1])
    # screen pt of grid corners for reference
# object footprints (xy of verts, subsampled) for objects intersecting zones
fps = {}
vis = map_visible_objects() + overlay_objects()
for o in vis:
    if o.name in ('T_land', 'L10_sea', 'L02_tiber', 'W_water_marks'): continue
    Wv = world_verts(o)
    if not len(Wv): continue
    for n, (x0, x1, y0, y1) in zones.items():
        m = (Wv[:, 0] > x0) & (Wv[:, 0] < x1) & (Wv[:, 1] > y0) & (Wv[:, 1] < y1)
        if m.sum() > 0:
            sub = Wv[m][:: max(1, m.sum() // 3000)]
            fps.setdefault(n, {})[o.name] = sub
for n, d in fps.items():
    res[n + '_objs'] = np.array(list(d.keys()))
    for k, v in d.items(): res[f'{n}__{k}'] = v
# screen-pt projection of grid for window mapping: store a function sample
np.savez_compressed(out, **res)
print('objects per zone', {n: sorted(d.keys()) for n, d in fps.items()})
