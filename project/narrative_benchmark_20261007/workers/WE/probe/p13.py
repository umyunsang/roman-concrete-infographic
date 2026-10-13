import bpy, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from welib import *
S = Screen(); L = Land()
sc = bpy.context.scene; dg = bpy.context.evaluated_depsgraph_get()
np.set_printoptions(suppress=True, precision=3, linewidth=220)
def hit(pt):
    o, d = S.ray(pt); r = sc.ray_cast(dg, o, d)
    return (r[4].name if r[0] else None, np.round(r[1][:], 3) if r[0] else None)
print('PLACE-11 area')
for y in range(696, 726, 3):
    print(y, [ (x, hit((x, y))[0][:8] if hit((x,y))[0] else None) for x in range(250, 272, 2)])
for pt in [(257, 700), (260, 705), (264, 711), (262, 718)]:
    print(pt, hit(pt))
print('landing1 fragments')
for pt in [(555, 510), (553, 508), (527, 504), (529, 505), (557, 512)]:
    print(pt, hit(pt))
print('landing5 strays')
for pt in [(940, 867), (945, 867), (948, 868), (956, 875), (960, 880), (963, 884)]:
    print(pt, hit(pt))
print('sw wedge')
for pt in [(365, 986), (366, 988), (364, 987)]:
    print(pt, hit(pt))
# terrain hole boundary near PLACE-11
r = hit((260, 705))[1]
print('world at 260,705', r, 'T', L.z(r[0], r[1]))
for dx in np.arange(-1.5, 1.6, 0.5):
    print(' x', round(r[0] + dx, 2), [round(L.z(r[0] + dx, r[1] + dy), 2) for dy in np.arange(-1.5, 1.6, 0.5)])
