"""워커 B · 비평 2 (명도 위계·깊이): 조명·음영 설정 + 물체별 회색 단계. render_final.py 앞에 실행.
위계(RUBRIC I2): 콜로세움 > CORE 길 > CORE 작업 장면 > DETAIL 모형 > SUPPORT 장소 > 배경
- 월드 고정 조명(studio roman_poster.sl을 세계 기준 220° 회전): 평평한 땅(글 바탕)은 밝게 남고 세운 면만 어두워져 물체가 땅에서 떨어져 보임
- 배경 땅 1.0(가장 밝음) / 바다·강 0.93 / 밭 0.86, 작물 0.6, 생울타리 0.66, 나무 0.72 / 길: 아피아 0.64, CORE 0.34(가장 진한 띠)
- SUPPORT 장소·산 1.0~0.97(하얀 석고 — 배경과 비슷한 밝기, 형태는 음영으로) / DETAIL 모형: 원래 회색 단계를 0.38+0.62g로 한 단계 밝힘(순서 유지)
- CORE 작업 장면 0.74(흰 SUPPORT·DETAIL보다 무겁게) / 콜로세움 0.9 + 진한 아치 그늘
"""
import math
import bpy
sc = bpy.context.scene; sh = sc.display.shading
sh.use_world_space_lighting = True
sh.studiolight_rotate_z = math.radians(220.0)
# 물체 윤곽선: 검정(0.1) → 회색(0.4) — 밭 판마다 생기던 진한 오려낸 테두리를 누그러뜨림(주요 물체 외곽은 유지)
sh.object_outline_color = (0.4, 0.4, 0.4)


import os
DET_A = float(os.environ.get('B_DET_A', 0.5))
CORE_G = float(os.environ.get('B_CORE_G', 0.68))


def setg(o, g):
    o.color = (g, g, g, 1.0)


# 화산 1.22: SUPPORT 장소인데 콜로세움 다음으로 진해 시선을 뺏던 것(그늘 쪽만 밝힘, 밝은 면은 255에서 멈춤)
TONE = {'L07_vesuvius': 1.22, 'T_land': 1.0, 'L10_sea': 0.86, 'L02_tiber': 0.86, 'W_water_marks': 1.0, 'COL_ruined': 0.9}
for n, g in TONE.items():
    if bpy.data.objects.get(n):
        setg(bpy.data.objects[n], g)
for o in bpy.data.collections['45_CORE_SCENES'].objects:
    if not o.name.startswith('C1_quarry'):
        setg(o, CORE_G)
for o in bpy.data.collections['60_TREES'].objects:
    setg(o, 0.72)
# DETAIL 모형: 첫 실행 때 원래 회색을 저장해 두고 그 값에서 다시 계산(여러 번 돌려도 누적되지 않게)
for c in ('50_DETAIL_MODEL', '81_NOSHADOW'):
    for o in bpy.data.collections[c].objects:
        if o.type != 'MESH':
            continue
        if 'g_orig' not in o:
            o['g_orig'] = float(o.color[0])
        setg(o, DET_A + (1 - DET_A) * o["g_orig"])
print('look applied')
# 노출 0.35 → 0.48: 배경 땅을 한 단계 더 밝게(글 바탕 ≈ 232, 밝은 면도 255 넘지 않음)
sc.view_settings.exposure = 0.48
# SSAO(World cavity) 거리 0.2 → 0.05, 표본 16 → 32: 완만한 비탈(해안·강둑·산괴)에 생기던 세로 줄무늬 잡음 제거, 물체 홈 음영은 유지
sc.display.matcap_ssao_distance = 0.05
sc.display.matcap_ssao_samples = 32
# 다리 위 포장 띠도 CORE 길 포장과 같은 회색(띠가 끊기지 않게)
for o in bpy.data.objects:
    if o.name.startswith('B_pons') and o.name.endswith('_pave'):
        setg(o, 0.34)
# 그림자 빛 방향: 기본(0.577,0.577,0.577)은 그림자가 물체 바로 오른쪽에 계단 모양 반투명 띠(유령 도형)로 붙음 → 카메라 쪽에 가까운 빛으로 그림자가 물체 뒤에 숨게(바닥 밝기는 그대로)
sc.display.light_direction = (0.58, 0.62, 0.53)   # 화산(스캔) 그림자가 뒤 기슭에 먼지처럼 찍히던 것까지 숨김
# 공동(cavity) 방식 BOTH → SCREEN: 월드 SSAO가 넓은 평지를 통째로 어둡게(글 바탕 ≈ 207) 하고 물가 비탈에 줄무늬를 만들던 것 —
# 화면 곡률만 쓰면 땅은 밝게(≈ 233), 물체 모서리·홈은 그대로 또렷. 바다·강은 0.86으로 땅보다 한 단계 어둡게(물·땅 구분)
sh.cavity_type = 'SCREEN'
