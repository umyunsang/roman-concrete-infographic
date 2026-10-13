"""워커 B: 바다 속 물체(실험실 섬·등대·방파제·항구 기둥)의 바닥이 z≈0, 수면은 -0.7 → 물 위 0.7에 떠 있었음(그림자가 띄워 보임).
바닥층 꼭짓점만 아래로 늘여(위쪽 모양·화면 자리는 그대로) 수면 아래 -0.85까지 잠기게. 한 번만(o['b_sunk']).
"""
import bpy
import numpy as np
SEA_Z = -0.7
SPEC = {'L09_portus_lighthouse': 0.15, 'L09_portus_mole': 0.12, 'L12_harbor_pilae': 0.12}
for n, band in SPEC.items():
    o = bpy.data.objects.get(n)
    if not o or o.get('b_sunk'):
        continue
    me = o.data
    M = np.array(o.matrix_world); Mi = np.linalg.inv(M)
    co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    W = co @ M[:3, :3].T + M[:3, 3]
    z = W[:, 2]
    zmin = float(z.min())
    t = np.clip((z - zmin) / band, 0, 1)          # 0 = 바닥, 1 = 띠 위
    W[:, 2] = z - (zmin - (SEA_Z - 0.15)) * (1 - t)
    co2 = W @ Mi[:3, :3].T + Mi[:3, 3]
    me.vertices.foreach_set('co', co2.ravel()); me.update()
    o['b_sunk'] = True
    print('sunk', n, 'zmin', round(zmin, 3), '->', round(float(W[:, 2].min()), 3))
