# 루브릭 · 7 명암·명도 구성 (value / tonal structure)

- 작성: 라운드 8 명도 비평가(2026-10-12). 이 분야는 사용자 질문("컬러그래픽 정밀검토할 때 명암도 같이 검토한 거지?")으로 새로 추가됐다. 다음 라운드부터 이 문서를 고정해 다른 비평가가 블라인드로 재현한다.
- 범위: **포스터 전체의 명도 설계**. 휘도(흑백)만 남겼을 때와 흐리게 봤을 때 위계가 유지되는지, 명도 덩어리·단계·분포·균형, 큰 면(땅·바다·강)의 명도 관계, 인쇄 뒤 명도 보존을 본다.
- 판정은 항목마다 예(합격) / 아니오(불합격). 같은 원인으로 불합격한 항목이 여럿이면 지적은 하나로 묶는다(부풀리기 금지).
- 수치 기준 가운데 문헌이 직접 준 값은 [문헌값], 문헌의 원리를 이 포스터에서 재현 가능한 값으로 옮긴 것은 [운영값]으로 표시한다.

## 다른 루브릭과의 경계 (겹치지 않게 뺀 것)
- 글자 하나하나의 대비(WCAG·APCA), 비텍스트 3:1, 색각이상, 인쇄 색역 → `color.md` CL-13~25, `hierarchy_access.md` C1~C6·V1~V3·P4.
- 광원 방향, 실루엣, 그림자·접지, 먹색 뭉개짐, 모형별 최소 그림-바탕 ΔL* ≥ 10, 구조 모형의 명도 순서 → `illustration3d.md` I3-02, I3-09~13, I3-15, I3-25.
- 글 크기·굵기에 따른 위계 → `hierarchy_access.md` H1~H4, `typography.md` TY-01·04. 콜로세움 면적, 좌우 화소 수 균형, 혼잡도 → `layout.md` LY-10·11·26.
- 이 루브릭은 위 항목을 다시 재지 않는다. 대신 **휘도 채널 하나로 본 위계, 거친 척도의 명도 덩어리, 명도 분포·범위·집중·균형, 큰 면 사이 명도 단계, 인쇄 뒤 명도 비율**을 잰다.

## 고정 조건 (감점하지 않음)
- 클레이 디오라마 렌더의 "약간 플랫한 음영"과 밝은 조(high key) 자체는 감점하지 않는다. 그 안에서의 명도 배분만 본다.
- CORE 제목 둘째 줄 #983821(L\* 37.1)은 흑백에서 첫째 줄 #2E2A22(L\* 17.2)보다 옅다. 고정 조건 5이므로 **판정하지 않는다**.
- 이정표 3개(석회암 기둥 + ②색 판)는 CORE 길잡이로 보고, VL-04·VL-06의 비교 대상(비CORE)에서 뺀다.

---

## 0. 측정 규약 (모든 항목 공통 · 재현용)

1. **자료**: `r<N>/poster_1x.png`(1191×1684, 1pt = 1px), `r<N>/map_only_2x.png`(글 없는 지도)를 LANCZOS로 1/2 축소해 1x로 맞춘다. PNG에 ICC가 없으면 sRGB로 본다. 글 상자는 `text_spec_r<N>.json`.
2. **L\***: sRGB → 선형(IEC 61966-2-1) → Y = 0.2126R + 0.7152G + 0.0722B → CIE L\*(Y > 0.008856이면 116·Y^(1/3) − 16, 아니면 903.3·Y).
3. **종이 L\*_paper**: poster_1x에서 84 < L\* < 92인 화소의 중앙값(R8 = 87.8).
4. **흐림 두 단계** [운영값]: 가우스 σ의 반진폭 주파수는 f50 = 0.1874/σ.
   - **S(실눈) σ = 7pt**: 최대 관람 거리 1.5m에서 1° = 74.2pt이므로 f50 ≈ 2 cycles/deg. 글자 획은 사라지고 물체 덩어리만 남는다.
   - **G(첫 흘끗) σ = 39pt**: 포스터 높이 1684pt 기준 f50 = 8 cycles/image. Schyns & Oliva(1994)와 Oliva·Torralba·Schyns(2006)가 30ms 노출에서 먼저 읽힌다고 한 저주파 대역의 차단 주파수다.
5. **ROI 표**(pt, x0–x1 × y0–y1, 지도 1x 좌표). 역할은 BRIEF §2 기준이다. ③·④·⑤ 그림은 CORE 그림(INF-15)과 DETAIL·SUPPORT를 겸하므로 **CORE 그림으로 센다**(관대한 해석).

| 키 | 역할 | 상자 |
|---|---|---|
| 콜로세움(영웅) | hero | 368–800 × 580–985 |
| C1 철근 골조 | CORE 그림 | 708–888 × 355–550 |
| C2 반죽 구덩이 장면 | CORE 그림 | 75–192 × 850–948 |
| C3 석회 알갱이 큐브 | CORE 그림(DETAIL 겸) | 440–568 × 1130–1292 |
| C4 큐브 3개 | CORE 그림(DETAIL 겸) | 620–845 × 1148–1252 |
| C5 시편 두 개 | CORE 그림(SUPPORT 겸) | 985–1158 × 665–758 |
| 제작 원리 주사위 | DETAIL | 68–135 × 965–1035 |
| 구조 원리 탑+단면 | DETAIL | 258–410 × 1185–1345 |
| 재료 원리 해수 큐브 | DETAIL | 30–132 × 1560–1662 |
| 프리베르눔 / 유적 관찰 / 폼페이 공사현장 / 항구 수조 / 방파제 블록 | SUPPORT | 1018–1128 × 1000–1092 / 865–966 × 1125–1242 / 648–752 × 1415–1505 / 113–227 × 1425–1518 / 398–492 × 1508–1582 |
| 이정표 M1 / M2 / M3 | 길잡이(비교 제외) | 458–516 × 368–456 / 196–258 × 912–1002 / 776–849 × 912–1002 |
| 베수비오 / 판테온 / 석회 가마 / 등대 / 폼페이 마을 / 수도교 / 산맥 / 나무 A / 나무 B | 배경 지물 | 908–1168 × 1270–1528 / 412–496 × 450–558 / 78–202 × 628–732 / 38–110 × 1385–1528 / 756–906 × 1392–1502 / 828–1172 × 350–668 / 238–1142 × 258–360 / 408–566 × 1350–1475 / 993–1170 × 1105–1250 |
| BASIC 왼쪽 / 오른쪽 아이콘 | BASIC | 20–330 × 50–140 / 870–1155 × 50–140 |
| 제목 글 상자 | 제목 | 368–824 × 27–107 |

6. **바탕 g·물체 화소**(map_only 1x): g = 상자 바깥 6~20pt 고리의 L\* 중앙값. 물체 화소 = 상자 안에서 |L\* − g| > 4. 대표 명도 = 물체 화소 중앙값. **Cmean** = g − 물체 화소 평균. **Cpeak** = g − 물체 화소 5백분위.
7. **휘도 주목도 4모형**: 입력은 poster_1x의 L\*/100 하나다(색 채널 없음).
   - (a) **Itti 강도 채널**(Itti·Koch·Niebur 1998): 9단 이진 가우스 피라미드(σ = 1, 2배 축소), 중심 c ∈ {2,3,4}, 주변 s = c + δ, δ ∈ {3,4}, 특징 지도 |I(c) − 확대(I(s))|. N(): [0,1]로 맞춘 뒤 5×5 국소 최대(> 0.05) 가운데 전역 최대를 뺀 평균 m̄을 구해 (1 − m̄)²를 곱한다. 6개 지도를 4단 해상도에서 더하고 다시 N()을 거쳐 쌍선형으로 원래 크기로 올린다.
   - (b) 같은 방식, c ∈ {3,4,5}.
   - (c) DoG 에너지: Σ_{s=4,8,16,32} |G_s − G_{4s}|를 구한 뒤 σ = 8로 다듬는다.
   - (d) 스펙트럼 잔차: 96×136으로 줄인 영상의 로그 진폭에서 3×3 평균을 빼고 위상과 합쳐 역변환한 제곱을 σ = 2.5로 다듬는다.
   - **정점** = ROI 안 최댓값 ÷ 영상 전체 최댓값. 여러 모형을 쓰는 항목은 **4모형 중 3개 이상**이 같은 판정일 때 그 판정을 따른다.
8. **WTA 응시**: 모형 (a)에 승자독식과 복귀 억제를 건다. 억제 원반 반지름은 짧은 변의 1/6 = 198.5pt(Itti 1998의 FOA 반지름)이다. "영웅·CORE에 닿음"은 응시점이 콜로세움·CORE 글 상자(번호 원판·제목·본문 합집합)·CORE 그림·제목·이정표 상자에서 50pt(1m에서 중심와 반지름 1°) 안에 있다는 뜻이다.
9. **인쇄 모의**: Pillow ImageCms(LittleCMS). sRGB → `PSOcoated_v3.icc`(ECI 2015, FOGRA51)로 상대 색도 + 흑점 보정을 걸어 보내고, 다시 sRGB로 **절대 색도**(종이색·잉크 농도 모의)를 걸어 돌아온 뒤 L\*을 잰다.
10. **명도 한 단계** = ΔL\* 10. Munsell 명도의 10배를 lightness로 정의한 관례(Glasser 1958, V20)에 따른다.

---

## A. 휘도(흑백)·흐림에서의 위계

**[VL-01] 첫 흘끗(G, σ = 39pt) 흐림에서 가장 큰 어두운 덩어리가 콜로세움이고, 둘째 덩어리의 2배 이상인가?**
- 측정: poster_1x를 σ = 39로 흐린 B에서 B < L\*_paper − 15인 영역을 8연결 성분으로 나눈다. 가장 큰 성분의 무게중심이 콜로세움 상자 안에 있는지 보고, 첫째와 둘째의 면적비를 잰다.
- 합격: 첫째가 콜로세움이고 면적비 ≥ 2 [운영값].
- 실패 시: major
- 근거: V7·V8(거친 덩어리가 먼저 처리됨), V1(노탄: 명도 덩어리의 배치가 구성의 힘), V10("물러서거나 실눈을 떠도 중요한 요소가 남는가").

**[VL-02] G 흐림에서 가장 어두운 점이 영웅이나 CORE 그림 안에 있는가?**
- 측정: VL-01의 B에서 전역 최솟값 좌표를 찾고, 그 점이 콜로세움 또는 C1~C5 상자 안인지 본다.
- 합격: 예.
- 실패 시: minor
- 근거: V2(인접 명도 대비가 구조상 중요한 가장자리를 강조), V6(가장 두드러진 한 점이 첫 응시를 이김).

**[VL-03] 휘도만으로 예측한 첫 응시 3개 가운데 2개 이상이 영웅·CORE·제목에 닿는가?**
- 측정: 규약 8의 WTA로 첫 3응시를 구한다.
- 합격: 3개 중 2개 이상이 규약 8의 "닿음"을 만족 [운영값].
- 실패 시: major
- 근거: V6(WTA·복귀 억제, FOA 반지름 1/6), V9(지도의 지각적 위계가 주제 위계와 맞아야 하고, 주목도 모형으로 미리 점검한다), V13(장면 내용이 응시 선택을 좌우).

**[VL-04] 비CORE 물체(순수 DETAIL·SUPPORT·배경 지물·BASIC) 가운데 휘도 주목 정점이 가장 높은 것도 CORE 그림·영웅의 정점 최댓값을 넘지 않는가?**
- 측정: 규약 7의 4모형마다, 비CORE ROI 정점의 최댓값과 CORE(영웅 + C1~C5) 정점의 최댓값을 비교한다.
- 합격: 4모형 중 3개 이상에서 비CORE 최댓값 ≤ CORE 최댓값.
- 실패 시: major
- 근거: V9(시각 위계 ≠ 주제 위계일 때 응시 행동·응답 시간이 달라짐), V5("휘도 대비는 색보다 더 주의를 관리한다"), V15·V16(방해물의 톤·노출을 낮추면 응시가 옮겨 감), BRIEF §2(CORE > DETAIL > SUPPORT).

**[VL-05] 영웅의 대표 명도가 배경 지물 무리와 명도 한 단계 이상 떨어지는가?**
- 측정: 규약 6의 대표 명도. 배경 지물 무리 = 베수비오·석회 가마·수도교·산맥·폼페이 마을 대표 명도의 중앙값.
- 합격: |영웅 − 무리| ≥ 10.
- 실패 시: major
- 근거: V3(휘도 채널이 그림-바탕·깊이를 맡는다, "the Where system is colorblind"), V10(배경과 명도가 뚜렷이 달라야 그림이 선다), V20.

**[VL-06] CORE 그림 5개가 각각 배경 지물보다 그림-바탕 정점 대비가 큰가?**
- 측정: 규약 6의 Cpeak. C1~C5 각각을 배경 지물(베수비오·판테온·석회 가마·등대·폼페이 마을·수도교·산맥·나무 A·나무 B) Cpeak의 최댓값과 비교한다.
- 합격: 5개 모두 ≥ 배경 최댓값.
- 실패 시: major (VL-04와 원인이 같으면 지적 하나로 묶는다)
- 근거: V9, V10(어두운 것이 눈을 끈다, 밝은 바탕일 때), V4(모양·세부는 휘도 채널, 색상 채널의 공간 해상도는 약 1/3).

**[VL-07] SUPPORT 장면의 그림-바탕 평균 대비가 CORE 그림보다 낮은가?**
- 측정: SUPPORT 5개의 Cmean 최댓값과 CORE(영웅 + C1~C5)의 Cmean 중앙값.
- 합격: SUPPORT 최댓값 ≤ CORE 중앙값.
- 실패 시: minor
- 근거: V9, BRIEF §2.

**[VL-08] 실눈(S, σ = 7pt)으로 봐도 글 덩이 진하기가 제목 ≥ 질문 ≥ CORE > DETAIL·SUPPORT 순서인가?**
- 측정: (map_only를 σ7로 흐린 것) − (poster를 σ7로 흐린 것) = 글이 더한 어둠. 글 덩이 상자(text_spec 합집합: 제목 790:82, 질문 790:86, CORE마다 제목 두 줄 + 본문, DETAIL마다 제목 + 설명, SUPPORT마다 제목 + 부제 + 설명) 안의 90백분위.
- 합격: 제목 ≥ 질문 ≥ CORE 최솟값 > DETAIL·SUPPORT 최댓값.
- 실패 시: major
- 근거: V10(실눈 시험), V7·V8, V17(포스터에서 글이 그림보다 시선을 잘 끈다).

## B. 명도 구조 (노탄·단계·분포·집중·균형)

**[VL-09] 실눈 3단 노탄에서 어둠 무리가 적당한 강조로만 쓰이고, 그 가장 큰 덩어리가 초점에 있는가?**
- 측정: poster σ7 흐림을 밝음(≥ 80)·중간(55~80)·어둠(< 55) 셋으로 나눈다. 어둠 무리의 면적 비율을 재고, 가장 큰 어둠 연결 성분의 무게중심이 어느 ROI에 있는지 본다.
- 합격: 어둠 2~15% [운영값] 그리고 최대 어둠 덩어리가 영웅 또는 C1~C5 안.
- 실패 시: minor
- 근거: V1(2~3명도로 덩어리 짓기), V2(높은 조·낮은 조·중간 조, 같은 명도는 위치와 상관없이 무리 지음).

**[VL-10] 명도 단계가 고르게 쓰이고 중간 톤 한 단계에 쏠리지 않는가?**
- 측정: poster_1x L\* 히스토그램을 10단(0–10, …, 90–100)으로 나눈다.
- 합격: 면적 ≥ 0.5%인 단계가 6개 이상이고, 종이 단계(80–90) 밖의 어떤 단계도 35% 미만 [운영값].
- 실패 시: minor
- 근거: V1, V2, V20(Munsell 명도는 지각적으로 고른 단계).

**[VL-11] 포스터 전체 명도 범위가 인쇄 그림 수준인가?**
- 측정: poster_1x L\* 0.5백분위와 99.5백분위의 차.
- 합격: ≥ 70. 이는 휘도비 약 30:1에 해당하며, V11이 보고한 그림의 동적 범위 약 30:1을 근거로 한 [문헌값 환산]이다.
- 실패 시: minor
- 근거: V11(그림은 약 30:1, 장면은 1000:1 이상. 화가는 비선형 압축으로 맞춤), V12(휘도 변화가 클수록 아름답게 평가됨).

**[VL-12] 가장 어두운 1%가 초점 구역에 모이는가?**
- 측정: map_only에서 text_spec 글 상자(±3pt)를 뺀 화소의 L\* 1백분위 이하 화소. 이 가운데 초점 구역(영웅·C1~C5·이정표 상자 합집합) 안에 있는 비율.
- 합격: ≥ 50% [운영값]. 초점 구역이 전체 면적의 17.1%이므로, 무작위라면 약 17%가 나온다.
- 실패 시: major
- 근거: V1, V2, V10(어두운 물체가 눈을 끈다).

**[VL-13] 가장 강한 국소 명암 대비가 초점 구역에 모이는가?**
- 측정: map_only L\*에서 15×15pt 창의 (최대 − 최소)를 구한다. 글 상자 밖에서 상위 1%인 화소 가운데 초점 구역 안 비율.
- 합격: ≥ 50% [운영값].
- 실패 시: major
- 근거: V6(중심-주변 차이가 주목도), V1(국소 대비로 명도를 판단 — "pay attention to localized contrast").

**[VL-14] 빈 땅(바탕)이 하나의 고요한 덩어리인가?**
- 측정: map_only 1x에서 바탕 화소 = 청록이 아니고(B ≤ R + 0.03) 75 < L\* < 95이며 Sobel 기울기 5×5 최대가 12 미만, y ≥ 240. 이 화소만으로 정규화한 σ = 20 흐림(가중치 > 0.5인 곳)의 L\* 5~95백분위 폭을 잰다.
- 합격: ≤ 6 [운영값, 명도 반 단계 남짓].
- 실패 시: minor (STATE R3의 ④⑤ 본문 밑 음영 띠는 다시 지적하지 않는다)
- 근거: V1(바탕도 하나의 명도 덩어리), V2(무리가 적을수록 통일), V10(대비가 낮으면 그림-바탕이 약해짐).

**[VL-15] 강한 명도 주목이 가장자리로 새지 않는가?**
- 측정: 재단선에서 60pt 띠(면적 비율 16.5%). 4모형마다 주목도 상위 5% 화소 가운데 띠 안 비율.
- 합격: 4모형 중 3개 이상에서 비율 ≤ 띠 면적 비율.
- 실패 시: minor
- 근거: V13(중앙 편향의 약 60%는 영상 내용으로 설명되지 않음 — 가장자리 강조는 그 편향을 거슬러 시선을 빼앗음), V17(포스터 응시 분포).

**[VL-16] 명도 무게가 균형을 이루고 영웅 칸에 모이는가?**
- 측정: 명도 무게 V = max(0, L\*_paper − L\*) (poster_1x). 좌/우 합의 비, 3×3 칸별 비율, 명도 무게중심.
- 합격: 좌/우 0.8~1.25, 가운데 칸이 9칸 중 최대, 무게중심이 프레임 중심(595.5, 842)에서 높이의 10%(168pt) 안 [운영값].
- 실패 시: minor
- 근거: V2(명도 무리의 배치가 디자인에 큰 영향), V1.
- 참고: LY-11은 종이와 다른 화소의 개수만 센다. 이 항목은 어두운 정도를 무게로 곱한다.

## C. 큰 면의 명도 관계

**[VL-17] 지도의 뼈대 면(땅/바다, 땅/강)이 휘도만으로 명도 한 단계 이상 갈리는가?**
- 측정: map_only 2x에서 경계 양쪽 면의 L\* 중앙값을 잰다. 바다(600–680 × 1600–1640), 땅(600–640 × 1100–1140), 강(262–280 × 1040–1060), 강가 땅(200–215 × 1040–1060).
- 합격: 두 쌍 모두 ΔL\* ≥ 10.
- 실패 시: ΔL\* < 5(사실상 등휘도)면 major / 5 ≤ ΔL\* < 10이면 minor [운영값]
- 근거: V3(등휘도 경계는 휘도 체계에서 사라지고 깊이·그림-바탕이 불안정해짐), V4, V5("흑백에서 먼저 맞게"), V20.

## D. 인쇄

**[VL-18] 인쇄(PSO Coated v3)로 모의해도 핵심 명도 차가 80% 이상 남는가?**
- 측정: 규약 9로 아래 11쌍의 ΔL\* 보존율(인쇄 후 ÷ 인쇄 전)을 잰다. 글 #2E2A22/땅, 큐브 오른면/왼면, 큐브 왼면/윗면, 콜로세움 그늘면/빛면, 콜로세움/산, 콜로세움/광장, 바다/땅, 탑 기초/중간, 골조/땅, #983821/땅, 나무/땅. 색 값은 렌더 실측 중앙값을 쓴다(R8: #2E2A22, #E2D7C2, #5F493D, #73594B, #8A6B5B, #9F7E5B, #AD8B65, #C3BDA5, #CDBD9E, #9CCACA, #575044, #9A8D76, #939798, #983821, #7E8E63).
- 합격: 11쌍 모두 보존율 ≥ 0.80 [운영값].
- 실패 시: major
- 근거: V19(FOGRA51, ISO 12647-2:2013, 톤값 증가 곡선 2013-A, 최대 면적 300%, K 96%), V11(인쇄물의 제한된 동적 범위).

---

## 출처 (실제로 열어 본 자료만)

| ID | 저자·연도 | 제목·매체 | 이 루브릭에서 쓴 내용 | URL |
|---|---|---|---|---|
| V1 | Berry, S. (2019), Dow, A. W. *Composition*(1899/1913) 해설 | A Reading Guide to Dow's "Composition", pt. 3 – Notan | 노탄 = 명암 덩어리의 배치("tone-composition"), 흑백으로 줄이기, 국소 대비로 명도 판단 | https://stephenberryart.com/blog/2019/2/23/a-reading-guide-to-dows-composition-pt-3-notan |
| V2 | Keister, D. (GVSU) | Design Principles in Art — Value Structure | 높은 조·낮은 조·중간 조·고대비, 같은 명도끼리 무리 짓기, 인접 명도 대비로 구조 가장자리 강조 | https://faculty.gvsu.edu/KEISTERD/design_principles_art/value_structure.html |
| V3 | *Harvard Magazine* (2003-07), M. Livingstone 연구 소개(*Vision and Art* 요지) | The Neurobiology of Art | 휘도 체계(Where)는 색맹으로, 깊이·공간을 맡는다. 등휘도 색은 떨리고 깊이가 사라진다. 음영이 입체감을 만든다 | https://www.harvardmagazine.com/2003/07/the-neurobiology-of-art-html |
| V4 | Stone, M. · Ware, C. (2009) | Colo(u)r in Information Display, SFU IAT 814 Week 3 강의 자료 | 적록·황청 채널의 공간 해상도는 흑백의 약 1/3, shape-from-shading은 되지만 shape-from-hue는 안 된다 | https://www.sfu.ca/siatclass/IAT814/Spring2009/Lectures/814week3A.pdf |
| V5 | Gossett, S. (2020-09-01), M. Stone 인터뷰 | Tableau's In-House Expert Discusses Color Accessibility for Data Viz. *Built In* | "get it right in black and white", "Luminance contrast manages attention even more than color" | https://builtin.com/data-science/dataviz-color-tableau |
| V6 | Itti, L., Koch, C., Niebur, E. (1998) | A model of saliency-based visual attention for rapid scene analysis. *IEEE TPAMI* 20(11):1254–1259 | I = (r+g+b)/3, 중심-주변 다중 척도, N() 연산자(강한 정점이 적은 지도를 키움), WTA, FOA 반지름 1/6 | https://hasler.ece.gatech.edu/Courses/MachineLearning/FoundationalPapers/Itti_Koch_Neiber1998.pdf |
| V7 | Schyns, P. G., Oliva, A. (1994) | From blobs to boundary edges. *Psychological Science* 5(4):195–200 | 거친 "덩어리"가 먼저 장면 인식을 시작하고, 세부가 뒤에 다듬음 | https://www.psychologicalscience.org/journals/psychological-science/j.1467-9280.1994.tb00500.x/ |
| V8 | Oliva, A., Torralba, A., Schyns, P. G. (2006) | Hybrid images. *ACM TOG* 25(3) (SIGGRAPH 2006) | 30ms에서는 저주파(8 cycles/image)를, 150ms에서는 고주파(24 cycles/image 이상)를 먼저 읽음. 저주파가 초기 처리를 지배 | https://wcours.gel.ulaval.ca/GIF4105/old/h23/tps/tp2/OlivaTorralb_Hybrid_Siggraph06.pdf |
| V9 | Fabrikant, S. I., Hespanha, S. R., Hegarty, M. (2010) | Cognitively Inspired and Perceptually Salient Graphic Displays for Efficient Spatial Inference Making. *Annals AAG* 100(1) | 주제 위계에 맞춘 시각 위계(그림-바탕), Itti 모형으로 지도 주목도를 미리 점검. 주목도 설계는 정확도가 아니라 응시 행동·응답 시간을 바꿈 | https://user.geo.uzh.ch/sfabri/pubs/fabrikant_etal_an09.pdf |
| V10 | Axis Maps | Cartography Guide — Visual Hierarchy | 대비가 낮을수록 그림-바탕·위계가 약해짐, 중요 요소는 특히 명도로 바탕과 달라야 함, 밝은 바탕에서는 어두운 것이 눈을 끎, 실눈·물러서기 시험 | https://axismaps.com/guide/visual-hierarchy |
| V11 | Graham, D. J., Field, D. J. (2008) | Variations in intensity statistics for representational and abstract art… *Perception* 37:1341–1352 | 그림의 동적 범위는 약 30:1, 장면은 1000:1 이상. 비선형 휘도 압축 | https://people.hws.edu/graham/Graham_perception08.pdf |
| V12 | Swartz, A., Skelton, A. E., Mather, G., Bosten, J. M., Maule, J., Franklin, A. (2024) | The perceived beauty of art is not strongly calibrated to the statistical regularities of real-world scenes. *Scientific Reports* 14:19368 | 휘도 대비(휘도 변화)가 아름다움 평가의 주요 예측 변수(통계량 전체로 설명량 6~15%) | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1038/s41598-024-69689-6&resultType=core |
| V13 | Kümmerer, M., Bethge, M., Wallis, T. S. A. (2022) | DeepGaze III. *Journal of Vision* 22(5):7 | 장면 내용이 응시 선택에 주는 영향이 응시 이력보다 큼. 중앙 편향의 약 60%는 내용으로 설명되지 않음 | https://pmc.ncbi.nlm.nih.gov/articles/PMC9055565/ |
| V14 | Chakraborty, S., Wei, Z., Kelton, C., Ahn, S., Balasubramanian, A., Zelinsky, G. J., Samaras, D. (2022/2024) | Predicting Visual Attention in Graphic Design Documents. *IEEE TMM* 25:4478–4493 (arXiv 2407.02439) | 구성 요소별 주목도와 응시 순서 예측, 포스터·만화·모바일 UI로 일반화 | https://arxiv.org/abs/2407.02439 |
| V15 | Aberman, K. 외 (2022) | Deep Saliency Prior for Reducing Visual Distraction. *CVPR 2022* (arXiv 2109.01980) | 방해물의 색을 주변과 맞추면(recolor) 그 영역의 주목도가 줄어듦 | https://arxiv.org/abs/2109.01980 |
| V16 | Miangoleh, S. M. H., Bylinskii, Z., Kee, E., Shechtman, E., Aksoy, Y. (2023) | Realistic Saliency Guided Image Enhancement. *CVPR 2023* (arXiv 2306.06092) | 노출·채도 같은 톤 편집으로 주제를 키우고 방해물을 줄여 시선을 유도 | https://arxiv.org/abs/2306.06092 |
| V17 | Jiang, Y., Leiva, L. A., Rezazadegan Tavakoli, H., Houssel, P. R. B., Kylmälä, J., Oulasvirta, A. (2023) | UEyes: Understanding Visual Saliency across User Interface Types. *CHI 2023* | 포스터는 왼쪽→오른쪽 훑기가 강하고, 글이 그림보다 시선을 잘 끈다 | https://arxiv.org/html/2402.05202v1 |
| V18 | Fosco, C. 외 (2020) | Predicting Visual Importance Across Graphic Design Types (UMSI). *UIST 2020* | 포스터·인포그래픽 중요도 예측(배경 근거) | https://arxiv.org/abs/2008.02912 |
| V19 | European Color Initiative (2015) | PSO Coated v3 — PSOcoated_v3_info.pdf | FOGRA51, ISO 12647-2:2013, 톤값 증가 곡선 2013-A, 최대 면적 300%, 최대 K 96% | https://www.eci.org/lib/exe/pso-coated_v3.zip |
| V20 | Wikipedia(2차 자료) | Lightness | Munsell 명도는 지각적으로 고른 명도 척도이며, Glasser 1958은 lightness를 Munsell 명도의 10배로 정의 | https://en.wikipedia.org/wiki/Lightness |

- 2022~2026 자료: V12(2024), V13(2022), V14(2022 저널 / 2024 arXiv), V15(2022), V16(2023), V17(2023) — 6개.
- 실눈 시험 자체를 검증한 동료 심사 연구는 찾지 못했다(실무 지침만 있음). 그래서 실눈 시험은 V7·V8의 거친 척도 우선 처리를 근거로 σ를 정하는 [운영값]으로만 쓴다.
