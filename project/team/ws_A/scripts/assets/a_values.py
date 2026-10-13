"""워커 A — 명도 위계(비평 2: I2·C3). 색 방식 OBJECT 회색 단계만.
배경 땅이 가장 밝고(1.0) → 밭 한 단계(0.84~0.93) → 길 중간·CORE 길은 가장 진한 띠(현무암 0.30, 흰 연석·흰 셰브런과 대비)
→ 주요 물체(콜로세움·CORE 장면·DETAIL)는 땅보다 어두운 중간 회색 몸체 + 그림자로 대비 최대.
지도 패스 노출은 render_final.py(MAP_EXPOSURE)에서, 겹 패스(도형·헤더)는 원래 노출 0.35 그대로.
모든 파이프라인 끝(감사·렌더 직전)에 실행: 새로 만든 물체는 색이 1.0으로 들어오므로.
"""
import bpy

G = {
    # 지형
    'T_land': 1.0, 'T_beach': 0.90, 'L10_sea': 0.84, 'L02_tiber': 0.80, 'W_water_marks': 1.0,
    # 밭·길
    'F_centuriatio': 0.86, 'F_pasture': 0.94, 'F_orchard': 0.90, 'F_vine_rows': 0.62, 'F_olive_trees': 0.60, 'F_hedge': 0.58,
    'R_core_road': 0.30, 'R_core_curb': 0.97, 'R_core_chev': 1.0, 'R_core_bed': 0.86, 'R_core_plaza': 0.30, 'R_core_mark': 0.80,
    'R_via_appia': 0.62, 'R_via_ostiensis': 0.62,
    'B_pons': 0.82,
    # 랜드마크·장면
    'COL_ruined': 0.78,
    'C1_': 0.55, 'C2_': 0.55, 'C3_': 0.55, 'C4_': 0.55, 'C5_': 0.55,
    # 근거 장소·지역
    'L03_': 0.84, 'L04_palatine': 0.84, 'L09_': 0.86, 'L08_': 0.86, 'L11_': 0.86, 'S_lab': 0.86, 'L12_': 0.86, 'D2_lime_kiln': 0.80,
    'L05_aqua': 0.86, 'L07_vesuvius': 0.90, 'L01_': 0.96, 'L13_': 0.86,
    # 나무
    'T_pine': 0.66, 'T_cypress': 0.56, 'T_olive': 0.64,
    # DETAIL 모형: 가장 어두운 면만 한 단계 밝힘(CORE 장면보다 시선을 덜 끌게, 가벼움→무거움 단계는 유지)
    'D2_cube': 0.42, 'D3_foundation': 0.30, 'D3_heavy': 0.47,
}
KEEP = ('L04_palatine_arch',)   # 어두운 아치 구멍 등 고유 회색 유지


def gray_for(name):
    if name in KEEP:
        return None
    best = None
    for k, g in G.items():
        if name == k or name.startswith(k):
            if best is None or len(k) > len(best[0]):
                best = (k, g)
    return best[1] if best else None


# terrain.py가 만드는 옛 평판 T_ground(z=0)가 같은 세션 렌더에 남아 T_land 평지(z≈0)와 z-충돌 → 맨 위 띠·콜로세움 둘레 유령 선. 렌더 전에 지움
_tg = bpy.data.objects.get('T_ground')
if _tg:
    bpy.data.objects.remove(_tg, do_unlink=True)
n = 0
for c in ('20_LANDMARK', '30_TERRAIN', '35_FIELDS_ROADS', '40_REGION', '45_CORE_SCENES', '50_DETAIL_MODEL', '60_TREES'):
    col = bpy.data.collections.get(c)
    for o in (col.all_objects if col else []):
        g = gray_for(o.name)
        if g is not None:
            o.color = (g, g, g, 1.0); n += 1
sh = bpy.context.scene.display.shading
sh.shadow_intensity = 0.42
bpy.context.scene['map_exposure'] = 0.62
print('a_values: colored', n, 'shadow', sh.shadow_intensity)
