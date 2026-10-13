# 루브릭 · 컬러그래픽(색채) — 로마 콘크리트 A2 포스터

- 작성: 라운드 1 컬러 비평가 (2026-10-12). 라운드 2부터 이 문서를 고정해서 쓴다.
- 판정 단위: 항목마다 예/아니오. 아래 "측정 규약"을 그대로 따르면 누가 재도 같은 값이 나와야 한다.
- 고정 조건(BRIEF §3)은 감점하지 않는다. 특히 CORE ①~⑤의 번호 원판·밑줄·제목 둘째 줄이 모두 #983821인 것, 이정표 화살표 판이 ②색인 것, 클레이 디오라마 렌더 자체는 전제로 둔다.

## 0. 측정 규약 (모든 항목 공통)

1. **자료**: 글 대비는 `r<N>/poster_2x.png`(2382×3368, 1pt = 2px)로, 면적·색 통계는 `r<N>/poster_1x.png`로 잰다. 글의 위치·크기·색 지정값은 `text_spec_r<N>.json`을 쓴다. PNG에 ICC가 없으면 sRGB로 본다.
2. **글자 마스크와 "바로 뒤 배경"**: 글 상자(box)를 1pt 넓혀 자른다. 글 색 지정값의 상대휘도를 Yt, 상자 안 휘도 80백분위(밝은 글은 15백분위)를 Yb₀라 할 때 |Y − Yt| < 0.5·|Yb₀ − Yt| 이고 CIELAB ΔE76(픽셀, 글 색) < 40 인 픽셀이 글자다. 글자 마스크를 3px 넓힌 영역을 빼고 9px 넓힌 영역 안에 남는 **고리(ring)** 가 "바로 뒤 배경"이다(2배 이미지 기준, 1.5~4.5pt 둘레). 밝은 글(번호 숫자)은 고리 중 휘도 < 0.25인 원판 픽셀만 쓴다.
3. **대비 값**: 배경 대표값 = 고리 픽셀 RGB 중앙값. 글 색 = 지정 hex(측정 글자 가장 어두운 5% 평균과 다르면 둘 다 기록하고 낮은 쪽으로 판정). WCAG 2.2 대비비(상대휘도 공식)와 **APCA-W3 0.0.98G-4g Lc**(절댓값)를 모두 잰다. "최악 배경"은 고리 픽셀 각각과의 |Lc| 분포의 10백분위다.
4. **글 역할 분류**(text_spec id 기준):
   - CORE 본문: 790:148, 154, 160, 166, 172 (11.5pt Regular).
   - 큰 제목: 790:82(70pt), 790:86(20pt), CORE 제목 790:146·147·152·153·158·159·164·165·170·171(21pt Bold).
   - 번호 숫자: 790:102, 105, 106, 110, 111 (#FFF4DD on 원판).
   - 내용 글: 나머지 전부(≤13pt 라벨·지명·캡션·설명·소제목·기호 +/→).
5. **대비 미달 심각도(C 절 공통)**: WCAG가 기준 미만이면 blocker. APCA는 역할 기준값과의 부족분으로 정한다 — 부족 ≥ 10 Lc: blocker, 3 ≤ 부족 < 10: major, 부족 < 3: minor. (APCA 단계가 15 Lc 간격이므로 1/5 단계 미만은 다듬기로 본다.)
6. **색 공간**: CIELAB은 D65, CIEDE2000(ΔE00)은 Sharma 식. 색상각·채도는 Oklab/Oklch(Ottosson 2020)로 잰다. 영역 대표색은 그 영역 픽셀의 RGB 중앙값, "밝은 면"은 휘도 60~90백분위 평균.
7. **CVD 모의**: Machado 2009 행렬(심각도 1.0: protan·deutan·tritan)을 **선형 sRGB**에 곱한 뒤 다시 감마를 입힌다.
8. **구별 거리 D(Szafir 2018 정규화)**: Szafir 2018 표 1(점 표지)의 ND(50%) 값 — 0.25°: L 8.37, a 16.11, b 19.46 / 0.5°: L 6.74, a 9.98, b 13.34 / 2°: L 5.47, a 6.84, b 7.99 (ΔE76 단위). 판별률 p = m·ΔX 이므로 2·ND(50%)에서 p ≈ 1. D = √[(ΔL/2N_L)² + (Δa/2N_a)² + (Δb/2N_b)²], **D ≥ 1 이면 믿을 만하게 구별**. 크기: 9.5~13pt 글 = 0.25°, 20pt 이상 글 = 0.5°, 넓은 면·3D 물체 = 2°(관람 거리 1 m에서 12pt ≈ 0.25°).
9. **인쇄 왕복**: ECI `PSOcoated_v3.icc`(FOGRA51)로 sRGB → CMYK(상대 색도, 검정점 보정) → Lab(D50) 변환 후 원래 sRGB → Lab(D50)과 ΔE00을 잰다(Pillow ImageCms/LittleCMS).
10. 크기(글자 pt 자체)의 적정성은 타이포그래피 루브릭이 본다. 이 루브릭은 **역할별 대비 수준**만 본다.

## A. 팔레트 · 조화 · 응집

| ID | 질문(예 = 합격) | 측정 방법 · 합격 수치 | 실패 심각도 | 근거 |
|---|---|---|---|---|
| CL-01 | 바탕(종이·땅·산·돌)이 저채도 한 색상군으로 응집하는가? | poster_1x 픽셀 중 Oklch C ≤ 0.05 비율 ≥ 60% **그리고** 0.015 ≤ C ≤ 0.05 픽셀의 색상각 10~90백분위 폭 ≤ 25° | major | S8(조화는 색상 유사·저채도와 함께 오름), S14 |
| CL-02 | 유채 색상군 수가 절제되어 있는가? | C ≥ 0.05 픽셀을 15° 칸 히스토그램으로 묶고, 이웃 칸을 합친 색상군 중 포스터 면적 ≥ 0.3%인 군이 **≤ 5** | minor | S18(고유 특징만 즉시 튐), S5, S15(구별성·조화 상충) |
| CL-03 | 과채도 면이 없는가? | Oklch C > 0.15 픽셀 ≤ 0.5% | minor | S8, S13(색채감이 첫인상을 좌우, 집단별 고채도 비선호) |
| CL-04 | 강조색 면적이 희소하면서 보이는가? | 강조색 계열(Oklch h 20~48°, C ≥ 0.10) 픽셀 비율 0.1% ~ 10% (상한 10%는 실무 관행, 학술 근거는 고유 특징 원리) | minor | S18 |

## B. 색의 의미 부호화 (같은 색 = 같은 역할)

| ID | 질문(예 = 합격) | 측정 방법 · 합격 수치 | 실패 심각도 | 근거 |
|---|---|---|---|---|
| CL-05 | 강조색(#983821)이 CORE에만 쓰이는가? | ① text_spec에서 CORE 밖 글이 #983821(semantic/type_heat) 0개 ② CORE 요소(제목 둘째 줄·번호 원판·밑줄 상자 ±4pt, 이정표 화살표 3곳) 밖의 강조색 계열 픽셀(CL-04 정의) ≤ 0.01%(1x 기준 ≈ 200px). 의미가 같은 '열' 소품(≤ 50px)은 제외 | major | S18, S6(의미 판별성), S7(범례 없이도 색-의미를 추론) |
| CL-06 | 같은 정보 역할의 글이 같은 색 변수를 쓰는가? | text_spec에서 역할별 색 변수 수: DETAIL 제목, SUPPORT 제목, SUPPORT 소제목·본문, BASIC 라벨, 지명 라벨 각각 **1개**(물 위 대비 확보용 예외 1개 허용) | major | S6, S7, S15 |
| CL-07 | 개념 색을 입힌 글과 그 그림의 색이 맞물리는가? | 개념색 글(물=청록 #195B61, 칼슘=갈 #784C26, 열=적갈)이 붙은 그림 단계/사물 상자 안에 같은 색상군(색상각 ±20°, C ≥ 0.04) 픽셀이 ≥ 20px(1x) 존재하고, **다른 단계에만** 나타나지 않음 | major | S7, S6 |
| CL-08 | 3D 재질의 시대 색 부호가 일관적인가? | 로마 시대 사물의 대표색 Oklch h 30~110°(흙·돌·나무), 현대·오늘(철근 건물·실험실·연구 도구) h 190~260°(슬레이트). 반대 계열 사물 0개 | 1개 minor / 2개 이상이거나 CORE 그림이면 major | S7, S6 |
| CL-09 | 같은 물질은 같은 색상군인가? | 물 표현(강·바다·시편 수조·물방울) 대표색 색상각이 서로 ±15° 안, 강-바다 렌더 ΔE00 ≤ 3 | minor | S7, S4 |
| CL-10 | 물 색이 물의 개념 연상과 맞는가? | 강·바다 대표색 Oklch h 180~250° | major | S7, S19(자연색 지도 관례) |
| CL-11 | CORE 강조 요소(원판·화살표 판)가 실제로 같은 색으로 렌더되었는가? | 번호 원판 렌더 중앙값 ΔE00(#983821) ≤ 3, 이정표 화살표 밝은 면 ΔE00 ≤ 8 이고 색상각 차 ≤ 10° | minor | 고정 조건 5·6 이행 검증, S4 |
| CL-12 | 강조색과 같은 색상 범위의 비CORE 3D 물체가 정상 시각에서 강조색과 구별되는가? | h 20~48° 비CORE 물체(시편 정육면체 등) 대표색 ΔE00(#983821) ≥ 10 | major | S4, S18 |

## C. 글-배경 대비 (WCAG 2.2 + APCA)

| ID | 질문(예 = 합격) | 측정 방법 · 합격 수치 | 실패 심각도 | 근거 |
|---|---|---|---|---|
| CL-13 | CORE 본문이 본문 대비 기준을 넘는가? | 5개 모두 APCA \|Lc\| ≥ 75 **그리고** WCAG ≥ 4.5:1 (고리 중앙값 기준) | 규약 5 | S3(Lc 75 = 본문 최소), S1(1.4.3) |
| CL-14 | 내용 글(라벨·지명·캡션·설명·소제목)이 기준을 넘는가? | 모두 \|Lc\| ≥ 60 **그리고** WCAG ≥ 4.5:1 | 규약 5 | S3(Lc 60 = 본문 외 내용 글 최소), S1 |
| CL-15 | 큰 제목이 기준을 넘는가? | 모두 \|Lc\| ≥ 45 **그리고** WCAG ≥ 3:1 | 규약 5 | S3(Lc 45 = 크고 굵은 글), S1(큰 글 3:1) |
| CL-16 | 번호 원판 숫자가 기준을 넘는가? | 5개 모두 \|Lc\| ≥ 60 **그리고** WCAG ≥ 4.5:1 | 규약 5 | S3, S1 |
| CL-17 | 글자 일부가 3D 물체·질감 위에 걸려도 최악 배경에서 읽히는가? | 모든 글의 최악 배경(고리 \|Lc\| 10백분위) ≥ 45 | major | S17(배경 질감·RMS 대비가 읽기 속도를 떨어뜨림), S3 |
| CL-18 | 정보를 담은 비텍스트 요소가 바탕과 3:1 이상인가? | 지시선(점선 포함)·순서 화살표·하중 화살표·번호 원판: 선 위 2배 창에서 가장 어두운 3% 평균 vs 창 중앙값 WCAG ≥ 3:1. 같은 선이 땅·물 둘 다 지나면 구간별로 잰다 | major | S1(1.4.11) |
| CL-19 | 색만으로 전달하는 정보가 없는가? | 색으로 구별되는 모든 정보(CORE 1·2줄, 개념색 라벨, 땅/물 등)에 글·모양·위치 단서가 함께 있음 | blocker | S1(1.4.1, A 등급) |
| CL-20 | 렌더된 바탕이 토큰과 같아서 토큰 기준 대비가 유지되는가? | 렌더 종이 대표색(포스터 최빈 바탕) vs `background` 토큰 #F3E8D4 ΔE00 ≤ 3 | minor | S3(대비는 실제 배경 기준), 토큰 운용 |

## D. 색각이상(CVD) 안전성

| ID | 질문(예 = 합격) | 측정 방법 · 합격 수치 | 실패 심각도 | 근거 |
|---|---|---|---|---|
| CL-21 | 의미를 가르는 글 색 쌍이 세 CVD에서 모두 구별되는가? | 쌍: CORE 제목 1줄(#2E2A22)/2줄(#983821) [0.5°], 개념색 라벨 물/칼슘 [0.25°], 주제색 제목끼리 [0.25°], 강조 제목/본문 [0.25°]. 규약 7 모의 후 D ≥ 1 | 색만으로 구별하면 major, 글·위치 단서가 있으면 minor | S9, S4, S10, S2(적록 CVD 별도 요구 검토) |
| CL-22 | 큰 면·물체 쌍이 세 CVD에서 모두 구별되는가? | 쌍: 땅/바다, 강/길, 이정표 화살표/종이·길, 강조색/비CORE 적갈 물체, 현대 슬레이트/로마 황토 [모두 2°]. 모의 후 D ≥ 1 | 색만으로 구별하면 major, 아니면 minor | S9, S4, S10 |

## E. 인쇄 재현 (A2 오프셋/고급 출력, PSO Coated v3 = FOGRA51)

| ID | 질문(예 = 합격) | 측정 방법 · 합격 수치 | 실패 심각도 | 근거 |
|---|---|---|---|---|
| CL-23 | 의미 색(강조·물·주제 글 색·화살표 렌더색)이 인쇄 색역 안인가? | 규약 9 왕복 ΔE00 ≤ 3 | 3~5 minor, > 5 major | S16 |
| CL-24 | 포스터 전체가 인쇄 색역 안인가? | poster_1x 픽셀 중 왕복 ΔE00 > 5 비율 ≤ 1% | minor | S16 |
| CL-25 | 총잉크량이 인쇄 조건 안인가? | PSO Coated v3 변환 후 C+M+Y+K 최댓값 ≤ 300%, K ≤ 96% | major | S16(ECI: 최대 면적 300%, 최대 K 96%) |

## 참고 · 기록만 하는 값 (판정 없음)
- Hasler–Süsstrunk 색채감 M3 (Reinecke 2013의 색채감 지표 중 하나, S12). 첫인상 연구(S13)는 색채감이 인포그래픽 첫인상을 좌우하지만 집단별 선호가 갈림을 보였으므로 판정하지 않고 값만 남긴다.

## 출처 (실제로 열어 본 자료만)
- **S1** W3C (2024). *Web Content Accessibility Guidelines (WCAG) 2.2*, W3C Recommendation, 12 Dec 2024. SC 1.4.1, 1.4.3, 1.4.6, 1.4.11. https://www.w3.org/TR/WCAG22/
- **S2** W3C (2026). *WCAG 3.0*, W3C Working Draft, 10 Sep 2026 — 대비 알고리즘 미정(크기·굵기 요인 포함 전제), 적록 CVD 별도 요구 가능성 명시. https://www.w3.org/TR/wcag-3.0/
- **S3** Somers, A. / Myndex Perception Research (2022). *APCA in a Nutshell* (Lc 90·75·60·45·30·15 사용 수준). https://git.apcacontrast.com/documentation/APCA_in_a_Nutshell
- **S4** Szafir, D. A. (2018). Modeling Color Difference for Visualization Design. *IEEE TVCG* 24(1), 392–401 (IEEE VIS 2017). 표 1 ND(50%). https://cmci.colorado.edu/visualab/VisColors/ · PDF https://par.nsf.gov/servlets/purl/10074616
- **S5** Gramazio, C. C., Laidlaw, D. H., & Schloss, K. B. (2017). Colorgorical: Creating discriminable and preferable color palettes for information visualization. *IEEE TVCG* 23(1). https://schlosslab.discovery.wisc.edu/portfolio/color-preference
- **S6** Mukherjee, K., Yin, B., Sherman, B. E., Lessard, L., & Schloss, K. B. (2022). Context Matters: A Theory of Semantic Discriminability for Perceptual Encoding Systems. *IEEE TVCG* 28(1). https://arxiv.org/abs/2108.03685
- **S7** Schloss, K. B. (2024). Color semantics in human cognition. *Current Directions in Psychological Science* 33(1), 58–67. https://schlosslab.discovery.wisc.edu/new-publication-color-semantics-in-human-cognition
- **S8** Schloss, K. B., & Palmer, S. E. (2011). Aesthetic response to color combinations: preference, harmony, and similarity. *Attention, Perception, & Psychophysics* 73(2), 551–571. https://pmc.ncbi.nlm.nih.gov/articles/PMC3037488/
- **S9** Machado, G. M., Oliveira, M. M., & Fernandes, L. A. F. (2009). A Physiologically-based Model for Simulation of Color Vision Deficiency. *IEEE TVCG* 15(6), 1291–1298. https://www.inf.ufrgs.br/~oliveira/pubs_files/CVD_Simulation/CVD_Simulation.html
- **S10** Angerbauer, K., Rodrigues, N., Cutura, R., Öney, S., Pathmanathan, N., Morariu, C., Weiskopf, D., & Sedlmair, M. (2022). Accessibility for Color Vision Deficiencies: Challenges and Findings of a Large Scale Study on Paper Figures. *CHI '22*. DOI 10.1145/3491102.3502133 (자료 기록: 네 가지 CVD 모의, VIS30K, 연구자 4명 + 크라우드 200명 평가) https://b2find.eudat.eu/dataset/31156dd8-2e55-5829-be66-427cf7387f11
- **S11** Ottosson, B. (2020). A perceptual color space for image processing (Oklab). https://bottosson.github.io/posts/oklab/
- **S12** Reinecke, K., Yeh, T., Miratrix, L., Mardiko, R., Zhao, Y., Liu, J., & Gajos, K. Z. (2013). Predicting users' first impressions of website aesthetics with a quantification of perceived visual complexity and colorfulness. *CHI '13*, 2049–2058. https://wildlab.cs.washington.edu/Publications_files/Reinecke_CHI2013.pdf
- **S13** Harrison, L., Reinecke, K., & Chang, R. (2015). Infographic Aesthetics: Designing for the First Impression. *CHI '15* (참가자 1,278명, 인포그래픽 330개). https://wildlab.cs.washington.edu/Publications_files/Harrison_CHI2015.pdf
- **S14** Liu, S., Tao, M., Huang, Y., Wang, C., & Li, C. (2024). Image-Driven Harmonious Color Palette Generation for Diverse Information Visualization. *IEEE TVCG* 30(7), 3089–3103. https://pure.ecnu.edu.cn/en/publications/image-driven-harmonious-color-palette-generation-for-diverse-info/
- **S15** Chen, J., Yang, W., Jia, Z., Xiao, L., & Liu, S. (2024). Dynamic Color Assignment for Hierarchical Data. IEEE VIS 2024. https://arxiv.org/abs/2407.14742
- **S16** European Color Initiative (2015). *PSO Coated v3* 프로필 안내(FOGRA51, ISO 12647-2:2013, 최대 면적 300%, 최대 K 96%). https://www.eci.org/lib/exe/pso-coated_v3.zip (PSOcoated_v3_info.pdf) · https://print.app/resources/icc-profiles/pso-coated-v3
- **S17** Scharff, L. F. V., Ahumada, A. J., & Hill, A. L. (1999). Discriminability Measures for Predicting Readability. *SPIE Proc.* 3644 (Human Vision and Electronic Imaging). 배경 RMS 대비와 읽기 속도 r = −.78. https://laurenscharff.com/research/spie99.html
- **S18** Healey, C. G. *Perception in Visualization* (NC State, 웹 문서) — 고유한 시각 특징이 튀어나옴, 결합 표적은 즉시 찾지 못함, 색 거리·선형 분리·색 범주 통제 필요. https://www.csc2.ncsu.edu/faculty/healey/PP/
- **S19** Patterson, T., & Kelso, N. V. (2004). Hal Shelton Revisited: Designing and Producing Natural-Color Maps with Satellite Land Cover Data. *Cartographic Perspectives* 47, 28–55. https://cartographicperspectives.org/index.php/journal/article/view/cp47-patterson-kelso

2022~2026년 자료: S1, S2, S3, S6, S7, S10, S14, S15 (8개).
