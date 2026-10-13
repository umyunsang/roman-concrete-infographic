"""워커 B: 물체별 면 음영 지정. B_SHADE='이름:smooth|flat,...' (기본은 최종값)"""
import os, bpy, numpy as np
spec = os.environ.get('B_SHADE', 'L07_vesuvius:smooth,L03_forum_vesta:flat')
for item in spec.split(','):
    n, mode = item.split(':')
    o = bpy.data.objects.get(n)
    if o:
        o.data.polygons.foreach_set('use_smooth', np.full(len(o.data.polygons), mode == 'smooth'))
        o.data.update(); print('shade', n, mode)
