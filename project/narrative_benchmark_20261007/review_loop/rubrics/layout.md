# 루브릭 · 레이아웃·구성 (Layout & Composition)

- 대상: A2 세로 인쇄 포스터 1191×1684pt(1pt = 1px@1x = 0.353mm). 자료는 `r<N>/poster_2x.png`(1pt = 2px)와 `text_spec_r<N>.json`.
- 판정은 항목마다 **예(합격) / 아니오(불합격)**. 불합격이면 적힌 심각도를 쓴다. 같은 원인의 불합격 여러 개는 리포트에서 지적 하나로 묶는다(부풀리기 금지).
- **고정 조건(BRIEF §3)은 감점하지 않는다**: 동심원 배치 자체, 반시계 순서 자체, 표·격자 레이아웃 금지, 기운 지명, 이정표 3개, ②색 통일, 배경판 없음. 이 틀 *안에서의* 실행 품질만 잰다.
- 수치 기준 중 문헌이 직접 준 값은 [문헌값], 문헌 원리를 이 포스터에 맞춰 재현 가능하게 바꾼 값은 [운영값]으로 표시한다.

## 공통 측정 절차 (모든 항목이 같은 방법을 쓴다)
- **잉크(글자) 화소**: 2x 이미지에서 명도 L = 0.299R+0.587G+0.114B < 140(빨강 제목·밑줄은 R−G > 40 & R > 100 & L < 170). 잉크 범위 = 글 상자 안 잉크 화소의 최소·최대 좌표 ÷ 2.
- **물체 화소**: 잉크를 4px(2pt) 팽창한 마스크 밖에서, 중앙차분 명도 기울기 > 12 이거나 주변 종이색과 RGB 거리 > 28인 화소. 종이색 = 상자 주변 30px 고리의 밝은 60% 화소 중앙값.
- **콜로세움 중심** C = (584, 783)pt(외곽 실루엣 x 368~800, y 580~985의 중앙). 각도는 수학 좌표(오른쪽 0°, 위쪽 90°, 반시계 +).
- **블록 중심**: CORE는 번호 원판·제목 두 줄·본문을 합친 text_spec 상자의 중심. DETAIL은 설명 글 상자와 짝 모형 외곽을 합친 상자의 중심.
- 픽셀 측정 스크립트는 `uv run --no-project --with pillow --with numpy python -I`로 돌린다.

---

## A. 겹침·여유 (가림이 없어야 읽힌다)

**[LY-01] 글과 지도 물체가 겹치지 않는가?**
- 측정: 모든 수평 글 상자(CORE·DETAIL·SUPPORT·BASIC·캡션)에 대해, 잉크 화소의 행 범위 × 글자 열 범위 안에 물체 화소(길 돌판·밭판·모형·강·물결)가 있는지 2x에서 행 단위로 본다(글자 위로 물체 질감이 지나가면 겹침).
- 합격: 겹친 글자 0개.
- 불합격 심각도: **blocker** (BRIEF: 겹침).
- 근거: Imhof 1975의 라벨 원칙(가독·대상 연결·다른 요소와 겹침 회피) 및 van Dijk 1999 '라벨 가시성 = 겹치지 않은 글 면적 비율'(Kern & Brewer 2008 정리); Hsu et al. 2023 PosterLayout Occ·Ove 지표.

**[LY-02] 글 잉크와 가장 가까운 물체 사이에 3pt 이상 여유가 있는가?** (LY-01을 통과한 글에 적용)
- 측정: 모든 수평 글(CORE·DETAIL·SUPPORT·캡션) 잉크 범위의 각 줄 끝·위아래와, 가장 가까운 물체 화소(길·밭판·모형·물결 무늬) 사이 수평·수직 거리. 라벨이 *자기* 물체를 가리키는 지명(예: 아피아 가도 ↔ 길)도 3pt 규칙은 같다.
- 합격: ≥ 3pt(본문 11.5pt의 약 ¼em) [운영값].
- 불합격 심각도: **major** (0~3pt 접촉은 글자가 물체 일부로 읽힘).
- 근거: Imhof 1975(Kern & Brewer 2008), Wagemans et al. 2012 균일 연결성(uniform connectedness: 맞닿은 영역은 한 단위로 묶임).

**[LY-03] CORE·DETAIL 본문 밑 바탕이 평탄한가?**
- 측정: 본문 상자(±1pt) 안 비잉크 화소(잉크 4px 팽창 밖)의 명도 분포. ① 질감 화소(기울기 > 12) 비율, ② 명도 p95 − p5.
- 합격: 질감 ≤ 0.5% 그리고 p95 − p5 ≤ 15 [운영값].
- 불합격 심각도: **minor** (대비 수치 자체는 위계·접근성 분야가 판정).
- 근거: Hsu et al. 2023 PosterLayout Rea(글 밑 영역의 비평탄도), Seol et al. 2024 PosterLlama(가독성 = 글 영역의 기울기 변화).

**[LY-04] 글 상자끼리 겹치지 않는가?**
- 측정: text_spec 수평 글 상자 쌍의 교집합 면적.
- 합격: 모든 쌍 0 (번호 원판 숫자와 원판은 제외).
- 불합격 심각도: **blocker**.
- 근거: Hsu et al. 2023 Ove(요소 쌍 IoU 평균); Haraguchi et al. 2024(겹침 원칙).

## B. 묶임(게슈탈트) — 글-물체 짝과 블록의 결속

**[LY-05] 지시선 없는 라벨이 자기 물체에 더 가까운가?**
- 측정: 지시선 없는 DETAIL·SUPPORT·캡션 라벨마다 d_own = 라벨 잉크 상자 ↔ 자기 모형 외곽 최단 거리, d_other = 라벨 ↔ 다른 *정보 물체*(라벨이 붙은 모형·랜드마크, 다른 글 블록) 최단 거리. 밭판·나무 같은 배경 소품은 경쟁 물체에서 뺀다.
- 합격: 모든 라벨에서 d_other / d_own ≥ 1.5 [운영값].
- 불합격 심각도: **major**.
- 근거: Kubovy, Holcombe & Wagemans 1998(근접 묶임 강도는 경쟁 배열 간 *상대 거리*의 지수 감소 함수, pure distance law); Wagemans et al. 2012.

**[LY-06] 지시선 라벨의 연결이 짧고 깨끗한가?**
- 측정: 점선 지시선 길이(라벨 잉크 끝 ↔ 물체 끝점), 지시선이 다른 글·물체를 가로지르는지.
- 합격: 길이 ≤ 60pt, 가로지름 0 [운영값].
- 불합격 심각도: **minor**.
- 근거: Wagemans et al. 2012(연결성은 근접을 보완하는 묶임 원리); Kern & Brewer 2008(Imhof: 이름과 대상의 가장 가까운 연결).

**[LY-07] CORE 블록 안 간격보다 블록 바깥 여백이 충분히 큰가?**
- 측정: g_in = 블록 안 최대 간격(제목1↔제목2↔밑줄↔본문, 잉크 기준), g_out = 블록 잉크 외곽에서 가장 가까운 *다른 묶음*(다른 글 블록, 이정표, 라벨·설명이 붙은 남의 모형)까지 거리. 블록 자기 삽화(예: ②의 섞는 장면)와 길·밭판·나무 같은 지도 바탕 요소는 빼고 잰다(바탕 요소와의 충돌은 LY-01·02가 판정).
- 합격: 다섯 CORE 모두 g_out / g_in ≥ 1.5 [운영값].
- 불합격 심각도: **major**.
- 근거: Kubovy et al. 1998; Lu et al. 2020 VIF(그룹 안 근접 + 그룹 간 규칙성으로 정보 흐름을 추적).

## C. 동심원 구성과 균형 (고정 조건의 *실행* 품질)

**[LY-08] 같은 방향에서 CORE가 DETAIL보다 콜로세움에 가까운가?**
- 측정: C 기준 각 블록 중심의 거리 r와 각도 θ. 각 DETAIL에 대해 각도 차 ≤ 35°인 CORE와 r를 비교.
- 합격: 모든 짝에서 r_CORE < r_DETAIL.
- 불합격 심각도: **major** (교수 지정 동심원 원칙의 실행 실패).
- 근거: Lu et al. 2020 VIF 'star' 패턴(중심 물체 주위에 그룹을 펼침, 원형 배치의 방사 균형); BRIEF §3-1.

**[LY-09] CORE 고리가 고른가?**
- 측정: 다섯 CORE 중심 거리 r의 변동계수 CV = σ/μ.
- 합격: CV ≤ 0.25 [운영값].
- 불합격 심각도: **minor**.
- 근거: Lu et al. 2020(Regularity: 그룹 간 규칙성 점수, 원형 흐름은 원주를 등뼈로 씀).

**[LY-10] 콜로세움이 중심 초점으로 우세한가?**
- 측정: 콜로세움 외곽 상자 면적 vs 다른 단일 물체 최대 면적; 콜로세움 중심이 지도 영역(헤더 아래 ~ 해안선 위)의 가운데 1/3 상자 안인지.
- 합격: 면적비 ≥ 2, 가운데 1/3 안.
- 불합격 심각도: **major**.
- 근거: Bylinskii et al. 2017(크고 중앙인 요소가 중요하게 지각됨); Fosco et al. 2020 UMSI.

**[LY-11] 좌우 시각 무게가 균형인가?**
- 측정: 지도 영역에서 종이색과 RGB 거리 > 28인 화소 수를 좌(x < 595.5)·우로 나눠 비율 L/R.
- 합격: 0.8 ≤ L/R ≤ 1.25 [운영값].
- 불합격 심각도: **minor**.
- 근거: Lu et al. 2020(VIF 패턴 대부분 대칭·방사 균형); Haraguchi et al. 2024(배치 평가 원칙).

## D. 시선 흐름 (반시계 고리)

**[LY-12] ①→⑤ 각도가 한 방향(반시계)으로 단조 증가하고, 흐름이 스스로 교차하지 않는가?**
- 측정: CORE 중심 θ①…θ⑤ (반시계 +).
- 합격: θ가 엄격히 증가(누적 회전 < 360°), 인접 CORE 연결선끼리 교차 0.
- 불합격 심각도: **major**.
- 근거: Lu et al. 2020(디자이너는 정보 흐름의 교차·먼 도약을 피함).

**[LY-13] 한 번에 뛰는 거리가 고른가?**
- 측정: 인접 CORE 중심 간 거리 4개(①②, ②③, ③④, ④⑤).
- 합격: 최댓값 ≤ 1.5 × 중앙값, 그리고 어떤 연결선도 다른 CORE 블록 상자를 지나지 않음 [운영값].
- 불합격 심각도: **major**.
- 근거: Lu et al. 2020(long-distance jump 회피).

**[LY-14] 기본 방향(시계)과 반대인 반시계 흐름을 명시 단서가 받쳐 주는가?**
- 측정: 거리 > 250pt인 CORE 전환마다 이정표가 (a) 두 블록 중심을 잇는 선에서 120pt 안, (b) 화살 방향이 다음 블록 방향 벡터와 ±45° 안.
- 합격: 해당 전환 모두 (a)·(b) 충족.
- 불합격 심각도: **major**.
- 근거: Lu et al. 2020 — 명시 단서가 없으면 방사 배치는 *시계 방향*으로 읽는다고 가정(가장 흔한 읽기 순서). BRIEF §3-6(이정표 형태는 고정).

**[LY-15] 번호 원판이 다섯 CORE에서 같은 자리에 있는가?**
- 측정: text_spec에서 (원판 숫자 x − 제목1 x), (원판 숫자 y − 제목1 y), (제목1 x − 제목2 x).
- 합격: 세 값 각각 다섯 블록 간 범위 ≤ 1pt.
- 불합격 심각도: **minor**.
- 근거: Wagemans et al. 2012(유사성 묶임); Lu et al. 2020(그룹 간 유사성으로 흐름 연결).

## E. 반복 모듈의 간격·규칙 일관성

**[LY-16] CORE 다섯 블록의 수직 리듬이 같은가?**
- 측정: 잉크 기준 (제목2 아래끝 → 밑줄 위끝), (밑줄 아래끝 → 본문 첫 줄 위끝).
- 합격: 두 값 각각 다섯 블록 간 범위 ≤ 1pt.
- 불합격 심각도: **major** (반복 모듈의 유사성이 깨지면 같은 역할로 묶이지 않음).
- 근거: Wagemans et al. 2012(유사성); Lu et al. 2020(Similarity_group·Regularity).

**[LY-17] CORE 밑줄 길이가 한 규칙을 따르는가?**
- 측정: 밑줄 잉크 길이를 (a) 제목2 잉크 폭, (b) 본문 잉크 최대 폭, (c) 상수와 비교.
- 합격: (a)·(b)·(c) 중 한 규칙에 다섯 블록 모두 ±3pt 안.
- 불합격 심각도: **minor**.
- 근거: Wagemans et al. 2012(유사성); Chen et al. 2024 LACE(정렬·일관성 미학 제약).

**[LY-18] DETAIL·SUPPORT 블록의 제목→부제→본문 간격이 일관한가?**
- 측정: 잉크 기준 '위 줄 잉크 아래끝 → 다음 줄 잉크 위끝' 간격. DETAIL끼리(제목→본문), SUPPORT끼리(이름→부제, 부제→본문) 대응 간격을 비교.
- 합격: 같은 역할 안에서 대응 간격 범위 ≤ 2pt.
- 불합격 심각도: **minor**.
- 근거: Wagemans et al. 2012; Haraguchi et al. 2024.

## F. 정렬선

**[LY-19] 각 글 블록 안의 줄이 같은 왼쪽 선에 서 있는가?**
- 측정: 블록 안 줄별 왼쪽 잉크 x(CORE 제목1은 원판 들여쓰기 예외).
- 합격: 블록마다 범위 ≤ 1.5pt.
- 불합격 심각도: **minor**.
- 근거: Hsu et al. 2023 Ali(비정렬도); Chen et al. 2024 LACE.

**[LY-20] 같은 기둥에 쌓이거나 나란히 놓인 블록끼리 '어긋난 정렬(near-miss)'이 없는가?**
- 측정: (a) 세로로 250pt 안에 쌓이고 가로로 겹치는 두 글 블록(같은 묶음의 지시 라벨 포함)의 왼쪽 잉크 x 차이 Δx. (b) 가로로 나란히 놓인 같은 역할 블록(예: ③·④)의 제목1 잉크 위끝 차이 Δy.
- 합격: Δx ≤ 1.5pt 또는 Δx ≥ 18.6pt(= 캔버스 폭 1191의 1/64); Δy ≤ 1.5pt 또는 Δy ≥ 26.3pt(= 캔버스 높이 1684의 1/64).
- 불합격 심각도: **minor**.
- 근거: Chen et al. 2024 LACE(캔버스 범위 1/64 안의 좌표를 '거의 정렬'로 보고 맞춤); Hsu et al. 2023 Ali.

**[LY-21] 제목판 좌우의 대칭 짝(BASIC 왼쪽·오른쪽)이 같은 기준선에 서 있는가?**
- 측정: text_spec y — 머리글(전제 ·), 항목 이름 줄.
- 합격: 짝마다 Δy ≤ 1pt; 제목판 가로 중심과 캔버스 중심 차 ≤ 2pt.
- 불합격 심각도: **minor**.
- 근거: Lu et al. 2020(대칭 균형); Haraguchi et al. 2024(정렬).

## G. 가장자리·재단

**[LY-22] 모든 글과 라벨 붙은 물체가 재단선에서 5mm(14.2pt) 이상 안쪽인가?**
- 측정: 잉크·물체 외곽의 프레임 가장자리까지 최소 거리(바다·땅 배경 채움은 제외).
- 합격: ≥ 14.2pt [문헌값].
- 불합격 심각도: 글 < 8.5pt(3mm)면 **blocker**, 8.5~14.2pt면 **major**.
- 근거: University of Bristol Print Services, *Crops and bleed*(재단선에서 5mm 이상, 도련 3mm).

**[LY-23] 바깥 여백이 일관한가?**
- 측정: 가장 왼쪽 글 잉크 x, 가장 오른쪽 글 잉크까지 1191−x, 가장 위 글 잉크 y.
- 합격: 세 값의 범위 ≤ 6pt [운영값].
- 불합격 심각도: **minor**.
- 근거: Haraguchi et al. 2024(여백·정렬 원칙); Bristol 지침.

## H. 헤더와 지도의 전환

**[LY-24] 헤더(제목판·BASIC)와 지도 첫 물체 사이가 분명히 떨어져 있는가?**
- 측정: x마다 헤더 요소 아래끝과 그 아래 첫 지도 물체 위끝 사이 거리의 최솟값; 헤더 띠 안으로 들어온 지도 물체 수.
- 합격: 최소 ≥ 16pt, 침범 0 [운영값].
- 불합격 심각도: **major**.
- 근거: Wagemans et al. 2012(전경-배경 분리·공통 영역); Bylinskii et al. 2017(제목·글이 시선을 먼저 끎).

## I. 밀도·여백 분포

**[LY-25] 지도 안쪽 고리에 죽은 빈터가 없는가?**
- 측정: 1x 이미지(0.8px 가우스 흐림)에서 물체 화소 = 명도 기울기 > 8 또는 청록(B > R+15), 글 상자 제외. 지도 땅 영역(y ≥ 240, 해안선 위)을 20pt 칸으로 나눠 물체 비율 < 2%이고 글이 없는 칸을 '빈 칸'으로 둔다. 중심이 C에서 450pt 안인 빈 칸들로 만들 수 있는 최대 직사각형 면적.
- 합격: ≤ 19,600pt²(140×140, CORE 블록 한 개 크기) [운영값].
- 불합격 심각도: **minor**.
- 근거: Haraguchi et al. 2024(여백 원칙); Rosenholtz, Li & Nakano 2007(혼잡과 빈터의 분포가 탐색 성능을 좌우).

**[LY-26] CORE 블록이 가장 혼잡한 구역에 놓이지 않았는가?**
- 측정: LY-25와 같은 물체 화소 정의로, CORE 블록(text_spec 합집합 상자) 바깥 30pt 고리(글 상자 제외)의 물체 화소 비율을 구하고, 지도 땅 칸(글 없는 20pt 칸) 물체 비율 분포에서의 백분위를 잰다.
- 합격: 다섯 CORE 모두 고리 혼잡도 ≤ 75백분위 [운영값].
- 불합격 심각도: **minor**.
- 근거: Rosenholtz et al. 2007(feature congestion: 국소 색·대비·방향 변이가 클수록 표적 탐색이 느려짐); Hsu et al. 2023 Occ·Rea.

**[LY-27] 바다·하단 영역이 제대로 처리됐는가?**
- 측정: (a) 해안선이 글 상자를 가로지르는지, (b) 바다 위 캡션의 왼쪽 정렬·지시선 일관, (c) 내용 없는 하단 띠 높이(마지막 글·물체 아래끝 → 1684).
- 합격: (a) 0건, (b) 바다 위 SUPPORT 캡션 형식(굵은 이름 → 부제 → 본문)이 같음, (c) ≤ 6%(101pt) [운영값].
- 불합격 심각도: **minor**.
- 근거: Hsu et al. 2023(Und·Rea: 글 밑 바탕); Haraguchi et al. 2024(여백).

---

## 출처 (모두 직접 열어 확인)
1. Wagemans, J., Elder, J. H., Kubovy, M., Palmer, S. E., Peterson, M. A., Singh, M., & von der Heydt, R. (2012). A century of Gestalt psychology in visual perception: I. Perceptual grouping and figure–ground organization. *Psychological Bulletin*, 138(6), 1172–1217. https://pmc.ncbi.nlm.nih.gov/articles/PMC3482144/
2. Kubovy, M., Holcombe, A. O., & Wagemans, J. (1998). On the lawfulness of grouping by proximity. *Cognitive Psychology*, 35(1), 71–98. https://lirias.kuleuven.be/retrieve/93542
3. Lu, M., Wang, C., Lanir, J., Zhao, N., Pfister, H., Cohen-Or, D., & Huang, H. (2020). Exploring Visual Information Flows in Infographics. *CHI 2020*. https://doi.org/10.1145/3313831.3376263 (전문: https://vcg.seas.harvard.edu/publications/20200301-exploring-visual-information-flows-in-infographics)
4. Fosco, C., Casser, V., Bedi, A. K., O'Donovan, P., Hertzmann, A., & Bylinskii, Z. (2020). Predicting Visual Importance Across Graphic Design Types. *UIST 2020*. https://arxiv.org/abs/2008.02912
5. Bylinskii, Z., Kim, N. W., O'Donovan, P., Alsheikh, S., Madan, S., Pfister, H., Durand, F., Russell, B., & Hertzmann, A. (2017). Learning Visual Importance for Graphic Designs and Data Visualizations. *UIST 2017*. https://arxiv.org/abs/1708.02660
6. Hsu, H. Y., He, X., Peng, Y., Kong, H., & Zhang, Q. (2023). PosterLayout: A New Benchmark and Approach for Content-aware Visual-Textual Presentation Layout. *CVPR 2023*. https://arxiv.org/abs/2303.15937
7. Seol, J., Kim, S., & Yoo, J. (2024). PosterLlama: Bridging Design Ability of Language Model to Contents-Aware Layout Generation. *ECCV 2024*. https://arxiv.org/abs/2404.00995
8. Haraguchi, D., Inoue, N., Shimoda, W., Mitani, H., Uchida, S., & Yamaguchi, K. (2024). Can GPTs Evaluate Graphic Design Based on Design Principles? *SIGGRAPH Asia 2024 Technical Communications*. https://arxiv.org/abs/2410.08885
9. Chen, J., Zhang, R., Zhou, Y., Jain, R., Xu, Z., Rossi, R., & Chen, C. (2024). Towards Aligned Layout Generation via Diffusion Model with Aesthetic Constraints (LACE). *ICLR 2024*. https://arxiv.org/abs/2402.04754
10. An, A., Sun, S., Huang, D., Cheng, M., Gao, Y., Li, J., Qiao, Y., & Bian, J. (2026). Can Vision Language Models Assess Graphic Design Aesthetics? A Benchmark, Evaluation, and Dataset Perspective (AesEval-Bench). *ICLR 2026*. https://arxiv.org/abs/2603.01083 — 자동 미학 평가의 한계 근거(이 루브릭이 VLM 인상 대신 픽셀 측정을 쓰는 이유).
11. Rosenholtz, R., Li, Y., & Nakano, L. (2007). Measuring visual clutter. *Journal of Vision*, 7(2):17, 1–22. doi:10.1167/7.2.17 — 저널 페이지는 접속 차단(403), 저자 소프트웨어 페이지 https://dspace.mit.edu/handle/1721.1/37593 와 MIT News(2007-08-21) https://news.mit.edu/2007/mits-clutter-detector-could-cut-confusion 로 내용 확인.
12. Kern, J. P., & Brewer, C. A. (2008). Automation and the Map Label Placement Problem: A Comparison of Two GIS Implementations of Label Placement. *Cartographic Perspectives*, 60, 22–45. (Imhof 1962/1975 라벨 원칙, van Dijk et al. 1999 라벨 품질 4기준 정리) https://cartographicperspectives.org/index.php/journal/article/download/cp60-kern-brewer/pdf/1397
13. University of Bristol Print Services. *Crops and bleed*. https://www.bristol.ac.uk/print-services/useful-information/crops-and-bleed/
