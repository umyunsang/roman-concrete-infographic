"""assets/peaks/*.npz → 봉우리 오브젝트 L01_<이름> (40_REGION) 를 헤더 아래 띠에 배치.
- 실제 방위대로 놓음(지리 동·북 → 세계: 화면 위 = 방위 29.8°)
- 화면 상자에 가로는 꽉, 세로는 높이 배율(z)로 맞춤 → 화산처럼 솟은 봉우리, 꼭대기 v ≥ 262(헤더 아래)
옛 L01_apennines(평평한 판)는 지움. Blender에서: exec(open(<이 파일>).read())
"""
import math
import bpy
import numpy as np

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_B/'
U = bpy.data.texts['asset_utils.py'].as_module()
exec(open(ROOT + 'scripts/assets/place.py').read())
BOXES = {   # 오브젝트 이름: (봉우리 고도 자료, z 회전°, 화면 상자 x0, 꼭대기 v, x1, 기슭 v) — 좁고 겹치는 기슭으로 이어진 산줄기
    'terminillo':   ('corno_grande', 200, (12, 262, 128, 336)),   # R13 깨진 덩어리처럼 보여 다른 실제 봉우리 자료(회전)로     # 16:42 강 발원 골짜기 왼쪽 산 — 기슭이 DETAIL ① 모형 뒤로 살짝 들어감
    'gennaro':      ('gennaro', 0, (225, 300, 405, 440)),
    'velino_w':     ('velino', 70, (352, 276, 505, 396)),
    'corno_grande': ('corno_grande', 0, (500, 262, 690, 366)),
    'velino':       ('velino', 0, (690, 266, 860, 392)),
    'autore':       ('autore', 0, (835, 274, 985, 410)),
    'viglio':       ('viglio', 0, (945, 262, 1110, 420)),
    'terminillo_e': ('terminillo', 150, (1060, 268, 1190, 402)),   # 수도교(클라우디아) 수원이 이 산 기슭
}
B = math.radians(29.8)
up = np.array([-1.0, 1.0]) / math.sqrt(2); right = np.array([1.0, 1.0]) / math.sqrt(2)
U.remove_obj('L01_apennines')
out = {}
for k in [o.name for o in bpy.data.objects if o.name.startswith('L01_')]:
    U.remove_obj(k)
for name, (src, rotz, box) in BOXES.items():
    D = np.load(ROOT + 'assets/peaks/' + src + '.npz')
    X, Y, H = D['x'], D['y'], D['h']
    n = X.shape[0]
    ca, sa = math.cos(math.radians(rotz)), math.sin(math.radians(rotz))
    E, N = X.ravel() * ca - Y.ravel() * sa, X.ravel() * sa + Y.ravel() * ca
    along_up = E * math.sin(B) + N * math.cos(B)
    along_r = E * math.cos(B) - N * math.sin(B)
    W = along_up[:, None] * up + along_r[:, None] * right
    verts = np.c_[W * 10.0, H.ravel() * 6.0]
    idx = np.arange(n * n).reshape(n, n)
    r = np.hypot(X, Y)
    cell = (r[:-1, :-1] <= 1.0) & (r[1:, :-1] <= 1.0) & (r[:-1, 1:] <= 1.0) & (r[1:, 1:] <= 1.0)
    ci, cj = np.nonzero(cell)
    a = idx[ci, cj]; b = idx[ci + 1, cj]; c = idx[ci + 1, cj + 1]; d = idx[ci, cj + 1]
    faces = np.concatenate([np.stack([a, b, c], 1), np.stack([a, c, d], 1)])
    used = np.unique(faces); remap = -np.ones(n * n, dtype=np.int64); remap[used] = np.arange(len(used))
    nm = 'L01_' + name
    ob = U.mesh_from_arrays(nm, verts[used], remap[faces], U.coll('40_REGION'))
    import bmesh
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data); bm.free()
    for p in ob.data.polygons:
        p.use_smooth = False
    ob.location = U.pt_to_world((box[0] + box[2]) / 2, box[3] - 10, 0)
    for _ in range(4):
        fit_contain(ob, box, align='bottom', step=2)
        bb = U.screen_bbox(ob, 2)
        # 가로가 남으면 xy 키우고, 세로는 z로 꼭대기를 상자 위에 맞춤
        kx = (box[2] - box[0]) / max(1e-6, bb[2] - bb[0])
        kz = (box[3] - box[1]) / max(1e-6, bb[3] - bb[1])
        ob.scale = (ob.scale.x * kx, ob.scale.y * kx, ob.scale.z * kz)
        bpy.context.view_layer.update()
    if ob.scale.z / ob.scale.x > 1.5:            # 바늘처럼 뾰족해지지 않게 높이 비율 1.5까지
        ob.scale = (ob.scale.x, ob.scale.y, ob.scale.x * 1.5)
        bpy.context.view_layer.update()
    got = fit_contain(ob, (box[0], box[1] - 400, box[2], box[3]), align='bottom', step=2)
    for _ in range(6):
        if got[1] >= box[1] - 0.5:
            break
        ob.scale = (ob.scale.x, ob.scale.y, ob.scale.z * 0.92)
        bpy.context.view_layer.update()
        got = fit_contain(ob, (box[0], box[1] - 400, box[2], box[3]), align='bottom', step=2)
    out[nm] = (got, len(faces), round(ob.scale.z / ob.scale.x, 2))
for k, v in out.items():
    print(k, v)
