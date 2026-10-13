import bpy, sys, runpy
sys.argv = [sys.argv[0]]
g = runpy.run_path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/WA/step.py', run_name='lib')
g['init_screen']()
import numpy as np
for k in range(4):
    PS, _ = g['screen_pts'](bpy.data.objects[f'S_sect{k}']); PD, dD = g['screen_pts'](bpy.data.objects[f'S_sect_dot{k}'])
    print(k, 'sect_left', PS[:,0].min(), 'dot cx', (PD[:,0].min()+PD[:,0].max())/2, 'center vert', PD[0], 'depth', np.median(dD))
    w = g['world_at']((400.0, 1250.0), 150.0); print('  roundtrip', g['pt_of'](w))
