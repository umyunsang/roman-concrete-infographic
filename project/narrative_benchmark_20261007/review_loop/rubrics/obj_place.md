# 루브릭 · 물체 단위 배치·구성 (obj_place)

- 작성: 라운드 11 물체 단위 배치·구성 비평가(2026-10-13). STATE.md D37(사용자 요청)에 따라 Blender에 배치된 **자산 57개 하나하나**를 심사하는 루브릭이다. 다음 라운드부터는 이 문서를 고정해 다른 비평가가 블라인드로 재현한다.
- 범위: 물체 하나가 **어디에·어떻게 놓였는가**. 땅에 제대로 서 있는지(떠 있음·묻힘·기울어짐), 이웃 물체·길·강·이름표와의 간격(겹침·관통·가림·4pt 미만 근접), 방향(정면·출입구·인물·화살 판), 이웃과의 축척 관계, 길·이정표·다리와의 관계, 장면 전체에서 자리의 타당성(방위·위상·받침 의미·묶음).
- 판정은 항목마다 **예(합격) / 아니오(불합격) / 해당 없음(N/A)**. 문헌이 직접 준 값은 [문헌값], 문헌 원리를 이 포스터에서 재현 가능한 수치로 옮긴 값은 [운영값]으로 표시한다.

## 등급·심각도·집계 규칙

- 심각도(BRIEF §6과 같음): **blocker** = 객관적으로 증명되는 결함(가림·겹침·판독 불가·사실/의미 오류) / **major** = 분명한 품질 저하 + 근거 문헌 / **minor** = 다듬기.
- **등급은 자산 단위**(BRIEF와 같은 규칙): **AAA** = blocker 0 · major 0 · minor ≤ 2 / **AA** = blocker 0 · major ≤ 2 / **A** = blocker 0 · major ≥ 3 / **B** = blocker 1~2 / **C** = blocker ≥ 3.
- **부풀리기 금지**: 같은 자산에서 같은 원인으로 여러 항목이 떨어지면 가장 높은 심각도 하나만 센다(예: 떠 있어서 01과 05가 함께 떨어지면 01 하나).
- **짝 문제의 귀속**(두 자산 사이 간격·겹침·관통·가림은 한 번만 센다):
  1. 글(Figma)·2D 표지(번호 원판·밑줄·핀·지시선) ↔ 3D 물체 → **3D 자산 쪽**에 기록(12). 글·2D 표지의 자리는 레이아웃·타이포 루브릭이 판정한다.
  2. 지형(ground_land)·물(water_*)이 물체를 덮거나 뚫고 올라옴 → **덮인 물체 쪽**(02·03). 단, 그 자리 지형이 주변 30pt 고리의 지형 높이 중앙값보다 화면 환산 2pt 이상 국소적으로 솟은 것이 원인이면 ground_land(또는 물) 쪽.
  3. 겹 패스(overlay) 3D(제목 아치·BASIC 아이콘·④ 큐브 등)가 지도 물체를 가림 → **겹 패스 자산 쪽**(08).
  4. 그 밖의 두 3D 자산 → 아래 '옮길 순서'에서 **앞에 오는 쪽**: 나무 → 밭 → 개념 모형 → SUPPORT 장면 → 지물 건물(콜로세움 제외) → 다리 → 길 → 이정표 → CORE 그림 → 콜로세움. 사용자가 자리를 정한 자산(milestone_1_to_2 — R1·고정 조건 9, 판테온 — D32·D34, 콜로세움 — D34, 핵심 길 — D32·D34)과의 짝은 상대 쪽에 기록한다.
- 리포트에는 자산마다 항목별 판정·측정값·심각도·귀속 근거를 남기고, 진행 중 결론은 바로 파일에 덧붙인다(BRIEF §6).

## 다른 루브릭·결정과의 경계

같은 현상을 다른 문턱으로 다시 재지 않는다. 겹치는 곳은 **같은 문턱**을 쓰거나 판정을 넘긴다.

| 현상 | 이 루브릭 | 다른 곳 |
|---|---|---|
| 사람끼리 키, 이정표 3개 높이, 아치 ÷ 사람 키 | 판정 안 함 | `illustration3d.md` I3-05·06·08 |
| 이정표 화살 방향(다음 CORE를 가리킴) | 판정 안 함(17은 판면 단축·가림만) | I3-28, `layout.md` LY-14, `infographic.md` INF-08 |
| 이정표–길 거리 | 22(같은 문턱 ≤ 10pt) | I3-17 |
| 막다른 길 끝 | 23(다리 양끝)·24(장소 앞 끊김)만 | I3-16(같은 문턱 5pt) |
| 글–물체 겹침·여유 | 12(겹침 = blocker, 수평 글 < 3pt = major, 기운 지명 < 2pt = major — 같은 문턱) | LY-01·02, TY-27·28, I3-20 |
| 라벨–자기 물체 근접 비율 | 13(같은 비 1.5, 같은 거리 20pt) | LY-05, INF-14 |
| 묶음 결속 비 | 28(같은 비 1.5) | LY-07 |
| 재단선·헤더와의 여백 | 판정 안 함 | LY-22(14.2pt), LY-24(16pt) |
| 지시선 길이 ≤ 60pt·가로지름 | 판정 안 함(29는 끝점만) | LY-06 |
| 모형 축척 위계(콜로세움 > CORE > DETAIL) | 판정 안 함 | I3-07 |
| 색·명도·대비·재질 | 판정 안 함(측정 보조로만 L*·ΔE00 사용) | `color.md`, `value.md`, obj 컬러·명암 루브릭 |
| 포스터 단위 접지 인상 | 01·02는 물체 기하로 잼 | I3-12(포스터 단위) |

## 고정 조건·결정·기각 (감점하지 않음 · 다시 내지 않음)

- BRIEF §3 고정 조건 전부. 특히 1(동심원 배치 — 방위 오차는 25에서 완화), 4(로마 시대 실제 장소·클레이 디오라마), 6(이정표 형태·색), 9(①→② 이정표 자리).
- R1: milestone_1_to_2가 길에서 떨어져 있음 → 22의 거리 조건 **판정 제외**(길 겹침만 본다).
- R3: 나무 그림자 → 05에서 나무는 **제외**. R5: 모형별 그림자 세기·방향 차 → 05는 **떨어짐(detached)만** 본다. R10: 밑동 접촉 어둠(Workbench 특성) → **판정하지 않음**.
- D21: 콜로세움 경기장 구덩이·기단 안쪽 가장자리가 무너진 벽 밑으로 들어감 → 02 **의도된 묻힘**.
- D27: 판테온 현관은 왼아래(관람자 쪽). 실제 판테온 현관은 북향이지만(위키백과) **D27이 우선**하고 14·15에서 실제 방위를 요구하지 않는다(Berann의 선택적 회전 관례, P7).
- D32·D34: 길 전 구간 보임(가려진 길 정점 0), 기단–길 4pt 이상, 판테온은 평탄지 위 — 08·10·27의 문턱이 이 결정과 같다.
- D12·D13: 기단–티베르강 ≥ 4pt, 눕힌 지명–밑동·그늘 ≥ 4pt — 11·12와 같은 문턱.
- 이 루브릭은 해법으로 고정 조건을 깨는 것(예: 동심원 해체, 이정표 평면 화살표화, 2D 전환)을 요구하지 않는다.

---

## 0. 측정 규약 (모든 항목 공통 · 재현용)

### 0-1. 자료와 좌표
1. **맥락 크롭** `nb_work/workers/inventory/assets/<id>/context.png`: 전체 Blender 렌더(글 없음)를 자산 상자 + 여백 12pt로 자름, 3px/pt. 상자는 `assets_index.json`의 `crop_pt`[x0, x1, y0, y1]. 화소 (u, v) → pt = (x0 + u/3, y0 + v/3).
2. **단독 크롭** `isolated.png`(회색 140 위) · `isolated_rgba.png`(**알파 = 그 자산만의 전체 실루엣**, 같은 카메라·같은 상자) · `iso_map_pass.png`/`iso_overlay_pass.png`.
3. **물체 ID 패스** `nb_work/workers/inventory/idpass/id_id_map.png`, `id_id_overlay.png`(2px/pt, Workbench FLAT, 앤티에일리어싱 없음). 물체 → 자산 대응은 `inventory.json`(objects[]·assets[]), 해독은 `inventory.py`의 `id_code`·`per_id_stats`와 같은 규칙. 최종 화면 ID = 겹 패스 ID가 있으면 그것, 없으면 지도 패스 ID.
4. **글 포함 포스터** `review_loop/r<N>/poster_2x.png`(2px/pt) + `text_spec_r<N>.json`. 맥락 크롭에는 Figma 글이 없다.
5. **Blender 원본**: 그 라운드의 blend(라운드 11 = `out/roman_concrete_narrative_v8_13.blend` 이후). **읽기 전용 — 저장 금지**. 투영은 `inventory.py`의 `to_pt_np`(오차 0.0007pt)를 `runpy.run_path`로 불러 쓴다.
6. 인벤토리·크롭이 심사 blend와 다르면(`blend_sha256` 비교) `inventory.py`·`render_assets.py`를 그 blend로 다시 돌린 결과를 쓴다(현재 자료는 v8_12 기준).

### 0-2. 마스크·거리 정의
- **M_A**(전체 실루엣): `isolated_rgba.png` 알파 ≥ 128을 포스터 pt 좌표로 옮긴 것. 남에게 가려진 부분도 포함.
- **V_A**(보이는 부분): 최종 화면 ID가 A의 물체인 화소.
- **발자국 F_A**: 0-3의 밑면 표본(접촉점)의 세계 XY 볼록 껍질을 화면에 투영한 다각형. 여러 부품이면 부품별 껍질의 합집합.
- **간격 gap(X, Y)**: 두 화소 집합 사이 최소 유클리드 거리(pt, 거리 변환). 0.5pt 미만의 판정은 화소가 아니라 Blender 기하로만 한다(ID 패스 해상도 0.5pt).
- **부호 간격 s(A, B)**(09에서 씀): M_A ∩ M_B가 비면 s = gap(M_A, M_B). 겹치면 s = −(겹친 영역 안 거리 변환 최댓값 × 2) = 겹침 두께의 음수.
- **화면 높이 h_A**: 밑면 접촉점에서 꼭대기까지 세계 수직 성분을 화면에 투영한 길이(pt).

### 0-3. Blender 기하 측정 (01·02·04·07·27)
- **밑면 표본**: 자산의 각 물체(평가된 메시, 세계 좌표)에서 최저 z부터 화면 환산 0.5pt 높이 안의 정점(최소 8개, 모자라면 최저 8개).
- **광선**: 표본마다 `scene.ray_cast(depsgraph, p + (0,0,ε), (0,0,−1))`로 아래를 쏘고, 맞은 물체가 자기 자산이면 그 아래에서 다시 쏜다. 처음 맞은 남의 표면 = **지지면**, 거리 g. 위로 쏴서(`(0,0,+1)`) 남의 표면이 표본 위에 있으면 그 거리 = **묻힘 깊이** d.
- **pt 환산**: `gap_pt = |to_pt(p) − to_pt(p − (0,0,g))|`(평행 투영이면 세계 수직 1단위 × 화면 배율 × cos 35.26°).
- **관통**: `mathutils.bvhtree.BVHTree.overlap`으로 A와 이웃 자산(A 상자 + 5pt 안)의 삼각형 교차 쌍을 구하고, 교차 깊이(상대 메시 안으로 들어간 A 정점의 최대 표면 거리)를 pt로 환산.
- 모든 스크립트는 장면 상태를 되돌리고 blend를 저장하지 않는다.

### 0-4. 빼기 렌더 (05·08)
- 자산 A의 물체만 `hide_render = True`로 두고, 같은 카메라·같은 Workbench 설정·같은 72% 해상도로 A의 `crop_pt` 상자만 border 렌더한 뒤 되돌린다.
- **D_A = L\*(맥락) − L\*(빼기)**. **그림자 Sh_A** = M_A 밖에서 D_A ≤ −2이고 면적 ≥ 4pt²인 연결 영역. **A가 가린 것** = 빼기 렌더에서 보이던 남의 물체 화소 중 맥락에서 A가 덮은 부분(ID 패스와 교차 확인).

### 0-5. 색 지표 (보조 측정)
- **L\***: sRGB → 선형(IEC 61966-2-1) → Y = 0.2126R + 0.7152G + 0.0722B → CIE L\*(D65). 다른 루브릭과 같은 정의.
- **ΔE00**: CIEDE2000(`skimage.color.deltaE_ciede2000`, Lab D65). **Oklch**: Ottosson 2020 Oklab의 극좌표.
- 이미지만으로 판정할 때(Blender를 못 쓸 때): 지형이 판을 뚫은 화소 = 판의 M_A 안에서 맥락 색이 지형 재질 렌더 색과 ΔE00 ≤ 5이고 판 재질 색과 ΔE00 > 10인 화소.

### 0-6. 시각 한계와 운영 문턱의 근거
- 정상 시력 한계 1′(P27): 0.5m에서 0.145mm = **0.41pt**, 1.5m에서 0.436mm = **1.24pt**(1pt = 0.353mm).
- **4pt = 1.41mm** = 1.5m에서 3.2′(한계의 약 2.6배): '확실히 떨어져 보이는' 최소 간격 [운영값]. 사용자 결정 D12·D13·D32·D34의 4pt와 같다. 0.41pt 미만 틈은 0.5m에서도 맞닿음으로 보이고, 0.41~4pt는 '붙었는지 떨어졌는지 애매한' 띠다(접선, P17·P18·P29).
- 지도 기호의 최소 치수는 관람 조건·과제마다 따로 정해야 한다(P21): 이 포스터는 A2 전시용, 관람 거리 0.5~1.5m(BRIEF §1).

### 0-7. 자산 유형과 적용 항목

| 유형 | 자산(57) |
|---|---|
| G 건물·장면(11) | landmark_colosseum, landmark_pantheon, landmark_lime_kiln, landmark_pompeii_town, landmark_aqueduct, support_privernum, support_ruin_observers, support_pompeii_site, support_harbor, core1_modern_building, core2_hot_mixing |
| B 다리(2) | bridge_north, bridge_south |
| V1 이정표(3) | milestone_1_to_2, milestone_2_to_34, milestone_34_to_5 |
| V2 나무(5) | tree_t_cypress, tree_t_pine_004, tree_t_pine_022, trees_s, trees_se |
| P1 길(6) | road_appia, road_core_nw, road_core_s, road_core_se, road_core_w, road_ostiensis |
| P2 밭(6) | fields_e, fields_nw, fields_s, fields_se, fields_sw, fields_w |
| W 물(2) | water_sea, water_tiber |
| T 지형(3) | ground_land, landmark_apennines, landmark_vesuvius |
| M 개념 모형(7, 지도와 축척이 다름) | detail_core3_lime_specimen, detail_core4_three_cubes, detail_d1_seawater, detail_d2_making, detail_d3_tower, support_breakwater_block, support_core5_lab |
| O1 겹 패스 3D(3) | header_gate, basic_recipe, basic_sources |
| O2 겹 패스 2D(9) | shape_core1~5_marker, shape_d2_leader, shape_d3_section, shape_pin_harbor, shape_pin_pompeii |

적용 표(● 적용, ○ 조건부 — 항목 본문의 '적용' 참조, 빈칸 = N/A):

| 항목 | G | B | V1 | V2 | P1 | P2 | W | T | M | O1 | O2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 01 떠 있음 | ● | ● | ● | ● |  |  |  |  | ● |  |  |
| 02 묻힘 | ● | ● | ● | ● |  |  |  | ○ | ● |  |  |
| 03 판 밀착 | ○ |  |  |  | ● | ● | ● | ○ |  |  |  |
| 04 기울기 | ● | ○ | ● | ● |  |  |  |  | ○ |  |  |
| 05 그림자 붙음 | ● | ● | ● |  |  |  |  |  | ● |  |  |
| 06 바닥선 |  |  |  |  |  |  |  |  | ○ | ● |  |
| 07 관통 | ● | ● | ● | ● | ● | ● |  | ○ | ● |  |  |
| 08 가림 | ● | ● | ● | ● | ● | ● |  | ○ | ● | ● |  |
| 09 접선 | ● | ● | ● | ● | ● | ● | ● | ○ | ● | ○ |  |
| 10 길 간격 | ● |  |  | ● |  | ● |  |  | ● |  |  |
| 11 물 간격 | ○ |  | ● | ● | ○ | ● |  |  | ○ |  |  |
| 12 글·표지 간격 | ● | ● | ● | ● | ● | ● | ○ | ○ | ● | ○ |  |
| 13 이름표 짝 | ○ | ○ |  |  | ○ |  | ● | ○ | ○ | ○ |  |
| 14 정면 가시성 | ○ | ● |  |  |  |  |  |  | ● | ● |  |
| 15 출입구 접근 | ○ |  |  |  |  |  |  |  |  |  |  |
| 16 인물 방향 | ○ |  |  |  |  |  |  |  |  |  |  |
| 17 화살 판 단축 |  |  | ● |  |  |  |  |  |  |  |  |
| 18 축 정렬 | ○ |  |  |  |  | ● |  |  |  |  |  |
| 19 크기 순서 | ● | ● | ● | ● |  |  |  |  |  |  |  |
| 20 반복 크기 | ○ |  |  | ○ |  |  |  |  |  |  |  |
| 21 개념 모형 분리 |  |  |  |  |  |  |  |  | ● |  |  |
| 22 이정표 길가 |  |  | ● |  |  |  |  |  |  |  |  |
| 23 다리 |  | ● |  |  |  |  |  |  |  |  |  |
| 24 길로 닿음 | ○ |  |  |  |  |  |  |  |  |  |  |
| 25 방위 | ○ |  |  |  | ○ |  | ● | ○ |  |  |  |
| 26 위상 | ○ | ● |  |  | ○ |  | ● | ○ |  |  |  |
| 27 받침 의미 | ● | ● | ● | ● | ● | ● |  |  | ● |  |  |
| 28 묶음 결속 | ○ |  |  | ○ |  |  |  |  | ○ | ● |  |
| 29 지시 끝점 |  |  |  |  |  |  |  |  |  |  | ○ |

- O2의 번호 원판·밑줄 5개(shape_core*_marker)는 자리가 레이아웃·타이포 루브릭(LY-15~17, TY-15)에서 정해지고, 3D 물체와의 충돌은 귀속 규칙 1에 따라 3D 쪽(12)에 기록하므로 이 루브릭의 적용 항목이 없다 → **N/A로 기록**(등급란에 'N/A — 이웃으로만 측정').
- ground_land는 귀속 규칙 2의 예외(국소 솟음)가 확인될 때만 02·03을 받는다.

### 0-8. 식별 부위와 의도된 접촉·묻힘

**식별 부위**(02·08·14·17·29에서 '식별 부위가 잘림·가려짐 = 상향'의 기준):

| 자산 | 식별 부위 |
|---|---|
| landmark_colosseum | 남은 높은 외벽 아치열, 경기장 안쪽 |
| landmark_pantheon | 현관 기둥·삼각 지붕, 돔·오쿨루스 |
| landmark_lime_kiln | 아궁이(입구), 돔 몸체 |
| landmark_aqueduct | 아치열 |
| landmark_vesuvius | 정상 윤곽 |
| bridge_* | 물 위 아치 |
| milestone_* | 화살 판(특히 머리 끝), 기둥, 받침 |
| support_privernum | 아치가 있는 성벽 면, 무너진 조각 |
| support_ruin_observers | 아치 벽, 인물 4명 |
| support_pompeii_site | 비계, 원료 더미 |
| support_harbor | 등대, 방파 부두, 바닷속 기둥 |
| support_core5_lab | 두 시편의 금·메움·누수 |
| core1_modern_building | 철근 골조, 금, 녹물 |
| core2_hot_mixing | 구덩이, 인물, 열 표시 |
| detail_core3 / core4 / d1 / d2 / d3 | 흰 알갱이 면 / 세 큐브의 물·흰 줄·메움 / 결정 바늘·물 / 주사위 흰 알갱이·열 표시 / 층별 재료 단면 |
| 나무 | 줄기 밑동, 잎 덩어리 |
| BASIC 아이콘 | 각 아이콘 전체 |

**의도된 접촉·묻힘**(실패로 세지 않음): 콜로세움 경기장 구덩이와 기단 안쪽(D21), 항구 기둥·방파 부두의 물속 부분, 방파제 블록·해수 수조의 수면 아래 부분, 해수 수조 속 결정, 길–길 접속, 길–다리 접속, 길 끝 광장, 물결 무늬–물, 밭·길 판–지형(03의 허용치 안), 판테온 평탄지(D34), 개념 모형–자기 받침.

---

## A. 접지 — 땅에 제대로 서 있는가

**[OBJ_PLACE-01] 바닥에 서야 할 물체의 밑면이 지지면에 닿아 있는가(떠 있음 없음)?**
- 적용: G·B·V1·V2·M. 물 위 구조물(항구 기둥·방파 부두·방파제 블록·해수 수조)은 지지면 = 수면이며, 수면과의 교차선이 밑동 둘레의 90% 이상에서 있어야 한다(물 위로 떠 있지 않음).
- 판정 방법: 0-3의 밑면 표본마다 아래로 광선을 쏴 지지면까지 거리를 pt로 환산(gap_pt). (a) 최대 gap_pt, (b) 접촉 표본(gap_pt ≤ 0.41pt)의 볼록 껍질 안에 자산 무게중심의 수직 투영이 들어가는지(SceneEval의 지지 판정을 이 장면 단위로 옮김).
- 합격 문턱: (a) ≤ 0.41pt [운영값: 0.5m에서 1′] 그리고 (b) 예.
- 심각도: (a) 0.41~1.24pt(1.5m 시각 한계 이하) 또는 (b)만 실패 → **minor** / (a) > 1.24pt → **major**.
- 출처: P2(접촉 문턱 1cm 광선 판정 + 무게중심 볼록 껍질), P1(지지 위반은 한 번의 응시로 탐지됨), P4(받침 단서가 없으면 떠 보임), P27.

**[OBJ_PLACE-02] 물체가 지지면에 파묻혀 밑동·문·발이 잘리지 않는가?**
- 적용: G·B·V1·V2·M. T는 귀속 규칙 2의 예외일 때만. 0-8의 의도된 묻힘은 뺀다.
- 판정 방법: (a) 밑면 표본에서 위로 쏜 광선의 최대 묻힘 깊이 d(pt 환산). (b) 지형·물·길이 덮은 실루엣 비율 b = |M_A ∩ 최종 ID(지형·물·길)| ÷ |M_A|(지지면에 닿는 밑 0.5pt 띠 제외). (c) 0-8 식별 부위의 노출률(V_A 안 비율).
- 합격 문턱: d ≤ max(1.0pt, h_A × 3%) 그리고 b ≤ 2% 그리고 식별 부위 노출 100% [운영값].
- 심각도: d 1~3pt 또는 b 2~10% → **minor** / d > 3pt, b > 10%, 또는 식별 부위(문·현관 기둥 밑·사람 발·줄기 밑동·이정표 받침)가 잘림 → **major**.
- 출처: P1(interposition: 바탕이 물체를 뚫고 지나가는 위반), P2(물체–구조 충돌), P4(밑동이 보이는 접촉 K자 교차가 접지 단서), P6(광학적 접촉점이 장면 배치를 정함).

**[OBJ_PLACE-03] 판형 지물(길·광장·밭·물 면·기단)이 지형에 밀착해, 땅이 뚫고 올라오거나 판이 들뜨지 않는가?**
- 적용: P1·P2·W. G는 콜로세움 기단만(○). T는 귀속 규칙 2의 예외일 때만.
- 판정 방법: ID 패스에서 판 A의 실루엣 M_A 안에 ground_land ID가 보이는 화소(지형 뚫림; 물 면이면 의도치 않은 섬)의 비율 p와 가장 큰 연결 덩어리 면적. 판 가장자리 옆면의 보이는 두께에서 설계 두께(길 돌 높이 0.094 등을 pt 환산)를 뺀 들뜸 초과분. Blender를 못 쓰면 0-5의 이미지 판정.
- 합격 문턱: p ≤ 0.5%, 최대 덩어리 < 2pt²(A2에서 0.25mm²) [운영값], 들뜸 초과분 ≤ 0.5pt.
- 심각도: 길·광장·다리 접속부: 덩어리 ≥ 2pt² 또는 들뜸 > 0.5pt → **major**(길이 끊겨 보임 — D32 '길 전 구간 보임'의 실행 실패). 밭: 덩어리 2~20pt² → **minor**, > 20pt² → **major**. 물 면의 의도치 않은 섬 ≥ 2pt² → **major**.
- 출처: P1(interposition), STATE D32, 인벤토리 보고(road_core_s 남쪽 포석 줄이 지형에 덮인 사례), P26(3D 지도의 기하 일반화).

**[OBJ_PLACE-04] 서 있는 물체가 곧게 서 있는가?**
- 적용: G, B의 교각(○), V1, V2, 장면 속 인물(G 안), 세워 둔 개념 모형(M의 d3 탑·⑤ 시편, ○).
- 판정 방법: Blender에서 물체(부품)의 세계 위 축(matrix_world의 Z열)과 세계 Z 사이 각. 이미지 확인: 단독 크롭에서 길이 ≥ 10pt인 건물 세로 모서리의 화면 각(Hough) — 평행 투영·롤 0에서 세계 수직은 화면 수직이다.
- 합격 문턱: 건물·교각·이정표·세운 모형 ≤ 1.0°, 나무·인물 ≤ 3° [운영값: 세로 근처 방향 판별 문턱 0.5~1°(P13) — 건물은 문턱 안, 나무·인물은 자연 흔들림 허용].
- 심각도: 건물류 1~3° / 나무·인물 3~8° → **minor**; 그보다 크면 → **major**.
- 출처: P13(세로 근처 방향 판별 문턱 약 0.5~1°), P1(지지 관계).

**[OBJ_PLACE-05] 그림자가 밑동에 붙어 있는가(떨어진 그림자 때문에 떠 보이지 않는가)?**
- 적용: G·B·V1·M 가운데 그림자 Sh_A가 있는 것. 나무는 R3으로 제외. 그림자의 세기·방향(R5)과 접촉 어둠(R10)은 판정하지 않는다.
- 판정 방법: 0-4의 Sh_A와, 01의 접촉 표본을 화면에 투영한 점들 사이 최소 거리 s_h(빛 반대쪽 밑동만).
- 합격 문턱: s_h ≤ 0.5pt [운영값: 지각되는 뜸 ≈ 그림자 어긋남의 2배(P4) → 1pt 미만].
- 심각도: 0.5~1.5pt → **minor** / > 1.5pt → **major**.
- 출처: P4(붙은 그림자 = K자 교차 = 접지, 떨어진 그림자의 어긋남이 떠 있는 높이의 지표, 그림자 있으면 '떠 있음' 응답 오즈비 0.004), P5(비사실 그림자도 표면 접촉 지각을 높임), P6.

**[OBJ_PLACE-06] 종이 위에 놓인 3D 아이콘·모형 줄이 같은 바닥선에 서 있는가?**
- 적용: O1(BASIC 아이콘 줄, 제목 아치의 두 기둥 받침), M 가운데 한 줄로 놓인 것(④ 큐브 3개, ⑤ 시편 2개, ○).
- 판정 방법: 줄을 이루는 각 아이콘(가로로 나란하고 세로 범위가 50% 이상 겹침)의 **바닥 접점** = 발자국 중심(최저 z 정점들의 x·y 평균, z = 최저)을 화면에 투영한 y. 줄 안 y의 범위. 그리고 줄 안에서 바닥 그림자가 있는 아이콘과 없는 아이콘이 섞였는지.
- 합격 문턱: y 범위 ≤ 1.0pt [운영값: 1.5m 시각 한계 1.24pt 아래] 그리고 그림자 유무 통일.
- 심각도: 1~3pt 또는 그림자 유무 섞임 → **minor** / > 3pt → **major**(한 아이콘이 줄에서 떠 있거나 가라앉아 보임).
- 출처: P30(바닥 위 물체의 화면 높이(시선 아래 각)가 거리·자리 판단을 정함), P15(좋은 연속), P4.

## B. 간격·겹침 — 이웃과 부딪치거나 애매하게 붙지 않는가

**[OBJ_PLACE-07] 다른 자산과 3D로 관통하지 않는가?**
- 적용: G·B·V1·V2·P1·P2·M, T의 산·화산(○). 0-8의 의도된 접촉은 뺀다.
- 판정 방법: 0-3의 BVH 교차로 비허용 교차 쌍과 교차 깊이(pt)를 구하고, 교차선이 화면에 보이는지(V_A 또는 V_B 위) 확인.
- 합격 문턱: 깊이 ≥ 0.5pt인 비허용 교차 0개(보이지 않는 교차는 기록만).
- 심각도: 보이는 교차 → **major** / 교차가 식별 부위를 자르거나 의미를 바꿈(나무가 건물 벽을 뚫음, 이정표·모형이 길 포석을 뚫음, 다리가 강둑 속으로 들어감) → **blocker**.
- 출처: P2(물체 충돌률 = 메시 충돌 검사), P3(충돌 없음 점수), P1(interposition), I3-22.

**[OBJ_PLACE-08] 이 자산이 정보 물체·길을 가리지 않는가?** (가린 쪽에 기록 — 귀속 규칙)
- 적용: 가릴 수 있는 모든 3D 자산(G·B·V1·V2·P1·P2·M·O1, T의 산·화산).
- 판정 방법: 가려진 정보 물체 B(CORE·DETAIL·SUPPORT·BASIC·이름 있는 지물·이정표·다리)마다 A가 가린 비율 o = |M_B ∩ V_A| ÷ |M_B|와 B의 식별 부위 가려짐. 길(핵심 길·가도)은 카메라 광선 기준 A에 가려진 길 정점 수(D32 방식; 다리 밑 강처럼 의도된 위아래 교차는 제외).
- 합격 문턱: o ≤ 3% [운영값] 그리고 식별 부위 가려짐 0 그리고 가려진 길 정점 0.
- 심각도: o 3~10% 또는 길 정점 1개 이상 → **major** / o > 10% 또는 식별 부위 가려짐 또는 길이 폭 전체로 끊겨 보임 → **blocker**(BRIEF: 가림).
- 출처: P7(Berann은 랜드마크·골짜기 바닥을 가리는 지형을 넓히거나 옮김), P8(관광 지도: 랜드마크·길의 가시성을 높이는 다중 시점 렌더), STATE D32, BRIEF §6.

**[OBJ_PLACE-09] 관계없는 이웃과 '애매한 접선'이 없는가(떨어지려면 확실히, 겹치려면 분명히)?**
- 적용: O2와 ground_land를 뺀 모든 자산. O1은 아이콘끼리만. 지지 관계·0-8의 의도된 접촉, 같은 이야기 묶음(예: CORE 그림과 자기 받침)은 뺀다. 도판 가장자리도 이웃으로 친다(제목 아치 아래끝은 LY-24로 넘김).
- 판정 방법: 이웃 B(A 상자 + 20pt 안)마다 부호 간격 s(A, B)(0-2). 그리고 두 윤곽이 1pt 안에서 나란히 가는 구간의 길이.
- 합격 문턱: s ≥ 4pt 또는 s ≤ −3pt(분명한 앞뒤 겹침 — 가림 여부는 08이 판정) [운영값: 0-6], 그리고 1pt 안 나란한 윤곽 < 20pt.
- 심각도: −3 < s < 4 → **minor** / 1pt 안 나란한 윤곽 ≥ 20pt(한 물체가 다른 물체에서 자라난 것처럼 읽힘) → **major**.
- 출처: P17(균일 연결: 맞닿은 영역은 한 단위로 지각), P15(근접·좋은 연속), P18(우연한 정렬은 일반 시점 가정에 어긋나 구조적 관계로 해석됨), P29(일러스트 실무: 접선은 깊이를 납작하게 하고 전경-배경을 흐림), P16.

**[OBJ_PLACE-10] 길이 아닌 물체가 길을 침범하거나 길에 애매하게 붙지 않는가?**
- 적용: G·V2·P2·M(이정표는 22, 다리는 23). 길 끝 목적지 광장·현관 접속은 뺀다.
- 판정 방법: 발자국 F_A(밭은 판 실루엣)와 길 자산(포석·연석·광장·다리 상판) 마스크의 겹침 면적과 최소 간격.
- 합격 문턱: 겹침 0 그리고 간격 ≥ 4pt(D32·D34) [운영값]. 밭은 간격 ≥ 4pt 또는 **정확히 붙임**(공유 변 80% 이상에서 간격 ≤ 0.5pt이고 평행 ±3° — 켄투리아 밭은 길을 따라 나뉨, P25).
- 심각도: 0.5~4pt(밭) / 0~4pt(그 밖) → **minor** / 겹침 > 0 → **major** / 길 폭의 50% 이상을 덮어 통행이 끊겨 보임 → **blocker**.
- 출처: STATE D32·D34(사용자 결정), P2(이동 가능 공간·기능 면 접근), P1(position), P25.

**[OBJ_PLACE-11] 땅 위 물체가 강·바다를 침범하지 않고 물가에서 떨어져 있는가?**
- 적용: G(항구 제외), V1, V2, P1(다리 밖 구간, ○), P2, M(해수 수조·방파제 블록 제외, ○).
- 판정 방법: F_A와 water_tiber·water_sea 마스크(물결 무늬 포함; 물가 = 물 마스크 경계)의 겹침 비율·최소 간격.
- 합격 문턱: 겹침 0 그리고 간격 ≥ 4pt(D12) [운영값].
- 심각도: 0~4pt → **minor** / 발자국의 0~10%가 물 위 → **major** / > 10%(물속에 선 건물·나무·밭) → **blocker**(사실·의미 오류).
- 출처: STATE D12, P1(position·probability 위반), P22(위상 보존은 경성 조건).

**[OBJ_PLACE-12] 물체와 글·2D 표지 사이 여유가 기준 이상인가?** (3D 쪽에 기록)
- 적용: 모든 3D 자산. W는 물결 무늬·물가선만 물체로 본다(물 면 위 글은 D5 결정). ground_land와 면 지물 안에 놓인 자기 이름(바다·산맥 이름)은 뺀다.
- 판정 방법: poster_2x에서 글 잉크(레이아웃 공통 정의: L = 0.299R + 0.587G + 0.114B < 140, 빨강 제목·밑줄은 R−G > 40 & R > 100 & L < 170)와 2D 표지(번호 원판·밑줄·핀·지시선) 화소, 그리고 V_A(ID 패스 → 2x). 기운 지명은 A의 밑동과 그림자 Sh_A까지 포함해 잰다.
- 합격 문턱: 수평 글·2D 표지 ≥ 4pt [운영값: 0-6], 기운 지명 ≥ 4pt(D13).
- 심각도: 겹침 → **blocker**(LY-01·I3-20·TY-28과 같음) / 수평 글·표지 < 3pt → **major**(LY-02와 같은 문턱), 3~4pt → **minor** / 기운 지명 < 2pt → **major**(TY-27), 2~4pt → **minor**(D13).
- 출처: P19(Imhof 원칙: 이름은 다른 요소와 겹치지 않고 가독), STATE D13, LY-01·02, TY-27·28, I3-20.

**[OBJ_PLACE-13] 자기 이름표가 가깝고, 다른 이름표보다 확실히 가까운가?**
- 적용: 이름표가 붙은 자산 — 지명(콜로세움·판테온·석회 가마·폼페이·베수비오 화산·아펜니노 산맥·수도교·티베르강·티레니아해·아피아 가도·항구), SUPPORT·DETAIL 이름표(지시선 없는 것), BASIC 아이콘 라벨. 지시선·핀이 있는 것은 29.
- 판정 방법: d_own = 이름표 잉크 상자 ↔ V_A 최소 거리. d_other = 그 이름표 ↔ 다른 이름 있는 자산 최소 거리. d_rev = A ↔ 다른 이름표 최소 거리. 면 지물은 가장 가까운 부분까지.
- 합격 문턱: 4pt ≤ d_own ≤ 20pt(INF-14) 그리고 d_other ÷ d_own ≥ 1.5 그리고 d_rev ÷ d_own ≥ 1.5(LY-05와 같은 비) [운영값].
- 심각도: d_own 20~40pt → **minor** / 비 1.0~1.5 → **major** / 비 < 1.0(이름표가 다른 물체에 더 가까움 → 잘못 읽힘) → **blocker**(의미 오류).
- 출처: P19(이름과 대상의 분명한 연결), P20(라벨–지물 연결의 명료함은 라벨 배치 연구의 합의된 요인), P16(근접 묶음 강도는 상대 거리로 정해짐), LY-05, INF-14.

## C. 방향 — 어디를 보고 있는가

**[OBJ_PLACE-14] 식별 면(정면)이 관람자 쪽으로 보이는가?**
- 적용: 정면이 정해진 G(판테온 현관, 석회 가마 아궁이, 프리베르눔 아치 벽면, 유적 관찰 장면 아치 벽, 폼페이 공사현장 비계 쪽, 항구 등대·부두 쪽, ○), B(물 위 아치 면), M(0-8 식별 면), O1(책 표지·돋보기·작은 콜로세움의 식별 면). 이정표는 17.
- 판정 방법: 식별 면들의 면적 가중 평균 법선 n_f(수평 성분)와 물체 → 카메라 방향 v(수평 성분, 평행 투영이면 카메라 앞 방향의 반대) 사이 각 α. 이미지 대안: 식별 면 투영 면적 ÷ 그 면을 카메라 정면으로 돌렸을 때 면적 = 단축 비 f(≈ cos α).
- 합격 문턱: α ≤ 60°(f ≥ 0.5) [운영값: 정준 시점은 식별 면이 보이는 3/4 시점(P9), 투영 면적이 시점 선호의 핵심 속성(P10)].
- 심각도: α 60~80° → **minor** / α > 80°(모서리만 보이거나 뒷면) → **major**.
- 출처: P9, P10, P7(Berann은 알아보는 면이 보이게 산맥을 55°까지 돌림), P8.
- 메모: 판테온은 D27(관람자 쪽)이 실제 북향보다 우선한다.

**[OBJ_PLACE-15] 출입구·기능 면이 길·광장 쪽을 향하고 앞이 막혀 있지 않은가?**
- 적용: 출입구·기능 면이 있는 G — 판테온 현관, 석회 가마 아궁이, 폼페이 도시 성문(있으면), 항구 부두(바다 쪽), 폼페이 공사현장 작업 면(○).
- 판정 방법: (a) n_f와 '출입구 중심 → 가장 가까운 길·광장 점' 방향 사이 각 β(수평). (b) 접근 띠(지면 위, 출입구 폭 × 그 0.5배 깊이)를 화면에 투영해, 그 안이 비어 있는(다른 자산이 아닌 지면·길) 비율(SceneEval ACC).
- 합격 문턱: β ≤ 90°(길이 정면 쪽 반평면에 있음) 그리고 비점유 ≥ 80% [운영값].
- 심각도: β 90~135° 또는 비점유 50~80% → **minor** / β > 135°(길이 뒤에만 있음) 또는 비점유 < 50%(나무·밭·다른 건물이 출입구를 막음) → **major**. 14·D27과 충돌하면 14가 우선하고 이 항목은 minor까지만.
- 출처: P2(기능 면 접근성 = 기능 면 앞 점유 분석, 비점유 화소 비율), P1(position).

**[OBJ_PLACE-16] 장면 속 인물이 자기 일(작업·관찰 대상)을 향하는가?**
- 적용: core2_hot_mixing(구덩이를 섞는 사람), support_ruin_observers(유적을 보는 연구자 4명), support_pompeii_site(인물이 있으면) — ○.
- 판정 방법: 인물마다 몸통·얼굴 정면 방향(수평 성분; Blender 부품 축 또는 얼굴 면 법선, 이미지에선 얼굴·가슴 정면의 화면 방향)과 '인물 → 대상 중심' 방향 사이 각 γ.
- 합격 문턱: 모든 인물 γ ≤ 45° [운영값].
- 심각도: 한 명이 45~90° → **minor** / 한 명이라도 > 90°(등을 돌림) 또는 과반이 45° 초과 → **major**.
- 출처: P12(그림 속 사람이 향한 물체를 관람자가 더 빨리·자주·오래 봄 — 인물 방향이 관람자 시선을 그 대상으로 이끎), I3-29.

**[OBJ_PLACE-17] 이정표 화살 판의 판면이 단축되지 않고 머리 끝까지 보이는가?**
- 적용: V1 3개. 화살 방향(다음 CORE)은 I3-28·LY-14·INF-08이 판정한다 — 여기서는 보이는 정도만.
- 판정 방법: 화살 판 앞면 법선과 카메라 방향의 각 → 판면 단축 비 f = |cos|. 화살 축 방향의 화면 길이 ÷ 실제 길이 L_p/L_t. 화살 판 실루엣 중 기둥에 가린 비율(Blender에서 판만 단독 렌더한 면적 대비 V_A의 판 부분), 화살 머리 끝 삼각형의 가림.
- 합격 문턱: f ≥ 0.6, L_p/L_t ≥ 0.7, 판 자기 가림 ≤ 10%, 머리 끝 가림 0 [운영값].
- 심각도: f 0.4~0.6 또는 L_p/L_t 0.5~0.7 또는 자기 가림 10~25% → **minor** / f < 0.4 또는 자기 가림 > 25% → **major** / 머리 끝이 가려 방향이 안 읽힘 → **blocker**(판독 불가).
- 출처: BRIEF 고정 조건 6, P10(투영 면적), P21(화살 방향 판독의 최소 치수는 관람 조건별 실험값), P23(지시 표지는 대상 면 위에 놓음).

**[OBJ_PLACE-18] 물체의 축이 주변 구조(길·밭 격자)와 맞는가?**
- 적용: P2(밭 6구역), G 가운데 직사각 평면이고 60pt 안에 길이 있는 것(폼페이 도시·프리베르눔·폼페이 공사현장·① 건물, ○). 14와 충돌하면 14가 우선하고 이 항목은 N/A.
- 판정 방법: 밭: 구역 안 판마다 바닥 사각형의 방위(Blender: 발자국 최소 외접 사각형, 이미지: 판 윤곽 Hough를 평행 투영 역변환). 구역 안 방위 범위, 구역 격자와 구역 경계 길 접선의 차 δ(0°·90° 중 가까운 쪽). 건물: 발자국 주축과 가장 가까운 길 접선의 δ.
- 합격 문턱: 밭 구역 안 방위 범위 ≤ 3°, 구역 격자–경계 길 δ ≤ 5°; 건물 δ ≤ 5° [운영값].
- 심각도: 범위·δ가 문턱 초과 ~15° → **minor** / 밭 구역 안 방위 범위 > 15°(격자가 흩어져 보임) → **major**.
- 출처: P25(켄투리아 밭의 띠는 카르도·데쿠마누스에 평행, 기존 길(비아 에밀리아 등)에 맞춘 격자, 땅은 길을 낸 뒤 나눔), P15(평행성 묶음).

## D. 축척 — 이웃과 크기 관계가 맞는가

**[OBJ_PLACE-19] 이웃과 실제 크기 순서가 뒤집히지 않는가?**
- 적용: 지도 축척 물체 G·B·V1·V2(M·O 제외).
- 판정 방법: A와 80pt 안 이웃 B마다 화면 높이 비 h_A/h_B와 참고 표 R-C의 실제 높이 비 H_A/H_B. 실제 비가 보수적으로(큰 쪽 하한 ÷ 작은 쪽 상한) 2 이상인 짝만 본다. 비율은 보지 않고 **순서만** 본다(랜드마크 과장은 파노라마 지도의 관례, P7).
- 합격 문턱: 그런 짝 모두 h 순서가 실제 순서와 같음 [운영값].
- 심각도: 40~80pt 이웃과 뒤집힘 → **minor** / 40pt 안 이웃과 뒤집힘 → **major**.
- 출처: P1(familiar size 관계 위반은 장면 판단을 늦춤), P11(실제 크기는 물체 표상에 자동으로 접근되는 속성, 정준 크기는 실제 크기의 로그를 따름), P7(선택적 과장은 허용하되 알아보게).

**[OBJ_PLACE-20] 같은 종류 반복 물체의 크기에 이상치가 없는가?**
- 적용: V2(나무 무리·같은 종의 외딴 나무), G 가운데 반복 부품이 있는 것(폼페이 도시의 집, 항구 바닷속 기둥, ○). 사람(I3-05)·이정표(I3-06)는 제외.
- 판정 방법: 같은 종·같은 부류 개체의 화면 높이 h(나무: 줄기 밑동 → 꼭대기) 중앙값 대비 각 개체 비.
- 합격 문턱: 모든 개체 0.75~1.33 [운영값: 자연 변이 허용, 이상치만].
- 심각도: 범위 밖 → **minor** / 0.5 이하 또는 2.0 이상 → **major**.
- 출처: P26(심벌화: 같은 부류는 같은 크기·색·밝기), P11.

**[OBJ_PLACE-21] 지도와 축척이 다른 개념 모형이 지도 물체와 섞이지 않고 떨어져 있는가?**
- 적용: M 7개.
- 판정 방법: (a) 모형 실루엣·발자국과 지도 축척 물체(길·밭·나무·건물·강·바다 — 물 관련 모형은 물 면 제외, 물결·해안·지도 물체만) 사이 최소 거리. (b) 자기 받침(판·수조·실험대) 위 또는 종이 빈터에 단독으로 서 있는지. (c) 40pt 안 지도 물체와 맞닿아 '거대한 물체'로 크기 비교가 생기는지.
- 합격 문턱: (a) ≥ 8pt [운영값: 4pt × 2 — 다른 축척은 공통 영역(받침·빈터)으로 갈라 보여야 함] 그리고 (b) 예 그리고 (c) 없음.
- 심각도: (a) 4~8pt → **minor** / (a) < 4pt 또는 (c) 있음 또는 지도 물체(길·밭·나무) 위에 놓임 → **major**.
- 출처: P1(size 위반), P11, P15(공통 영역 묶음), INF-15·20(개념 모형 표시).

## E. 길·이정표·다리

**[OBJ_PLACE-22] 이정표가 길가에 서 있되 포석 위를 막지 않는가?**
- 적용: V1. milestone_1_to_2는 R1·고정 조건 9로 **거리 조건 제외**(겹침만 본다).
- 판정 방법: 받침 발자국과 길 포석·연석 마스크의 겹침 면적과 최소 간격(pt).
- 합격 문턱: 겹침 0 그리고 1pt ≤ 간격 ≤ 10pt(I3-17과 같은 위 문턱; 1pt는 포석에 붙지 않는 최소) [운영값].
- 심각도: 간격 < 1pt(포석에 붙음) → **minor** / 간격 > 10pt 또는 받침이 포석 위 → **major**.
- 출처: P24(로마 이정표 miliarium은 길 가장자리에 세운 원기둥, 높이 2~4m, 네모 받침), BRIEF 고정 조건 6·9, I3-17.

**[OBJ_PLACE-23] 다리가 강을 제대로 건너고 양끝이 길에 이어지는가?**
- 적용: B 2개.
- 판정 방법: (a) 다리 축과 다리 아래 강 중심선 접선의 직교 편차 ε. (b) 양쪽 교대 끝이 물가(물 마스크 경계) 밖 땅 위로 나간 길이. (c) 양끝에서 길 포석까지 틈과 방향 꺾임. (d) 다리 아치 안·밑으로 물 화소가 이어짐(강이 다리 밑으로 흐름).
- 합격 문턱: ε ≤ 20°, (b) 양끝 ≥ 2pt, (c) 틈 ≤ 1pt·꺾임 ≤ 15°, (d) 예 [운영값].
- 심각도: ε 20~35° 또는 꺾임 15~30° → **minor** / 한쪽 끝이 물 위에서 끝남, 길과 틈 > 1pt(막다른 다리), 또는 (d) 실패 → **major** / 다리가 강을 건너지 않음 → **blocker**.
- 출처: I3-16(막다른 길 없음), P22(위상 보존), P2(양끝 지지 = 지지 판정), P1.

**[OBJ_PLACE-24] 사람이 쓰는 장소가 길로 닿을 수 있는가?**
- 적용: 콜로세움·판테온·석회 가마·폼페이 도시·폼페이 공사현장·항구·프리베르눔·유적 관찰 장면(○). 수도교·현대 건물(①)은 제외.
- 판정 방법: 발자국 둘레에서 가장 가까운 길·광장까지 거리 d_r, 그 사이(폭 4pt 띠)를 막는 물·건물 화소 유무(다리 경유 허용). 길 끝이 이 장소 쪽으로 오다가 멈춘 경우 그 끝과 발자국의 거리.
- 합격 문턱: d_r ≤ 30pt 그리고 막힘 없음 [운영값]. 길 끝이 이 장소를 향해 멈췄다면 그 거리 ≤ 5pt(I3-16과 같은 문턱).
- 심각도: d_r 30pt 초과 또는 막힘 → **minor** / 이 장소를 향한 길 끝이 5~30pt 앞에서 끊김(닿을 듯 말 듯) → **major**.
- 출처: P2(이동 가능 공간의 연결), I3-16, P25(로마 땅은 길을 먼저 낸 뒤 나눔).

## F. 장면 속 자리 — 지도 전체에서 자리가 타당한가

**[OBJ_PLACE-25] 실제 장소의 방위가 실제와 맞는가?**
- 적용: 실제 장소 자산(판테온, 항구, 오스티아 가도, 아피아 가도, 티베르강, 티레니아해, 베수비오, 폼페이 도시, 폼페이 공사현장, 프리베르눔, 수도교, 아펜니노). 콜로세움이 기준점.
- 판정 방법: 화면 방위 θ = atan2(Δx, −Δy)(화면 위 = 북, 시계 방향 +), Δ = 자산 V_A 무게중심 − 콜로세움 V_A 무게중심(D34 이동 뒤 값으로 다시 잰다). 늘어진 지물(산맥·강·바다·길)은 자산 화소들의 방위 범위. 참고 표 R-A와 비교.
- 합격 문턱: 점 지물은 |θ − 실제| ≤ 45°, 늘어진 지물은 화면 방위 범위의 50% 이상이 실제 범위와 겹침 [운영값: 이웃 위치 관계를 한 구획(±45°) 안에서 유지하는 도식 지도 관례(P22)].
- 심각도: 45~90° → **minor**(동심원 배치 고정 조건 때문에 완화) / > 90° → **major**. 위상(어느 기슭·어디에 닿음)은 26.
- 출처: P22(위상 보존 = 경성, 이웃 상대 위치 보존 = 연성 조건), BRIEF 고정 조건 4, P7(선택적 이동은 알아볼 수 있게), R-A의 좌표.

**[OBJ_PLACE-26] 지도 위 위상 관계가 실제와 같은가?**
- 적용: 참고 표 R-B의 명제에 등장하는 자산(명제마다 '기록 자산'에 기록).
- 판정 방법: R-B의 명제를 화면 마스크로 하나씩 참/거짓 판정.
- 합격 문턱: 해당 명제 모두 참.
- 심각도: 거리 문턱만 넘고 위상은 맞음 → **minor** / 위상이 틀림(예: 판테온이 강 건너편, 항구가 바다에 닿지 않음, 다리가 강을 안 건넘) → **blocker**(사실 오류).
- 출처: P22(위상 보존은 경성 조건), BRIEF 고정 조건 4, INF-19(사실 정확성).

**[OBJ_PLACE-27] 물체를 받치는 바탕이 그 물체에 맞는가?**
- 적용: G·B·V1·V2·P1·P2·M.
- 판정 방법: 01의 접촉 표본이 맞은 지지면의 종류 분포(ID: 지형/길·광장/밭/물/기단/다리 상판/자기 받침)와, 건물·이정표 발자국 아래 지형 법선의 기울기(광선 맞은 면 법선).
- 허용 표: 건물·장면 → 지형·자기 기단·광장(포석 길 ×, 밭 ×, 물 ×) / 나무 → 지형, 밭 판은 가장자리 3pt 안만(길·광장·다리 ×) / 이정표 → 지형·자기 받침(포석 ×) / 길 → 지형·다리 / 밭 → 지형 / 항구 → 물·해안 / 개념 모형 → 자기 받침·종이 빈터 지형·물(물 관련 모형만).
- 합격 문턱: 접촉 표본의 ≥ 95%가 허용 지지면 그리고 건물·이정표 아래 지형 기울기 ≤ 8° 또는 자기 기단·평탄지 위(D34) [운영값].
- 심각도: 비허용 5~25% 또는 기울기 8~15° → **minor** / 비허용 > 25% 또는 기울기 > 15° → **major**(물 위에 선 땅 물체는 11에서 blocker).
- 출처: P1(probability·position: 물체는 장면의 정해진 자리에 놓임), P2(지지 유형 판정 — 바닥·물체·벽), STATE D34.

**[OBJ_PLACE-28] 여러 부품으로 된 자산이 한 덩어리로 묶여 보이는가?**
- 적용: O1(BASIC 아이콘 묶음), V2 무리(trees_s·trees_se), 부품 여럿인 G(항구, 폼페이 공사현장, 폼페이 도시, 유적 관찰 장면, ② 장면, ○), M(해수 수조 결정들, ④ 큐브 3개, ⑤ 시편 2개, d2·d3, ○).
- 판정 방법: 부품(연결 성분) 사이 최소 신장 트리의 가장 긴 변 g_in(pt) vs 자산 외곽에서 가장 가까운 다른 자산(지지면·길 제외)까지 g_out.
- 합격 문턱: g_out ÷ g_in ≥ 1.5(LY-07과 같은 비) [운영값].
- 심각도: 1.0~1.5 → **minor** / < 1.0(부품이 남의 물체에 더 가까워 섞여 읽힘) → **major**.
- 출처: P16(근접 묶음 = 상대 거리 법칙), P15, LY-07.

**[OBJ_PLACE-29] 지시 도형(핀·지시선·단면 지시)이 대상에 정확히 닿고, 대상의 식별 부위를 가리지 않는가?**
- 적용: O2 가운데 shape_pin_harbor, shape_pin_pompeii, shape_d2_leader, shape_d3_section(지시선 부분).
- 판정 방법: 대상 쪽 끝점(점·핀 끝) 중심이 대상 V_A 윤곽에서 안쪽으로 들어간 거리. 끝점이 다른 자산 위에 있는지. 끝점 표지가 대상 식별 부위를 덮는 비율(ID 패스 겹 패스 가림, `inventory.json`의 `covered_by_overlay_pct`). 글 쪽 끝은 LY-06이 판정.
- 합격 문턱: 점 끝이 대상 면 안쪽 ≥ 1pt(점 = 면을 가리킴, P23) 그리고 다른 자산 위 아님 그리고 식별 부위 덮음 ≤ 25% [운영값].
- 심각도: 안쪽 0~1pt(윤곽에 걸침) 또는 덮음 25~50% → **minor** / 끝점이 대상 밖 또는 덮음 > 50% → **major** / 끝점이 다른 이름 있는 물체를 가리킴 → **blocker**(오지시).
- 출처: P23(BS ISO 128-22: 화살 끝은 모서리, 점 끝은 면을 가리킴), P19(이름과 대상의 분명한 연결), LY-06.

---

## 참고 표

### R-A. 실제 방위(콜로세움 기준, 북 = 0°, 시계 방향)
좌표는 위키백과 정보상자 값(콜로세움 41.890°N 12.492°E)으로 계산한 대권 근사 방위다. 비평가는 다시 계산해도 되며 ±3° 안에서 같아야 한다.

| 자산 | 실제 대상(좌표) | 실제 방위 | 허용(±45° / 범위) |
|---|---|---|---|
| landmark_pantheon | 판테온(41.899°N 12.477°E, 1.6km) | 306° | 261~351° |
| support_harbor | 오스티아 안티카(41.756°N 12.292°E)·포르투스 | 228~237° | 183~282° |
| road_ostiensis | 로마 → 오스티아 | 바다 쪽 끝 방위 228° | 183~273° |
| water_tiber | 상류 북쪽(로마 북쪽에서 들어옴), 하구 232° | 범위 약 330°~20°(상류)·232°(하구) | 범위 겹침 ≥ 50% |
| water_sea | 티레니아해 | 범위 약 200~270° | 범위 겹침 ≥ 50% |
| road_appia | 시작 157°(포르타 산 세바스티아노) → 카푸아 쪽 122° | 범위 약 120~160° | 범위 겹침 ≥ 50% |
| landmark_vesuvius | 베수비오(40.821°N 14.426°E) | 126° | 81~171° |
| landmark_pompeii_town, support_pompeii_site | 폼페이(40.750°N 14.486°E) | 127° | 82~172° |
| support_privernum | 프리베르노(41.467°N 13.183°E, 현대 마을 좌표) | 129° | 84~174° |
| landmark_aqueduct | 아쿠아 클라우디아: 수원(비아 술라켄시스 38마일, 수비아코 쪽) 약 86° ~ 로마 남동 들판 아치 약 126° | 범위 약 80~130° | 범위 겹침 ≥ 50% |
| landmark_apennines | 토스카나·에밀리아 아펜니노 약 330° ~ 캄파니아 아펜니노 약 120°(테르미닐로 33°, 프레네스티니 82°) | 범위 약 330~120° | 범위 겹침 ≥ 50% |

### R-B. 위상 명제(26)

| # | 명제 | 화면 판정 | 기록 자산 |
|---|---|---|---|
| T1 | 판테온과 콜로세움은 티베르강의 같은 기슭(동안)에 있다 | 두 무게중심을 잇는 선분이 강 마스크를 가로지르지 않음 | landmark_pantheon |
| T2 | 항구는 티베르강 하구 곁, 바닷가에 있다 | 항구 발자국 ↔ 강 하구(강·바다 마스크가 만나는 구간) ≤ 60pt, 항구가 바다 마스크에 닿음 | support_harbor |
| T3 | 폼페이 도시는 베수비오 기슭(약 8km)에 있다 | 폼페이 발자국 ↔ 베수비오 실루엣 ≤ 30pt | landmark_pompeii_town |
| T4 | 폼페이 공사현장은 폼페이 곁에 있다 | 공사현장 ↔ 폼페이 도시 ≤ 40pt | support_pompeii_site |
| T5 | 아피아 가도는 로마에서 남동으로 뻗는다 | 한쪽 끝이 핵심 길·콜로세움 고리에 5pt 안으로 이어지고 다른 끝이 R-A 범위 쪽(도판 가장자리 포함) | road_appia |
| T6 | 오스티아 가도는 로마와 항구를 잇는다 | 양끝이 로마 쪽 길망과 항구에 각각 5pt 안 | road_ostiensis |
| T7 | 수도교는 산 쪽에서 로마로 물을 끌어온다 | 콜로세움에 가까운 끝이 도시 쪽(콜로세움 고리 쪽), 먼 끝이 산·도판 가장자리 쪽 | landmark_aqueduct |
| T8 | 티베르강은 로마 서쪽을 지나 바다로 흐른다 | 콜로세움 높이에서 강 마스크가 콜로세움보다 화면 왼쪽, 하구가 바다에 닿음 | water_tiber |
| T9 | 프리베르눔 곁으로 아피아 가도가 지난다 | 프리베르눔 발자국 ↔ 아피아 가도 ≤ 60pt | support_privernum |
| T10 | 다리는 강을 건넌다 | 23(d)와 양끝 땅 | bridge_* |

### R-C. 실제 높이(19)

| 부류 | 실제 높이 | 출처 |
|---|---|---|
| 사람 | 1.6~1.8m | 상식값 |
| 로마 이정표(받침 포함) | 2~4m | P24 |
| 우산소나무 | 보통 12~20m(25m 넘기도) | P28 |
| 사이프러스 | 최대 35m(성목 하한 10m는 운영 가정) | P28 |
| 판테온 | 43.3m(돔 꼭대기·안지름) | P28 |
| 콜로세움 외벽 | 48m | P28 |

- 보수적 비 ≥ 2인 짝: 나무 > 이정표·사람, 판테온·콜로세움 > 이정표·사람, 판테온·콜로세움 > 우산소나무(43.3 ÷ 20 = 2.2, 48 ÷ 20 = 2.4), 이정표 > 사람은 비 < 2라 보지 않음(I3 몫).

---

## 출처 (항목의 P 번호)

| ID | 저자·연도 | 제목·학회/저널 | URL | 확인 범위 |
|---|---|---|---|---|
| P1 | Biederman, Mezzanotte, Rabinowitz 1982 | Scene perception: Detecting and judging objects undergoing relational violations. *Cognitive Psychology* 14(2):143–177 (다섯 관계: interposition·support·probability·position·familiar size) | https://www.cs.princeton.edu/courses/archive/spring08/cos598B/Readings/Biederman1982.pdf | 초록·2차 요약 |
| P2 | Tam, Pun, Wang, Chang, Savva 2025 | SceneEval: Evaluating Semantic Coherence in Text-Conditioned 3D Indoor Scene Synthesis. arXiv 2503.14756 (WACV 2026) — 충돌(메시 충돌 검사), 지지(최저 정점에서 광선, 1cm 안 접촉, 접촉점 볼록 껍질 안 무게중심), 이동 가능성, 기능 면 접근성(비점유 화소 비율) | https://arxiv.org/abs/2503.14756 | 본문(3장·부록 B.2.2) 직접 확인 |
| P3 | Sun, Liu 외 2025 | LayoutVLM: Differentiable Optimization of 3D Layout via Vision-Language Models. *CVPR 2025*:29469–29478 (Collision-Free·In-Boundary 점수) | https://openaccess.thecvf.com/content/CVPR2025/html/Sun_LayoutVLM_Differentiable_Optimization_of_3D_Layout_via_Vision-Language_Models_CVPR_2025_paper.html | 본문 지표 정의 확인 |
| P4 | Cooper, Casati, Farid, Cavanagh 2023 | The art of the float. *Journal of Vision* 23(8):13 (붙은 그림자 = K자 교차, 그림자 어긋남이 뜬 높이의 지표, 지각된 분리 ≈ 어긋남 × 2, 그림자 있으면 떠 있음 오즈비 0.004) | https://pmc.ncbi.nlm.nih.gov/articles/PMC10434713/ | 본문 확인 |
| P5 | Adams, Gagnon, Creem-Regehr, Stefanucci, Bodenheimer 2022 | Stay in Touch! Shape and Shadow Influence Surface Contact in XR Displays. arXiv 2201.01889 (비사실 그림자 셰이딩이 표면 접촉 지각을 높임). 같은 그룹: Adams 외 2022, Shedding Light on Cast Shadows, *IEEE TVCG* 28(12):4624–4639, doi:10.1109/TVCG.2021.3097978 | https://arxiv.org/abs/2201.01889 | 초록 확인(TVCG는 서지만) |
| P6 | Ni, Braunstein, Andersen 2004 | Perception of scene layout from optical contact, shadows, and motion. *Perception* 33:1305–1318 | https://wichita.edu/academics/fairmount_las/psychology/documents/Ni_2004_Perception_Shadow.pdf | 서지·초록 |
| P7 | Patterson 2000 | A View From On High: Heinrich Berann's Panoramas and Landscape Visualization Techniques for the U.S. National Park Service. *Cartographic Perspectives* 36:38–65 (랜드마크 선택 과장, 테톤 산맥 55° 회전, 골짜기 바닥을 가리는 지형 넓힘, 인공물 축척 과장) | https://cartographicperspectives.org/index.php/journal/article/download/cp36-patterson/pdf | 본문 확인 |
| P8 | Grabler, Agrawala, Sumner, Pauly 2008 | Automatic Generation of Tourist Maps. *ACM TOG* 27(3) (SIGGRAPH 2008), doi:10.1145/1360612.1360699 (랜드마크·길의 가시성을 높이는 다중 시점 렌더 + 일반화(단순화·변형·이동)) | https://history.siggraph.org/?p=112905 | 초록 |
| P9 | Blanz, Tarr, Bülthoff 1999 | What object attributes determine canonical views? *Perception* 28(5):575–599 (Palmer, Rosch, Chase 1981의 정준 시점을 3D 조작으로 재현, 기하·경험·기능 속성) | https://kilthub.cmu.edu/articles/journal_contribution/What_object_attributes_determine_canonical_views_/6619112 | 초록 |
| P10 | Secord, Lu, Finkelstein, Singh, Nealen 2011 | Perceptual Models of Viewpoint Preference. *ACM TOG* 30(5) (투영 면적·실루엣이 시점 선호의 핵심 속성) | https://gfx.cs.princeton.edu/pubs/Secord_2011_PMO/ | illustration3d S18과 같음 |
| P11 | Konkle, Oliva 2011 | Canonical Visual Size for Real-World Objects. *JEP: HPP* 37(1):23–37 (정준 크기는 실제 크기의 로그를 따름; 2012 후속에서 실제 크기 자동 접근) | https://pmc.ncbi.nlm.nih.gov/articles/PMC3408867 | 초록·요약 |
| P12 | Zwickel, Võ 2010 | How the presence of persons biases eye movements. *Psychonomic Bulletin & Review* 17:257–262, doi:10.3758/PBR.17.2.257 (사람이 향한 물체를 더 빨리·자주·오래 봄) | https://link.springer.com/article/10.3758/PBR.17.2.257 | 초록 |
| P13 | Burr, Wijesundra 1991 | Orientation discrimination depends on spatial frequency. *Vision Research* 31:1449–1452 (고대비 세로 근처 격자 방향 판별 문턱 약 1° → 0.5°) | https://flore.unifi.it/handle/2158/680197 | 초록 |
| P15 | Wagemans, Elder, Kubovy, Palmer, Peterson, Singh, von der Heydt 2012 | A century of Gestalt psychology in visual perception: I. *Psychological Bulletin* 138(6):1172–1217 (근접·좋은 연속·평행·공통 영역·균일 연결) | https://pmc.ncbi.nlm.nih.gov/articles/PMC3482144/ | layout.md와 같음 |
| P16 | Kubovy, Holcombe, Wagemans 1998 | On the lawfulness of grouping by proximity. *Cognitive Psychology* 35(1):71–98 | https://lirias.kuleuven.be/retrieve/93542 | layout.md와 같음 |
| P17 | Palmer, Rock 1994 | Rethinking perceptual organization: The role of uniform connectedness. *Psychonomic Bulletin & Review* 1:29–55, doi:10.3758/BF03200760 | https://doi.org/10.3758/BF03200760 | 서지·2차 요약 |
| P18 | Freeman 1994 | The generic viewpoint assumption in a framework for visual perception. *Nature* 368:542–545 (예비본 MERL TR93-19a) | https://www.merl.com/publications/docs/TR93-19a.pdf | 서지·2차 요약 |
| P19 | Kern, Brewer 2008 | Automation and the Map Label Placement Problem. *Cartographic Perspectives* 60:22–45 (Imhof 1975 라벨 원칙: 가독·대상 연결·겹침 회피; van Dijk 1999 품질 기준) | https://cartographicperspectives.org/index.php/journal/article/download/cp60-kern-brewer/pdf/1397 | layout.md와 같음 |
| P20 | Bobák, Čmolík, Čadík 2024 | From Top-Right to User-Right: Perceptual Prioritization of Point-Feature Label Positions. arXiv 2407.11996 (라벨 충돌 회피·라벨–지물 연결 명료성은 합의된 요인) | https://arxiv.org/abs/2407.11996 | 본문 요약 확인 |
| P21 | Ledermann 2023 | Minimum Dimensions for Cartographic Symbology: Towards a Comprehensive Definition and Assessment Method. *Abstracts of the ICA* 6:134 (최소 치수는 관람 조건·대상·과제별로 정의; 화살 방향 판독 실험에서 선폭 0.5mm) | https://doi.org/10.5194/ica-abs-6-134-2023 | 본문 확인 |
| P22 | Nöllenburg, Wolff 2011 | Drawing and Labeling High-Quality Metro Maps by Mixed-Integer Programming. *IEEE TVCG* 17(5):626–641 (경성: 입력 위상 보존; 연성: 이웃 역의 상대 위치 보존) | https://algo.iti.kit.edu/en/projects/geovis/metro | 프로젝트 쪽 기준 목록 확인 |
| P23 | BS ISO 128-22:1999 (해설: The CAD Setter Out) | Technical drawings — leader lines and reference lines (화살 끝 = 모서리, 점 끝 = 면) | https://cadsetterout.com/drawing-standards/technical-drawing-standards-leader-lines/ | 2차 해설 |
| P24 | Wikipedia | Miliarium — 로마 길 가장자리에 세운 원기둥, 높이 2~4m, 지름 50~80cm, 네모 받침 | https://en.wikipedia.org/wiki/Miliarium | 2차 자료 |
| P25 | Wikipedia | Centuriation — 띠는 카르도·데쿠마누스에 평행, 기존 길(비아 에밀리아)에 맞춘 격자, 길을 낸 뒤 땅을 나눔 | https://en.wikipedia.org/wiki/Centuriation | 2차 자료 |
| P26 | Häberling, Bär, Hurni 2008 / Santos, Delazari, Brandalize 2013 | Proposed Cartographic Design Principles for 3D Maps. *Cartographica* 43(3):175–188 / 그 3단계(모델링 → 심벌화 → 시각화) 요약 | https://www.redalyc.org/pdf/3939/393937730006.pdf | illustration3d S1·S2와 같음 |
| P27 | Wikipedia | Visual acuity — 정상 시력의 임계 간격 1′ | https://en.wikipedia.org/wiki/Visual_acuity | 2차 자료 |
| P28 | Wikipedia | Colosseum(외벽 48m), Pantheon, Rome(43.3m, 현관 북향), Pinus pinea(12~20m), Cupressus sempervirens(최대 35m), Aqua Claudia(아치 30m 넘음, 포르타 마조레로 들어옴), Ostia Antica·Pompeii(베수비오에서 8km)·Privernum 좌표 | https://en.wikipedia.org/wiki/Colosseum · https://en.wikipedia.org/wiki/Pantheon,_Rome · https://en.wikipedia.org/wiki/Pinus_pinea · https://en.wikipedia.org/wiki/Cupressus_sempervirens · https://en.wikipedia.org/wiki/Aqua_Claudia · https://en.wikipedia.org/wiki/Pompeii · https://en.wikipedia.org/wiki/Privernum | 2차 자료 |
| P29 | Notes on Illustration (실무 자료) | On a tangent — 접선은 깊이를 납작하게 하고 전경-배경을 흐림 | https://illustrationdept.substack.com/p/on-a-tangent | 2차 실무 자료 |
| P30 | Ooi, Wu, He 2001 | Distance determined by the angular declination below the horizon. *Nature* 414:197–200 (바닥 위 물체의 시선 아래 각이 거리 판단을 정함) | https://www.sciencenews.org/article/how-far-away-0 | 2차 보도 |

- 2022~2026 자료: P2(2025, WACV 2026), P3(2025), P4(2023), P5(2022), P20(2024), P21(2023) — 6개.
- P14는 비워 둔다(Appelle 1972 사각 효과 리뷰는 원문을 열지 못해 쓰지 않음).
