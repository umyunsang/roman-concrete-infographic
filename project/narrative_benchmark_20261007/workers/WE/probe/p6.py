import bpy, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from welib import *
from common import overlay_objects
S = Screen(); L = Land()
np.set_printoptions(suppress=True, precision=3, linewidth=220)
print('overlay objs', [o.name for o in overlay_objects()][:400])
sc = bpy.context.scene; dg = bpy.context.evaluated_depsgraph_get()
def hit(pt):
    o, d = S.ray(pt)
    r = sc.ray_cast(dg, o, d)
    return (r[4].name if r[0] else None), (np.round(r[1][:], 3) if r[0] else None)
for pt in [(720, 1190), (780, 1200), (760, 1170), (800, 1250), (850, 1240), (720, 1250), (1080, 995), (1060, 985), (1100, 1000)]:
    print(pt, hit(pt))
