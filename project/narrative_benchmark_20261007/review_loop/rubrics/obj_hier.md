# 루브릭 · 물체 단위 시각 위계 (field = obj_hier)

- 작성: 2026-10-13, 물체 위계 비평가(라운드 11 첫 심사용). STATE D37에 따라 Blender 자산 57개를 **자산 하나하나** 판정한다. 다음 라운드부터 이 파일을 고정해 다른 비평가가 블라인드로 재현한다.
- 질문 하나: **이 물체의 크기·명도 대비·색 대비(채도)·디테일 밀도가 자기 역할(CORE > DETAIL > SUPPORT > BASIC > 지물 > 배경)에 맞는가? 특히 하위 물체가 근처 CORE보다 눈을 먼저 끌지 않는가?**
- 판정은 항목마다 예(합격) / 아니오(불합격)이다. 등급은 **자산마다** 매기고 BRIEF와 같다: **AAA** = blocker 0 · major 0 · minor ≤ 2 / **AA** = blocker 0 · major ≤ 2 / **A** = blocker 0 · major ≥ 3 / **B** = blocker 1~2 / **C** = blocker ≥ 3. 적용 항목이 하나도 없는 자산(§1의 X)은 "해당 없음 = AAA"로 둔다.
- 수치 가운데 문헌이 직접 준 값은 [문헌값], 문헌의 원리를 이 포스터에서 재현할 수 있게 옮긴 값은 [운영값]으로 표시한다.
- 작성 때 라운드 10 인벤토리(`roman_concrete_narrative_v8_12.blend`, sha256 4e4fe70b…)로 모든 항목을 끝까지 계산해 측정이 돌아가는지 확인했다. 블라인드 심사를 해치지 않으려고 그 값은 적지 않는다.

## 고정 조건과 결정 (감점하지 않음 · BRIEF §3, STATE)
- 클레이 디오라마 3D 렌더(약간 플랫한 음영), 콜로세움 중심 동심원 배치, 로마 시대 실제 장소(베수비오·아펜니노·티베르강·티레니아해·수도교·아피아 가도·폼페이)가 있다는 것 자체는 감점하지 않는다. 2D로 바꾸거나 장소를 빼는 해법은 내지 않는다.
- CORE 번호 원판·밑줄의 #983821(고정 조건 5), 이정표 화살 판의 ②색과 석회암 기둥(고정 조건 6)의 **색**은 판정하지 않는다. 그래서 `shape_core1~5_marker`는 판정에서 빼고, 이정표 3개는 크기·디테일만 본다(OBJ_HIER-17).
- 콜로세움이 가장 큰 물체라는 것은 의도다(LY-10이 따로 잰다). 영웅의 크기·디테일은 감점하지 않고, 영웅이 CORE보다 **대비**에서 앞서는지만 본다(OBJ_HIER-11).
- D35(밭 작물색), D36(현무암색 포석·석회암 연석), D27(판테온 실제 형태)은 사용자 결정이다. 칠하거나 형태를 바꾼 것 자체는 감점하지 않는다. 그 결과 위계가 뒤집혔을 때만 지적하고, 해법은 그 결정 안에서 채도·명도·국소 대비를 낮추는 것만 낸다.
- 기각·보류 목록의 원인은 다시 내지 않는다: R3(나무 그림자), R5(모형별 그림자 세기·방향), R10(밑동 접촉 어둠), R11(베수비오 북서 능선 지느러미).

## 다른 루브릭과의 경계 (겹치지 않게 뺀 것)
- 포스터 단위로 이미 재는 것: 콜로세움 면적 우세(LY-10), 휘도 주목도·흐림 덩어리·첫 응시(VL-01~VL-08), 모형 대표면 그림-바탕 ΔL\* ≥ 10(I3-15), 축척 순위(I3-07), 글 크기 위계(H1~H4, TY-01), 글 대비(CL-13~18), 강조색 독점(CL-05).
- 물체 단위 다른 분야가 볼 것(겹치면 그쪽에 맡긴다): 같은 재질 같은 색·팔레트 조화(컬러), 물체 안 명도 계단·먹색 뭉개짐(명암), 메시·실루엣 결함(3D 형태), 단서가 뜻을 맞게 전하는가(인포그래픽 의미), 간격·정렬·글과의 거리(배치).
- 이 루브릭은 **역할 사이의 상대 세기**만 잰다. 네 경로(크기, 명도 대비, 색 대비·채도, 디테일 밀도)는 Wolfe & Horowitz(H3)가 주의를 이끈다고 확정한 속성(크기·색)과 지도학·일러스트레이션의 강조 수단(H1·H8·H10·H12)에서 골랐다.

---

## 0. 측정 규약 (모든 항목 공통 · 재현용)

### 0.1 자료
- **자산 크롭**: 라운드마다 다시 렌더한 `assets_index.json`과 `assets/<id>/`를 쓴다(현재 위치 `nb_work/workers/inventory/`. 라운드 폴더로 복사되면 그 경로). `blend_sha256`가 그 라운드 blend와 같은지 먼저 확인한다. 다시 만드는 명령: `Blender -b <blend> --factory-startup --python render_assets.py -- <out_dir> --percent 72 --scale 3 --margin 12 --iso-bg 140,140,140`.
  - `context.png`는 포스터 전체 렌더를 자산 상자 ±12pt로 자른 맥락 크롭이고, `isolated.png`와 `isolated_rgba.png`는 같은 카메라·같은 상자로 그 자산만 렌더한 단독 크롭이다. 배율 S = `crop_scale`(현재 3 px/pt)이다.
- **CORE 글 상자**: `text_spec_r<N>.json`. ① 790:102·146·147·148 / ② 790:105·152·153·154 / ③ 790:110·158·159·160 / ④ 790:111·164·165·166 / ⑤ 790:106·170·171·172의 합집합 상자를 쓴다.
- PNG에 ICC가 없으면 sRGB로 본다.

### 0.2 화소 집합
- **M(물체)** = `isolated_rgba` 알파 ≥ 128.
- **V(보이는 물체)** = M 가운데 |L\*(context) − L\*(isolated)| < 6인 화소. 다른 물체에 가려지거나 그 그림자를 받은 화소를 뺀 것이다. **vis** = |V| / |M|.
- **고리 R** = M 바깥으로 3pt < 거리 ≤ 15pt인 context 화소(맥락의 실제 주변).
- **안쪽 I** = V를 1pt(S px) 깎은 영역. 실루엣 테두리를 빼려는 것이다.

### 0.3 색 공간
- L\* = sRGB → 선형(IEC 61966-2-1) → Y = 0.2126R + 0.7152G + 0.0722B → CIE L\*(value.md 규약 2와 같음).
- Oklab·Oklch = Ottosson 2020 행렬(H18). C = √(a² + b²).
- 대표색은 V 화소 CIELAB(D65) 중앙값이고, ΔE00은 CIEDE2000(skimage `deltaE_ciede2000`)이다.
- **JND** [문헌값]: Oklch 차 0.02, ΔE2000 2(CSS Color 4, H17).

### 0.4 네 경로 지표 (자산마다)
| 기호 | 이름 | 정의 |
|---|---|---|
| **A** | 덩어리 면적(pt²) | V를 2pt 닫힘(closing)한 뒤 가장 큰 연결 성분의 면적 ÷ S². 여러 조각인 자산(밭·나무 무리·항구)은 가장 큰 덩어리를 쓴다 |
| **K** | 정점 명도 대비(L\*) | max(median L\*(R) − P5 L\*(V), P95 L\*(V) − median L\*(R)) |
| **Kc** | 색 대비(종이에서 떨어진 정도) | V 화소마다 ‖(a,b)_Oklab − (a,b)_종이‖의 90백분위. (a,b)_종이는 `ground_land`의 V 화소 Oklab (a,b) 중앙값이다(라운드 10에서 약 (0.004, 0.032), 따뜻한 베이지). 채도와 색상 차를 함께 잰다 |
| **D** | 강한 디테일 비율 | I 안에서 \|L\* − N(L\*)\| > 8인 화소의 비율. N은 V로 정규화한 가우스 흐림(σ = 2pt)으로, N = G(L·V) / G(V)이다. 2pt 크기에서 명도가 크게 바뀌는 결(창·기둥·포석 이음·밭 이랑)의 밀도를 잰다 |

- 보조 지표: L\*_med(V 중앙값), C_med와 C90(V의 Oklch C 중앙값·90백분위), **강채도 면적** = V 가운데 Oklch C ≥ 0.10인 화소 면적(pt²).

### 0.5 주의 창(FOA)과 CORE 기준값
- **CORE 구역 k** = CORE k 그림 자산의 `bbox_visible_final_pt`, 그리고 0.1의 CORE k 글 합집합 상자. 직사각형 두 개다.
- **FOA 안** = 두 직사각형 사이 최소 간격이 **198.5pt 이하**. 짧은 변의 1/6로, Itti 1998의 주의 반지름이며 value.md 규약 8과 같다(H20).
- **CORE 중앙값 med_c / 최댓값 max_c** = CORE 그림 5개(§1 T1)의 경로 c 값의 중앙값·최댓값.
- **기준값 R_c** (자산 X, 경로 c):
  - X가 CORE k의 FOA 안이면 그런 k마다 **R_c = max(v_k,c, med_c)**. 한 CORE가 일부러 약하게 둔 경로(예: ①의 무채색, ③의 단순한 면)가 있어도 그 CORE 몫까지 깎지 않으려는 것이다. 여러 k 가운데 가장 나쁜 결과 하나만 센다.
  - 어느 FOA에도 없으면 **R_c = max_c**(전역 경쟁). 포스터 전체에서 모든 CORE보다 셀 때만 걸린다.

### 0.6 묶음 규칙 §M (OBJ_HIER-06~09의 심각도)
같은 자산이 같은 기준(같은 CORE k 또는 전역)에서 여러 경로로 넘으면 **지적 하나로 묶고** 아래 점수 n으로 심각도를 정한다.
- 경로마다 넘음 1점. **큰 넘음** 2점(A ≥ 3R, K ≥ R+10, Kc ≥ R+0.06). D는 넘어도 큰 넘음 없이 최대 1점이다. 선 밀도 강조는 색 강조보다 효과가 약하다는 결과(H1)에 따른 것이다. 전역 기준(FOA 밖)에서는 큰 넘음도 1점이다(H5: 멀수록 신호가 약함).
- **크기 보상**: A만 넘고 K ≤ 0.8R_K, Kc ≤ 0.8R_Kc, D ≤ 0.8R_D이면 n = 0이다. 크지만 옅고 단순한 면은 뒤로 물러난다(Imhof 색 규칙 H11, 대기 원근 H12) [운영값 0.8].
- **n = 1 → minor, n ≥ 2 → major.** FOA 안에서 **네 경로를 모두 넘으면 blocker**다. 그 CORE는 자기 주의 창에서 어떤 단서로도 1위가 아니게 되고, 이는 측정으로 증명된다.
- 같은 자산의 OBJ_HIER-10 지적과 원인이 같으면 높은 쪽 하나로 센다.

---

## 1. 역할 단계표 (자산 57개)
인벤토리 `role`을 기본으로 하고, value.md 규약 5와 같이 ③·④·⑤ 그림은 **CORE 그림으로 센다**(그 CORE의 유일한 그림, INF-15).

| 단계 | 자산 |
|---|---|
| **T0 영웅** | landmark_colosseum |
| **T1 CORE 그림** | core1_modern_building(①), core2_hot_mixing(②), detail_core3_lime_specimen(③), detail_core4_three_cubes(④), support_core5_lab(⑤) |
| **T2 DETAIL** | detail_d1_seawater, detail_d2_making, detail_d3_tower · 부속: shape_d3_section(DETAIL로 판정하되 역할 중앙값·사다리의 위 기준에서는 뺀다) |
| **T3 SUPPORT** | support_breakwater_block, support_harbor, support_pompeii_site, support_privernum, support_ruin_observers |
| **T4 BASIC** | basic_recipe, basic_sources |
| **T5a 이름 붙은 지물** | landmark_pantheon, landmark_lime_kiln, landmark_aqueduct, landmark_vesuvius, landmark_pompeii_town, landmark_apennines, road_appia, road_ostiensis |
| **T5b 일반 지물** | bridge_north, bridge_south, fields_e/nw/s/se/sw/w, road_core_nw/s/se/w, tree_t_cypress, tree_t_pine_004, tree_t_pine_022, trees_s, trees_se |
| **T6 면 지물** | water_sea, water_tiber |
| **T7 배경** | ground_land |
| **G 길잡이** | milestone_1_to_2, milestone_2_to_34, milestone_34_to_5 |
| **N 주석 선** | shape_d2_leader, shape_pin_harbor, shape_pin_pompeii |
| **F 틀** | header_gate |
| **X 판정 제외** | shape_core1~5_marker(고정 조건 5, D1) |

새 자산이 생기면 인벤토리 `role`을 따른다. 지물은 지명 이름표(text_spec)가 있으면 T5a, 없으면 T5b로 둔다.

### 적용표
| 항목 | T0 | T1 | T2 | T3 | T4 | T5a | T5b | T6 | T7 | G | N | F |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 01~03 | | ● | | | | | | | | | | |
| 04 | | ●(①③④⑤) | ●(d1·d2) | | | | | | | | | |
| 05 | | ● | ● | ● | | | | | | | | |
| 06~09 | | | ● | ● | ● | ● | ● | | | | | |
| 10 | | | ● | ● | | ● | ● | | | | | |
| 11 | ● | | | | | | | | | | | |
| 12 | | | | | | ● | | | | | | |
| 13 | | | | | | ● | ● | ● | ● | | | ● |
| 14 | ● | | ● | ● | ● | ● | ● | ● | ● | | | ● |
| 15 | | | | | | ● | ● | | | | | |
| 16 | | | | | | | | ● | ● | | | |
| 17 | | | | | | | | | | ● | | |
| 18 | | | | | | | | | | | ● | |
| 19 | | | | | | | | | | | | ● |
| 20 | | ● | ● | ● | ● | | | | | ● | | |

---

## A. CORE 그림 — 위계의 꼭대기가 실제로 센가

**[OBJ_HIER-01] CORE 그림이 역할에 맞게 큰가?**
- 적용: T1.
- 측정: `bbox_visible_final_pt`의 짧은 변(pt), A, 그리고 T2(d1·d2·d3) A 중앙값과 T3 A 중앙값.
- 합격: 짧은 변 ≥ **74pt**(최대 관람 거리 1.5m에서 시각 1°) **그리고** A ≥ max(T2 중앙값, T3 중앙값) [운영값].
- 실패 심각도: 짧은 변 < 74pt면 **major**, 면적 순위만 어긋나면 **minor**.
- 근거: H5(큰 물체가 더 자주·빨리 응시되고 효과는 로그형), H4(1.5배 큰 물체는 과제와 무관해도 주의를 잡음), H7(3D 장면 지도 주의 모형의 세 요인 가운데 하나가 크기), H10("larger objects appear more important").

**[OBJ_HIER-02] CORE 그림이 강한 명도 정점을 갖는가?**
- 적용: T1.
- 측정: K(§0.4).
- 합격: K ≥ **40**(명도 4단계, 단계 = ΔL\* 10, value.md V20) [운영값].
- 실패 심각도: **major**(30 ≤ K < 40) / **blocker**(K < 30. 밝은 종이 위에서 가장 어두운 5%도 종이와 3단계가 못 되면 그림-바탕이 서지 않는다).
- 근거: H10("lightness" 차가 특히 중요, 대비가 낮으면 위계가 약함), H14(초점 요소를 가장 밝거나 대비가 큰 곳으로 둠), H8(주제 관련도와 지각 위계를 맞춤).

**[OBJ_HIER-03] CORE 그림이 주의 창 안 지물과 색이나 명도로 갈리는가?**
- 적용: T1. 비교 대상은 그 CORE의 FOA 안 T0·T5a·T5b. 같은 재질을 일부러 공유하는 T2·T3는 빼는데, 같은 재질은 같은 색이어야 하기 때문이다(I3-01).
- 측정: 대표색 ΔE00, 그리고 K 차(K_CORE − K_지물).
- 합격: 모든 비교 대상에서 ΔE00 ≥ **10**(5 JND) **또는** K 차 ≥ **10**(명도 1단계) [운영값].
- 실패 심각도: **minor**. 대상이 여럿이어도 CORE마다 지적 하나다.
- 근거: H3(표적과 방해물의 차이가 클수록, 방해물이 서로 닮을수록 표적이 튐 — T-D 이질성 규칙), H17(JND).

**[OBJ_HIER-04] CORE·DETAIL 그림 안에서 가장 강한 디테일이 핵심 단서에 놓였는가?**
- 적용: ①(단서: 철근·금·녹물), ③(흰 알갱이), ④(물·흰 칼슘·금), ⑤(금·흰 메움·물), d1(흰 결정·물), d2(흰 알갱이·열 표시). ②는 장면 행위가 단서라 색으로 가를 수 없어서, d3은 단계 명도가 단서라서 뺀다.
- 측정: I에서 |L\* − N(L\*)|(§0.4 D와 같은 N) 상위 2% 화소를 고른다. 단서 마스크를 1pt 넓힌 영역 안에 드는 비율을 잰다. 단서 마스크는 V 안에서 다음과 같다. 흰색은 L\* ≥ 88이고 C ≤ 0.04, 금 홈은 L\* ≤ 22, 물은 Oklch h 180~240°이고 C ≥ 0.06, 철근은 h 200~270°이고 C ≥ 0.02이며 L\* < 50, 녹물은 h 40~90°이고 C ≥ 0.03(①의 무채색 콘크리트 위에서만), 열은 h 20~50°이고 C ≥ 0.10.
- 합격: ≥ **50%** [운영값: 과반].
- 실패 심각도: CORE는 35% 미만이면 **major**, 35~50%면 **minor**. DETAIL은 **minor**.
- 근거: H1(국소 대비·채도·선 밀도로 강조한 곳에 시선이 감, p < 0.001), H2(디테일을 뜻 있는 곳에만 남기면 시선이 그곳으로 모이고 훑는 위치가 10~20% 줄어듦), H13(중요한 것은 강조하고 덜 중요한 것은 단순화).

**[OBJ_HIER-05] 상위 역할 그림이 다른 물체에 가려지거나 덮이지 않는가?**
- 적용: T1, T2, T3.
- 측정: vis(§0.2). 0.95 미만이면 2배 크롭에서 원인을 확인한다. 가림(다른 물체가 앞에 옴)인지, 드리운 그림자만인지 가린다.
- 합격: vis ≥ **0.95** [운영값].
- 실패 심각도: T1이 하위 물체에 가려 vis < 0.90이면 **blocker**(BRIEF: 가림), 0.90~0.95면 **major**, 원인이 그림자뿐이면 **minor**. T2·T3는 **minor**.
- 근거: H10(그림-바탕, 앞에 오는 것이 그림이 됨), BRIEF §6(가림 = blocker).

## B. 하위 역할의 상한 — 근처 CORE보다 눈을 끌지 않는가 (심각도는 §M)

**[OBJ_HIER-06] 크기: A ≤ 1.5·R_A 인가?**
- 적용: T2, T3, T4, T5a, T5b.
- 큰 넘음: A ≥ 3·R_A(길이로 약 1.7배, H4가 쓴 1.5배 길이 차를 넘음). 크기 보상 규칙(§M)이 먼저 적용된다.
- 근거: H4, H5, H7, H10 [1.5·3배는 운영값].

**[OBJ_HIER-07] 명도 대비: K ≤ R_K + 3 인가?**
- 적용: T2, T3, T4, T5a, T5b.
- 여유 3 L\*는 밝은 바탕에서 약 1 JND(ΔE2000 2, H17)다. 큰 넘음은 K ≥ R_K + 10(명도 1단계)이다.
- 근거: H10, H14("배경 디테일은 밝고 어두운 차가 작게", "모든 것이 주의를 끌면 아무것도 끌지 못함"), H12(대기 원근: 가깝고 중요한 지형은 더 대비 있게, 먼 저지대는 누그러뜨림).

**[OBJ_HIER-08] 색 대비·채도: Kc ≤ R_Kc + 0.02 인가?**
- 적용: T2, T3, T4, T5a, T5b.
- 여유 0.02는 Oklch 1 JND(H17)다. 큰 넘음은 Kc ≥ R_Kc + 0.06(3 JND)이다. 의미색(물=청록 등)이 칠해진 작은 물체도 같은 잣대를 쓰되, FOA 밖이면 §M에 따라 1점만 받는다.
- 근거: H6(채도·밝기가 가장 높은 색이 주의를 가장 끔, 67%), H3(색은 확정된 유도 속성), H1(채도 강조가 선 강조보다 강함, p < 0.01), H11(배경에는 옅고 밝은 색, 먼저 볼 것에 진한 색).

**[OBJ_HIER-09] 디테일 밀도: D ≤ 1.25·R_D 인가?**
- 적용: T2, T3, T4, T5a, T5b.
- D는 큰 넘음이 없다(최대 1점).
- 근거: H2("디테일이 높으면 배경이 산만하게 번잡해 보임"), H1(선 밀도·질감으로 강조·약화), H15(가장자리 밀도가 지각 복잡도의 지배 요인, PLS 계수 0.36), H16(국소 특징 변이 = 혼잡), H12. [1.25배는 운영값]

**[OBJ_HIER-10] CORE 아래 사다리(DETAIL > SUPPORT > 이름 붙은 지물 > 일반 지물)가 주의 창 안에서 뒤집히지 않는가?**
- 적용: 아래 단계 자산 X(T3, T5a, T5b)와, X의 FOA 안에 있는 위 단계 자산 Y(T2, T3, T5a. shape_d3_section은 Y에서 뺀다). FOA는 자산 상자끼리의 간격 ≤ 198.5pt다.
- 측정: OBJ_HIER-06~09와 같은 넘음 판정을 쓰되 R = **Y 자신의 값**으로 둔다(중앙값으로 올리지 않음).
- 합격: 넘는 경로가 **2개 이하**.
- 실패 심각도: **minor**(3경로 이상). X 하나에 Y가 여럿이어도 지적은 하나다.
- 근거: H8(주제 관련도 순서와 지각 위계를 맞춤), H9(지도는 앞 요소가 먼저 응시되는 위계가 분명해야 함), H13.

## C. 영웅과 랜드마크

**[OBJ_HIER-11] 영웅(콜로세움)이 주의 창 안 CORE 그림보다 명도·색 대비가 세지 않은가?**
- 적용: T0. 비교 대상은 콜로세움 상자에서 FOA 안에 있는 CORE 구역 k마다 R(§0.5)이다.
- 측정: K ≤ R_K + 3, Kc ≤ R_Kc + 0.02. 크기와 D는 판정하지 않는다(고정 조건·LY-10).
- 합격: 모든 k에서 둘 다 만족.
- 실패 심각도: 하나만 넘으면 **minor**, 둘 다 넘으면 **major**. 영웅은 이미 크기로 압도하므로 대비까지 이기면 CORE가 영웅에 묻힌다.
- 근거: H1(시선을 끄는 강한 특징이 초점 밖에 있으면 더 약화해야 함), H5, H3.

**[OBJ_HIER-12] 이름 붙은 지물이 영웅을 넘지 않는가?**
- 적용: T5a.
- 측정: 영웅 값 기준으로 K > K_영웅 + 3, Kc > Kc_영웅 + 0.02, D > 1.25·D_영웅 가운데 몇 개가 성립하는가.
- 합격: **1개 이하**.
- 실패 심각도: **minor**.
- 근거: H13(랜드마크 위계), H8, H21(사실적 3D 랜드마크가 지도-현실 대응을 돕는다. 그래서 해법은 실루엣·형태를 지키고 국소 대비만 낮춘다).

## D. 면·바탕·무리 — 크게 깔리는 것은 옅고 고르게

**[OBJ_HIER-13] 큰 면 물체가 밝고 연한가?**
- 적용: A_vis(V 면적) ≥ **20,000pt²**인 T5a·T5b·T6·T7·F. T0·T1~T3은 뺀다.
- 측정: L\*_med, C_med, C90(Oklch).
- 합격: L\*_med ≥ **70**, C_med ≤ **0.06**(CIELAB C\* 약 20), C90 ≤ **0.08** [운영값].
- 실패 심각도: **minor**. C_med > 0.08이거나 L\*_med < 60이면 **major**.
- 근거: H11(Imhof: 강하고 짙은 색은 좁은 곳에만, 넓은 바탕색은 옅게 물러나게), H12, H10.

**[OBJ_HIER-14] 강한 채도가 좁은 면에만 쓰였는가?**
- 적용: T0, T2~T7, F. G의 화살 판과 X는 고정 조건이라 뺀다.
- 측정: 강채도 면적(V 안 Oklch C ≥ 0.10, pt²).
- 합격: ≤ **1,000pt²**(약 11×11mm) [운영값].
- 실패 심각도: 1,000~3,000pt²면 **minor**, 3,000pt² 초과면 **major**.
- 근거: H11(Imhof 규칙), H6.

**[OBJ_HIER-15] 되풀이되는 지물 무리(밭·나무·산)가 서로 고른가?**
- 적용: 알파 M의 연결 성분 가운데 20pt² 이상이고 그 절반 넘게 보이는 성분이 3개 이상인 T5a·T5b.
- 측정: 성분마다 V 화소의 CIELAB L\*·C\* 중앙값을 구하고, 성분들 사이의 10~90백분위 폭을 잰다.
- 합격: L\* 폭 ≤ **10**(명도 1단계), C\* 폭 ≤ **8** [운영값]. D35의 작물색은 이 폭 안에서만 쓴다.
- 실패 심각도: **minor**.
- 근거: H3(방해물이 서로 닮으면 배경으로 물러나고 표적이 튐 — 방해물 이질성), H16(특징 변이가 혼잡을 만든다), value.md V2(같은 명도는 무리 지음).

**[OBJ_HIER-16] 땅과 물의 결이 가장 조용한가?**
- 적용: T7(ground_land), T6(water_sea, water_tiber).
- 측정: D.
- 합격: 땅은 D ≤ **0.02**, 물은 D ≤ min(**0.08**, med_D) [운영값].
- 실패 심각도: **minor**. 땅 D > 0.05면 **major**(바탕 전체가 질감을 띠면 모든 물체의 그림-바탕이 약해진다).
- 근거: H10, H14(배경 디테일은 낮은 명도 차로), H2.

## E. 길잡이·주석·틀 — 보조 장치는 내용보다 가볍게

**[OBJ_HIER-17] 이정표가 CORE 그림보다 작고 단순한가?**
- 적용: G. K·Kc는 고정 조건(②색 화살 판)이라 판정하지 않는다.
- 측정: A, D.
- 합격: A ≤ CORE 그림 A의 **최솟값**, D ≤ 1.25·med_D.
- 실패 심각도: **minor**.
- 근거: H19(가장 작은 효과적 차이), H5, BRIEF 고정 조건 6.

**[OBJ_HIER-18] 지시선·핀이 CORE 표지보다 가는가?**
- 적용: N.
- 측정: 알파 M의 중축(skimage `medial_axis`) 위 거리변환 값 d(px). 선폭 = (2·median(d) − 1) / S(pt), 끝점 지름 = (2·max(d) − 1) / S(pt).
- 합격: 선폭 < **1.2pt**(D1의 CORE 밑줄 두께), 끝점 지름 ≤ **3.5pt**.
- 실패 심각도: **minor**.
- 근거: H19, H10, STATE D1·D5.

**[OBJ_HIER-19] 제목 아치 틀이 제목 글보다 약한가?**
- 적용: F(header_gate).
- 측정: K, D, L\*_med. 제목 글 대비 = L\*_med − 17.2(#2E2A22의 L\*).
- 합격: K ≤ **0.5 ×** 제목 글 대비, D ≤ **0.05** [운영값].
- 실패 심각도: **minor**.
- 근거: H19, H14, H10.

## F. 같은 역할 안의 고름

**[OBJ_HIER-20] 같은 역할 물체끼리 크기가 한 단계 안에 있는가?**
- 적용: T1, T2(d1·d2·d3), T3, T4, G. 각 집합 안에서 잰다.
- 측정: A ÷ (그 역할 A 중앙값).
- 합격: **0.5 ~ 2.0**(크기 두 배 = 한 단계, H5의 로그형 효과) [운영값].
- 실패 심각도: **minor**. 범위를 벗어난 자산에 매긴다.
- 근거: H8(같은 관련도 수준은 같은 지각 수준), H5, H7.

---

## 해법 작성 규칙 (수치로)
- **K를 낮춤**: 가장 어두운 재질의 선형 반사율 배율 = Y(목표 L\*) ÷ Y(현재 P5 L\*), Y = ((L\* + 16)/116)³. hex와 배율을 함께 적는다. 그림자·AO는 R5·R10 보류 범위라 건드리지 않는다.
- **Kc·채도를 낮춤**: 재질 기본색의 Oklch C를 목표값으로 줄이고 L·h는 유지한 hex를 적는다(예: C 0.09 → 0.05).
- **D를 낮춤**: 실루엣·형태는 지키고(H21, D27) 국소 대비만 줄인다. 홈·틈 재질을 몸체 명도 쪽으로 ΔL\* 몇 만큼 올리는지, 또는 법선 다듬기 반복 수·결합할 작은 부품 수를 적는다.
- **A를 줄임**: Blender 배율 s = √(목표 A ÷ 현재 A). 화면 위치(pt)가 바뀌면 이름표 이동량도 적는다.
- **CORE를 키우거나 세게**: 반대 방향 계산을 쓴다. 이때 다른 루브릭의 고정·결정(D1·D8, 고정 조건 5·6)을 건드리지 않는 해법만 낸다.

## 참조 구현 (요약, `uv run --no-project --with pillow --with numpy --with scipy --with scikit-image python -I`)
```python
def lin(c): c=c/255; return np.where(c<=.04045, c/12.92, ((c+.055)/1.055)**2.4)
def Lstar(l): Y=l@[.2126,.7152,.0722]; return np.where(Y>.008856, 116*np.cbrt(Y)-16, 903.3*Y)
# oklab(l): Ottosson 2020 행렬 (H18)
M  = rgba[...,3] >= 128
V  = M & (abs(Lstar(lin(ctx)) - Lstar(lin(iso))) < 6)
d  = ndi.distance_transform_edt(~M); ring = (d > 3*S) & (d <= 15*S)
A  = max_component_area(ndi.binary_closing(V, iterations=int(2*S))) / S**2
K  = max(med(L[ring]) - P(L[V],5), P(L[V],95) - med(L[ring]))
Kc = P(norm(ok[V][:,1:] - ab_paper, axis=1), 90)          # ab_paper = ground_land V 중앙값
N  = gauss(L*V, 2*S) / maximum(gauss(V*1., 2*S), 1e-6)
I  = ndi.binary_erosion(V, iterations=int(S));  D = mean((abs(L - N) > 8)[I])
def exceed(x, R, in_foa):
    e = dict(A=x.A > 1.5*R.A, K=x.K > R.K+3, Kc=x.Kc > R.Kc+.02, D=x.D > 1.25*R.D)
    big = dict(A=x.A >= 3*R.A, K=x.K >= R.K+10, Kc=x.Kc >= R.Kc+.06, D=False) if in_foa else dict.fromkeys(e, False)
    if e['A'] and not (e['K'] or e['Kc'] or e['D']) and x.K <= .8*R.K and x.Kc <= .8*R.Kc and x.D <= .8*R.D:
        e['A'] = False                                        # 크기 보상
    n = sum((2 if big[c] else 1) for c in e if e[c])
    return n, all(e.values()) and in_foa                      # n=1 minor, n>=2 major, 4경로 모두(FOA 안) blocker
```

---

## 출처 (실제로 열어 본 자료)

| ID | 저자·연도 | 제목·매체 | 이 루브릭에서 쓴 내용 | URL |
|---|---|---|---|---|
| H1 | Cole, F., DeCarlo, D., Finkelstein, A., Kin, K., Morley, K., Santella, A. (2006) | Directing Gaze in 3D Models with Stylized Focus. *EGSR 2006*, 377–387 | 대비·채도·선 밀도·선명도 네 가지로 강조. 시선 추적에서 강조 영역을 더 봄(p < 0.001). 색 강조가 선 강조보다 강하고(p < 0.01) 둘을 합치면 가장 강함. 초점 밖의 눈에 띄는 특징은 더 약화해야 함 | https://gfx.cs.princeton.edu/pubs/Cole_2006_DGI/cole06_stylizedfocus.pdf |
| H2 | DeCarlo, D. (2008), Santella & DeCarlo 2004(NPAR) 연구 정리 | SIGGRAPH 2008 강좌 *Line Drawings from 3D Models* — Abstraction 강의 노트 | 디테일을 뜻 있게 국소 조절하면 훑는 위치가 10~20% 줄고 시선이 디테일 지점에 모임. 디테일이 높으면 배경이 산만하게 번잡해 보임 | https://gfx.cs.princeton.edu/proj/sg08lines/lines-10-abstraction.pdf |
| H3 | Wolfe, J. M., Horowitz, T. S. (2017) | Five factors that guide attention in visual search. *Nature Human Behaviour* 1, 0058 | 확정된 유도 속성은 색·움직임·방향·크기. 표적-방해물 차이가 클수록, 방해물이 서로 닮을수록 두드러짐. 장면 의미도 주의를 이끎 | https://pmc.ncbi.nlm.nih.gov/articles/PMC9879335/ |
| H4 | Proulx, M. J. (2010) | Size Matters: Large Objects Capture Attention in Visual Search. *PLoS ONE* 5(12):e15293 | 길이 1.5배 큰 물체(0.9° vs 0.6°)가 자극 주도로 주의를 잡음 | https://pmc.ncbi.nlm.nih.gov/articles/PMC3009719/ |
| H5 | Peschel, A. O., Orquin, J. L. (2013) | A review of the findings and theories on surface size effects on visual attention. *Frontiers in Psychology* 4:902 | 큰 물체가 더 자주·빨리 응시됨. 효과는 로그형. 신호 세기는 크기·물체 수·중심에서의 거리에 달림 | https://pmc.ncbi.nlm.nih.gov/articles/PMC3856423/ |
| H6 | Camgöz, N., Yener, C., Güvenç, D. (2004) | Effects of hue, saturation, and brightness: Part 2 — Attention. *Color Research & Application* 29(1):20–28 | 채도·밝기가 최대인 색이 주의를 가장 끔(67%) | https://repository.bilkent.edu.tr/items/f71941a7-d7b2-4d57-ab51-92503ae069ea |
| H7 | Yang, B., Li, H. (2021) | A Visual Attention Model Based on Eye Tracking in 3D Scene Maps. *ISPRS IJGI* 10(10):664 | 시선 추적으로 만든 3D 장면 지도 주의 모형에서 색·형태·크기 세 요인이 주의 값을 설명(R² > 0.699) | https://api.crossref.org/works/10.3390/ijgi10100664 |
| H8 | Fabrikant, S. I., Hespanha, S. R., Hegarty, M. (2010) | Cognitively Inspired and Perceptually Salient Graphic Displays for Efficient Spatial Inference Making. *Annals AAG* 100(1) | 주제 관련도의 수준을 그림-바탕 지각 위계에 맞추는 것이 기본 과제. 두드러짐 설계가 응시 행동·반응 시간을 바꿈 | https://user.geo.uzh.ch/sfabri/pubs/fabrikant_etal_an09.pdf |
| H9 | Wenclik, L., Touya, G. (2024) | EyeCatchingMaps, a Dataset to Assess Saliency Models on Maps. *AGILE GIScience Series* 5:51 | 지도는 앞 요소가 먼저 주의를 끄는 위계를 가짐. 지도 322장, 3초 시선 기록(각 20회 이상). 지도용 주목도 모형 검증(CovSal 평균 CC 0.724) | https://agile-giss.copernicus.org/articles/5/51/2024/agile-giss-5-51-2024.pdf |
| H10 | Axis Maps | Cartography Guide — Visual Hierarchy | 큰 것·어두운 것이 눈을 끎, 명도 차가 특히 중요, 대비가 낮으면 그림-바탕·위계가 약함, 실눈 시험 | https://axismaps.com/guide/visual-hierarchy |
| H11 | Ordnance Survey (Imhof 1982 규칙 정리) | More than Maps — Guide to cartography: Colour | 강하고 짙은 색은 좁은 극단 영역에만, 넓은 영역에 나란히 두지 않음. 바탕색은 물러나게. 배경은 옅고 밝은 톤, 먼저 볼 것은 진하고 채도 높게 | https://docs.os.uk/more-than-maps/geographic-data-visualisation/guide-to-cartography/colour |
| H12 | Tóth, T. (2010) | Accidental cARTographer. *Cartographic Perspectives* No. 67 (2010 겨울호) | 대기 원근(Imhof): 가깝고 높은 지형은 더 디테일하고 대비 있게, 먼 저지대는 누그러뜨림 | https://cartographicperspectives.org/index.php/journal/article/download/cp67-toth/pdf/ |
| H13 | Grabler, F., Agrawala, M., Sumner, R. W., Pauly, M. (2008) | Automatic Generation of Tourist Maps. *ACM TOG* 27(3) (SIGGRAPH 2008) | 중요도(시각 분석 + 웹 정보)로 고르고, 단순화·변형·이동으로 랜드마크를 강조하고 덜 중요한 건물을 약화 | https://history.siggraph.org/?p=112905 |
| H14 | Angstadt, P. (2015-03-12) | How to Reduce Visual Confusion in Your Game. *Game Developer* | 실무: 초점 요소를 가장 밝거나 대비가 큰 곳으로, 배경 디테일은 명암 차를 작게, 흑백으로 점검. "if everything is drawing attention, nothing will" | https://www.gamedeveloper.com/design/how-to-reduce-visual-confusion-in-your-game |
| H15 | Chu, M., Qiu, Z., Ling, M., Jiang, S., Laramee, R. S., Sedlmair, M., Chen, J. (2025) | What Makes a Visualization Image Complex? *IEEE VIS 2025* (arXiv 2510.08332v3) | 1,800장·349명. 가장자리 밀도(Canny)가 지각 복잡도의 지배 요인(PLS 계수 0.36, p < 0.001), 색·질감 변이에는 feature congestion | https://arxiv.org/html/2510.08332v3 |
| H16 | Rosenholtz, R., Li, Y., Mansfield, J., Jin, Z. (2005) | Feature Congestion: A Measure of Display Clutter. *CHI 2005* (MIT 프로젝트 쪽) | 혼잡 = 주목도 모형 기반의 국소 색·명도 대비 변이. 사람이 매긴 지도 혼잡 순위와 잘 맞음 | https://people.csail.mit.edu/yzli/clutter.htm |
| H17 | W3C (2026-10-09) | CSS Color Module Level 4, Candidate Recommendation Draft | JND: Oklch 차 0.02, ΔE2000 2 | https://www.w3.org/TR/css-color-4/ |
| H18 | Ottosson, B. (2020-12-23, 행렬 2021-01-25 갱신) | A perceptual color space for image processing (Oklab) | 선형 sRGB → Oklab 행렬, C = √(a² + b²) | https://bottosson.github.io/posts/oklab/ |
| H19 | Tufte, E. (1997) *Visual Explanations* p.73, Brown, D. (2002-11-24)의 인용 | Three Lessons From Tufte. *Boxes and Arrows* | 가장 작은 효과적 차이: "Make all visual distinctions as subtle as possible, but still clear and effective"(2차 인용) | https://boxesandarrows.com/three-lessons-from-tufte-special-deliverable-6 |
| H20 | Itti, L., Koch, C., Niebur, E. (1998) | A model of saliency-based visual attention for rapid scene analysis. *IEEE TPAMI* 20(11) | 주의 반지름 = 짧은 변의 1/6(198.5pt). value.md V6에서 연 자료를 다시 씀 | https://hasler.ece.gatech.edu/Courses/MachineLearning/FoundationalPapers/Itti_Koch_Neiber1998.pdf |
| H21 | Hilton, C., Kapaj, A., Fabrikant, S. I. (2024) | Fixation-related potentials during mobile map assisted navigation in the real world: The effect of landmark visualization style. *Attention, Perception, & Psychophysics* (doi 10.3758/s13414-024-02864-z) | 사실적 3D 랜드마크 표현이 지도-현실 랜드마크 대응을 도움(P200 증폭). 그래서 디테일을 줄일 때 형태는 지킨다 | https://geo.uzh.ch/en/units/giva/news0/landmark-visualization-style.html |

- 내부 자료: BRIEF §2·§3·§6, STATE D1(밑줄 1.2pt)·D5·D27·D35·D36·D37, R3·R5·R10·R11, value.md 규약 2·5·8과 V2·V20, illustration3d.md I3-01·I3-07·I3-15, layout.md LY-10.
- 2022~2026 자료: H9(2024), H15(2025), H17(2026), H21(2024) — 4개.
- 한계: Rosenholtz·Li·Nakano 2007(J. Vision)의 원문은 열지 못했다. 그래서 혼잡도 근거는 H16(2005, 프로젝트 쪽)과 H15로만 쓴다. Yang & Li 2021은 초록(Crossref)만 확인했다. 나무·밭·포석 같은 3D 디오라마 지물의 디테일 문턱을 직접 실험한 동료 심사 연구는 찾지 못했다. D·A·채도 문턱은 모두 [운영값]이고, 그 방향(하위 물체는 덜 크고·덜 대비 있고·덜 진하고·덜 촘촘하게)만 H1·H2·H3·H10·H11·H12가 뒷받침한다.
