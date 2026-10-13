"""시험용: 환경변수 B_SMOOTH='on'/'off', B_SMOOTH_OBJS='a,b' — 'on'이면 원래 면 음영을 저장하고 부드럽게, 'off'면 되돌림."""
import os, bpy, numpy as np
mode = os.environ.get('B_SMOOTH', 'on')
for n in os.environ.get('B_SMOOTH_OBJS', '').split(','):
    o = bpy.data.objects.get(n)
    if not o:
        continue
    me = o.data
    if mode == 'on':
        a = np.zeros(len(me.polygons), bool); me.polygons.foreach_get('use_smooth', a)
        o['b_smooth_orig'] = a.astype(np.int8).tobytes().hex()
        me.polygons.foreach_set('use_smooth', np.ones(len(me.polygons), bool))
    elif 'b_smooth_orig' in o:
        a = np.frombuffer(bytes.fromhex(o['b_smooth_orig']), np.int8).astype(bool)
        me.polygons.foreach_set('use_smooth', a); del o['b_smooth_orig']
    me.update()
    print('smooth', mode, n)
