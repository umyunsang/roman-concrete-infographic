import bpy, sys, runpy
sys.argv = [sys.argv[0]]
g = runpy.run_path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/WA/step.py', run_name='lib')
g['init_screen']()
import numpy as np
for k, rn in ((1, 'S_lead06'), (2, 'S_lead08'), (0, 'S_lead04')):
    PS, _ = g['screen_pts'](bpy.data.objects[f'S_sect{k}']); PR, dR = g['screen_pts'](bpy.data.objects[rn])
    PD, _ = g['screen_pts'](bpy.data.objects[f'S_sect_dot{k}'])
    print(rn, 'sect_left', PS[:,0].min(), 'line', PR[:,0].min(), PR[:,0].max(), 'dot cx', (PD[:,0].min()+PD[:,0].max())/2, 'target', PS[:,0].min()+1.7-0.5)
