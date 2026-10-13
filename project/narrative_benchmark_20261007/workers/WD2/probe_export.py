"""WD2 probe: export camera matrix + local verts/tris of my objects for offline layout search."""
import bpy, sys
import numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, need

out = sys.argv[sys.argv.index('--') + 1]
S = Screen()
data = {'M': S.M}
for n in ['L09_portus_lighthouse', 'L09_portus_mole', 'L12_harbor_pilae', 'NB_marine_breakwater', 'T_cypress',
          'L11_privernum_wall', 'C5_researchers', 'L08_pompeii_site']:
    o = need(n); me = o.data
    co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    me.calc_loop_triangles()
    tri = np.empty(len(me.loop_triangles) * 3, np.int32); me.loop_triangles.foreach_get('vertices', tri)
    mi = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi)
    tp = np.empty(len(me.loop_triangles), np.int32); me.loop_triangles.foreach_get('polygon_index', tp)
    key = n.replace('.', '_')
    data[key + '_co'] = co.astype(np.float32); data[key + '_tri'] = tri.reshape(-1, 3); data[key + '_mw'] = np.array(o.matrix_world)
    data[key + '_trimat'] = mi[tp]
np.savez_compressed(out, **data)
print('WROTE', out)
