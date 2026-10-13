"""워커 A(비평 6): 아펜니노 봉우리(L01_*)를 땅 메시 T_land에 합침 — 봉우리와 능선이 같은 물체가 되어 밑동의 윤곽선(물체 경계 선)이 사라지고
'탁자 위 바위' 대신 능선에서 솟은 산으로 읽힘. 봉우리 물체는 지우지 않고 렌더에서만 숨김(다시 돌릴 때 원본).
T_land를 다시 만들 때마다(terrain_mesh2.py 뒤) 이 스크립트를 다시 돌림. 봉우리 자리·크기는 그대로(화면 상자 변화 없음).
"""
import bpy
import bmesh
import numpy as np
ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_A/'
U = bpy.data.texts['asset_utils.py'].as_module()
_D = np.load(ROOT + 'assets/terrain_hf.npz')
_HG = (_D['h_rel'] if 'h_rel' in _D.files else _D['h']).astype(np.float64); _G0 = float(_D['u'][0, 0]); _GS = float(_D['u'][1, 0] - _D['u'][0, 0])


def _h_world(P):
    uv = U.project_pts(np.c_[P[:, :2], np.zeros(len(P))])
    fi = (uv[:, 0] - _G0) / _GS; fj = (uv[:, 1] - _G0) / _GS
    i0 = np.clip(np.floor(fi).astype(int), 0, _HG.shape[0] - 2); j0 = np.clip(np.floor(fj).astype(int), 0, _HG.shape[1] - 2)
    a = np.clip(fi - i0, 0, 1); b = np.clip(fj - j0, 0, 1)
    return (_HG[i0, j0] * (1 - a) + _HG[i0 + 1, j0] * a) * (1 - b) + (_HG[i0, j0 + 1] * (1 - a) + _HG[i0 + 1, j0 + 1] * a) * b


land = bpy.data.objects['T_land']
if land.get('peaks_merged'):
    print('mtn merge: already merged')
else:
    dg = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new(); bm.from_mesh(land.data)
    n0 = len(bm.faces); Minv = land.matrix_world.inverted()
    peaks = [o for o in bpy.data.objects if o.name.startswith('L01_') and o.type == 'MESH']
    for o in peaks:
        me = o.evaluated_get(dg).to_mesh()
        me2 = me.copy(); o.evaluated_get(dg).to_mesh_clear()
        me2.transform(o.matrix_world)
        # 능선 위에 걸침: z' = z + 땅높이·(1 - z/zmax) — 꼭대기는 그대로(화면 상자 유지), 밑동은 능선 면에 얹혀 묻힌 작은 봉우리가 혹처럼 뚫고 나오지 않음
        co = np.empty(len(me2.vertices) * 3); me2.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
        zmax = co[:, 2].max(); ht = _h_world(co)
        z0_ = co[:, 2].copy()
        co[:, 2] = z0_ + ht * np.clip(1 - z0_ / zmax, 0, 1) - 0.3 * np.clip(1 - z0_ / (0.1 * zmax), 0, 1) ** 2   # 둘레(잘린 원 테두리)는 땅 속으로 0.3 — 술 같은 테두리 선 없앰
        me2.vertices.foreach_set('co', co.ravel()); me2.update()
        me2.transform(Minv)
        # 작은 떨어진 조각(높이장 원형 자르기에서 남은 섬) 지움
        _b = bmesh.new(); _b.from_mesh(me2); _b.faces.ensure_lookup_table()
        seen = set(); kill = []
        for f in _b.faces:
            if f.index in seen:
                continue
            comp = []; stack = [f]; seen.add(f.index)
            while stack:
                g = stack.pop(); comp.append(g)
                for e in g.edges:
                    for h in e.link_faces:
                        if h.index not in seen:
                            seen.add(h.index); stack.append(h)
            if len(comp) < 400:
                kill += comp
        if kill:
            bmesh.ops.delete(_b, geom=kill, context='FACES')
        _b.to_mesh(me2); _b.free()
        for p in me2.polygons:
            p.use_smooth = False
        bm.from_mesh(me2); bpy.data.meshes.remove(me2)
        o.hide_render = True
    bm.to_mesh(land.data); bm.free()
    land['peaks_merged'] = True
    print('mtn merge: peaks', len(peaks), 'faces', n0, '->', len(land.data.polygons))
