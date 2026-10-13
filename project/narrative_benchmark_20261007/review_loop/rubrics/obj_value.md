# 루브릭 · 물체 단위 명암·명도 (obj_value)

- 작성: 라운드 11 물체 단위 명암·명도 비평가(2026-10-13). STATE D37에 따라 Blender에 배치된 자산을 **하나씩** 심사하는 6분야 가운데 하나다. 다음 라운드부터 이 문서를 고정하고, 다른 비평가가 블라인드로 재현한다.
- 범위: 자산 하나의 **면 명도 단계**(윗면·왼면·오른면, 빛 무리·그늘 무리), **국소 바탕과의 그림-바탕 명도 차**, **그림자·접지 어둠**, **물체 안 디테일**(금·알갱이·이랑·줄눈·아치 등)의 명도 대비가 관람 거리에서 읽히는지 본다.
- 판정: 항목마다 예(합격) / 아니오(불합격) / 해당 없음 / 보류 Rn(STATE 기각·보류 목록과 같은 원인). 해당 없음과 보류는 등급에 넣지 않는다.
- **등급(자산 단위, BRIEF §6과 같음)**: AAA = blocker 0 · major 0 · minor ≤ 2 / AA = blocker 0 · major ≤ 2 / A = blocker 0 · major ≥ 3 / B = blocker 1~2 / C = blocker ≥ 3.
- **부풀리기 금지**: 한 자산에서 같은 원인으로 여러 항목이 불합격하면 지적은 하나로 묶고 가장 높은 심각도만 센다(예: 자산 전체가 너무 밝아 09·10·11이 함께 떨어짐 → 지적 1개).
- 수치 기준 가운데 문헌이 직접 준 값은 [문헌값], 문헌 원리를 이 포스터에서 재현 가능한 값으로 옮긴 것은 [운영값], 기존 루브릭과 맞춘 값은 [기존값 ID]로 표시한다.

## 다른 루브릭과의 경계 (겹치지 않게 뺀 것)
- 포스터 전체 명도 위계·노탄·명도 분포·인쇄 보존 11쌍 → `value.md` VL-01~18. 이 루브릭은 포스터 단위 값을 다시 재지 않고, 같은 측정 관례(L\*, 고리 6~20pt, 실눈 σ = 7pt, 한 단계 = ΔL\* 10, 인쇄 모의 규약 9, 보존율 0.80)를 **자산 하나에** 적용한다.
- 장면 전체 광원 일관(I3-09), 같은 재질 다른 모형 비교(I3-01), 지형 실루엣(I3-10), 구조 모형 재료 계단 ΔL\* ≥ 8(I3-25) → `illustration3d.md`. 문턱이 겹치는 항목(I3-02·12·13·15·23·26·27)은 **같은 값**을 쓴다(충돌 금지).
- 색상·채도의 뜻(시대 색 부호, 강조색 독점) → `color.md`, `obj_color`. 형태·메시·실루엣 모양 자체 → `obj_form`. 단서의 의미 정확성 → `obj_infographic`. CORE와의 경쟁·주목 순서 → `value.md` VL-04·06, `obj_hierarchy`. 위치·간격 → `obj_layout`.

## 고정 조건·결정·보류 처리 (감점하지 않음)
- BRIEF §3-4: 클레이 디오라마의 **약간 플랫한 음영**과 밝은 조 자체는 감점하지 않는다. 문턱은 "면이 갈리는 최소"로만 둔다.
- BRIEF §3-5·6: 번호 원판·밑줄·이정표 화살 판의 색 #983821은 고정이다. 이 부품의 해법은 색 변경이 아니라 조명·두께·베벨·그림자로만 낸다.
- STATE D35·D36(사용자 결정): 밭 재질 렌더 L\* 62~84, 포석 #A9A69F(L\* 67), 연석·다리 #C7BEAA(L\* 79). 이 범위 안에서만 해법을 낸다.
- STATE 보류: **R3**(나무 그림자), **R5**(모형별 그림자 세기·방향 차이), **R10**(Workbench 접촉 어둠 부족), **R11**(베수비오 스캔 지느러미), **R12**(②→③ 이정표 화살 머리 앞 가장자리 대비). 원인이 같으면 "보류 Rn"으로 기록만 하고 등급에 넣지 않는다. 새 근거(예: 떠 보임, 디테일 소실)가 있을 때만 판정한다.

---

## 0. 측정 규약 (모든 항목 공통 · 재현용)

**0.1 자료와 크롭**
1. **맥락 크롭 C**: 글 없는 지도 2배 이미지 `out/figma_import/map_v8_<N>_without_text_2x.png`(= `r<N>/map_only_2x.png`)에서 자산 외곽 상자 + 사방 24pt. 1pt = 2px, 좌표는 프레임 왼쪽 위 원점의 pt.
2. **단독 크롭 I**: 같은 .blend에서 카메라·해상도(2배)·Workbench 조명·색 관리(View Transform)를 그대로 두고 렌더한다.
   - **I_a**: 이 자산의 물체만 렌더 가시, 지면도 숨기고 필름 투명 → 알파 ≥ 0.5를 **자산 마스크 M**으로 쓴다.
   - **I_g**: 이 자산 + 지면(T_land·L02_tiber·L10_sea)만 가시 → 그림자 분리용.
   - **G0**: 지면만(모든 자산 숨김).
3. 단독 렌더를 만들 수 없으면 M = |L\*(C) − L\*(같은 장면에서 이 자산만 숨긴 렌더)| > 2로 정한다. 그것도 없으면 손 다각형으로 정하고, 꼭짓점 pt를 보고서에 적는다.
4. **법선 패스(권장)**: I_a와 같은 카메라로 Normal 패스(카메라 공간·세계 공간)를 렌더한다.

**0.2 면 지도**
- 윗면 F_top: 세계 법선 z ≥ 0.7. 왼면 F_L: |z| < 0.7이고 카메라 공간 법선 x ≤ −0.35. 오른면 F_R: |z| < 0.7이고 x ≥ 0.35.
- 빛 무리 Λ: N·ℓ ≥ 0.2. 그늘 무리 Σ: N·ℓ ≤ 0. ℓ은 장면 주광 방향이다. 씬의 Workbench 조명 방향을 읽고, 읽을 수 없으면 0.10의 기준 면 순서로 정한다(왼쪽 위 앞).
- **법선 패스가 없을 때**:
  - 상자형(K1·K5): **면 창**을 쓴다. 면 창은 면 안쪽 4×4pt 이상이고, 면 가장자리·디테일에서 2pt 침식한다. 좌표를 기록한다.
  - 곡면(K2·K4): **기하 절반**을 쓴다. 화면 속 빛 방향 ℓ′ = (−0.71, −0.71)(x 오른쪽, y 아래)일 때, M의 무게중심 c와 등가 반지름 R = √(면적/π)에 대해 Λ = {p ∈ M : (p − c)·ℓ′ > 0.15R}, Σ = {p ∈ M : (p − c)·ℓ′ < −0.15R}로 정한다. 명도 백분위로 Λ·Σ를 나누지 않는다(06이 저절로 합격하게 되므로).
- 면 대표 명도 = 창(또는 무리) 안 L\* 중앙값. 디테일 마스크(0.5)는 뺀다. **넓은 면** = M 면적의 15% 이상인 면.

**0.3 색 계산**
- L\*: sRGB → 선형(IEC 61966-2-1) → Y = 0.2126R + 0.7152G + 0.0722B → CIE L\*(value.md 규약 2와 같음). CIELAB(D65), ΔE00(Sharma 2005 식), ΔE76, Oklab/Oklch(Ottosson 2020).
- **알베도 정규화 음영비** s = Y_면 / Y_알베도. Y_알베도는 `palette_part_materials.json` → `actual_materials` hex의 상대 휘도다. 재질이 다른 면끼리 비교할 때만 쓴다.
- 해법 환산: 면 L\*을 L1에서 L2로 옮기는 재질 선형 반사율 배율은 k = Y(L2)/Y(L1), Y(L\*) = ((L\* + 16)/116)³이다(D29와 같은 방식).

**0.4 국소 바탕 g**
- C에서 M 바깥 6~20pt 고리의 L\* 중앙값(value.md 규약 6과 같은 고리). 다른 자산의 마스크와 이 자산의 그림자 Sh(0.7)는 뺀다.
- 남은 화소가 고리의 50% 미만이면 20~40pt 고리를 쓴다. 물 위 자산은 물이 바탕이다.

**0.5 고역 성분과 디테일**
- hp = L\* − G_σ(L\*), σ = 3pt(2배 이미지에서 6px). σ_hp = 창 안 hp의 표준편차. 진폭 A = hp의 90백분위 − 10백분위.
- **디테일 마스크 D_k**: 의미 디테일 종류 k마다(금 홈, 흰 알갱이, 흰 메움, 물방울·물, 열 표시, 이랑, 포석 줄눈, 아치·창·구멍, 물결 기호, 기둥 홈 등) 따로 만든다. 자동으로는 M 안에서 |hp| ≥ 3인 연결 성분 가운데 면 경계에서 1pt 넘게 떨어진 것을 잡는다. 손으로 보정해도 되지만 기록한다.
- **디테일 대비** ΔL\*_det = |median(L\*[D_k]) − median(L\*[주인 고리])|. 주인 고리 = D_k 바깥 1~3pt, 같은 면, 다른 디테일 제외. **극성**: 디테일이 더 어두우면 (−), 더 밝으면 (+).
- **크기 s**:
  - 선·점: 성분별 획 폭 = 2 × (거리 변환 최댓값)의 중앙값(pt).
  - 반복 무늬(이랑·포석): **반주기** = 주된 방향 자기상관 첫 정점 거리 ÷ 2.

**0.6 관람 거리와 가시 문턱 표 T(s, d)**
- 1° = 24.7pt(0.5m), 49.5pt(1.0m), 74.2pt(1.5m). 공간 주파수 f = (1°의 pt) ÷ (2s) cycles/deg.
- 아래 표는 Barten CSF(OV25, colour-science 0.4.7 구현)로 구한 문턱 대비를 주인 명도 L\* 40~75에서 L\* 차로 바꾼 값이다.
  - 조건: 종이 휘도 100 cd/m²(실내 약 400 lx), 자극 크기 0.5°, 미켈슨 대비 m = |Y_d − Y_h|/(Y_d + Y_h). 주인 L\*에 따른 차는 ±1 이내라 올림한 값만 적는다.
  - **k = 1은 감지 문턱**, **k = 3은 예비 3배**다(대비 예비 개념 OV29를 운영값으로 씀).

| s (pt) | 0.5m: k3 (k1) | 1.0m: k3 (k1) | 1.5m: k3 (k1) |
|---|---|---|---|
| 0.75 | 3 (1) | > 40 (23) | > 40 (> 40) |
| 1.0 | 2 (1) | 11 (4) | > 40 (> 40) |
| 1.25 | 2 (1) | 5 (2) | 40 (10) |
| 1.5 | 2 (1) | 3 (1) | 11 (4) |
| 2.0 | 2 (1) | 2 (1) | 4 (2) |
| 3.0 | 2 (1) | 2 (1) | 2 (1) |

- 해석:
  - 크기가 문턱을 지배한다. s가 0.75pt 아래면 1.0m에서 사실상 안 보이고, 1.5pt 아래면 1.5m에서 안 보인다.
  - s ≥ 2pt부터는 CSF가 거의 걸리지 않는다. 그 위의 실제 한계는 바탕 질감에 의한 가림(masking)이므로, 디테일 문턱에 **잡음 대비 조건 ΔL\*_det ≥ 3·σ_hp(주인 고리)**를 함께 둔다. 이는 Rose 기준(OV30)을 보수 쪽으로 낮춘 [운영값]이다.
  - 문턱 위 대비에서는 대비 항상성이 CSF 모양을 평평하게 만든다(OV20이 인용한 Georgeson & Sullivan 1975). 그래서 이 표는 **하한**으로만 쓴다.

**0.7 그림자 분리**
- Sh = {L\*(G0) − L\*(I_g) ≥ 1} ∩ ¬M.
- **접촉선** = M의 밑 경계 가운데 지면(또는 받침)과 맞닿는 부분이다.
- 그림자 중심 명도 = Sh 안 L\*(I_g)의 10백분위. 그림자 세기 ΔL\*_sh = 같은 화소의 L\*(G0) − L\*(I_g) 중앙값(중심 10% 화소).

**0.8 인쇄 모의**
- `value.md` 규약 9와 같다: Pillow ImageCms, sRGB → `PSOcoated_v3.icc`(상대 색도 + 흑점 보정) → sRGB(절대 색도).

**0.9 역할·부류 지정** (자산 목록이 따로 있으면 그것을 따른다. 역할은 BRIEF §2와 이름표로 정한다.)

| Blender 물체(접두어) | 역할 | 부류 |
|---|---|---|
| COL_ruined, R4_arena_skin | H 영웅(콜로세움) | K2 |
| R3_colosseum_podium | H(기단) | K3 |
| NB_modern_building, R1_frame_rust, R3_frame_crack_col* (① 철근 골조) | C | K1 |
| C2_hot_mixing (② 반죽 구덩이 장면) | C | K4 |
| NB_lime_clast_specimen(+_LIME*) (③ 큐브) | C | K1 |
| NB_core4_sequence_*, R8_* (④ 큐브 3개·단계 단서) | C | K1 |
| R1_lab_bench, R1_specimen_*, R1_leak_*, R1_healed_*, R3_healed_fill, R3_leak_crack (⑤ 시편) | C | K1·K2 |
| D1_* (재료 원리 해수 큐브), D2_cube·D2_lime*·D2_heat* (제작 원리), D3_* (구조 원리 탑·하중), S_sect* (구조 단면) | D | K1(S_sect*는 K6) |
| L11_privernum_wall, C5_researchers, L08_pompeii_site, L12_harbor_pilae, NB_marine_breakwater, L09_portus_mole, R1 시편 장면 받침 | S | K4(블록은 K1) |
| L01_* (산), L07_vesuvius, L05_aqua_claudia, R8_pantheon, D2_lime_kiln, L09_portus_lighthouse, L08_pompeii, T_* (나무) | L 배경 지물 | K2 |
| F_centuriatio(밭), R_*·R1_road*·R4_bridge_west_bed(길), B_pons*(다리), L02_tiber, L10_sea, W_water_marks | G 지면 덮개 | K3(다리 몸체는 K1) |
| MS1·MS2·MS3 (이정표) | M | K5 |
| H_* (제목 띠 아이콘·책·돋보기·원뿔·상자·미니 콜로세움), H_gate_* (제목 틀) | B | K1·K2 |
| S_core*_badge·_underline, S_lead*, S_pin_*, H_core_band* | 기호(그것이 섬기는 역할의 심각도를 따름) | K6 |

- 부류:
  - **K1** 상자·평면 입체
  - **K2** 곡면·덩어리
  - **K3** 납작한 지면 덮개
  - **K4** 장면 묶음(본체 + 인물·도구)
  - **K5** 이정표(기둥 + 판)
  - **K6** 평면 기호·장식

**0.10 장면 기준값** (라운드마다 다시 재서 갱신한다. r11 지도 v8_13 실측)
- 종이 L\*: 빈 땅 중앙값 90.3(89~91).
- 기준 면 순서: 같은 재질(석회 콘크리트) 상자 ④ 큐브 3개의 윗면 53.6 > 왼면 45.2 > 오른면 37.5다. 빛은 왼쪽 위 앞에서 온다. 장면 순서 = **윗면 ≥ 왼면 > 오른면**.

---

## A. 면 명도 단계 (빛이 만든 형태)

**[OBJ_VALUE-01] 보이는 면의 명도 순서가 장면 광원과 맞는가?**
- 적용: K1, K5, K4 본체. K2는 기하 절반 Λ/Σ를 쓴다.
- 측정: 같은 재질 면끼리는 면 대표 L\*로, 재질이 다른 면끼리는 알베도 정규화 음영비 s로 비교한다(0.3).
- 합격: 0.10의 장면 순서와 같다.
  - 윗면 = 왼면 동률(ΔL\* ≤ 2 또는 s 차 ≤ 5%)은 순서 위반으로 보지 않는다. 대신 02에서 본다.
  - K2는 median(Λ) > median(Σ)이면 합격이다.
- 실패 시:
  - 빛 쪽 면이 그늘 쪽 면보다 ΔL\* ≥ 3 어두운 **역전** → major(H·C·D·M) / minor(그 밖).
  - 역전 폭 < 3 → minor.
- 근거: OV1(가정 광원은 바로 위가 아니라 왼쪽 위, 평균 26° — 장면 빛이 이 사전 가정과 맞을 때 볼록이 볼록으로 읽힘), OV2(빛 방향이 사전 가정과 어긋나면 지형 반전), OV12(반복된 같은 모양 물체에서는 조명 불일치가 드러남), I3-09.

**[OBJ_VALUE-02] 맞닿은 보이는 면끼리 명도로 갈리는가?**
- 적용: K1, K5. K2·K4 본체는 median(Λ) − median(Σ).
- 측정: 모서리를 공유하는 같은 재질 면 쌍(윗면–왼면, 왼면–오른면, 윗면–오른면)마다 |ΔL\*|를 잰다.
- 합격: 모든 쌍 ≥ 6 [운영값, OV5의 2° 표지 ND50 명도 5.47을 올림 — 50% 판별선 바로 위].
- 실패 시:
  - 3 ≤ ΔL\* < 6 → minor.
  - ΔL\* < 3(두 면이 한 면으로 붙어 보임) → major(H·C·D, 형태가 단서를 맡을 때) / minor(그 밖).
- 근거: OV5, OV6(톤 음영으로 면 방향 전달), BRIEF 고정 조건 4(플랫 음영 — 그래서 상한 없이 최소만 둠).
- 참고: 구조 원리 탑의 재료 계단(I3-25, ≥ 8)은 여기서 다시 재지 않는다.

**[OBJ_VALUE-03] 그늘면이 먹색으로 뭉개지지 않는가?**
- 적용: 3D 자산 전부(K1·K2·K4·K5). 의도된 어두운 디테일(금 홈·구멍)은 D_k로 빼고 잰다.
- 측정: 가장 어두운 넓은 면(보통 F_R 또는 Σ)의 대표 L\*, 그리고 그 면 안 L\* < 20 화소 비율.
- 합격: 대표 L\* ≥ 25 그리고 L\* < 20 화소 ≤ 2% [L\* 20·2%는 기존값 I3-02].
- 실패 시:
  - 20 ≤ 대표 L\* < 25 → minor.
  - 대표 L\* < 20 → major(그 면에 의미 디테일이 있을 때) / minor(없을 때).
- 근거: OV6(음영은 중간 톤에, 극단 명암은 윤곽·하이라이트에만), OV31(오프셋 망점 확대가 어두운 톤 디테일을 메움), I3-02.

**[OBJ_VALUE-04] 빛면이 하얗게 날아가지 않는가?**
- 적용: 3D 자산 전부.
- 측정: M 안에서 max(R, G, B) ≥ 254인 화소 비율(흰 디테일 마스크 제외). 흰 재질 자산(알베도 L\* ≥ 92: raw_lime, calcium_crystal, 원뿔 더미 등)은 빛 쪽 면 대표 L\*와 그늘 쪽 면 대표 L\*도 잰다.
- 합격: 포화 화소 ≤ 2% [운영값]. 흰 재질 자산은 추가로 빛면 L\* ≤ 98이고 빛–그늘 차 ≥ 6이어야 한다(02와 같은 값).
- 실패 시: minor.
- 근거: OV32(그림은 넓은 휘도 범위를 비선형 압축해 담음 — 끝을 잘라 내면 형태 정보가 사라짐), OV6.

**[OBJ_VALUE-05] 평평하거나 매끈해야 할 면 안의 얼룩이 면 사이 단계보다 충분히 작은가?**
- 적용: K1의 면, 그리고 K2 가운데 매끈한 클레이 면(원뿔·돔·원통·큐브형 덩어리). 스캔 질감 지형(산·화산)과 의도된 디테일 면은 뺀다.
- 측정: 면 창마다 σ_hp(디테일 마스크 제외), 그리고 이 자산의 가장 작은 인접 면 단계 Δ_min(02의 값).
- 합격: σ_hp ≤ 3 그리고 σ_hp ≤ 0.35·Δ_min [운영값].
- 실패 시: minor.
- 근거: OV7(고른 명도의 연결 영역이 지각 단위가 됨 — 얼룩이 면 단위를 쪼갬), OV8(과잉 디테일은 해석을 흐림), OV4(손 음영 지도는 불필요한 디테일을 지움).

**[OBJ_VALUE-06] 빛 무리와 그늘 무리가 명도로 겹치지 않는가?**
- 적용: K2, K4 본체(콜로세움, 판테온, 산, 화산, 석회 가마, 나무, 등대, 마을, 수도교, 원뿔 더미).
- 측정: 0.2의 Λ·Σ(법선 패스, 없으면 기하 절반). 오목부·창·아치 안쪽 마스크는 뺀다. P10(Λ) − P90(Σ)를 구한다.
- 합격: ≥ 0.
- 실패 시:
  - −6 ≤ 값 < 0 → minor.
  - 값 < −6 → major(H) / minor(그 밖).
- 근거: OV9(빛 무리와 그늘 무리를 따로 묶고, 그늘 안 반사광은 가장 어두운 중간 톤보다 어둡게), OV10(노탄: 2~3명도 덩어리), OV6.

**[OBJ_VALUE-07] 둥근 물체의 그늘 쪽 윤곽 안쪽에 음영 기울기가 있는가?**
- 적용: K2 가운데 원통·원뿔·돔·둥근 덩어리(콜로세움 바깥벽, 판테온 로툰다, 원뿔 더미, 석회 가마, 나무 수관, 이정표 기둥, 시편 원통, 화산).
- 측정:
  - ℓ′의 반대쪽 120° 호에 있는 윤곽 위에 1pt 간격으로 단면 10곳 이상을 둔다.
  - 각 단면에서 법선 방향으로 안쪽 0.5~6pt의 L\* 단면을 재서 ΔL\* = L\*(6pt) − L\*(0.5pt)와 단조성(스피어만 ρ)을 구한다.
- 합격: 단면 ΔL\* 중앙값 ≥ 4(윤곽 쪽이 더 어두움) 그리고 ρ 중앙값 ≥ 0.7 [운영값].
- 실패 시: minor.
- 근거: OV11(극값 윤곽: 윤곽과 나란한 등휘도선을 가진 음영 기울기 쪽이 거의 언제나 앞의 그림으로 지각됨, Palmer & Ghose 2008), OV6.

**[OBJ_VALUE-08] 같은 재질·같은 방향 면이 다른 자산과 같은 명도인가?**
- 적용: 재질을 공유하는 자산 무리.
  - 석회 콘크리트 큐브: ③·④·제작 주사위·해수 큐브
  - roman_stone 계열 건물
  - 나무 잎
  - 포석
  - 이정표 기둥 3개
- 측정: 이 자산의 면 대표 L\* − 같은 재질·같은 방향 면의 무리 중앙값.
- 합격: |차| ≤ 3 [기존값 I3-01].
- 실패 시: minor.
- 근거: OV13(심벌 속성의 통일), OV12, I3-01.

## B. 그림-바탕 (국소 바탕과의 명도 분리)

**[OBJ_VALUE-09] 자산의 대표 명도가 국소 바탕과 갈리는가?**
- 적용: 전부(K6 포함).
- 측정: ΔL\*_fg = |median(L\*[M]) − g|(C에서 잼). ΔE76·ΔE00(M의 중앙 Lab과 고리의 중앙 Lab)도 기록한다.
- 문턱 T_fg: G(지면 덮개) 6, 그 밖 10 [기존값 VL-05·I3-15 — 명도 한 단계].
- 합격: ΔL\*_fg ≥ T_fg.
- 실패 시:
  - ΔL\*_fg < T_fg이지만 ΔE76 ≥ 25(색으로만 갈림) → minor. 이것은 I3-15의 합격 조건과 같지만, 명도 분야에서는 등휘도 경계를 약점으로 기록한다.
  - S·B·M·L·G에서 T_fg/2 ≤ ΔL\*_fg < T_fg이고 OBJ_VALUE-10이 합격(윤곽이 닫혀 그림이 섬) → minor.
  - 그 밖의 미달 → major(H·C·D·S·B·M) / minor(L·G).
  - ΔL\*_fg < 3 그리고 ΔE00 < 5(바탕에 녹아 사라짐) → blocker(H·C·D) / major(그 밖).
- 근거: OV14(휘도 체계가 그림-바탕·깊이를 맡고, 등휘도 경계는 흔들림), OV16(중요 요소는 명도로 바탕과 달라야 함), OV5(2° 표지의 2·ND50 ≈ 10.9), VL-05, I3-15.

**[OBJ_VALUE-10] 실루엣 윤곽이 명도 대비로 닫혀 있는가?**
- 적용: 전부. 지면에 닿는 밑변은 15·16에서 보므로 빼고, 위쪽·옆 윤곽만 잰다.
- 측정:
  - M의 윤곽을 1pt 간격으로 표본한다. 각 점에서 안쪽 1~3pt 중앙값과 바깥 1~3pt 중앙값(다른 자산·그림자 제외)의 |ΔL\*|를 잰다.
  - 표본 합격 문턱 T_e = 10(G는 6). I3-13과 같이 ΔE76 ≥ 25인 표본도 합격으로 친다.
  - **덮임** = 합격 표본 비율. 가장 긴 연속 미달 구간 = 윤곽 둘레에 대한 %.
- 합격: 덮임 ≥ 80% 그리고 가장 긴 미달 구간 ≤ 15% [운영값].
- 실패 시:
  - 60% ≤ 덮임 < 80% 또는 미달 구간 15~25% → minor.
  - 덮임 < 60% 또는 미달 구간 > 25% → major(H·C·D·S·B·M) / minor(L·G).
- 근거: OV11(Elder & Zucker 1993: 닫힘은 1차원 윤곽을 2차원 형태로 잇는 다리이고, 닫힘의 작은 변화가 형태 변별을 크게 바꿈), I3-13.

**[OBJ_VALUE-11] 실눈(σ = 7pt)으로 흐려도 자산이 한 덩어리로 남는가?**
- 적용: 면적 ≥ 400pt²인 자산. 그보다 작은 부품은 25에서 본다.
- 측정: C를 1배로 줄이고 σ = 7pt로 흐린다(value.md 규약 4의 S). M을 3pt 침식한 핵의 흐림 L\* 중앙값과 고리의 흐림 L\* 중앙값의 |차|를 잰다.
- 합격: ≥ 8(G는 ≥ 5) [운영값 ≈ 0.8·T_fg — 흐림이 깎는 대비 몫을 뺀 값].
- 실패 시: minor. 단 H·C에서 < 5면 major.
- 근거: OV17·OV18(거친 덩어리가 먼저 처리됨), OV16(실눈·물러서기 시험), VL-01·08.

**[OBJ_VALUE-12] 윤곽 바깥에 후광(밝은 띠)이나 합성 테두리가 없는가?**
- 적용: 전부. 따로 합성되는 층(81_NOSHADOW·80_SHAPES·85_HEADER)은 반드시 잰다.
- 측정: 둘레 표본마다 M 바깥 0.5~4pt 띠(Sh 제외)의 L\* 중앙값 − g를 잰다. |차| ≥ 3인 표본 비율과 띠의 폭을 기록한다.
- 합격: |차| ≥ 3인 표본 ≤ 20%.
- 실패 시:
  - minor.
  - 밝거나 어두운 띠가 ΔL\* ≥ 5이고 폭 2~15pt이며 둘레의 50% 이상이면 major(H·C·D·B). 이 폭은 1m에서 약 0.05~0.3°로, 후광 허용치가 가장 낮은 대역이다.
- 근거: OV20(후광 허용치는 폭에 대해 U자형이고 약 0.2°에서 가장 낮음, 거슬리는 문턱은 눈에 띄는 문턱보다 약 4 JND 위).

**[OBJ_VALUE-13] 배경 역할 자산이 '높은 조·낮은 대비' 대역에 머무는가?**
- 적용: L·G 역할만.
- 측정: Cmean = g − mean(L\*[M]), 내부 범위 R = P95 − P5(L\*[M]).
- 합격: Cmean ≤ 30 그리고 R ≤ 40 [운영값, 명도 세·네 단계].
- 실패 시: minor. CORE와의 경쟁 순위는 VL-04·06과 obj_hierarchy가 본다.
- 근거: OV3(손 음영 전통에서 톤 균형·선택적 강조·지형 위계를 사실성과 함께 우선함, 대기 원근), OV16, OV19(주제 위계에 맞춘 시각 위계), OV8.

**[OBJ_VALUE-14] 같은 부류 자산끼리 그림-바탕 명도 차가 고른가?**
- 적용: 같은 부류가 3개 이상인 자산(산 L01_\*, 나무 T_\*, 밭 판, 이정표 MS\*, 인물, 같은 종류 기호 S_\*).
- 측정: 이 자산의 부호 있는 (median(L\*[M]) − g)와 그 부류 중앙값의 차.
- 합격: |차| ≤ 6 [운영값].
- 실패 시: minor.
- 근거: OV13, OV12, OV33(같은 무리 가운데 하나만 다르면 고유 특징으로 튀어 의도치 않게 시선을 끎).

## C. 그림자·접지

**[OBJ_VALUE-15] 바닥에 선 자산의 밑동에 광학 접촉 어둠이 있는가?**
- 적용: 지면·물·받침 위에 서는 3D 자산(K1·K2·K4·K5). 떠 있는 기호(K6)와 일부러 띄운 부품(물방울, 하중 화살)은 뺀다.
- 측정:
  - (a) 접촉선 아래 0~2pt 바닥의 L\*(I_g) 중앙값이 g보다 얼마나 어두운가.
  - (b) 접촉선 위 0~1.5pt 밑테의 L\* 중앙값이 바로 위 면 대표 L\*보다 얼마나 어두운가.
  - 접촉선 길이를 따라 표본한다.
- 합격: 접촉선의 70% 이상에서 (a) ≥ 3 [기존값 I3-12] 또는 (b) ≥ 8.
- 실패 시: minor. 단 원인이 R10(Workbench 접촉 어둠)과 같고 OBJ_VALUE-16이 합격이면 "보류 R10"으로 기록만 한다.
- 근거: OV21(그림자가 있으면 "떠 있음" 응답이 거의 없음), OV9(접촉 그림자는 그림자 무리에서 가장 어두운 곳), OV23(어두움 = 깊음).

**[OBJ_VALUE-16] 자산이 떠 보이지 않는가?**
- 적용: 15와 같다.
- 측정:
  - 접촉선을 따라 자산 밑 경계와 그 그림자(또는 밑동 어둠) 사이에 바닥 밝기(L\* ≥ g − 1) 화소가 폭 ≥ 1pt로 끼어 있는 구간의 비율.
  - 밑면(세계 법선 z ≤ −0.3)이 M의 1% 넘게 보이는가.
- 합격: 끼인 구간 ≤ 25% 그리고 밑면이 보이지 않는다.
- 실패 시: major(H·C·D·S·M·B) / minor(L·G). I3-12의 '떠 있음'을 자산 단위로 잰 것이다.
- 근거: OV21(그림자가 떨어지면 뜸), OV22(물체에 붙은 그림자와 떨어진 그림자, 떨어진 그림자는 떠 보임).

**[OBJ_VALUE-17] 그림자가 자산보다 무겁지 않은가?**
- 적용: Sh 면적이 M의 5% 이상인 자산. 그림자가 없거나 약한 것은 '해당 없음'이다(R3·R5·R10 보류).
- 측정: ΔL\*_sh(0.7), 그리고 그림자 중심 L\*와 이 자산의 가장 어두운 넓은 면 대표 L\*(03).
- 합격: ΔL\*_sh ≤ 25 그리고 그림자 중심 L\* ≥ 가장 어두운 넓은 면 L\* − 5 [운영값].
- 실패 시: minor.
- 근거: OV22(밝은 비사실 그림자가 어두운 그림자보다 AR에서 접지 판단을 더 잘 도왔고, 사실적인 어두운 그림자는 필수가 아님), OV8(그림자가 해석을 흐릴 수 있음).

**[OBJ_VALUE-18] 그림자가 바닥 무늬를 지우지 않고 투명하게 덮는가?**
- 적용: Sh가 무늬 있는 바닥(포석·밭 이랑·물결·기단 줄눈)이나 다른 자산 위에 떨어지는 경우만.
- 측정: 같은 무늬를 그림자 안과 바깥(경계에서 2~6pt)에서 선형 Y로 잰 미켈슨 대비 c = (Y90 − Y10)/(Y90 + Y10). 비 r = c_안/c_밖. 무늬 극성(밝은 줄은 그늘 안에서도 밝게)이 보존되는지 확인한다.
- 합격: 0.6 ≤ r ≤ 1.6 그리고 극성 보존 [운영값].
- 실패 시: minor.
- 근거: OV24(그림자·투명은 새 '대기'를 씌우는 것이고, 부호를 보존하는 X 접합이 대기 경계 신호다. 이중 반전 X는 투명이 아니라 페인트로 보임).

**[OBJ_VALUE-19] 오목한 곳이 둘레 면보다 어두운가?**
- 적용: 오목부·개구부가 형태의 정체인 자산(콜로세움 아치·창, 수도교 아치, 판테온 현관·오쿨루스, 반죽 구덩이, 항구 수조, 성벽 조각의 구멍, 폼페이 건물 문, 상자 아이콘 안쪽).
- 측정: 오목부 마스크(손 또는 법선·깊이)의 L\* 중앙값과 둘레 1~3pt 같은 면 L\* 중앙값의 차. 뒤가 뚫린 개구부(바탕이 보임)는 바탕과의 대비를 09 기준으로 잰다.
- 합격: 오목부가 ≥ 8 어둡다 [운영값].
- 실패 시: minor. 오목부가 둘레보다 밝은 반전이면 major(H·C·D).
- 근거: OV23(확산광에서 사람은 '어두움 = 깊음'에 가깝게 깊이를 판단), OV9(가림 그림자), OV6.

## D. 물체 안 디테일

**[OBJ_VALUE-20] 핵심 현상 단서(CORE·DETAIL)가 명도 대비로 읽히는가?**
- 적용: 단서를 가진 자산.
  - ① 골조의 금(R3_frame_crack_col\*)
  - ② 열 표시(D2_heat\*, C2 장면의 열)
  - ③ 흰 알갱이(\_LIME\*)
  - ④ 단계 단서(R8_water_step1·crack_step1·crack_step2·calcium_step2·healed_step3)
  - ⑤ 시편의 금·메움·누수(R3_leak_crack, R3_healed_fill, R1_leak_drop\*, R1_healed_clast\*)
  - 제작 주사위 알갱이(D2_lime\*), 해수 결정(D1_crystal\*), 구조 하중 화살(D3_press\*)
- 측정: 0.5의 ΔL\*_det, s, σ_hp(주인 고리).
- 합격:
  - 선·홈·줄·방울·화살: s ≥ 1.5pt 그리고 ΔL\*_det ≥ 20 [기존값 I3-26].
  - 흰 알갱이: 지름 ≥ 3pt 그리고 ΔL\*_det ≥ 40 [기존값 I3-23].
  - 해수 결정 바늘: 밑동 폭 ≥ 2pt 그리고 L\* ≥ 80 [기존값 I3-27].
  - 모두 공통으로 ΔL\*_det ≥ 3·σ_hp.
- 실패 시:
  - 위 문턱에 못 미치지만 1.5m에서 예비 문턱 T(s, 1.5m, k3) 이상 → major.
  - 0.5m에서도 감지 문턱 미만(ΔL\*_det < T(s, 0.5m, k1), 또는 s < 0.75pt, 또는 ΔL\*_det < 5로 질감에 묻힘) → **blocker**(의미 단서 판독 불가).
  - 그 사이 → major.
- 근거: I3-23·26·27, OV25·OV26·OV27(크기·휘도·면적에 따른 대비 문턱), OV29(대비 예비), OV30(잡음 속 감지).

**[OBJ_VALUE-21] 정체를 알려 주는 일반 디테일이 1.0m에서 보이는가?**
- 적용: 이랑(밭), 포석 줄눈(길·다리), 아치·창·기둥 홈(콜로세움·수도교·판테온·마을), 지붕, 물결 기호, 나무 수관의 덩이, 산 능선, 인물의 피부·옷 구분, BASIC 아이콘의 책장·상자 테.
- 측정: s, ΔL\*_det(반복 무늬는 진폭 A), σ_hp(주인 고리).
- 문턱: T_id = max(5, T(s, 1.0m, k3), 3·σ_hp) [운영값. 하한 5는 OV5의 ND50(2°)].
- 합격: s ≥ 1.0pt 그리고 ΔL\*_det ≥ T_id.
- 실패 시:
  - minor.
  - 1.0m에서 감지조차 안 되고(ΔL\*_det < T(s, 1.0m, k1) 또는 s < 0.75pt) 그 디테일이 자산의 **유일한** 정체 단서면 major.
- 근거: OV25·OV26·OV27, OV29, OV30, OV5.

**[OBJ_VALUE-22] 작은 디테일이 색상만이 아니라 명도로 구별되는가?**
- 적용: s < 3pt인 모든 디테일(20·21의 대상).
- 측정: ΔL\*_det, ΔE00(디테일, 주인), Oklch ΔC·Δh.
- 합격: ΔL\*_det ≥ 5. 핵심 단서는 20의 문턱이 우선한다.
- 실패 시:
  - ΔL\*_det < 5인데 ΔE00 ≥ 10 또는 Oklch Δh ≥ 20°·ΔC ≥ 0.04(색상·채도로만 갈림) → minor(일반 디테일) / major(핵심 단서).
  - 둘 다 작으면 20·21에서만 판정한다(중복 집계 금지).
- 근거: OV28(색 대비 감도는 저역 통과이고 고주파 한계가 11~12 cycles/deg. 0.5 c/deg 위에서는 휘도 대비 감도가 더 큼 — 1.0m에서 s = 2pt는 약 12 c/deg), OV14, OV15(색 채널의 공간 해상도는 흑백의 약 1/3), OV27.

**[OBJ_VALUE-23] 지면 덮개의 무늬가 고요한 바탕으로 머무는가?**
- 적용: G 역할(밭, 길·다리, 기단, 물·물결).
- 측정: M 안의 진폭 A(0.5).
- 합격: A ≤ 15 [운영값, 명도 한 단계 반].
- 실패 시: minor.
- 근거: OV8, OV10(바탕도 하나의 명도 덩어리), OV4, VL-14.

**[OBJ_VALUE-24] 같은 뜻의 디테일이 같은 명도 극성·비슷한 대비로 그려졌는가?**
- 적용: 같은 뜻 디테일이 2곳 이상 있는 자산, 그리고 자산 사이.
  - 같은 뜻 기준: 열린 금 = 어두운 홈(−), 석회 알갱이·칼슘 메움 = 밝음(+), 물 = 청록 중간 명도. STATE D11·D28 참고.
- 측정: 디테일 종류별 극성과 ΔL\*_det.
- 합격: 극성이 같고, 같은 종류끼리 ΔL\*_det 차 ≤ 10 [운영값, 명도 한 단계].
- 실패 시: minor. 핵심 단서 종류에서 극성이 반대면 major.
- 근거: OV13, OV33, I3-24.

**[OBJ_VALUE-25] 작은 하위 부품(인물·도구·소품)이 바로 둘레와 명도로 갈리는가?**
- 적용: K4 장면과 BASIC 아이콘에서 높이 8~25pt인 부품(인물, 삽·물동이·삼각대, 책, 돋보기, 짚더미 등).
- 측정: 부품 마스크(단독 렌더의 물체별 마스크)와 바깥 1~3pt 고리 중앙값의 |ΔL\*|. 부품 안 두 톤(피부/옷 등)의 ΔL\*와 윤곽 덮임(10의 방식)도 잰다.
- 합격: 부품–둘레 |ΔL\*| ≥ 13.5 [문헌값 환산: OV5의 0.5° 표지 2·ND50(명도) = 13.48]. 또는 ≥ 10이면서 윤곽 덮임 ≥ 70%.
- 실패 시: minor. 장면의 행동을 맡는 주 부품(예: ② 장면의 반죽하는 인물·도구, 유적 관찰 인물)이 < 6이면 major.
- 근거: OV5(작은 표지일수록 더 큰 명도 차가 필요 — 0.5°에서 6.74, 0.25°에서 8.37), I3-29.

**[OBJ_VALUE-26] 인쇄 모의 뒤에도 면 단계와 디테일 대비가 남는가?**
- 적용: 02·20·21이 해당되는 자산.
- 측정: 0.8로 C와 I를 바꾼 뒤 02의 인접 면 ΔL\*, 20·21의 ΔL\*_det를 다시 잰다. 보존율 = 인쇄 후 ÷ 인쇄 전.
- 합격: 모든 값의 보존율 ≥ 0.80 [기존값 VL-18], 그리고 인쇄 뒤에도 각 항목의 합격 문턱 이상.
- 실패 시: 핵심 단서(20)가 인쇄 뒤 문턱 아래로 떨어지면 major / 그 밖 minor.
- 근거: OV31(PSO Coated v3 = FOGRA51, ISO 12647-2:2013, 톤값 증가 곡선 2013-A), VL-18.

---

## 적용 표 (✓ 적용 · ○ 조건부 · – 해당 없음)

| 항목 | K1 상자 | K2 곡면 | K3 지면 덮개 | K4 장면 | K5 이정표 | K6 기호 |
|---|---|---|---|---|---|---|
| 01 면 순서 | ✓ | ✓ | – | ✓(본체) | ✓ | – |
| 02 면 단계 | ✓ | ✓ | – | ✓(본체) | ✓ | – |
| 03 그늘면 뭉개짐 | ✓ | ✓ | – | ✓ | ✓ | – |
| 04 빛면 날림 | ✓ | ✓ | – | ✓ | ✓ | – |
| 05 면 안 얼룩 | ✓ | ○ 매끈한 면 | – | ○ | ✓ | – |
| 06 빛·그늘 무리 | – | ✓ | – | ✓(본체) | – | – |
| 07 윤곽 음영 기울기 | – | ○ 둥근 형 | – | – | ✓(기둥) | – |
| 08 같은 재질 일치 | ○ | ○ | ○ | ○ | ✓ | – |
| 09 그림-바탕 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 10 윤곽 닫힘 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 11 실눈 덩어리 | ○ ≥ 400pt² | ○ | ○ | ○ | ✓ | ○ |
| 12 후광 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 13 배경 대역 | ○ L·G | ○ L·G | ✓ | ○ L·G | – | – |
| 14 부류 일관 | ○ ≥ 3개 | ○ | ○ | ○ | ✓ | ○ |
| 15 접촉 어둠 | ✓ | ✓ | – | ✓ | ✓ | – |
| 16 뜸 없음 | ✓ | ✓ | – | ✓ | ✓ | – |
| 17 그림자 무게 | ○ 그림자 있음 | ○ | – | ○ | ○ | – |
| 18 그림자 투명성 | ○ 무늬 위 | ○ | – | ○ | ○ | – |
| 19 오목부 어둠 | ○ 오목부 | ○ | – | ○ | – | – |
| 20 핵심 단서 | ○ 단서 | ○ | – | ○ | – | – |
| 21 정체 디테일 | ○ | ○ | ✓ | ○ | ○ | – |
| 22 명도로 구별 | ○ s < 3pt | ○ | ○ | ○ | ○ | – |
| 23 덮개 무늬 상한 | – | – | ✓ | – | – | – |
| 24 디테일 극성 | ○ | ○ | – | ○ | – | – |
| 25 하위 부품 | – | – | – | ✓ | – | – |
| 26 인쇄 보존 | ○ | ○ | ○ | ○ | ○ | – |

## 보고 형식 (자산마다)
- 자산 id(Blender 물체 이름들), 역할(H·C·D·S·L·G·B·M), 부류(K1~K6), 크롭 좌표(pt), g, 단독 렌더 사용 여부(I_a·I_g·G0·법선).
- 항목마다 {id, 판정(합격/불합격/해당 없음/보류 Rn), 측정값, 쓴 창·마스크 좌표}. 불합격은 {심각도, 근거 ID, 해법}.
- 해법은 수치로 낸다. 예: 재질 선형 반사율 ×k(0.3의 환산식), 목표 면 L\*, 디테일 폭(pt)·목표 ΔL\*, 그림자 세기, 물체 이동(pt).
- Workbench의 Cavity·Outline·Shadow 설정은 장면 전체에 걸린다. 이것을 해법으로 내면 영향을 받는 다른 자산을 함께 적는다.
- 진행 중 결론은 자기 리포트 파일에 자산마다 바로 덧붙인다(BRIEF §6).

---

## 출처 (실제로 열어 본 자료 · 상태 표기)
- 상태 표기:
  - [열람]: 본문 또는 원문 페이지를 직접 열어 확인했다.
  - [초록]: 초록·서지 페이지만 확인했다.
  - [2차]: 다른 자료의 인용으로만 확인했다.
  - [기존 ID]: 기존 루브릭에서 이미 연 자료다.

| ID | 저자·연도 | 제목·매체 | 이 루브릭에서 쓴 내용 | 상태 · URL |
|---|---|---|---|---|
| OV1 | Mamassian, P., Goutcher, R. (2001) | Prior knowledge on the illumination position. *Cognition* 81:B1–B9 | 가정 광원은 바로 위가 아니라 왼쪽 위이고, 형태 변별 과제에서 평균 26°다 | [초록] https://eprints.gla.ac.uk/25130 |
| OV2 | Gołębiowska, I. 외 (2025) | Mitigating relief inversion illusion with multidirectional sky illumination model. *Abstracts of the ICA* 10:92 | 225°(왼쪽 아래) 빛에서 지형 반전이 가장 많음 | [기존 I3 S11] https://ica-abs.copernicus.org/articles/10/92/2025/ica-abs-10-92-2025.pdf |
| OV3 | Stefanakis, E. (2026) | Neural-Based Cartographic Relief Shading for Alberta. *Abstracts of the ICA* 12:135 (EuroCarto 2026) | 스위스 손 음영은 톤 균형·선택적 강조·지형 위계·가독성을 사실성과 함께 우선한다. 빛이 지형 결과 나란하면 대비가 줄어든다. 대기 원근 | [열람] https://ica-abs.copernicus.org/articles/12/135/2026/ica-abs-12-135-2026.pdf |
| OV4 | Jenny, B., Heitzler, M., Singh, D., Farmakis-Serebryakova, M., Liu, J. C., Hurni, L. (2021) | Cartographic Relief Shading with Neural Networks. *IEEE TVCG* 27(2):1225–1235 | 손 음영은 불필요한 지형 디테일을 지우고, 빛 방향을 국소적으로 조정하며, 큰 지형을 밝기로 강조한다 | [초록] https://arxiv.org/abs/2010.01256 |
| OV5 | Szafir, D. A. (2018) | Modeling Color Difference for Visualization Design. *IEEE TVCG* 24(1) | 표 1 ND(50%) 명도축: 2° 5.47 · 0.5° 6.74 · 0.25° 8.37(ΔE76). 2·ND50에서 판별률 ≈ 1 | [기존 color S4] https://cmci.colorado.edu/visualab/VisColors/ |
| OV6 | Gooch, A., Gooch, B., Shirley, P., Cohen, E. (1998) | A Non-Photorealistic Lighting Model for Automatic Technical Illustration. *SIGGRAPH 98* | 음영은 중간 톤 안에서 면 방향을 전하고, 극단 명암은 윤곽·하이라이트에만 쓴다 | [기존 I3 S7] https://users.cs.northwestern.edu/~ago820/SIG98/abstract.html |
| OV7 | Palmer, S. E., Rock, I. (1994) | Rethinking perceptual organization: The role of uniform connectedness. *Psychonomic Bulletin & Review* 1:29–55 | 고른(또는 매끄럽게 변하는) 명도의 연결 영역이 지각 단위가 된다(강도는 후속 연구에서 논란) | [초록·2차] https://doi.org/10.3758/BF03200760 |
| OV8 | Jenny, H., Jenny, B. (2013) | Challenges in adapting example-based texture synthesis for panoramic map creation. *CaGIS* | 과잉 디테일과 그림자가 해석을 흐린다 | [기존 I3 S6] https://mail.colororacle.org/berniejenny/pdf/2013_Jenny_TextureSynthesisForPanoramicMaps.pdf |
| OV9 | The Drawing Source | Value, Light and Form | 빛 무리(직사광·하이라이트·중간 톤)와 그늘 무리(심 그림자·반사광·드리운 그림자·가림 그림자). 반사광의 가장 밝은 곳은 가장 어두운 중간 톤보다 어두워야 한다. 가림 그림자는 형태가 면에 닿는 곳으로, 드리운 그림자에서 가장 어둡다 | [열람] https://www.thedrawingsource.com/light-and-form.html |
| OV10 | Berry, S. (2019), Dow, A. W. 해설 | A Reading Guide to Dow's "Composition", pt. 3 – Notan | 명도 덩어리 짓기, 바탕도 하나의 덩어리 | [기존 value V1] https://stephenberryart.com/blog/2019/2/23/a-reading-guide-to-dows-composition-pt-3-notan |
| OV11 | Wagemans, J., Elder, J. H., Kubovy, M., Palmer, S. E., Peterson, M. A., Singh, M., von der Heydt, R. (2012) | A century of Gestalt psychology in visual perception: I. Perceptual grouping and figure–ground organization. *Psychological Bulletin* 138(6):1172–1217 | 극값 윤곽(EE): 윤곽과 나란한 등휘도선의 음영 기울기를 가진 쪽이 거의 언제나 앞으로 지각됨(Palmer & Ghose 2008). Elder & Zucker(1993): 닫힘은 윤곽→형태의 다리이고, 작은 변화가 형태 변별을 크게 바꿈 | [열람] https://ruccs.sas.rutgers.edu/images/archive/personal-manish-singh/papers/Wagemans_etal_2012_I.pdf |
| OV12 | Ostrovsky, Y., Cavanagh, P., Sinha, P. (2005) | Perceiving illumination inconsistencies in scenes. *Perception* 34 | 반복된 같은 모양 물체에서는 조명 불일치가 드러난다 | [기존 I3 S13] https://dspace.mit.edu/handle/1721.1/7243 |
| OV13 | Häberling, C. 외 (2008) / Santos 외 (2013) 요약 | Proposed Cartographic Design Principles for 3D Maps | 심벌화 단계에서 형태·크기·색·밝기·질감을 통일한다 | [기존 I3 S1·S2] https://www.redalyc.org/pdf/3939/393937730006.pdf |
| OV14 | *Harvard Magazine* (2003), M. Livingstone 연구 소개 | The Neurobiology of Art | 휘도 체계는 색맹이고 깊이·그림-바탕을 맡는다. 등휘도 경계는 흔들리고 깊이가 사라진다 | [기존 value V3] https://www.harvardmagazine.com/2003/07/the-neurobiology-of-art-html |
| OV15 | Stone, M., Ware, C. (2009) | Colo(u)r in Information Display (SFU IAT 814) | 색 채널의 공간 해상도는 흑백의 약 1/3이다. 음영으로 형태를 읽을 수 있지만 색상으로는 읽을 수 없다 | [기존 value V4] https://www.sfu.ca/siatclass/IAT814/Spring2009/Lectures/814week3A.pdf |
| OV16 | Axis Maps | Cartography Guide — Visual Hierarchy | 중요 요소는 명도로 바탕과 달라야 한다. 실눈·물러서기 시험 | [기존 value V10] https://axismaps.com/guide/visual-hierarchy |
| OV17 | Schyns, P. G., Oliva, A. (1994) | From blobs to boundary edges. *Psychological Science* 5(4) | 거친 덩어리가 먼저 장면 인식을 시작한다 | [기존 value V7] https://www.psychologicalscience.org/journals/psychological-science/j.1467-9280.1994.tb00500.x/ |
| OV18 | Oliva, A., Torralba, A., Schyns, P. G. (2006) | Hybrid images. *ACM TOG* 25(3) | 짧은 노출에서는 저주파가 지배한다 | [기존 value V8] https://wcours.gel.ulaval.ca/GIF4105/old/h23/tps/tp2/OlivaTorralb_Hybrid_Siggraph06.pdf |
| OV19 | Fabrikant, S. I., Hespanha, S. R., Hegarty, M. (2010) | Cognitively Inspired and Perceptually Salient Graphic Displays… *Annals AAG* 100(1) | 주제 위계에 맞춘 시각 위계 | [기존 value V9] https://user.geo.uzh.ch/sfabri/pubs/fabrikant_etal_an09.pdf |
| OV20 | Trentacoste, M., Mantiuk, R., Heidrich, W., Dufrot, F. (2012) | Unsharp Masking, Countershading and Halos: Enhancements or Artifacts? *Computer Graphics Forum* 31(2):555–564 | 후광 허용치는 폭에 대해 U자형이고 약 0.2°에서 가장 낮다. 거슬리는 문턱은 눈에 띄는 문턱보다 약 4 JND 위다(Ihrke 2009 인용). 문턱 위 대비에서는 대비 항상성이 CSF를 평평하게 만든다(Georgeson & Sullivan 1975) | [열람] https://www.cl.cam.ac.uk/~rkm38/pdfs/trentacoste12countershading.pdf |
| OV21 | Cooper, E. A. 외 (2023) | The art of the float. *Journal of Vision* 23(8):13 | 그림자가 접지 판단을 지배하고, 떨어진 그림자는 뜸을 만든다 | [기존 I3 S12] https://pmc.ncbi.nlm.nih.gov/articles/PMC10434713/ |
| OV22 | Adams, H., Stefanucci, J. K., Creem-Regehr, S. H., Pointon, G. D., Thompson, W. B., Bodenheimer, B. (2022) | Shedding Light on Cast Shadows: An Investigation of Perceived Ground Contact in AR and VR. *IEEE TVCG* 28(12):4624–4639. 관련 예비 논문 arXiv 2201.01889 | 밝은(비사실) 그림자가 어두운 그림자보다 AR 접지 판단을 개선했다. 사실적 그림자는 접촉 지각에 필수가 아니다. 떨어진 그림자는 떠 보인다 | [서지: dblp, 본문: 예비 논문 열람] https://arxiv.org/abs/2201.01889 |
| OV23 | Langer, M. S., Bülthoff, H. H. (2000) | Depth discrimination from shading under diffuse lighting. *Perception* 29(6):649–660 | 확산광에서 깊이 판단이 '어두움 = 깊음' 모형과 유의하게 상관된다(실제 수행은 그보다 나음) | [초록] https://pure.korea.ac.kr/en/publications/depth-discrimination-from-shading-under-diffuse-lighting/ |
| OV24 | Adelson, E. H. (2000) | Lightness Perception and Lightness Illusions. In *The New Cognitive Neurosciences* 2nd ed., 339–351 | 그림자·투명·연무는 하나의 '대기 전달 함수'로 묶인다. 부호를 보존하는 X 접합은 대기(투명) 경계 신호이고, 이중 반전 X는 페인트로 보인다 | [열람] https://persci.mit.edu/gaz/publications/gazzan.dir/gazzan.htm |
| OV25 | Barten, P. G. J. (1999 / 2003) | *Contrast Sensitivity of the Human Eye and Its Effects on Image Quality* / Formula for the contrast sensitivity of the human eye. *Proc. SPIE* 5294:231–238. 구현: colour-science 0.4.7 `contrast_sensitivity_function_Barten1999` | 휘도·자극 크기·공간 주파수에 따른 대비 감도. 0.6의 표를 계산함 | [서지·구현 문서] https://colour.readthedocs.io/en/v0.4.7/_modules/colour/contrast/barten1999.html |
| OV26 | Mantiuk, R. K., Ashraf, M., Chapiro, A. (2022) | stelaCSF — A unified model of contrast sensitivity… *ACM TOG* 41(4):145 (SIGGRAPH 2022) | 공간·시간 주파수, 이심률, 휘도, 면적의 5차원 CSF. 11개 연구 자료를 한 매개변수로 설명 | [열람] https://www.cl.cam.ac.uk/research/rainbow/projects/stelaCSF/ |
| OV27 | Ashraf, M., Mantiuk, R. K., Chapiro, A., Wuerger, S. (2024) | castleCSF — A contrast sensitivity function of color, area, spatiotemporal frequency, luminance and eccentricity. *Journal of Vision* 24(4) | 색 변조 방향·배경 휘도·색도·면적까지 다루는 CSF. 18개 연구, 오차 3.59 dB | [열람] https://www.cl.cam.ac.uk/research/rainbow/projects/castleCSF/ |
| OV28 | Mullen, K. T. (1985) | The contrast sensitivity of human colour vision to red-green and blue-yellow chromatic gratings. *J. Physiol.* 359:381–400 | 색 CSF는 저역 통과이고 고주파 한계는 11~12 c/deg다. 0.5 c/deg 위에서는 휘도 격자 감도가 더 크다 | [초록] https://pmc.ncbi.nlm.nih.gov/articles/PMC1193381 |
| OV29 | Whittaker, S. G., Lovie-Kitchin, J. (1993) | Visual requirements for reading. *Optometry and Vision Science* 70(1):54–65 | 대비 예비(읽는 대비 ÷ 문턱 대비)와 시력 예비 개념. 여기서는 k = 3을 운영값으로만 씀 | [2차] https://pmc.ncbi.nlm.nih.gov/articles/PMC6456801 |
| OV30 | Rose, A. (1948) 요약 · Burgess, A. E. (1999) | Rose 기준 / The Rose model, revisited. *JOSA A* 16(3) | 잡음 표준편차의 약 5배 차이면 작은 물체를 거의 100% 찾는다. Rose 모형은 좁게 정의된 조건에서만 이상 관찰자 근사 | [2차·초록] https://en.wikipedia.org/wiki/Albert_Rose_(physicist) · https://www.doi.org/10.1364/JOSAA.16.000633 |
| OV31 | European Color Initiative (2015) | PSO Coated v3 (FOGRA51) | ISO 12647-2:2013, 톤값 증가 곡선 2013-A, 최대 면적 300%, K 96% | [기존 value V19] https://www.eci.org/lib/exe/pso-coated_v3.zip |
| OV32 | Graham, D. J., Field, D. J. (2008) | Variations in intensity statistics for representational and abstract art… *Perception* 37 | 그림의 동적 범위는 약 30:1, 비선형 휘도 압축 | [기존 value V11] https://people.hws.edu/graham/Graham_perception08.pdf |
| OV33 | Healey, C. G. | Perception in Visualization (NC State) | 고유한 시각 특징 하나는 즉시 튄다 | [기존 color S18] https://www.csc2.ncsu.edu/faculty/healey/PP/ |

- 2022~2026 자료는 6개다: OV2(2025), OV3(2026), OV21(2023), OV22(2022), OV26(2022), OV27(2024).
  - 이 가운데 이번에 새로 연 자료는 OV3·OV22·OV26·OV27이다.
  - 실무 SOTA로는 신경망 지형 음영(OV4 2021, OV3 2026의 Eduard)과 통합 CSF 모형(OV26·OV27)을 문턱 계산과 지형 자산 판정에 썼다.
- 원문을 열지 못한 자료:
  - Cavanagh & Leclerc(1989, 그림자는 바탕보다 어두워야 한다는 조건)는 인용 확인에 실패해 쓰지 않았다. 그림자 극성은 OV24로만 근거를 댄다.
  - Sun & Perona(1998)도 원문을 확인하지 못해 OV1로 대신했다.
- 계산 재현: 0.6의 표는 `uv run --no-project --with colour-science --with numpy python -I`로 `colour.contrast.contrast_sensitivity_function_Barten1999`(X_0 = 0.5°, 휘도 = 100·Y_주인/Y_종이 cd/m², 동공·망막 조도는 같은 모듈의 Barten 식)를 써서 얻었다. 주인 L\* 40·55·75에서 계산해 가장 큰 값을 올림했다.
