"""지형: 땅판(T_ground), 티레니아해(L10_sea), 티베르강(L02_tiber).
입력: assets/terrain_polys.json (scripts/assets/terrain_polys.py로 만든 화면 pt 다각형)
Blender에서: exec(open(<이 파일>).read())  — 다시 돌리면 같은 이름 오브젝트를 지우고 새로 만든다.
모두 low_terrain=True (글 자리 검사에서 '낮은 지형'으로 허용).
"""
import bpy
import json
import math
import numpy as np

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/'
U = bpy.data.texts['asset_utils.py'].as_module()
D = json.load(open(ROOT + 'assets/terrain_polys.json'))
C = U.coll('30_TERRAIN')

SEA_Z = -0.7      # 바다 수면 (R6: 해안 벽 낮게)
RIVER_Z = -0.4    # 강 수면
SLAB_BOTTOM = -1.6

def to_world(uv, z):
    """화면 pt → 땅(z=0) 위 점의 xy에 높이 z (원근 카메라: 시야 영역 = 사다리꼴 땅)."""
    w = U.pts_to_world(np.asarray(uv, dtype=np.float64), 0.0)
    w = np.array(w)
    w[..., 2] = z
    return w


def inside(poly, x, y):
    """짝홀 규칙 점-다각형 (벡터화). poly: (N,2)"""
    poly = np.asarray(poly)
    xi, yi = poly[:, 0], poly[:, 1]
    xj, yj = np.roll(xi, 1), np.roll(yi, 1)
    res = np.zeros(x.shape, dtype=bool)
    for a, b, c, d in zip(xi, yi, xj, yj):
        cond = ((b > y) != (d > y))
        with np.errstate(divide='ignore', invalid='ignore'):
            xint = (c - a) * (y - b) / (d - b + 1e-12) + a
        res ^= cond & (x < xint)
    return res


def dist_to_poly_edges(poly, x, y):
    poly = np.asarray(poly)
    best = np.full(x.shape, 1e9)
    a = poly[:-1]
    b = poly[1:]
    for (ax, ay), (bx, by) in zip(a, b):
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy + 1e-12
        t = np.clip(((x - ax) * dx + (y - ay) * dy) / L2, 0, 1)
        px, py = ax + t * dx, ay + t * dy
        best = np.minimum(best, np.hypot(x - px, y - py))
    return best


def grid_surface(name, ring, step, z0, ripple, pad=8.0):
    """다각형 ring(화면 pt) 안쪽 + pad 만큼 넓힌 영역의 격자 수면."""
    ring = np.asarray(ring)
    u0, v0 = ring.min(0) - pad
    u1, v1 = ring.max(0) + pad
    nu = int((u1 - u0) / step) + 1
    nv = int((v1 - v0) / step) + 1
    uu, vv = np.meshgrid(u0 + np.arange(nu) * step, v0 + np.arange(nv) * step, indexing='ij')
    ins = inside(ring, uu, vv)
    near = dist_to_poly_edges(ring, uu, vv) < pad
    keep_v = ins | near
    # 면: 네 꼭짓점 중 하나라도 keep이면 그 칸 유지
    k = keep_v
    cell = k[:-1, :-1] | k[1:, :-1] | k[:-1, 1:] | k[1:, 1:]
    idx = -np.ones((nu, nv), dtype=np.int64)
    used = np.zeros((nu, nv), dtype=bool)
    used[:-1, :-1] |= cell
    used[1:, :-1] |= cell
    used[:-1, 1:] |= cell
    used[1:, 1:] |= cell
    idx[used] = np.arange(used.sum())
    uvs = np.stack([uu[used], vv[used]], 1)
    z = z0 + ripple(uvs[:, 0], uvs[:, 1])
    verts = to_world(uvs, 0.0)
    verts[:, 2] = z
    ci, cj = np.nonzero(cell)
    faces = np.stack([idx[ci, cj], idx[ci + 1, cj], idx[ci + 1, cj + 1], idx[ci, cj + 1]], 1)
    ob = U.mesh_from_arrays(name, verts, faces, C)
    ob['low_terrain'] = True
    return ob


def sea_ripple(u, v):
    # 해안과 평행한 긴 물결 + 교차 잔물결 + 저주파 흔들림
    a = 0.055 * np.sin(u * 0.045 + v * 0.20 + 0.8 * np.sin(u * 0.011))
    b = 0.03 * np.sin(u * 0.13 - v * 0.09 + 1.7)
    c = 0.02 * np.sin(u * 0.31 + v * 0.27) * np.sin(v * 0.05)
    return a + b + c


def river_ripple(u, v):
    a = 0.035 * np.sin(v * 0.33 + u * 0.18 + 0.6 * np.sin(u * 0.07))
    b = 0.02 * np.sin(u * 0.41 - v * 0.23)
    return a + b


def build_ground():
    U.remove_obj('T_ground')
    tris = np.array(D['land_tris'])          # (n,3,2)
    pts = tris.reshape(-1, 2)
    keyed = {}
    verts, faces = [], []

    def vid(p, z):
        k = (round(p[0], 3), round(p[1], 3), z)
        if k not in keyed:
            keyed[k] = len(verts)
            verts.append(to_world(np.array(p), z))
        return keyed[k]

    for t in tris:
        a, b, c = (vid(p, 0.0) for p in t)
        # 위를 보도록 감기 방향 확인 (세계 좌표에서 법선 z>0)
        pa, pb, pc = verts[a], verts[b], verts[c]
        n = np.cross(pb - pa, pc - pa)
        faces.append((a, b, c) if n[2] > 0 else (a, c, b))
    # 둘레 벽(해안·강둑): 모든 고리
    for poly in D['land']:
        for ring in poly:
            ring = ring[:-1] if ring[0] == ring[-1] else ring
            n = len(ring)
            for i in range(n):
                p, q = ring[i], ring[(i + 1) % n]
                a, b = vid(p, 0.0), vid(q, 0.0)
                c, d = vid(q, SLAB_BOTTOM), vid(p, SLAB_BOTTOM)
                faces.append((a, d, c, b))
    ob = U.mesh_from_arrays('T_ground', np.array(verts), faces, C)
    ob['low_terrain'] = True
    # 벽 법선 바깥으로 정리
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    return ob


def tri_surface(name, uv, faces, z0):
    # WATER_TRI: 다각형을 직접 삼각분할한 평평한 수면(가장자리 계단 없음)
    W = U.pts_to_world(np.asarray(uv, float), 0.0); W[:, 2] = z0
    ob = U.mesh_from_arrays(name, W, np.asarray(faces, np.int64), C)
    ob['low_terrain'] = True
    return ob


def build():
    g = build_ground()
    WT = np.load(ROOT + 'assets/water_tri.npz')
    s = tri_surface('L10_sea', WT['sea_uv'], WT['sea_f'], SEA_Z)
    r = tri_surface('L02_tiber', WT['river_uv'], WT['river_f'], RIVER_Z)
    # R10 하구 30pt에서 강 수면을 바다 높이로 부드럽게
    _t = np.clip(WT['river_dsea'] / 30.0, 0, 1)
    co = np.empty(len(r.data.vertices) * 3); r.data.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    co[:, 2] = SEA_Z + (RIVER_Z - SEA_Z) * _t * _t * (3 - 2 * _t)
    r.data.vertices.foreach_set('co', co.ravel()); r.data.update()
    for o in (g, s, r):
        for p in o.data.polygons:
            p.use_smooth = False
    return g, s, r


if __name__ == '__main__' or True:
    objs = build()
    print([(o.name, len(o.data.polygons), U.tri_count(o)) for o in objs])
