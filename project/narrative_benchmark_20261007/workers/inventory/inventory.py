"""inventory.py - list every render-visible mesh of a poster blend and group them into review assets.

Read-only: never saves the blend. Run headless:
  Blender -b <in.blend> --factory-startup --python inventory.py -- <out_inventory.json> [id_pass_prefix]

Per object: name, type, collections, faces (base / evaluated), materials (name, diffuse hex sRGB, linear,
faces using it), projected screen box (pt, all evaluated vertices, clipped to the 1191x1684 frame) and visible
screen area / visible box measured from an object-ID render (Workbench FLAT + OBJECT colour, no AA, same camera,
same two-pass split as integrate_assets.render_two_pass: map pass, then 80_SHAPES/81_NOSHADOW/85_HEADER overlay on top).

Assets: ordered name rules (ASSET_RULES). Rules with split=True are cut into screen regions by clustering the
mesh islands (fields, core road). Water marks are assigned to the water body directly under each island.
Any render-visible mesh no rule claims becomes its own 'unmatched' asset (never silently dropped).
Importable: runpy.run_path(this)['build_inventory'](id_prefix) returns the inventory dict and restores the scene.
"""
import bpy, json, math, re, sys, time, hashlib
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

W_PT, H_PT = 1191, 1684
OVERLAY_COLLECTIONS = {'80_SHAPES', '81_NOSHADOW', '85_HEADER'}   # same set as integrate_assets.py
RENDERABLE = {'MESH', 'CURVE', 'FONT', 'SURFACE', 'META'}
ROLE_ORDER = ['CORE', 'DETAIL', 'SUPPORT', 'BASIC', '지물', '배경', '도형']

# (id, Korean name, role, kind, [object name regexes], options)
ASSET_RULES = [
    ('core1_modern_building', '① 현대 철근 콘크리트 건물(녹물·금)', 'CORE', '①번 그림 · 철근이 있어도 금은 생기는데',
     [r'^NB_modern_building$', r'^R1_frame_rust$', r'^R3_frame_crack_col\d*$'], {}),
    ('core2_hot_mixing', '② 물을 붓자 열이 나는 배합 장면', 'CORE', '②번 그림 · 물을 넣자, 열이 났다',
     [r'^C2_hot_mixing$'], {}),
    ('detail_core3_lime_specimen', '③ 석회 알갱이 확대 개념 모형(큰 시편)', 'DETAIL', '③번 아래 · 석회 알갱이를 확대한 개념 모형',
     [r'^NB_lime_clast_specimen'], {}),
    ('detail_core4_three_cubes', '④ 금이 메워지는 순서 · 세 큐브', 'DETAIL', '④번 아래 · 메움 원리(물이 스밈→칼슘 이동→결정이 메움)',
     [r'^NB_core4_sequence', r'^R8_(water_step|crack_step|calcium_step|healed_step)\d*$',
      r'^R1_(water_in_crack|calcium_dot)\d*$'], {}),
    ('support_core5_lab', '⑤ 오늘의 실험실 · 금 메움 시편 두 개', 'SUPPORT', '⑤번 그림 · 사례 오늘의 실험실(MIT 2023)',
     [r'^R1_(specimen_|lab_bench|healed_clast|leak_)', r'^R3_(healed_fill|leak_crack)$'], {}),
    ('detail_d1_seawater', '재료 원리 · 해수 수조 속 광물 결정', 'DETAIL', '재료 원리 · 해수 속 광물 결정',
     [r'^D1_'], {}),
    ('landmark_lime_kiln', '석회 가마', '지물', '석회 가마(지명)', [r'^D2_lime_kiln$'], {}),
    ('detail_d2_making', '제작 원리 · 열과 석회 주사위', 'DETAIL', '제작 원리 · 열과 석회(+열 표시)',
     [r'^D2_'], {}),
    ('detail_d3_tower', '구조 원리 · 철근 없는 구조 탑', 'DETAIL', '구조 원리 · 위는 가볍게 아래는 두껍게(+누름 화살표)',
     [r'^D3_'], {}),
    ('detail_d4_crack_old', '(구) 균열 원리 D4 모형', 'DETAIL', '이전 판 D4 순서 모형', [r'^D4_'], {}),
    ('support_privernum', '프리베르눔 성벽 조각', 'SUPPORT', '사례 · 프리베르눔 성벽 조각', [r'^L11_privernum'], {}),
    ('support_ruin_observers', '유적 관찰 장면(연구자들)', 'SUPPORT', '사례 · 유적 관찰 장면', [r'^C5_researchers$'], {}),
    ('support_pompeii_site', '폼페이 공사현장(서기 79년)', 'SUPPORT', '사례 · 폼페이 공사현장 · 생석회 원료 더미',
     [r'^L08_pompeii_site$'], {}),
    ('support_harbor', '로마 항구(등대·방파 부두·바닷속 기둥)', 'SUPPORT', '사례 · 로마 항구 콘크리트',
     [r'^L09_portus_', r'^L12_harbor_pilae$'], {}),
    ('support_breakwater_block', '방파제 블록 개념 모형', 'SUPPORT', '방파제 블록 · 개념 모형', [r'^NB_marine_breakwater$'], {}),
    ('basic_recipe', '전제 · 로마 콘크리트란? 재료 그림(생석회·화산재 원뿔, 깬 돌·벽돌, 나무 틀)', 'BASIC',
     '맨 위 왼쪽 · 생석회 + 화산재 → 깬 돌·벽돌 + 틀에 부어 굳힘',
     [r'^H_lime', r'^H_ash', r'^H_stone', r'^H_mold'], {}),
    ('basic_sources', '전제 · 어떻게 알았나 그림(책 두 권, 코어 시료·돋보기, 작은 콜로세움)', 'BASIC',
     '맨 위 오른쪽 · 로마 때 기록 / 오늘의 연구 / 살펴볼 건물',
     [r'^H_book', r'^H_core_', r'^H_lens_', r'^H_colosseum'], {}),
    ('landmark_colosseum', '콜로세움(폐허·기단·경기장 흙)', '지물', '중심 건물',
     [r'^COL_', r'^R3_colosseum_podium$', r'^R4_arena_skin$'], {}),
    ('landmark_pantheon', '판테온(철근 없는 돔)', '지물', '판테온 · 철근 없는 돔', [r'^R8_pantheon$'], {}),
    ('milestone_1_to_2', '이정표 ①→②', '지물', '읽기 방향 이정표(석회암 기둥+화살표 판)', [r'^MS1_'], {}),
    ('milestone_2_to_34', '이정표 ②→③④', '지물', '읽기 방향 이정표(석회암 기둥+화살표 판)', [r'^MS2_'], {}),
    ('milestone_34_to_5', '이정표 ③④→⑤', '지물', '읽기 방향 이정표(석회암 기둥+화살표 판)', [r'^MS3_'], {}),
    ('landmark_aqueduct', '수도교(아쿠아 클라우디아)', '지물', '수도교', [r'^L05_'], {}),
    ('landmark_vesuvius', '베수비오 화산', '지물', '베수비오 화산', [r'^L07_'], {}),
    ('landmark_apennines', '아펜니노 산들', '지물', '아펜니노 산맥', [r'^L01_'], {}),
    ('landmark_pompeii_town', '폼페이 도시', '지물', '폼페이(지명)', [r'^L08_pompeii$'], {}),
    ('landmark_forum_old', '(구) 포룸 신전', '지물', '이전 판 포룸', [r'^L03_forum'], {}),
    ('landmark_palatine_old', '(구) 팔라티노', '지물', '이전 판 팔라티노', [r'^L04_palatine'], {}),
    ('landmark_lab_island_old', '(구) 실험실 섬', '지물', '이전 판 실험실 섬', [r'^S_lab_island$'], {}),
    ('trees', '나무 무리', '지물', '소나무·사이프러스', [r'^T_(pine|cypress)'], {'cluster_objects': 60.0}),
    ('fields', '밭(켄투리아티오)', '지물', '바둑판 밭·이랑', [r'^F_'], {'split': True, 'join_pt': 40.0}),
    ('road_core', '핵심 길(①~⑤를 잇는 길)', '지물', 'CORE 사이를 잇는 포장 길·도착 마당',
     [r'^R_core_road$', r'^R1_road_landing\d*$', r'^R1_road5_bed$'], {'split': True, 'join_pt': 8.0}),
    ('road_appia', '아피아 가도', '지물', '아피아 가도', [r'^R_via_appia$'], {}),
    ('road_ostiensis', '오스티아 가도(항구로 가는 길)', '지물', '항구로 가는 길', [r'^R_via_ostiensis$', r'^R_roadgeo_ostiensis_junction_fill$'], {}),
    ('bridge_north', '티베르강 북쪽 다리', '지물', '다리(난간 포함)', [r'^B_pons1'], {}),
    ('bridge_south', '티베르강 남쪽 다리', '지물', '다리(난간·서쪽 받침 포함)', [r'^B_pons2', r'^R4_bridge_west_bed$'], {}),
    ('water_tiber', '티베르강(+물결)', '지물', '강과 강 위 물결 무늬', [r'^L02_tiber$'], {'water_body': True}),
    ('water_sea', '티레니아해(+물결·해안선)', '지물', '바다와 물결·해안 무늬', [r'^L10_sea$'], {'water_body': True}),
    ('ground_land', '땅(지형 바탕)', '배경', '디오라마 땅', [r'^T_land$'], {}),
    ('header_gate', '제목 아치(헤더 문)', '도형', '제목 뒤 로마식 아치 틀', [r'^H_gate'], {}),
    ('shape_core1_marker', '① 번호 원판·밑줄', '도형', 'CORE ① 번호 원판과 제목 밑줄', [r'^S_core1_'], {}),
    ('shape_core2_marker', '② 번호 원판·밑줄', '도형', 'CORE ② 번호 원판과 제목 밑줄', [r'^S_core2_'], {}),
    ('shape_core3_marker', '③ 번호 원판·밑줄', '도형', 'CORE ③ 번호 원판과 제목 밑줄', [r'^S_core3_'], {}),
    ('shape_core4_marker', '④ 번호 원판·밑줄', '도형', 'CORE ④ 번호 원판과 제목 밑줄', [r'^S_core4_'], {}),
    ('shape_core5_marker', '⑤ 번호 원판·밑줄', '도형', 'CORE ⑤ 번호 원판과 제목 밑줄', [r'^S_core5_'], {}),
    ('shape_d2_leader', '석회 알갱이 지시선', '도형', '제작 원리 주사위 → 석회 알갱이 글', [r'^S_lead02$', r'^S_lead_dot2$'], {}),
    ('shape_d3_section', '구조 원리 단면도·지시선', '도형', '구조 탑 층별 단면과 이름표 지시선',
     [r'^S_sect', r'^S_lead(0[3-9]|1\d)$'], {}),
    ('shape_lead_old', '(구) 지시선', '도형', '이전 판 지시선', [r'^S_lead(00|01)$', r'^S_lead_dot[01]$'], {}),
    ('shape_pin_harbor', '항구 사례 핀', '도형', '사례 · 로마 항구 핀', [r'^S_pin_harbor'], {}),
    ('shape_pin_pompeii', '폼페이 사례 핀', '도형', '사례 · 폼페이 공사현장 핀', [r'^S_pin_pompeii'], {}),
    ('shape_pin_old', '(구) 사례 핀', '도형', '이전 판 핀', [r'^S_pin_(lab|privernum)'], {}),
    ('shape_timeline_old', '(구) 연표', '도형', '사용자가 지운 연표', [r'^S_time_'], {}),
    ('labels_test', '(시험용 3D 글자)', '도형', '70_LABELS_TEST', [r'^L_(C|D|P|S)\d?_'], {}),
]
WATER_MARK_RE = r'^W_water_marks'
SPLIT_MAX_PT = 420.0      # a region wider or taller than this is cut at the median of its longer axis
CLUSTER_CELL_PT = 18.0    # field/road island clustering grid (8-neighbour connectivity on occupied cells)
MIN_REGION_ISLANDS = 25   # smaller island clusters merge into the nearest region


# ---------------------------------------------------------------- camera helpers (from scripts/user_v8_13.py)
sc = bpy.context.scene
cam = sc.camera


def to_pt(p):
    """reference per-point projection (identical to user_v8_13.py / review_r8_fixes_v8_11.py)."""
    v = world_to_camera_view(sc, cam, p)
    return np.array((v.x * W_PT, (1 - v.y) * H_PT))


def to_pt_np(P):
    """vectorised world_to_camera_view (perspective or ortho) for N x 3 world points -> N x 2 pt."""
    P = np.asarray(P, dtype=np.float64).reshape(-1, 3)
    inv = np.array(cam.matrix_world.normalized().inverted())
    co = P @ inv[:3, :3].T + inv[:3, 3]
    frame = [np.array(v) for v in cam.data.view_frame(scene=sc)[:3]]
    if cam.data.type != 'ORTHO':
        frame = [(f / (f[2] / -1.0)) for f in frame]
        z = -co[:, 2]
        with np.errstate(divide='ignore', invalid='ignore'):
            x = co[:, 0] / z
            y = co[:, 1] / z
    else:
        x, y = co[:, 0], co[:, 1]
    min_x, max_x = frame[2][0], frame[1][0]
    min_y, max_y = frame[1][1], frame[0][1]
    u = (x - min_x) / (max_x - min_x)
    v = (y - min_y) / (max_y - min_y)
    return np.stack([u * W_PT, (1 - v) * H_PT], 1)


def srgb_hex(c):
    return '#%02X%02X%02X' % tuple(round(255 * (x * 12.92 if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055))
                                   for x in [min(max(v, 0.0), 1.0) for v in c[:3]])


def srgb_to_linear(s):
    return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4


# ---------------------------------------------------------------- visibility
def collection_hidden(ob):
    """True when every collection path holding the object is hide_render or excluded from the view layer."""
    vl = bpy.context.view_layer
    lc_by_name = {}

    def walk(lc, hidden):
        h = hidden or lc.exclude or lc.collection.hide_render
        lc_by_name[lc.collection.name] = h
        for ch in lc.children:
            walk(ch, h)
    walk(vl.layer_collection, False)
    return all(lc_by_name.get(c.name, True) for c in ob.users_collection)


def render_visible(ob):
    return ob.type in RENDERABLE and not ob.hide_render and not collection_hidden(ob)


def in_overlay(ob):
    return any(c.name in OVERLAY_COLLECTIONS for c in ob.users_collection)


# ---------------------------------------------------------------- geometry
def eval_mesh_arrays(ob, dg):
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    try:
        nv, nf = len(me.vertices), len(me.polygons)
        co = np.empty(nv * 3)
        me.vertices.foreach_get('co', co)
        M = np.array(ob.matrix_world)
        P = co.reshape(-1, 3) @ M[:3, :3].T + M[:3, 3]
        mi = np.empty(nf, dtype=np.int64)
        me.polygons.foreach_get('material_index', mi)
        ev_ = np.empty(len(me.edges) * 2, dtype=np.int64)
        me.edges.foreach_get('vertices', ev_)
        tris = 0
        if nf:
            lt = np.empty(nf, dtype=np.int64)
            me.polygons.foreach_get('loop_total', lt)
            tris = int((lt - 2).clip(min=0).sum())
        return P, mi, ev_.reshape(-1, 2), nf, tris
    finally:
        ev.to_mesh_clear()


def islands(nv, edges):
    """vertex island labels via min-label propagation with pointer jumping."""
    lab = np.arange(nv)
    if len(edges) == 0:
        return lab
    a, b = edges[:, 0], edges[:, 1]
    while True:
        m = np.minimum(lab[a], lab[b])
        new = lab.copy()
        np.minimum.at(new, a, m)
        np.minimum.at(new, b, m)
        new = new[new]
        while True:
            nn = new[new]
            if np.array_equal(nn, new):
                break
            new = nn
        if np.array_equal(new, lab):
            return lab
        lab = new


def clip_box(b):
    return [max(0.0, b[0]), min(float(W_PT), b[1]), max(0.0, b[2]), min(float(H_PT), b[3])]


def box_of(uv):
    return [float(uv[:, 0].min()), float(uv[:, 0].max()), float(uv[:, 1].min()), float(uv[:, 1].max())]


def union_box(boxes):
    boxes = [b for b in boxes if b]
    if not boxes:
        return None
    return [min(b[0] for b in boxes), max(b[1] for b in boxes), min(b[2] for b in boxes), max(b[3] for b in boxes)]


def rbox(b, nd=1):
    return None if b is None else [round(v, nd) for v in b]


# ---------------------------------------------------------------- object-ID render
def id_code(i):
    r, g, b = i % 64, (i // 64) % 64, i // 4096
    return tuple(srgb_to_linear((2 + 4 * k) / 255.0) for k in (r, g, b))


def render_id_pass(objs, prefix, percent=48):
    """Render object-ID images for the map pass and overlay pass; returns (map_ids, ovl_ids, px_per_pt, stats)."""
    scene, render = sc, sc.render
    shading, disp, vs = scene.display.shading, scene.display, scene.view_settings
    saved = {
        'render': {n: getattr(render, n) for n in ['filepath', 'use_border', 'resolution_percentage',
                                                    'film_transparent', 'dither_intensity']},
        'fmt': (render.image_settings.file_format, render.image_settings.color_mode, render.image_settings.color_depth),
        'shading': {n: getattr(shading, n) for n in ['light', 'color_type', 'show_shadows', 'show_cavity',
                                                     'show_object_outline', 'show_specular_highlight', 'show_xray',
                                                     'use_dof']},
        'aa': disp.render_aa,
        'vs': (vs.view_transform, vs.look, vs.exposure, vs.gamma, vs.use_curve_mapping),
        'coll': {c.name: c.hide_render for c in bpy.data.collections},
        'color': {o.name: tuple(o.color) for o in objs},
    }
    ids = {o.name: i + 1 for i, o in enumerate(objs)}
    out = {}
    try:
        render.use_border = False
        render.resolution_percentage = percent
        render.dither_intensity = 0.0
        render.image_settings.file_format = 'PNG'
        render.image_settings.color_mode = 'RGBA'
        render.image_settings.color_depth = '8'
        render.film_transparent = True
        shading.light = 'FLAT'
        shading.color_type = 'OBJECT'
        for n in ['show_shadows', 'show_cavity', 'show_object_outline', 'show_specular_highlight', 'show_xray', 'use_dof']:
            setattr(shading, n, False)
        disp.render_aa = 'OFF'
        vs.view_transform = 'Standard'
        vs.look = 'None'
        vs.exposure = 0.0
        vs.gamma = 1.0
        vs.use_curve_mapping = False
        for o in objs:
            o.color = (*id_code(ids[o.name]), 1.0)
        for pas in ('map', 'overlay'):
            for c in bpy.data.collections:
                hidden = saved['coll'][c.name]
                c.hide_render = hidden or ((c.name in OVERLAY_COLLECTIONS) if pas == 'map'
                                           else (c.name not in OVERLAY_COLLECTIONS | {'Collection'}))
            path = str(prefix) + f'_id_{pas}.png'
            render.filepath = path
            bpy.ops.render.render(write_still=True)
            img = bpy.data.images.load(path, check_existing=False)
            w, h = img.size
            px = np.empty(w * h * 4, dtype=np.float32)
            img.pixels.foreach_get(px)
            bpy.data.images.remove(img)
            px = (px.reshape(h, w, 4)[::-1] * 255.0)
            k = np.rint((px[..., :3] - 2.0) / 4.0).astype(np.int64)
            resid = np.abs(px[..., :3] - (2.0 + 4.0 * k))
            code = k[..., 0] + 64 * k[..., 1] + 4096 * k[..., 2]
            alpha = px[..., 3] > 127.5
            code[~alpha] = 0
            bad = alpha & ((resid.max(-1) > 1.01) | (code > len(objs)) | (code < 1))
            out[pas] = (code, int(bad.sum()), int(alpha.sum()), path)
    finally:
        for n, v in saved['render'].items():
            setattr(render, n, v)
        render.image_settings.file_format, render.image_settings.color_mode, render.image_settings.color_depth = saved['fmt']
        for n, v in saved['shading'].items():
            setattr(shading, n, v)
        disp.render_aa = saved['aa']
        vs.view_transform, vs.look, vs.exposure, vs.gamma, vs.use_curve_mapping = saved['vs']
        for c in bpy.data.collections:
            c.hide_render = saved['coll'][c.name]
        for o in objs:
            o.color = saved['color'][o.name]
    m_code, m_bad, m_cov, m_path = out['map']
    o_code, o_bad, o_cov, o_path = out['overlay']
    final = np.where(o_code > 0, o_code, m_code)
    pxpt = m_code.shape[1] / W_PT
    stats = {'id_render_percent': percent, 'id_px_per_pt': round(pxpt, 4), 'size_px': list(m_code.shape[::-1]),
             'map_png': m_path, 'overlay_png': o_path,
             'undecodable_px_map': m_bad, 'covered_px_map': m_cov,
             'undecodable_px_overlay': o_bad, 'covered_px_overlay': o_cov}
    return ids, m_code, o_code, final, pxpt, stats


def per_id_stats(code, n, pxpt):
    """pixel count and pixel bbox per id (vectorised)."""
    h, w = code.shape
    flat = code.ravel()
    cnt = np.bincount(flat, minlength=n + 1)
    ys, xs = np.divmod(np.arange(flat.size), w)
    big = np.iinfo(np.int64).max
    x0 = np.full(n + 1, big); x1 = np.full(n + 1, -1); y0 = np.full(n + 1, big); y1 = np.full(n + 1, -1)
    np.minimum.at(x0, flat, xs); np.maximum.at(x1, flat, xs)
    np.minimum.at(y0, flat, ys); np.maximum.at(y1, flat, ys)
    res = {}
    for i in range(1, n + 1):
        if cnt[i]:
            res[i] = (int(cnt[i]), [x0[i] / pxpt, (x1[i] + 1) / pxpt, y0[i] / pxpt, (y1[i] + 1) / pxpt])
        else:
            res[i] = (0, None)
    return res


# ---------------------------------------------------------------- clustering
def grid_clusters(centers, cell=CLUSTER_CELL_PT):
    """connected components of occupied grid cells (8-neighbour)."""
    keys = np.floor(centers / cell).astype(np.int64)
    cells = {}
    for i, k in enumerate(map(tuple, keys)):
        cells.setdefault(k, []).append(i)
    lab, cur = {}, 0
    for k in cells:
        if k in lab:
            continue
        st = [k]; lab[k] = cur
        while st:
            a = st.pop()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nb = (a[0] + dx, a[1] + dy)
                    if nb in cells and nb not in lab:
                        lab[nb] = cur; st.append(nb)
        cur += 1
    out = np.empty(len(centers), dtype=np.int64)
    for k, idx in cells.items():
        out[idx] = lab[k]
    return [np.where(out == c)[0] for c in range(cur)]


def split_large(members, boxes, centers):
    b = union_box([boxes[i] for i in members])
    if (b[1] - b[0]) <= SPLIT_MAX_PT and (b[3] - b[2]) <= SPLIT_MAX_PT:
        return [members]
    ax = 0 if (b[1] - b[0]) >= (b[3] - b[2]) else 1
    med = np.median(centers[members, ax])
    lo = members[centers[members, ax] <= med]; hi = members[centers[members, ax] > med]
    if len(lo) == 0 or len(hi) == 0:
        return [members]
    return split_large(lo, boxes, centers) + split_large(hi, boxes, centers)


def direction_name(cx, cy, ref):
    dx, dy = cx - ref[0], ref[1] - cy
    if math.hypot(dx, dy) < 120:
        return '가운데'
    ang = (math.degrees(math.atan2(dy, dx)) + 360) % 360
    names = ['동', '북동', '북', '북서', '서', '남서', '남', '남동']
    return names[int(((ang + 22.5) % 360) // 45)]


# ---------------------------------------------------------------- main build
def build_inventory(id_prefix, log=print):
    t0 = time.time()
    O = bpy.data.objects
    dg = bpy.context.evaluated_depsgraph_get()
    renderables = sorted([o for o in O if o.type in RENDERABLE], key=lambda o: o.name)
    visible = [o for o in renderables if render_visible(o)]
    hidden = [o for o in renderables if not render_visible(o)]

    # projection self-check against the reference per-point function from the project scripts
    chk = []
    for o in visible[:: max(1, len(visible) // 12)]:
        P, *_ = eval_mesh_arrays(o, dg)
        if len(P):
            sel = P[np.linspace(0, len(P) - 1, min(20, len(P))).astype(int)]
            ref = np.array([to_pt(Vector(p)) for p in sel])
            chk.append(float(np.abs(ref - to_pt_np(sel)).max()))
    proj_err = max(chk) if chk else None

    ids, m_code, o_code, final, pxpt, id_stats = render_id_pass(visible, id_prefix)
    n = len(visible)
    st_final = per_id_stats(final, n, pxpt)
    st_pass = {}
    st_m = per_id_stats(m_code, n, pxpt); st_o = per_id_stats(o_code, n, pxpt)

    objects = {}
    geo = {}
    for o in visible:
        P, mi, edges, nf, tris = eval_mesh_arrays(o, dg)
        uv = to_pt_np(P) if len(P) else np.zeros((0, 2))
        geo[o.name] = (P, uv, edges)
        mats = []
        for si, slot in enumerate(o.material_slots):
            m = slot.material
            mats.append({'slot': si, 'material': m.name if m else None,
                         'diffuse_hex': srgb_hex(m.diffuse_color) if m else None,
                         'diffuse_linear': [round(v, 4) for v in m.diffuse_color[:3]] if m else None,
                         'faces': int((mi == si).sum())})
        i = ids[o.name]
        ov = in_overlay(o)
        own = st_o[i] if ov else st_m[i]
        raw = box_of(uv) if len(uv) else None
        objects[o.name] = {
            'name': o.name, 'type': o.type, 'collections': [c.name for c in o.users_collection],
            'pass': 'overlay' if ov else 'map', 'parent': o.parent.name if o.parent else None,
            'faces_base': len(o.data.polygons) if o.type == 'MESH' else None,
            'faces_eval': nf, 'tris_eval': tris, 'vertices_eval': int(len(P)),
            'modifiers': [m.type for m in o.modifiers],
            'materials': mats if mats else [{'slot': None, 'material': None, 'diffuse_hex': '#CCCCCC (workbench default)',
                                             'faces': nf}],
            'bbox_projected_pt': rbox(clip_box(raw)) if raw else None,
            'bbox_projected_unclipped_pt': rbox(raw) if raw else None,
            'area_visible_final_pt2': round(st_final[i][0] / pxpt ** 2, 1),
            'bbox_visible_final_pt': rbox(st_final[i][1]),
            'area_visible_own_pass_pt2': round(own[0] / pxpt ** 2, 1),
            'bbox_visible_own_pass_pt': rbox(own[1]),
        }
        objects[o.name]['covered_by_overlay_pct'] = (
            round(100 * (1 - st_final[i][0] / own[0]), 1) if (own[0] and not ov) else 0.0)

    # ------------------------------------------------ assets
    claimed = {}
    assets = []
    ref_center = None
    if 'COL_ruined' in objects and objects['COL_ruined']['bbox_projected_pt']:
        b = objects['COL_ruined']['bbox_projected_pt']; ref_center = ((b[0] + b[1]) / 2, (b[2] + b[3]) / 2)
    else:
        ref_center = (W_PT / 2, H_PT / 2)
    vis_names = [o.name for o in visible]
    hidden_names = {o.name for o in hidden}

    def members_of(patterns, pool):
        return [nm for nm in pool if any(re.search(p, nm) for p in patterns)]

    water_bodies = {}
    for aid, name, role, kind, pats, opt in ASSET_RULES:
        mem = [nm for nm in members_of(pats, vis_names) if nm not in claimed]
        hid = members_of(pats, sorted(hidden_names))
        if not mem:
            if hid:
                assets.append({'id': aid, 'name': name, 'role': role, 'kind': kind, 'objects': [], 'hidden_objects': hid,
                               'status': '숨김(렌더 제외)'})
            continue
        for nm in mem:
            claimed[nm] = aid
        base = {'name': name, 'role': role, 'kind': kind, 'hidden_objects': hid, 'status': 'visible'}
        if opt.get('cluster_objects'):
            cents = np.array([[(objects[nm]['bbox_projected_pt'][0] + objects[nm]['bbox_projected_pt'][1]) / 2,
                               (objects[nm]['bbox_projected_pt'][2] + objects[nm]['bbox_projected_pt'][3]) / 2] for nm in mem])
            groups = grid_clusters(cents, cell=opt['cluster_objects'])
            groups.sort(key=lambda g: (-len(g), cents[g, 1].mean()))
            used = {}
            for g in groups:
                gm = [mem[i] for i in g]
                bx = union_box([objects[nm]['bbox_projected_pt'] for nm in gm])
                dname = direction_name((bx[0] + bx[1]) / 2, (bx[2] + bx[3]) / 2, ref_center)
                label = f'{dname}쪽 {name}' if len(gm) > 1 else f'{dname}쪽 외딴 나무({gm[0]})'
                k = used.get(dname, 0); used[dname] = k + 1
                suffix = '' if k == 0 else f'_{k + 1}'
                dd = {'동': 'e', '북동': 'ne', '북': 'n', '북서': 'nw', '서': 'w', '남서': 'sw', '남': 's', '남동': 'se', '가운데': 'c'}[dname]
                assets.append({**base, 'id': f'{aid}_{dd}{suffix}', 'name': label + ('' if not suffix else f' {k + 1}'),
                               'objects': gm, 'object_regions': None, 'bbox_pt': rbox(bx)})
            continue
        if opt.get('split'):
            isl_c, isl_b, isl_o, isl_n = [], [], [], []
            for nm in mem:
                P, uv, edges = geo[nm]
                if not len(P):
                    continue
                lab = islands(len(P), edges)
                _, inv = np.unique(lab, return_inverse=True)
                cnt = np.bincount(inv)
                order = np.argsort(inv, kind='stable')
                starts = np.concatenate([[0], np.cumsum(cnt)[:-1]])
                for s, c in zip(starts, cnt):
                    sel = order[s:s + c]
                    u = uv[sel]
                    isl_c.append(u.mean(0)); isl_b.append(box_of(u)); isl_o.append(nm); isl_n.append(int(c))
            centers = np.array(isl_c)
            inside = (centers[:, 0] > -50) & (centers[:, 0] < W_PT + 50) & (centers[:, 1] > -50) & (centers[:, 1] < H_PT + 50)
            idx_all = np.where(inside)[0]
            comps = grid_clusters(centers[idx_all])
            comps = [idx_all[c] for c in comps]
            # merge small clusters into the nearest large one
            big = [c for c in comps if len(c) >= MIN_REGION_ISLANDS]
            small = [c for c in comps if len(c) < MIN_REGION_ISLANDS]
            if not big:
                big, small = [np.concatenate(comps)], []
            for c in small:
                cc = centers[c].mean(0)
                j = int(np.argmin([np.linalg.norm(centers[b].mean(0) - cc) for b in big]))
                big[j] = np.concatenate([big[j], c])
            regions = []
            for c in big:
                regions += split_large(c, isl_b, centers)
            regions.sort(key=lambda r: (centers[r, 1].mean(), centers[r, 0].mean()))
            used = {}
            for r in regions:
                bx = clip_box(union_box([isl_b[i] for i in r]))
                dname = direction_name((bx[0] + bx[1]) / 2, (bx[2] + bx[3]) / 2, ref_center)
                k = used.get(dname, 0); used[dname] = k + 1
                dd = {'동': 'e', '북동': 'ne', '북': 'n', '북서': 'nw', '서': 'w', '남서': 'sw', '남': 's', '남동': 'se', '가운데': 'c'}[dname]
                objs_r = sorted({isl_o[i] for i in r})
                assets.append({**base, 'id': f'{aid}_{dd}' + ('' if k == 0 else f'_{k + 1}'),
                               'name': f'{name} · {dname}쪽 구역' + ('' if k == 0 else f' {k + 1}'),
                               'objects': objs_r, 'object_regions': {nm: f'{sum(1 for i in r if isl_o[i] == nm)} islands'
                                                                     for nm in objs_r},
                               'island_count': int(len(r)), 'bbox_pt': rbox(bx)})
            continue
        bx = union_box([objects[nm]['bbox_projected_pt'] for nm in mem])
        a = {**base, 'id': aid, 'objects': mem, 'object_regions': None, 'bbox_pt': rbox(bx)}
        if opt.get('water_body'):
            water_bodies[aid] = a
        assets.append(a)

    # water marks: each island goes to the water body directly under it (downward ray to the river / sea mesh)
    wm = [nm for nm in vis_names if re.search(WATER_MARK_RE, nm) and nm not in claimed]
    if wm and water_bodies:
        bvhs = {}
        for aid, a in water_bodies.items():
            verts, polys = [], []
            for nm in a['objects']:
                ob = O[nm]; ev = ob.evaluated_get(dg); me = ev.to_mesh(); mw = ob.matrix_world; b0 = len(verts)
                verts += [mw @ v.co for v in me.vertices]; polys += [[b0 + i for i in p.vertices] for p in me.polygons]
                ev.to_mesh_clear()
            bvhs[aid] = BVHTree.FromPolygons(verts, polys)
        for nm in wm:
            P, uv, edges = geo[nm]
            lab = islands(len(P), edges)
            _, inv = np.unique(lab, return_inverse=True)
            counts = {aid: 0 for aid in bvhs}
            boxes = {aid: [] for aid in bvhs}
            unassigned = 0
            for k in range(inv.max() + 1):
                sel = np.where(inv == k)[0]
                c = P[sel].mean(0)
                best, bd = None, 1e9
                for aid, bv in bvhs.items():
                    h = bv.ray_cast(Vector((c[0], c[1], c[2] + 50.0)), Vector((0, 0, -1)))
                    if h[0] is not None and abs(h[0].z - c[2]) < bd:
                        best, bd = aid, abs(h[0].z - c[2])
                if best is None:   # fall back to nearest screen box
                    cu = uv[sel].mean(0)
                    best = min(bvhs, key=lambda a: max(0, water_bodies[a]['bbox_pt'][0] - cu[0], cu[0] - water_bodies[a]['bbox_pt'][1])
                               + max(0, water_bodies[a]['bbox_pt'][2] - cu[1], cu[1] - water_bodies[a]['bbox_pt'][3]))
                    unassigned += 1
                counts[best] += 1
                boxes[best].append(box_of(uv[sel]))
            claimed[nm] = 'water'
            for aid, a in water_bodies.items():
                if counts[aid]:
                    a['objects'].append(nm)
                    a['object_regions'] = (a['object_regions'] or {})
                    a['object_regions'][nm] = f'{counts[aid]} islands over this water body'
                    a['bbox_pt'] = rbox(clip_box(union_box([a['bbox_pt'], union_box(boxes[aid])])))
            for a in water_bodies.values():
                a['water_mark_islands_without_hit'] = unassigned

    # anything visible no rule claimed -> its own asset
    unmatched = [nm for nm in vis_names if nm not in claimed]
    for nm in unmatched:
        ob = objects[nm]
        role = '도형' if ob['pass'] == 'overlay' else '지물'
        assets.append({'id': 'unmatched_' + re.sub(r'[^A-Za-z0-9_]+', '_', nm), 'name': f'미분류 {nm}', 'role': role,
                       'kind': '규칙에 없는 물체', 'objects': [nm], 'object_regions': None, 'hidden_objects': [],
                       'status': 'visible', 'bbox_pt': ob['bbox_projected_pt']})
        claimed[nm] = assets[-1]['id']

    # per-asset measured visibility (final composite) + face totals + colour list
    for a in assets:
        if not a['objects']:
            continue
        mem = a['objects']
        fins = [objects[nm] for nm in mem]
        if a.get('object_regions'):
            # region assets: count visible pixels of member objects inside the region box only
            bx = a['bbox_pt']
            x0, x1, y0, y1 = [int(round(v * pxpt)) for v in bx]
            sub = final[y0:y1, x0:x1]
            a['area_visible_final_pt2'] = round(sum(int((sub == ids[nm]).sum()) for nm in mem) / pxpt ** 2, 1)
        else:
            a['area_visible_final_pt2'] = round(sum(f['area_visible_final_pt2'] for f in fins), 1)
        a['bbox_visible_final_pt'] = rbox(union_box([f['bbox_visible_final_pt'] for f in fins]))
        if a.get('object_regions'):
            a['bbox_visible_final_pt'] = None if a['bbox_visible_final_pt'] is None else rbox([
                max(a['bbox_visible_final_pt'][0], a['bbox_pt'][0]), min(a['bbox_visible_final_pt'][1], a['bbox_pt'][1]),
                max(a['bbox_visible_final_pt'][2], a['bbox_pt'][2]), min(a['bbox_visible_final_pt'][3], a['bbox_pt'][3])])
        a['bbox_area_pt2'] = round((a['bbox_pt'][1] - a['bbox_pt'][0]) * (a['bbox_pt'][3] - a['bbox_pt'][2]), 1)
        a['faces_eval'] = int(sum(f['faces_eval'] for f in fins)) if not a.get('object_regions') else None
        a['passes'] = sorted({f['pass'] for f in fins})
        cols = {}
        for f in fins:
            for m in f['materials']:
                key = (m['material'], m['diffuse_hex'])
                cols[key] = cols.get(key, 0) + (m['faces'] or 0)
        a['materials'] = [{'material': k[0], 'diffuse_hex': k[1], 'faces': v}
                          for k, v in sorted(cols.items(), key=lambda kv: -kv[1])]
        a['zero_visible_objects'] = [nm for nm in mem if objects[nm]['area_visible_final_pt2'] == 0]

    role_rank = {r: i for i, r in enumerate(ROLE_ORDER)}
    vis_assets = [a for a in assets if a['objects']]
    vis_assets.sort(key=lambda a: (role_rank.get(a['role'], 99), a['id']))
    hid_assets = [a for a in assets if not a['objects']]
    hidden_list = []
    for o in hidden:
        reason = []
        if o.hide_render:
            reason.append('object.hide_render')
        if collection_hidden(o):
            reason.append('collection hidden: ' + ','.join(c.name for c in o.users_collection))
        hidden_list.append({'name': o.name, 'type': o.type, 'collections': [c.name for c in o.users_collection],
                            'reason': ' + '.join(reason), 'status': '숨김'})
    inv = {
        'blend': bpy.data.filepath,
        'frame_pt': [W_PT, H_PT],
        'camera': cam.name,
        'render_engine': sc.render.engine,
        'projection_check_max_err_pt': proj_err,
        'id_pass': id_stats,
        'counts': {'renderable_objects': len(renderables), 'visible_objects': len(visible), 'hidden_objects': len(hidden),
                   'visible_assets': len(vis_assets), 'hidden_assets': len(hid_assets),
                   'unmatched_objects': len(unmatched),
                   'visible_objects_with_zero_visible_area': sum(1 for v in objects.values() if v['area_visible_final_pt2'] == 0)},
        'unmatched_objects': unmatched,
        'assets': vis_assets,
        'hidden_assets': hid_assets,
        'objects': [objects[nm] for nm in vis_names],
        'hidden': hidden_list,
        'seconds': round(time.time() - t0, 1),
    }
    # every visible object belongs to at least one asset
    in_assets = {nm for a in vis_assets for nm in a['objects']}
    inv['all_visible_objects_in_assets'] = set(vis_names) <= in_assets
    log(f'INVENTORY visible={len(visible)} hidden={len(hidden)} assets={len(vis_assets)} unmatched={len(unmatched)} '
        f'proj_err={proj_err} id_bad={id_stats["undecodable_px_map"]}/{id_stats["undecodable_px_overlay"]} t={inv["seconds"]}s')
    return inv


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for blk in iter(lambda: f.read(1 << 20), b''):
            h.update(blk)
    return h.hexdigest()


if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    if not argv:
        raise SystemExit('usage: Blender -b in.blend --factory-startup --python inventory.py -- <out_inventory.json> [id_prefix]')
    out = Path(argv[0]).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    prefix = Path(argv[1]).resolve() if len(argv) > 1 else out.with_name(out.stem + '_idpass')
    src = bpy.data.filepath
    h0 = sha256_file(src)
    inv = build_inventory(prefix)
    inv['blend_sha256'] = h0
    if sha256_file(src) != h0:
        raise RuntimeError('input blend changed on disk during inventory')
    out.write_text(json.dumps(inv, ensure_ascii=False, indent=1))
    print('WROTE', out)
