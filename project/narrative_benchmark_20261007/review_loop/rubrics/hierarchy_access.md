# 루브릭 · 시각 위계·가독성·접근성·인쇄 (field = hierarchy_access)

- 버전: v1 · 라운드 1에서 작성(2026-10-12). 라운드 2부터 이 파일을 고정해 다른 비평가가 그대로 쓴다.
- 대상: A2 세로 인쇄 포스터(420×594mm, Figma 프레임 1191×1684pt, 1pt = 0.3528mm 실제 크기), 관람 거리 0.5~1.5m(BRIEF §1).
- 고정 조건(BRIEF §3)은 감점하지 않는다. 기운 지명(±30°)·동심원 배치·②색 통일·이정표·배경판 금지 안에서만 판정하고 해법을 낸다.

## 0. 공통 측정 규약 (모든 항목에 적용, 재현용)

| 기호 | 정의 |
|---|---|
| 좌표 | pt, 프레임 왼쪽 위 원점. `r<N>/poster_2x.png`에서 1pt = 2px |
| 글 크기·색 | `text_spec_r<N>.json` 값만 쓴다(BRIEF §5) |
| 참 배경 | 글이 없는 지도 `out/figma_import/map_v8_2_milestones_without_text_2x.png`(라운드마다 Figma 배경 fill과 같은 파일인지 receipt의 sha256으로 확인). 없으면 포스터에서 글 픽셀을 지운 주변 중앙값을 쓴다 |
| 글자 마스크 | `|poster_2x − 참 배경|`의 RGB 합 > 24 인 픽셀. **halo** = 마스크를 2px(1pt) 팽창한 영역 |
| 글자별 배경 | halo를 3px 팽창해 연결 성분(≈한 음절)으로 나누고, 성분마다 참 배경 halo 픽셀의 중앙값 |
| WCAG 대비 | WCAG 2.2 상대 휘도 공식. 큰 글 = 18pt 이상 또는 14pt 이상 Bold(한국어도 같은 pt 적용) |
| APCA Lc | APCA-W3 0.0.98G-4g: Y = 0.2126729·R^2.4 + 0.7151522·G^2.4 + 0.0721750·B^2.4 (R,G,B = sRGB/255), Y<0.022이면 Y += (0.022−Y)^1.414. 정극성 S = (Yb^0.56 − Yt^0.57)·1.14, 역극성 S = (Yb^0.65 − Yt^0.62)·1.14, \|S\|<0.1이면 0, 아니면 Lc = (S ∓ 0.027)·100 |
| APCA 등급(Bronze Simple Mode) | **본문 body** = CORE 본문 5개(790:148/154/160/166/172) → Lc ≥ 75. **그 밖의 읽는 글 content**(제목·소제목·캡션·라벨·지명) → Lc ≥ 60. **큰 글 large**(관람 거리에서 CSS px 환산 > 36px; 이 포스터에선 제목뿐) → Lc ≥ 45 |
| CSS px 환산 | 거리 D(mm)에서 px = pt × 1.3333 × 711.2 / D (CSS 기준 픽셀 = 팔 길이 28in에서 0.0213°) |
| 한글 잉크 높이 | 음절 60자 렌더 중앙값: Noto Sans KR Regular/Medium 0.893em, Bold 0.917em, Noto Serif KR Bold 0.960em. 잉크 높이(mm) = pt × 0.3528 × 비율 |
| 한글 임계 글자 크기(CPS) | He·Baek·Legge 2018: 한국어 CPS = 0.17°(간격 기준) = 잉크 높이 **0.226°**. 최대 판독 거리 **D_max = 잉크 높이(mm) / tan 0.226° = 잉크 높이 / 0.003945** |
| 관람 거리 등급 | **T1 신호 글**(제목·질문·CORE 제목) = 1.5m(BRIEF 최대 거리). **T2 읽기 글**(CORE 본문, BASIC·DETAIL·SUPPORT 본문·소제목) = 0.711m(CSS 기준 팔 길이). **T3 라벨**(9~10.5pt 지명·모형 라벨·짧은 캡션) = 0.5m(BRIEF 최소 거리) |
| 색각이상 | Machado·Oliveira·Fernandes 2009 행렬, 심각도 1.0(protan·deutan·tritan), 선형 RGB에 적용 |
| 인쇄 | 소프트프루프 = sRGB → PSO Coated v3(FOGRA51, ECI 2015) 상대 색도 + 흑점 보정 → sRGB |

**심각도 공통 원칙**: blocker = 표준 수치 미달이 판독 불가·가림·잘림으로 이어짐(글자 대비 < 3:1, 획이 물체에 가려짐, 재단선 3mm 안의 글, D_max < 0.5m). major = 표준·문헌 기준 미달이지만 읽을 수는 있음. minor = 기준선 근처(아래 각 항목의 허용 폭 안) 또는 다른 단서로 보상되는 결함. 같은 원인의 결함은 한 항목으로만 센다.

---

## A. 첫 3초 위계 (제목 → 질문 → CORE → DETAIL → SUPPORT)

**[H1] 제목이 가장 먼저 잡히는가?**
- 측정: 제목 pt ÷ 그다음으로 큰 글 pt (text_spec), 제목 APCA Lc(참 배경 중앙값).
- 합격: 크기비 ≥ 3.0 그리고 Lc ≥ 45(large).
- 불합격: major.
- 근거: Bylinskii 2017(UIST), Fosco 2020(UMSI, UIST) — 글 크기·대비가 그래픽 디자인의 시각 중요도를 좌우; APCA Bronze(large Lc 45).

**[H2] 질문(2위)이 CORE 제목(3위)보다 작지 않은가? (크기 역전 없음)**
- 측정: 질문 pt ≥ CORE 제목 pt (text_spec).
- 합격: 질문 pt ≥ CORE 제목 pt.
- 불합격: minor(질문이 제목 바로 아래·같은 틀 안에 있어 위치로 보상될 때) / major(위치 보상도 없을 때).
- 근거: Fosco 2020, Bylinskii 2017; UEyes(Jiang 2023, CHI) — 포스터 첫 응시는 크기·위치 편향을 따른다.

**[H3] CORE 제목이 DETAIL·SUPPORT 제목보다 확실히 크고, 순서 단서가 5개 모두 있는가?**
- 측정: CORE 제목 pt ÷ DETAIL·SUPPORT 제목 최대 pt; 번호 원판 ①~⑤ 존재(text_spec 790:102/105/110/111/106).
- 합격: 크기비 ≥ 1.5 그리고 원판 5개.
- 불합격: major.
- 근거: Fosco 2020; Chakraborty 2022(IEEE TMM) — 구성 요소별 중요도가 응시 순서(스캔패스)를 예측.

**[H4] DETAIL 제목 묶음과 SUPPORT 제목 묶음이 '일관된' 단서로 위계가 갈리는가?**
- 측정: DETAIL 제목(790:174, 177, 180, 183)과 SUPPORT 제목(790:109, 121, 122, 192)의 pt·굵기·색. 색은 모든 DETAIL–SUPPORT 쌍의 최소 ΔE00, 명도는 두 묶음 APCA Lc 범위의 겹침.
- 합격: 다음 중 하나 이상이 **모든 쌍**에 성립 — 크기비 ≥ 1.15 / 굵기 한 단계 이상 차이 / 색 ΔE00 ≥ 10 이면서 Lc 범위가 겹치지 않음.
- 불합격: major(BRIEF가 정한 역할 순서가 시각적으로 평평해짐).
- 근거: Fosco 2020; Bylinskii 2017; BRIEF §2 역할 구조.

## B. 관람 거리별 판독

**[D1] T1 신호 글이 1.5m에서 읽히는가?**
- 측정: 제목·질문·CORE 제목 각각 D_max(§0 공식).
- 합격: 모두 D_max ≥ 1.5m.
- 불합격: major / D_max < 0.711m면 blocker.
- 근거: He·Baek·Legge 2018(Vision Research 150); Legge & Bigelow 2011(J Vision 11(5):8).

**[D2] T2 읽기 글이 0.711m(팔 길이)에서 읽히는가?**
- 측정: CORE 본문(11.5pt), DETAIL·SUPPORT·BASIC 소제목·본문(9.5~12pt) D_max.
- 합격: 모두 D_max ≥ 0.711m.
- 불합격: major / D_max < 0.5m면 blocker.
- 근거: He 2018; CSS Values 4(W3C 2024) 기준 픽셀·팔 길이 정의.

**[D3] T3 라벨이 0.5m에서 읽히는가?**
- 측정: 9~10.5pt 라벨·캡션 D_max.
- 합격: 모두 D_max ≥ 0.5m.
- 불합격: blocker(가장 가까운 거리에서도 CPS 미달 = 판독 불가 수준).
- 근거: He 2018; Legge & Bigelow 2011.

**[D4] 고령 관람자 여유: CPS가 1.27배 큰 독자도 0.5m에서 모든 글을 읽는가?**
- 측정: 모든 글 D_max ÷ 1.27 (한국 고령/청년 CPS 비 0.52°/0.41°).
- 합격: 모두 ≥ 0.5m.
- 불합격: minor.
- 근거: 한국인지및생물심리학회지 27(3) 367–384(2015) 한글 글자 크기와 읽기 속도.

**[D5] 제목 글자 높이가 표지판 시각 문자 최소 높이를 넘는가?**
- 측정: 제목 잉크 높이(mm) vs ADA 703.5.5(시거리 6ft 미만 5/8in = 15.9mm; 6ft 초과 시 1ft마다 +1/8in).
- 합격: 1.5m에서 ≥ 15.9mm.
- 불합격: major.
- 근거: U.S. Access Board, ADA Standards 703.5.

## C. 대비 실측

**[C1] 모든 글이 WCAG 2.2 SC 1.4.3을 F83 절차로 통과하는가?**
- 측정: (1) 빠른 검사 = 글 색 vs halo 참 배경의 가장 어두운 2%(밝은 글은 가장 밝은 2%); (2) 실패 시 글자별 배경 중앙값으로 재검사.
- 합격: 일반 글 4.5:1, 큰 글 3:1을 (1) 또는 (2)에서 모든 글자가 넘음.
- 불합격: major(어떤 글자 3.0~기준 미만) / blocker(어떤 글자 < 3:1).
- 근거: WCAG 2.2 SC 1.4.3, Understanding 1.4.3, Technique F83.

**[C2] CORE 본문이 APCA 본문 기준(Lc 75)을 넘는가?**
- 측정: 5개 본문 Lc(참 배경 halo 중앙값).
- 합격: 모두 Lc ≥ 75.
- 불합격: minor(부족분 < 5 Lc이고 WCAG ≥ 7:1) / major(그 밖).
- 근거: APCA in a Nutshell(Myndex 2022), ARC Bronze Simple Mode(2023).

**[C3] 그 밖의 읽는 글이 APCA content 기준(Lc 60)을 넘는가?**
- 측정: CORE 본문 외 모든 글 Lc(참 배경 halo 중앙값).
- 합격: 모두 Lc ≥ 60.
- 불합격: minor(최저 55~59.9) / major(어느 하나라도 < 55).
- 근거: APCA Bronze; WCAG 3 draft how-to 'Visual contrast of text'(작고 가는 글일수록 더 큰 대비 필요).

**[C4] 밝은 글(번호 원판 숫자)이 역극성에서 충분한가?**
- 측정: #FFF4DD 숫자 vs 원판 색, WCAG·|Lc|.
- 합격: WCAG ≥ 4.5(12pt Bold는 일반 글) 그리고 |Lc| ≥ 60.
- 불합격: major.
- 근거: WCAG 2.2 1.4.3; APCA.

**[C5] 읽기 순서·구조를 맡는 비텍스트 요소가 3:1을 넘는가?**
- 측정: 번호 원판, 이정표 화살 판, CORE 밑줄 vs 바로 옆 배경(참 배경).
- 합격: 각각 ≥ 3:1.
- 불합격: major(원판·이정표) / minor(밑줄·지시선).
- 근거: WCAG 2.2 SC 1.4.11.

**[C6] 3D 물체(길·건물·물결 등)가 글자 획 밑으로 들어오지 않는가?**
- 측정: 글자 halo 아래 참 배경 픽셀 중 주변 지면 휘도(글 상자 ±20pt 창의 중앙값)와 |ΔY| > 0.08 인 픽셀의 비율·위치. 확인된 곳은 2배 확대로 눈으로 재확인.
- 합격: 모든 글에서 0%(1% 미만은 측정 잡음으로 보고 눈으로 확인).
- 불합격: major(획이 물체 위에 놓였으나 글자별 대비는 기준 통과) / blocker(그 때문에 글자별 대비가 기준 미만이거나 획이 가려짐).
- 근거: WCAG F83(배경 형태가 글과 혼동), Wianto 2025(JEMR 18(3)) — 배경 대비가 목표 탐색을 늦춤.

## D. 색각이상

**[V1] 색만으로 전달되는 정보가 없는가?**
- 측정: 색 부호(열·물·칼슘 의미색, CORE 둘째 줄, 원판, 이정표, 바다/땅)마다 글·숫자·모양 단서 동반 여부.
- 합격: 모두 동반.
- 불합격: major.
- 근거: WCAG 2.2 SC 1.4.1.

**[V2] 색각이상 시뮬레이션에서도 색 글자의 대비가 기준을 유지하는가?**
- 측정: 색 글(#983821, #195B61, #784C26, #365864, #FFF4DD/원판)과 그 배경을 Machado 2009(1.0)로 변환 후 WCAG.
- 합격: 세 유형 모두 일반 4.5 / 큰 글 3.0 유지.
- 불합격: major.
- 근거: Machado 2009(IEEE TVCG 15(6)); WCAG 2.2.

**[V3] 의미가 다른 색 짝이 색각이상에서도 갈리는가?**
- 측정: '물'(#195B61) vs '칼슘'(#784C26) 라벨, 이정표 판 vs 주변 지면 — 시뮬레이션 후 ΔE00.
- 합격: 모두 ΔE00 ≥ 10.
- 불합격: minor(V1이 합격이면 색은 보조 단서이므로).
- 근거: Machado 2009.

## E. 인쇄

**[P1] 배경 래스터가 A2 실제 크기에서 충분한 해상도인가?**
- 측정: Figma 배경 fill 이미지의 픽셀 폭 ÷ 16.535in(420mm).
- 합격: ≥ 175ppi(0.5m에서 1 arcmin = 0.145mm). 권장 240ppi.
- 불합격: major(120~174ppi) / blocker(< 120ppi).
- 근거: Vistaprint 2026(18×24in 240DPI, 근접 300DPI); 4OVER4 2026(팔 길이 150ppi 하한); 시력 1 arcmin 환산.

**[P2] 재단 여분(bleed)이 있는가?**
- 측정: 인쇄 파일에서 그림이 재단선 밖으로 이어지는 폭(그림이 가장자리까지 닿는 변만).
- 합격: 모든 해당 변 ≥ 3mm(8.5pt).
- 불합격: major.
- 근거: Vistaprint 2026(0.125in bleed).

**[P3] 모든 글이 안전 영역 안에 있는가?**
- 측정: 글 상자와 재단선 사이 최소 거리(text_spec).
- 합격: ≥ 6.35mm(18pt).
- 불합격: major(3~6.35mm) / blocker(< 3mm).
- 근거: Vistaprint 2026(0.25in safe zone).

**[P4] 인쇄 색(PSO Coated v3)으로 바꿔도 글 대비가 유지되는가?**
- 측정: 글 색·글 배경 대표색을 §0 소프트프루프로 왕복 변환 후 WCAG·Lc, 왕복 ΔE00.
- 합격: 변환 후에도 C1·C2·C3 기준 유지, 글 색 ΔE00 ≤ 5.
- 불합격: major(기준 깨짐) / minor(ΔE00만 > 5).
- 근거: ECI/Fogra 2015(ISO 12647-2:2013, FOGRA51, PSO Coated v3, 총 잉크 300%).

**[P5] 가장 가는 작은 글의 획이 인쇄에서 살아남는가?**
- 측정: 가장 작고 가는 글(9pt Noto Sans KR Regular)의 세로획 폭(mm) — 1000단위 렌더에서 'ㅣ' 획 폭 × pt × 0.3528/1000.
- 합격: ≥ 0.1mm.
- 불합격: major.
- 근거: Legge & Bigelow 2011(획·x-height와 판독), 인쇄 실무 최소 선폭 0.1mm.

---

## 출처 (실제로 열어 본 자료)

1. W3C (2024). *Web Content Accessibility Guidelines (WCAG) 2.2*, W3C Recommendation 12 Dec 2024. https://www.w3.org/TR/WCAG22/
2. W3C (2024). *Understanding SC 1.4.3 Contrast (Minimum)*. https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
3. W3C. *Technique F83: background images that do not provide sufficient contrast*. https://www.w3.org/WAI/WCAG22/Techniques/failures/F83
4. Somers, A. / Myndex (2022). *APCA in a Nutshell*. https://git.apcacontrast.com/documentation/APCA_in_a_Nutshell.html
5. Myndex / ReadTech (2023, rev. 2023-02-10). *ARC Bronze Simple Mode*. https://readtech.org/ARC/tests/bronze-simple-mode/?tn=criterion
6. W3C (2024). *CSS Values and Units Module Level 4*, WD 12 Mar 2024 (reference pixel 0.0213°, 28in). https://www.w3.org/TR/css-values-4/
7. W3C AGWG. *WCAG 3 how-to: Visual contrast of text* (draft). https://www.w3.org/WAI/GL/WCAG3/2022/how-tos/visual-contrast-of-text
8. Legge, G. E., & Bigelow, C. A. (2011). Does print size matter for reading? *Journal of Vision* 11(5):8. https://pmc.ncbi.nlm.nih.gov/articles/PMC3428264/
9. He, Y., Baek, S., & Legge, G. E. (2018). Korean reading speed: Effects of print size and retinal eccentricity. *Vision Research* 150, 8–14. https://legge.dl8.umn.edu/sites/legge.psych.umn.edu/files/files/media/he18_korean_reading_speed-_effects_of_print_size_and_retinal_eccentricity.pdf
10. (2015). The Effect of Hangul Print Size on Reading Speed of Young and Older Adults in a Computer Environment. *Korean J. Cognitive and Biological Psychology* 27(3), 367–384. https://www.accesson.kr/cogpsych/v.27/3/367/17617
11. U.S. Access Board. *Guide to the ADA Accessibility Standards, Ch. 7 Signs (703.5)*. https://www.access-board.gov/ada/guides/chapter-7-signs/
12. Bylinskii, Z. et al. (2017). Learning Visual Importance for Graphic Designs and Data Visualizations. *UIST 2017*. https://arxiv.org/abs/1708.02660
13. Fosco, C. et al. (2020). Predicting Visual Importance Across Graphic Design Types (UMSI). *UIST 2020*. https://arxiv.org/abs/2008.02912
14. Jiang, Y., Leiva, L. A., et al. (2023). UEyes: Understanding Visual Saliency across User Interface Types. *CHI 2023*. https://userinterfaces.aalto.fi/ueyeschi23
15. Chakraborty, S. et al. (2022). Predicting Visual Attention in Graphic Design Documents. *IEEE Trans. Multimedia* 25. https://arxiv.org/abs/2407.02439
16. Jiang, Y. et al. (2024). EyeFormer: Predicting Personalized Scanpaths with Transformer-Guided RL. *UIST 2024*. https://arxiv.org/abs/2404.10163
17. Wianto, E., Toba, H., & Malinda, M. (2025). *Journal of Eye Movement Research* 18(3):22. https://pmc.ncbi.nlm.nih.gov/articles/PMC12194738/
18. Machado, G. M., Oliveira, M. M., & Fernandes, L. A. F. (2009). A Physiologically-based Model for Simulation of Color Vision Deficiency. *IEEE TVCG* 15(6), 1291–1298. https://www.inf.ufrgs.br/~oliveira/pubs_files/CVD_Simulation/CVD_Simulation.html
19. ECI / HdM Stuttgart (2015-09-30). *Neue Druckbedingungen nach ISO 12647-2:2013* (FOGRA51, PSO Coated v3: 총 잉크 300%, K 최대 96%). https://eci.org/lib/exe/arbeitsmittel_iso_12647-2_2013_-_suessl_-_2015-10-01.pdf ; 프로파일 https://eci.org/lib/exe/pso-coated_v3.zip
20. Vistaprint (2026-06-09). *Pre-print checklist for posters*. https://vistaprint.com/hub/poster-printing-preparation-guide
21. 4OVER4 (2026-10-09). *Big Poster Printing Sizes and the Resolution Each One Needs*. https://v2.4over4.com/guide/how-to-print-large-posters
