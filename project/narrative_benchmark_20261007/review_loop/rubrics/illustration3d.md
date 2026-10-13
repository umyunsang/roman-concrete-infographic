# 루브릭 · 5 3D 일러스트·이미지 표현 (illustration3d)

- 대상: A2 세로 포스터(1191×1684pt, 1pt=1px=0.353mm), 관람 거리 0.5~1.5m. 배경 지도 = Blender 클레이 미니어처 디오라마 렌더(약간 플랫한 음영, 고정 조건).
- 고정 조건(BRIEF §3)은 감점하지 않는다: 동심원 배치, 클레이 디오라마 3D(2D 전환 금지), 이정표 3개(석회암 기둥 + #983821 화살표 판), 떠 있는 글 수평.
- 측정 도구: `r<N>/poster_2x.png`(2382×3368, pt×2), `r<N>/poster_1x.png`, `text_spec_r<N>.json`. 파이썬 예: `uv run --no-project --with pillow --with numpy --with scipy python -I …`.
- 공통 측정 정의
  - **L\***: sRGB → 선형 → Y → CIE L\*(D65). 면 색은 영역 median.
  - **바탕 L\***: 같은 높이 ±20pt 안의 빈 바닥 median(R1 기준 87~89).
  - **획 굵기**: 2x 이미지에서 단서 색 마스크의 가로 연속 화소 수 median ÷ 2(pt).
  - **시각 한계 환산**: 크기(mm) ÷ 거리(mm) × 3437.7 = arcmin. 1.5pt(0.53mm)는 1.5m에서 1.2′(정상 시력 한계 1′ 바로 위).
  - 판정은 예(합격)/아니오(불합격). 같은 원인의 불합격 항목이 여럿이면 지적은 하나로 묶는다(부풀리기 금지).
- 심각도: blocker = 객관적 겹침·가림·판독 불가·의미 오류 / major = 분명한 품질 저하 + 근거 문헌 / minor = 다듬기.

## A. 클레이 디오라마 스타일 일관성

**[I3-01] 같은 재질은 같은 색으로 렌더되는가?**
- 측정: 같은 재질 모형(③ 큐브, ④ 큐브 3개, 제작 원리 큐브, 재료 원리 큐브)의 윗면·왼면·오른면 중앙 median Lab. 같은 방향 면끼리 ΔL\* ≤ 3, Δh ≤ 5°면 합격.
- 실패 시: minor
- 근거: S2(심벌화 단계의 색·밝기·질감 속성 통일), S15·S17(질감-형상 일관성 평가축)

**[I3-02] 음영이 중간 톤 안에 머무는가(먹색 뭉개짐 없음)?**
- 측정: text_spec 글 상자(+4pt, 기운 글은 +15pt)를 뺀 영역에서 물체 화소(L\*<84) 중 L\*<20 비율. ≤ 2%면 합격.
- 실패 시: minor
- 근거: S7(음영은 중간 톤, 극단 명암은 윤곽·하이라이트에만)

**[I3-03] 곡면 물체가 같은 추상화 수준(매끈한 클레이)으로 렌더되는가?**
- 측정: 2x 이미지 4배 확대로 곡면(돔·지붕·원뿔)에 직선 경계의 평면 패싯이 보이고 인접 패싯 ΔL\* ≥ 5인 물체 수. 0개면 합격.
- 실패 시: minor(배경 물체) / major(CORE·영웅 물체)
- 근거: S4(LoA 일관), S3(3D 지도는 추상화·일반화 규칙을 따름), S17(형상 품질)

**[I3-04] 의미 색 부호(로마=따뜻한 흙색, 현대=차가운 회청)가 지켜지는가?**
- 측정: 현대 물체(① 철근 골조, 오늘의 실험실) 벽면 Lab의 색상각 h 150~260° 또는 채도 C ≤ 6, 로마 물체(콜로세움·폼페이·이정표 기둥·프리베르눔) h 40~100°. 모두 맞으면 합격.
- 실패 시: minor
- 근거: S2(색을 시각 변수로), S4(주제 정보의 선택적 양식화)

## B. 물체 간 스케일

**[I3-05] 한 장면 안 성인 인물의 크기가 같은가?**
- 측정: 같은 받침 위 인물의 머리 꼭대기~발끝(pt), 머리 폭(pt). 큰 쪽/작은 쪽 ≤ 1.15면 합격(카메라는 평행 투영에 가까움: 이정표 3개 높이에 깊이 의존성 없음으로 확인).
- 실패 시: major
- 근거: S19(그림 단서가 지각된 크기·축척을 결정), S15·S17(3D 그럴듯함)

**[I3-06] 이정표 3개가 같은 축척인가?**
- 측정: 기둥 꼭대기~받침 바닥 높이(pt). 평균 대비 편차 ≤ ±10%면 합격.
- 실패 시: minor
- 근거: S2(같은 부류 심벌 크기 통일)

**[I3-07] 축척 위계가 정보 위계와 맞는가?**
- 측정: 외곽 상자 면적 순위가 콜로세움(영웅) > CORE 모형 최댓값 ≥ DETAIL 모형 최댓값. 맞으면 합격.
- 실패 시: major
- 근거: S5(랜드마크 아이콘화), S3(Near-Far/Distance-Density)

**[I3-08] 인물과 건축의 비가 그럴듯한가?**
- 측정: 같은 장면 안 아치·문 개구부 높이 ÷ 인물 키 ≥ 1.2면 합격.
- 실패 시: minor
- 근거: S19, S16(다물체 장면 일관성 약점)

## C. 조명·그림자·접지

**[I3-09] 주광 방향이 모든 상자형 모형에서 같은가?**
- 측정: 상자형 모형 ≥ 5개의 같은 재질 면 L\* 순서(윗면 > 왼면 > 오른면 또는 공통 순서). 일치율 100%면 합격.
- 실패 시: major
- 근거: S13(사람은 국소 조명 불일치를 잘 못 잡지만, 같은 모양 반복 물체에서는 드러남), S14(물체-그림자 관계는 기하 타당성 검사 단서)

**[I3-10] 지형(산·화산)의 높낮이가 음영만이 아니라 실루엣으로 고정되는가(음영 반전 위험 없음)?**
- 측정: 산 덩어리·화산마다 윗변 윤곽이 빈 바탕과 맞닿아 있는지(겹친 물체 없이 ΔL\* ≥ 8). 맞닿은 산 비율 ≥ 80%면 합격.
- 실패 시: major
- 근거: S10·S11(음영이 주 단서일 때 225°(왼쪽 아래) 빛에서 지형 반전 최다, NNW 337.5° 권장), S6(파노라마 지도의 그림자·명암은 해석을 흐릴 수 있음)

**[I3-11] 그림자 표현이 물체 부류 사이에 일관되는가?**
- 측정: 높이 ≥ 30pt 독립 물체의 그늘 쪽 바닥 1~15pt 거리 L\*와 바탕 L\* 차. 선명한 그림자(ΔL\* ≥ 5)를 가진 부류와 그림자 0(ΔL\* < 1)인 부류가 섞이지 않으면 합격.
- 실패 시: minor
- 근거: S12(그림자가 접지 판단을 지배), S14

**[I3-12] 바닥에 서야 할 물체가 모두 접지되어 보이는가?**
- 측정: (a) 밑동 3pt 안 바닥 어둡기 ΔL\* ≥ 3, (b) 밑면이 보이며 바닥과 띄워진 물체 0개(의도된 인셋 표시가 없을 때). 둘 다 맞으면 합격.
- 실패 시: minor(광학 접촉은 있음) / major(의도 표시 없는 떠 있음 2개 이상)
- 근거: S12(그림자 있으면 "떠 있음" 응답 거의 없음, 그림자 없으면 타일 바닥에서도 접촉 판단 약 60%), S19

## D. 실루엣·식별

**[I3-13] 랜드마크가 실루엣만으로 구별되는가?**
- 측정: 콜로세움·화산·등대·수도교·이정표 외곽선 안팎 2~10pt 영역 median의 ΔL\* ≥ 10 또는 ΔE76 ≥ 25(물 위 물체처럼 색상 대비로 갈리는 경우), 외곽선 윗변이 다른 물체와 겹치지 않음. 모두 맞으면 합격.
- 실패 시: major
- 근거: S18(투영 면적·실루엣 길이가 좋은 시점 판단의 핵심 속성), S5

**[I3-14] 정체가 모호한 물체가 이름표 없이 놓여 있지 않은가?**
- 측정: 일반 지물(나무·밭·길·산·물)을 뺀 3D 물체 중 40pt 안에 이름표·지시선이 없고 실루엣이 로마 시대 사물로 특정되지 않는 물체 수. 0개면 합격.
- 실패 시: major(CORE 인접 또는 면적 ≥ 5,000pt²) / minor(그 밖)
- 근거: S15·S16·S17(글-자산 의미 정렬), S5(랜드마크 아이콘화), S2(심벌 해석 가능성)

**[I3-15] 전경-배경 위계가 맞는가?**
- 측정: CORE·DETAIL 모형 대표면 L\*와 주변 바탕의 ΔL\* ≥ 10(또는 ΔE76 ≥ 25), 배경 지물(밭)의 ΔL\*는 CORE 최솟값 이하. 맞으면 합격.
- 실패 시: major
- 근거: S4(중요 정보 강조·덜 중요한 정보 걸러냄), S6(과잉 디테일은 해석 방해)

## E. 지형·물·길(3D 지도 지도학)

**[I3-16] 도로가 막다른 곳 없이 이어지는가?**
- 측정: 모든 도로 끝이 (a) 다른 도로, (b) 목적지 물체(이정표·건물·다리·항구), (c) 도판 가장자리 중 하나에 5pt 안으로 닿는가. 막다른 끝 0개면 합격.
- 실패 시: major
- 근거: S3(지도 규칙: 일반화·심벌화), S2(지도 모형의 논리)

**[I3-17] 이정표가 길가에 서 있는가?**
- 측정: 이정표 받침 외곽과 가장 가까운 도로 가장자리 거리 ≤ 10pt. 3개 모두면 합격.
- 실패 시: major(고정 조건 6의 '로마 가도 이정표' 의미가 깨짐)
- 근거: BRIEF 고정 조건 6, S5

**[I3-18] 강이 자연스러운 곳에서 시작하고 하류로 넓어지는가?**
- 측정: (a) 강 머리가 도판 가장자리·산 뒤·수원 표시 중 하나에 닿음, (b) y 100pt 간격 폭이 하류로 감소하지 않음(±10% 허용), (c) 하구가 바다에 닿음. 모두 맞으면 합격.
- 실패 시: minor
- 근거: S6(파노라마 화가의 지형·물 묘사 관례), S3

**[I3-19] 물(강·바다) 표현이 일관되는가?**
- 측정: 강 하류와 바다의 median 색 ΔE76 ≤ 3, 물결·흐름 기호가 흰색 계열로 통일. 맞으면 합격.
- 실패 시: minor
- 근거: S2, S6

**[I3-20] 3D 지물이 글과 겹치지 않는가?**
- 측정: text_spec 글 상자 안팎에서 글자 획 화소(L\*<45)와 3D 지물 화소(55 ≤ L\* < 84)의 최소 거리. 모든 글 상자에서 ≥ 4pt면 합격(글자 획이 지물 위에 얹히면 즉시 불합격).
- 실패 시: blocker(겹침)
- 근거: BRIEF §6(겹침=blocker), S1·S2(3D 지도의 글·지물 배치), S6

## F. 메시 결함

**[I3-21] 잔여·파편 메시가 없는가?**
- 측정: 2x 4배 확대로 (a) 폭 < 2pt이고 본체와 떨어진 조각, (b) 물체 밑으로 번진 바닥 잔여면, (c) 바닥이 비치는 구멍(주변 면보다 L\* +8 이상 밝은 화소 덩어리 ≥ 20pt²) 수. 0개면 합격.
- 실패 시: major(영웅·CORE 물체) / minor(그 밖)
- 근거: S17(형상 일관성 평가), S15, S16(품질·시점 불일치 검출)

**[I3-22] 관통·의도치 않은 잘림이 없는가?**
- 측정: 물체끼리 연결부 없이 뚫고 지나가는 곳, 도판 가장자리·제목판에 잘린 랜드마크 수(지도 연속을 뜻하는 밭·수도교·길의 가장자리 이탈은 제외). 0개면 합격.
- 실패 시: major
- 근거: S14(기하 오류 검출 단서), S17

## G. 원리 모형 형태 명료성

**[I3-23] ③ 석회 알갱이 확대 모형이 알갱이를 분명히 보여주는가?**
- 측정: 보이는 면의 흰 알갱이 ≥ 5개, 지름 ≥ 3pt, 갈색 면과 ΔL\* ≥ 40. 맞으면 합격.
- 실패 시: major
- 근거: S8(보여야 할 표적 구조를 드러내는 도해), S7

**[I3-24] ④ 균열 3단계 모형의 단계별 단서가 이름표와 1:1로 맞는가?**
- 측정: 이름표(물이 스밈 625~693 / 칼슘 이동 698~766 / 결정 충전 771~839pt) 위 큐브마다 그 단계만의 새 단서(1 물=청록 물방울·물 채움, 2 칼슘=흰 알갱이에서 틈으로 흰 줄, 3 결정=흰 충전)가 그 큐브 외곽 ±10pt 안에 있는가. 3단계 모두 맞으면 합격.
- 실패 시: major
- 근거: S8(구조의 순서·관계를 드러내는 도해 관례), S15(의미 정렬)

**[I3-25] 구조 모형의 재료 무게가 명도 단계로도 읽히는가?**
- 측정: 같은 면(왼면)에서 가벼운 벽돌 → 중간 돌 → 무거운 돌 → 기초 L\*가 단조 감소, 인접 단계 ΔL\* ≥ 8. 맞으면 합격.
- 실패 시: minor
- 근거: S2(밝기를 순서 변수로), S7

**[I3-26] 핵심 현상 단서가 관람 거리에서 보이는가?**
- 측정: CORE ①~⑤ 이미지와 DETAIL 원리 모형의 핵심 현상(① 금, ② 열, ③ 흰 알갱이, ④ 물·칼슘·결정, ⑤ 시편의 금·누수, 제작 원리의 열) 단서가 존재하고 획 ≥ 1.5pt, 주변과 ΔL\* ≥ 20(색만 다를 땐 ΔE76 ≥ 30). 모두 맞으면 합격.
- 실패 시: major
- 근거: 시각 한계 1′(S20) × 관람 거리 1.5m → 0.44mm(1.25pt), S8, S7

**[I3-27] 재료 원리(해수 속 새 결정) 모형의 결정·바닷물이 읽히는가?**
- 측정: 결정 바늘 밑동 폭 ≥ 2pt·L\* ≥ 80, 바닷물 면(청록)이 보이고 지시선이 바늘·물에 각각 닿음. 맞으면 합격.
- 실패 시: minor
- 근거: S8, S2

## H. 이정표·인물 장면

**[I3-28] 이정표 화살표 판의 색·방향이 맞는가?**
- 측정: 화살표 판 붉은 화소 밝기 상위 10% 색과 #983821의 ΔE76 ≤ 10, 화살표 방향과 '다음 CORE 제목 중심' 방향의 각도 차 ≤ 45°. 3개 모두면 합격.
- 실패 시: major
- 근거: BRIEF 고정 조건 5·6, S2

**[I3-29] 인물 장면의 동작이 판독되는가?**
- 측정: 인물 키 ≥ 18pt, 손·도구(물동이·삼각대 등) 중 하나 이상이 인물 실루엣 밖으로 2pt 이상 드러남. 모든 인물 장면에서 맞으면 합격.
- 실패 시: minor
- 근거: S18(실루엣 길이·투영 면적), S19

## 출처(실제로 연 자료)

| ID | 저자·연도 | 제목·학회/저널 | URL |
|---|---|---|---|
| S1 | Häberling, Bär, Hurni 2008 | Proposed Cartographic Design Principles for 3D Maps. *Cartographica* 43(3):175–188 (서지 확인) | https://signal.sciencespo-lyon.fr/article/520044 |
| S2 | Santos, Delazari, Brandalize 2013 | Projeto cartográfico para representação tridimensional de redes de energia. *Bol. Ciênc. Geod.* 19(2):247–267 (Häberling의 모델링→심벌화(형태·크기·색·밝기·질감·선명도·투명도)→시각화(조명·음영) 3단계 요약) | https://www.redalyc.org/pdf/3939/393937730006.pdf |
| S3 | Sieber, Eichenberger, Hurni 2019 | 3D Carto-Graphics – Principles, Methods and Examples for Interactive Atlases. *Abstracts of the ICA* 1:338 (실감 정도, Near-Far/Distance-Density, "3D 지도는 사실 재현이 아니라 추상화·심벌화·일반화") | https://www.research-collection.ethz.ch/server/api/core/bitstreams/f69b41a2-2c66-4f1d-add0-93a2a49b9fff/content |
| S4 | Semmo, Hildebrandt, Trapp, Döllner 2012 | Concepts for Cartography-Oriented Visualization of Virtual 3D City Models. *PFG* 2012(4):455–465 (LoA, 일반화 연산, 윤곽 강조, "NPR만으로는 지도 설계가 빠진 단조로운 결과") | https://www.dgpf.de/pfg/2012/pfg2012_4_Semmo.pdf |
| S5 | Semmo, Trapp, Jobst, Döllner 2015 | Cartography-Oriented Design of 3D Geospatial Information Visualization – Overview and Techniques. *ICC 2015* (3D 랜드마크 아이콘화) | https://icaci.org/files/documents/ICC_proceedings/ICC2015/papers/31/34.html |
| S6 | Jenny & Jenny 2013 | Challenges in adapting example-based texture synthesis for panoramic map creation: a case study. *CaGIS* (doi 10.1080/15230406.2013.795001) (과잉 디테일·그림자·색 흔들림은 해석을 흐림, 거리·조명에 따른 묘사 변화) | https://mail.colororacle.org/berniejenny/pdf/2013_Jenny_TextureSynthesisForPanoramicMaps.pdf |
| S7 | Gooch, Gooch, Shirley, Cohen 1998 | A Non-Photorealistic Lighting Model for Automatic Technical Illustration. *SIGGRAPH 98* | https://users.cs.northwestern.edu/~ago820/SIG98/abstract.html |
| S8 | Li, Ritter, Agrawala, Curless, Salesin 2007 | Interactive Cutaway Illustrations of Complex 3D Models. *ACM TOG* 26(3) (SIGGRAPH 2007) | https://grail.cs.washington.edu/projects/cutaways |
| S10 | Çöltekin, Rautenbach, Coetzee, Mokwena 2018 | Landform perception accuracy in shaded relief maps: NNW better than NW. *ISPRS Archives* XLII-4:101–106 (Biland & Çöltekin 2017, CaGIS 44(4) 재현) | https://isprs-archives.copernicus.org/articles/XLII-4/101/2018/ |
| S11 | Gołębiowska, Kennelly, Karsznia, Çöltekin, Trantham, Borczon 2025 | Mitigating relief inversion illusion with multidirectional sky illumination model: A user study. *Abstracts of the ICA* 10:92 (ICC 2025) (225° 빛에서 반전 최다, 다방향 하늘광이 완화) | https://ica-abs.copernicus.org/articles/10/92/2025/ica-abs-10-92-2025.pdf |
| S12 | Cooper, Casati, Farid, Cavanagh 2023 | The art of the float. *Journal of Vision* 23(8):13 | https://pmc.ncbi.nlm.nih.gov/articles/PMC10434713/ |
| S13 | Ostrovsky, Cavanagh, Sinha 2005(메모 2001) | Perceiving illumination inconsistencies in scenes. *Perception* 34:1301–1314 / MIT AI Memo AIM-2001-029 | https://dspace.mit.edu/handle/1721.1/7243 |
| S14 | Sarkar, Mai, Mahapatra, Lazebnik, Forsyth, Bhattad 2024 | Shadows Don't Lie and Lines Can't Bend! Generative Models don't know Projective Geometry…for now. *CVPR 2024* (arXiv 2311.17138) | https://arxiv.org/abs/2311.17138 |
| S15 | Wu, Yang, Li, Zhang, Liu, Guibas, Lin, Wetzstein 2024 | GPT-4V(ision) is a Human-Aligned Evaluator for Text-to-3D Generation (GPTEval3D). *CVPR 2024*:22227–22238 | https://mlanthology.org/cvpr/2024/wu2024cvpr-gpt4v/ |
| S16 | He, Bai, Lin, Zhao, Hu, Sheng, Yi, Li, Liu 2023 | T³Bench: Benchmarking Current Progress in Text-to-3D Generation. arXiv 2310.02977 (다물체·주변 장면 생성이 공통 약점) | https://arxiv.org/abs/2310.02977 |
| S17 | Duggal, Hu, Michel, Kembhavi, Freeman, Smith, Krishna, Torralba, Farhadi, Ma 2025 | Eval3D: Interpretable and Fine-grained Evaluation for 3D Generation. *CVPR 2025* | https://arxiv.org/abs/2504.18509 |
| S18 | Secord, Lu, Finkelstein, Singh, Nealen 2011 | Perceptual Models of Viewpoint Preference. *ACM TOG* 30(5) | https://gfx.cs.princeton.edu/pubs/Secord_2011_PMO/ |
| S19 | Held, Cooper, O'Brien, Banks 2010 | Using Blur to Affect Perceived Distance and Size. *ACM TOG* 29(2) | https://history.siggraph.org/?p=123134 |
| S20 | Wikipedia(2차 자료) | Visual acuity — 20/20 시력의 임계 간격 1′ | https://en.wikipedia.org/wiki/Visual_acuity |

- 2022~2026 자료: S11(2025), S12(2023), S14(2024), S15(2024), S16(2023), S17(2025) — 6개.
- S9(Biland & Çöltekin 2017, CaGIS 44(4):358–372)는 원문을 열지 못해 S10·S11의 인용으로만 쓴다.
