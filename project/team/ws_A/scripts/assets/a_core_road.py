"""워커 A — CORE 흐름 길 재설계(비평 1: I1). fill_plains.py 안에서 exec로 불림(ROADS·h_xy·wet_uv·poly_dist·BRIDGE_SPANS·build·U 공유).
로마 가도 단면 그대로: 돋운 노반(agger, 밝은 흙 0.86) 위에 현무암 다각 포장석(basoli, 진한 0.30) + 양쪽 흰 연석(crepido).
진행 방향 신호(글 아님): 포장 위 흰 돌 셰브런(>) 상감을 일정 간격으로 — ①→⑤ 방향을 가리킴(Lu et al. CHI 2020: 반시계 흐름은 명시 신호 필요).
시작 ①: 채석장 앞 둥근 포장 광장 + 가운데 이정표 기둥(miliarium aureum 격) / 끝 ⑤: 둥근 도착 광장 + 길을 가로지르는 개선문(fornix).
물체: R_core_bed · R_core_road(포장석) · R_core_curb · R_core_chev · L13_core_start_column · L13_core_arrival_arch
"""
import math
import bmesh
import numpy as np
from mathutils import Vector

ZB = 0.12            # 노반 높이(땅 위)
CH_SP = 6.2          # 셰브런 간격(세계 단위)
CH_FIRST = 4.5       # 첫 셰브런(광장 끝 뒤)


def _core_build():
    name = 'R_core_road'
    pts_uv = ROADS[name]
    P = U.pts_to_world(np.asarray(pts_uv, float), 0.0)[:, :2]
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
    s = np.arange(0, seg[-1], 0.45)
    C = np.c_[np.interp(s, seg, P[:, 0]), np.interp(s, seg, P[:, 1])]
    Tg = np.gradient(C, axis=0); Tg /= np.linalg.norm(Tg, axis=1, keepdims=True) + 1e-9
    N = np.c_[-Tg[:, 1], Tg[:, 0]]
    zc, uvc = h_xy(C)
    keep = np.ones(len(C), bool)
    for i in range(len(C)):
        if wet_uv(uvc[i, 0], uvc[i, 1]):
            keep[i] = False; continue
        if any(float(poly_dist(np.array([a_, b_]), np.array([uvc[i, 0]]), np.array([uvc[i, 1]]))[0]) < 4 for a_, b_ in BRIDGE_SPANS):
            keep[i] = False
    W = np.array([road_width(name, uvc[i, 0], uvc[i, 1]) for i in range(len(C))])
    BV, BF = [], []          # 노반
    SV, SF = [], []          # 포장석
    KV, KF = [], []          # 연석
    HV, HF = [], []          # 셰브런

    def box(V_, F_, cx, cy, tx, ty, nx, ny, L, Wd, z0, hgt):
        base = len(V_)
        for sz in (0.0, hgt):
            for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                V_.append((cx + tx * a * L / 2 + nx * b * Wd / 2, cy + ty * a * L / 2 + ny * b * Wd / 2, z0 + sz))
        F_.extend([(base + 4, base + 5, base + 6, base + 7), (base, base + 1, base + 5, base + 4), (base + 1, base + 2, base + 6, base + 5),
                   (base + 2, base + 3, base + 7, base + 6), (base + 3, base, base + 4, base + 7)])

    def ribbon(V_, F_, run, prof):
        """run: 표본 번호 목록, prof: [(가로 위치 함수(w), 높이)] 단면 → 이어진 띠"""
        base = len(V_); m = len(prof)
        for i in run:
            cx, cy = C[i]; nx, ny = N[i]; z0 = zc[i]
            for fa, dz in prof:
                a = fa(W[i])
                zz = float(h_xy(np.array([[cx + nx * a, cy + ny * a]]))[0][0]) if dz < 0 else z0
                V_.append((cx + nx * a, cy + ny * a, zz + (dz if dz >= 0 else 0.0) + (-0.05 if dz < 0 else 0.0)))
        for j in range(len(run) - 1):
            for k in range(m - 1):
                a0 = base + j * m + k; b0 = a0 + m
                F_.append((a0, a0 + 1, b0 + 1, b0))

    runs, cur = [], []
    for i in range(len(C)):
        if keep[i]:
            cur.append(i)
        elif cur:
            runs.append(cur); cur = []
    if cur:
        runs.append(cur)
    for run in runs:
        if len(run) < 2:
            continue
        # 노반: 바깥 비탈(땅 높이) → 윗면 → 반대 비탈
        ribbon(BV, BF, run, [(lambda w: -(w / 2 + 0.34), -1), (lambda w: -(w / 2 + 0.27), ZB), (lambda w: (w / 2 + 0.27), ZB), (lambda w: (w / 2 + 0.34), -1)])
        # 연석 두 줄(사각 단면)
        for sg in (-1, 1):
            ribbon(KV, KF, run, [(lambda w, sg=sg: sg * (w / 2 + 0.01), ZB), (lambda w, sg=sg: sg * (w / 2 + 0.01), ZB + 0.15),
                                 (lambda w, sg=sg: sg * (w / 2 + 0.27), ZB + 0.15), (lambda w, sg=sg: sg * (w / 2 + 0.27), ZB)])
        # 포장석: 엇갈린 줄눈
        for i in run:
            cx, cy = C[i]; tx, ty = Tg[i]; nx, ny = N[i]; w = W[i]
            nac = max(4, int(round(w / 0.55)))
            off = (i % 2) * 0.5
            for k in range(nac):
                a = (-w / 2) + (k + 0.5 + off * 0.5) * w / nac
                if abs(a) > w / 2 - 0.1:
                    continue
                box(SV, SF, cx + nx * a, cy + ny * a, tx, ty, nx, ny, 0.40 + rng.uniform(-0.04, 0.03), w / nac - 0.07,
                    zc[i] + ZB, 0.035 + rng.uniform(0, 0.02))
    # 셰브런(>) — 진행 방향(경로 순서 = ①→⑤)을 가리킴
    n_ch = 0
    for sc_ in np.arange(CH_FIRST, s[-1] - 3.0, CH_SP):
        i = int(np.searchsorted(s, sc_))
        lo_, hi_ = max(0, i - 4), min(len(C) - 1, i + 4)
        if not keep[lo_:hi_ + 1].all():
            continue
        cx, cy = C[i]; tx, ty = Tg[i]; nx, ny = N[i]; w = W[i]
        hw = 0.38 * w; d = 0.55 * w; th = 0.62; a0 = d / 2
        poly = [(a0, 0), (a0 - d, hw), (a0 - d - th, hw), (a0 - th, 0), (a0 - d - th, -hw), (a0 - d, -hw)]
        quads = [(0, 1, 2, 3), (0, 3, 4, 5)]
        b = len(HV)
        for (al, ac) in poly:
            x, y = cx + tx * al + nx * ac, cy + ty * al + ny * ac
            z = float(h_xy(np.array([[x, y]]))[0][0])
            z = max(z, zc[i])
            HV.append((x, y, z + ZB + 0.025))
        for (al, ac) in poly:
            x, y = cx + tx * al + nx * ac, cy + ty * al + ny * ac
            z = float(h_xy(np.array([[x, y]]))[0][0]); z = max(z, zc[i])
            HV.append((x, y, z + ZB + 0.085))
        for q in quads:
            HF.append(tuple(b + 6 + k for k in q))
        for k in range(6):
            HF.append((b + k, b + (k + 1) % 6, b + 6 + (k + 1) % 6, b + 6 + k))
        n_ch += 1
    # 시작·끝 광장
    def plaza(center_xy, R, tag, gap_dir=None, gap_w=0.0):
        cx, cy = center_xy
        z0 = float(h_xy(np.array([[cx, cy]]))[0][0])
        # 노반 원판(가장자리 비탈)
        nseg = 40; b = len(BV)
        BV.append((cx, cy, z0 + ZB))
        for r_, dz in ((R + 0.27, ZB), (R + 0.36, -1)):
            for k in range(nseg):
                a = 2 * math.pi * k / nseg; x, y = cx + r_ * math.cos(a), cy + r_ * math.sin(a)
                zz = float(h_xy(np.array([[x, y]]))[0][0])
                BV.append((x, y, (max(zz, z0) + ZB) if dz >= 0 else zz - 0.05))
        for k in range(nseg):
            BF.append((b, b + 1 + k, b + 1 + (k + 1) % nseg))
            BF.append((b + 1 + k, b + 1 + nseg + k, b + 1 + nseg + (k + 1) % nseg, b + 1 + (k + 1) % nseg))
        # 둥근 연석
        b = len(KV)
        for k in range(nseg):
            a = 2 * math.pi * k / nseg
            for r_, zz in ((R, ZB), (R, ZB + 0.15), (R + 0.26, ZB + 0.15), (R + 0.26, ZB)):
                KV.append((cx + r_ * math.cos(a), cy + r_ * math.sin(a), z0 + zz))
        for k in range(nseg):
            if gap_dir is not None:   # 길이 드나드는 입구엔 연석 없음(흰 선이 길을 가로지르지 않게)
                am = 2 * math.pi * (k + 0.5) / nseg
                if math.cos(am - gap_dir) * R > 0 and abs(math.sin(am - gap_dir)) * R < gap_w / 2 + 0.35:
                    continue
            for j in range(3):
                a0 = b + 4 * k + j; b0 = b + 4 * ((k + 1) % nseg) + j
                KF.append((a0, b0, b0 + 1, a0 + 1))
        # 동심원 포장석
        for r_ in np.arange(0.45, R - 0.15, 0.5):
            nn = max(5, int(2 * math.pi * r_ / 0.5))
            for k in range(nn):
                a = 2 * math.pi * (k + 0.5 * (int(r_ * 2) % 2)) / nn
                tx, ty = -math.sin(a), math.cos(a); nx, ny = math.cos(a), math.sin(a)
                box(SV, SF, cx + r_ * nx, cy + r_ * ny, tx, ty, nx, ny, 2 * math.pi * r_ / nn - 0.07, 0.43, z0 + ZB, 0.035 + rng.uniform(0, 0.02))
        return z0

    t0 = Tg[0]; t1 = Tg[-1]
    RP = 2.3
    p_start = C[0] - t0 * 0.4; p_end = C[-1] + t1 * 0.4
    zs = plaza(p_start, RP, 'start', math.atan2(t0[1], t0[0]), float(W[0])); ze = plaza(p_end, RP, 'end', math.atan2(-t1[1], -t1[0]), float(W[-1]))
    for nm in ('R_core_bed', 'R_core_curb', 'R_core_chev', 'L13_core_start_column', 'L13_core_arrival_arch'):
        U.remove_obj(nm)
    bed = build('R_core_bed', BV, BF, '35_FIELDS_ROADS', low=True)
    road = build(name, SV, SF, '35_FIELDS_ROADS', low=True)
    curb = build('R_core_curb', KV, KF, '35_FIELDS_ROADS', low=True)
    chev = build('R_core_chev', HV, HF, '35_FIELDS_ROADS', low=True)
    for o_ in (bed, curb):
        for p_ in o_.data.polygons:
            p_.use_smooth = False

    # 이정표 기둥(시작): 받침 2단 + 원기둥 + 머리
    bm = bmesh.new()
    def cyl(r1, r2, z0_, h_, seg=16):
        rr = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r1, radius2=r2, depth=h_)
        for v in rr['verts']:
            v.co.z += z0_ + h_ / 2
    def cube(sx, sy, z0_, h_):
        rr = bmesh.ops.create_cube(bm, size=1.0)
        for v in rr['verts']:
            v.co = Vector((v.co.x * sx, v.co.y * sy, z0_ + (v.co.z + 0.5) * h_))
    cube(1.1, 1.1, 0.0, 0.24); cube(0.8, 0.8, 0.24, 0.2)
    cyl(0.30, 0.26, 0.44, 2.2); cube(0.66, 0.66, 2.64, 0.16); cyl(0.2, 0.06, 2.8, 0.26, 12)
    me = bpy.data.meshes.new('L13_core_start_column'); bm.to_mesh(me); bm.free()
    col = bpy.data.objects.new('L13_core_start_column', me); U.coll('40_REGION').objects.link(col)
    col.location = (p_start[0], p_start[1], zs + ZB - 0.02)
    for p_ in me.polygons:
        p_.use_smooth = False

    # 도착 개선문(끝): 길을 가로지름, 두 기둥 + 반원 아치 + 처마 + 다락
    w_end = float(W[-1]); Wd = w_end + 1.3; wo = w_end + 0.25; hs = 1.15; H = hs + wo / 2 + 0.45; DEP = 0.9
    tt = Vector((t1[0], t1[1], 0)); nn_ = Vector((-t1[1], t1[0], 0))
    bm = bmesh.new()
    def prism(poly2):   # poly2: [(가로, z)] → 길 방향(tt)으로 두께 DEP
        f = [bm.verts.new(nn_ * a + tt * (-DEP / 2) + Vector((0, 0, z))) for a, z in poly2]
        b_ = [bm.verts.new(nn_ * a + tt * (DEP / 2) + Vector((0, 0, z))) for a, z in poly2]
        bm.faces.new(f); bm.faces.new(list(reversed(b_)))
        k_ = len(poly2)
        for i_ in range(k_):
            j_ = (i_ + 1) % k_
            bm.faces.new((f[i_], f[j_], b_[j_], b_[i_]))
    arc = [(wo / 2 * math.cos(a), hs + wo / 2 * math.sin(a)) for a in np.linspace(math.pi, math.pi / 2, 9)]
    prism([(-Wd / 2, 0), (-wo / 2, 0)] + arc + [(0, H), (-Wd / 2, H)])
    arcR = [(wo / 2 * math.cos(a), hs + wo / 2 * math.sin(a)) for a in np.linspace(math.pi / 2, 0, 9)]
    prism([(0, H), (0, hs + wo / 2)] + arcR[1:] + [(wo / 2, 0), (Wd / 2, 0), (Wd / 2, H)])
    def slab(a0_, a1_, z0_, z1_, d_):
        rr = bmesh.ops.create_cube(bm, size=1.0)
        for v in rr['verts']:
            p = nn_ * ((a0_ + a1_) / 2 + v.co.x * (a1_ - a0_)) + tt * (v.co.y * d_) + Vector((0, 0, (z0_ + z1_) / 2 + v.co.z * (z1_ - z0_)))
            v.co = p
    slab(-Wd / 2 - 0.12, Wd / 2 + 0.12, H, H + 0.16, DEP + 0.2)        # 처마
    slab(-Wd / 2 + 0.1, Wd / 2 - 0.1, H + 0.16, H + 0.75, DEP - 0.1)    # 다락
    for sg in (-1, 1):                                                  # 기둥 앞 붙임 기둥(pilaster)
        slab(sg * (Wd / 2 - 0.32) - 0.12, sg * (Wd / 2 - 0.32) + 0.12, 0.0, H, DEP + 0.14)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new('L13_core_arrival_arch'); bm.to_mesh(me); bm.free()
    arch = bpy.data.objects.new('L13_core_arrival_arch', me); U.coll('40_REGION').objects.link(arch)
    pa = C[-1] - t1 * (RP + 1.1)
    za = float(h_xy(np.array([pa]))[0][0])
    arch.location = (pa[0], pa[1], za + ZB - 0.02)
    for p_ in me.polygons:
        p_.use_smooth = False
    print('core road: chevrons', n_ch, 'tris bed/road/curb/chev', U.tri_count(bed), U.tri_count(road), U.tri_count(curb), U.tri_count(chev),
          'start col bbox', [round(x, 1) for x in U.screen_bbox(col, 1)], 'arch bbox', [round(x, 1) for x in U.screen_bbox(arch, 1)])
    return road


_core_obj = _core_build()
