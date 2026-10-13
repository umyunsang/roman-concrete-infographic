# 루브릭 · 타이포그래피(한글 조판) — 로마 콘크리트 A2 포스터

- 작성: 라운드 1 타이포그래피 비평가 (2026-10-12). 라운드 2부터 이 파일을 **고치지 않고** 그대로 쓴다.
- 판정은 항목마다 예(합격)/아니오(불합격) 하나. 불합격이면 적힌 심각도를 그대로 쓴다(심각도 규칙이 둘이면 적힌 조건으로 고른다).
- BRIEF의 고정 조건은 감점하지 않는다: 명조 제목 + 고딕 나머지, 부가 설명 2줄 안팎, 떠 있는 글 수평, 땅에 눕힌 지명(±30°, 땅 축 — 등각 투영의 기울임·전단 포함), CORE 원판·밑줄·제목 둘째 줄 #983821, 소제목 배경판 없음. 해법도 이 조건을 깨면 안 된다(배경판·후광 판 제안 금지).
- 같은 원인에서 나온 불합격 여러 개는 **지적 하나**로 묶는다(리포트에 "TY-xx와 같은 결함"이라고 적는다).

## 0. 공통 상수와 측정법 (재현용)

| 기호 | 값 | 근거 |
|---|---|---|
| K1 | Noto Sans KR 한글 줄 잉크 높이 = **0.906 em**(Regular), **0.93 em**(Bold). Noto Sans CJK KR로 1000px em 렌더해 문장 10줄 중앙값을 잼. 2배 타일 실측(본문 11.5pt → 10.5pt)과 일치 | 렌더 실측 |
| K2 | 한국어 임계 글자 크기(CPS) = 0.17°(영문 x-height 등가) × 1.33(한글 잉크 높이 환산) = **잉크 높이 0.226°** | S5 He·Baek·Legge 2018 Table 1·§2 |
| K3 | 필요한 잉크 높이 h = 거리 × tan 0.226° → **0.5 m 1.97 mm · 1.0 m 3.94 mm · 1.5 m 5.92 mm** | S4 Legge & Bigelow 2011(각도 = 57.3 × 크기 ÷ 거리) |
| K4 | 1 pt = 0.3528 mm(Figma 프레임 1191×1684 pt = A2 실물 1:1). 필요 글자 크기(pt) = h ÷ (0.3528 × K1) → 0.5 m 6.2 pt · 1.0 m 12.35 pt · 1.5 m(Bold) 18.0 pt | BRIEF §1 |
| K5 | 관람 거리 0.5~1.5 m(BRIEF). 역할별 기준 거리: 제목·질문·CORE 소제목 1.5 m(먼 끝), CORE 본문 1.0 m(범위 가운데), 그 밖의 모든 글 0.5 m(가까운 끝) | BRIEF §1 |

측정 절차
- **크기·굵기·행간·자간·정렬**: `text_spec_r<N>.json` 값으로 판단(BRIEF 규칙). 잉크 높이·간격은 `poster_2x.png`에서 잰다(2배 → pt는 ÷2).
- **잉크 띠**: 글 상자를 잘라 휘도 L(Rec.709)을 구하고, 문턱 = 바탕(85백분위) − 0.5×(바탕 − 잉크(1백분위)). 문턱보다 어두운 화소가 있는 행의 연속 구간 = 줄 잉크 띠.
- **바탕 간섭**: 낱말 하나(잉크 상자)를 잘라 글자 화소(L < 120을 2px 팽창)를 빼고 남은 바탕 화소의 L 표준편차를 잰다. 같은 글의 민바탕 낱말이 기준(이 포스터 종이 2~3.5, 바다 1.9~2.0).
- **국소 최저 대비**: WCAG 상대 휘도. 잉크 = 글자 화소 중 어두운 20% 평균, 바탕 = 같은 상자 바탕 화소의 **5백분위**(가장 어두운 쪽). (L_bg+0.05)/(L_ink+0.05).
- **밑줄**: R−G > 40 그리고 R−B > 40인 화소가 한 행에 75 pt 이상 이어지면 밑줄 행.
- **회전 글**: 글 상자를 잘라 −θ만큼 되돌린 뒤(평탄화) 정상 글자로 읽히는지 눈과 정규상관(같은 글을 렌더한 기준과 비교)으로 확인.
- 도구 예: `uv run --no-project --with pillow --with numpy python -I script.py`.

## A. 크기 위계와 비율

**[TY-01] 위계 순서가 뒤집히거나 같아지지 않는가?**
- 측정: 역할 사슬 제목 > 핵심 질문 > CORE 소제목 > {CORE 본문, DETAIL·SUPPORT 제목} > {DETAIL·SUPPORT 설명, 캡션} > {키커, 부품 라벨}에서 이웃한 두 역할의 잉크 높이 비(= 크기 × K1 비).
- 합격: 위 역할 ÷ 아래 역할 ≥ **1.10** (모든 이웃 쌍).
- 심각도: 역전·동률이고 위 역할을 위치·테두리(띠·액자 안, 또는 제목 바로 밑)로도 구분하지 못하면 **major**, 위치·테두리로 구분되면 **minor**.
- 근거: S8 Butterick(Headings: "smallest increment necessary to make a visible difference"), S10 Brown 2011(모듈러 스케일), S16 Brath 2021(크기·굵기는 위계 채널).

**[TY-02] 같은 역할의 글은 크기·굵기·행간이 하나로 같은가?**
- 측정: text_spec에서 역할별(아래 표)로 (크기, 굵기, 행간 ÷ 크기)의 종류 수.
- 역할: CORE 소제목 / CORE 본문 / DETAIL 제목 / DETAIL 설명 / SUPPORT 제목 / SUPPORT 키커 / SUPPORT 설명 / 모형 캡션 / 지시선 부품 라벨 / 원리 단계 라벨 / BASIC 제목·이름·부가·설명 / 지명.
- 합격: 역할마다 종류 1개(행간 비 차 ≤ 2%p는 같은 것으로 봄). 지명은 면 지물(바다)을 한 단계 키우는 것을 허용.
- 심각도: 차이가 모두 ≤ 0.5 pt면 **minor**, 1 pt 이상이거나 굵기가 다르면 **major**.
- 근거: S8 Butterick(Mixing fonts: "each font has a consistent role"), S9 Smithsonian(consistent letterspacing/spacing).

**[TY-03] 글 크기 단계가 7개 이하인가?**
- 측정: text_spec의 서로 다른 글 크기 수(+, → 같은 기호 제외).
- 합격: ≤ 7. 심각도: **minor**(TY-02와 원인이 같으면 하나로 묶음).
- 근거: S10 Brown 2011, S8 Butterick(Headings: 단계 3개 이하 권장).

**[TY-04] 제목이 압도적 진입점인가?**
- 측정: 제목 잉크 높이 ÷ (질문, CORE 소제목 중 큰 것).
- 합격: ≥ 2.5. 심각도: **major**. 근거: S4(유창 범위 안에서 크기 = 주목), S10.

## B. 굵기 대비

**[TY-05] 소제목과 그 본문의 굵기·크기 대비가 충분한가?**
- 합격: 굵기 차 ≥ 300(Bold 700 ↔ Regular 400) 그리고 크기비 ≥ 1.2. 심각도: **major**. 근거: S8 Headings, S16.

**[TY-06] 같은 크기로 위아래 붙은 다른 위계(키커 ↔ 설명)가 눈에 보이게 다른가?**
- 측정: 굵기 단계 차, 그리고 획 농도(잉크 띠 안 덮임 비율) 차.
- 합격: 굵기 차 ≥ 100 그리고 획 농도 차 ≥ 10%, 또는 색·크기(≥ 1.1배) 차. 심각도: **minor**. 근거: S8, S16.

**[TY-07] 쓰인 굵기가 3단계(Regular·Medium·Bold) 이하인가?** — 심각도 **minor**. 근거: S8 Mixing fonts.

## C. 행간·자간·한 줄 길이

**[TY-08] 2줄 이상 본문·설명의 행간이 글자 크기의 120~170%인가?**
- 측정: text_spec 행간 ÷ 크기, 그리고 2배 타일에서 줄 잉크 띠 윗선 간격.
- 심각도: 110% 미만 또는 190% 초과 **major**, 그 밖의 범위 밖 **minor**.
- 근거: S9 Smithsonian("at least 20 percent greater than the font size"), S8 Line spacing(120~145%, 라틴), S1 KLREQ §7.4.1(한국어 예시 160%).

**[TY-09] 2줄 소제목의 행간이 100~135%인가?** — 심각도 **minor**. 근거: S8.

**[TY-10] 자간이 본문·라벨 0% ± 2%, 40 pt 이상 제목 −3~0%인가?** — 심각도 **minor**. 근거: S1 KLREQ §7.3.1(한글 기본 글자 사이 0), S9("do not allow letters to touch").

**[TY-11] 설명문 한 줄 길이가 공백 포함 30자 이하이고, 2줄 이상 덩이의 가장 긴 줄은 10자 이상인가?**
- 심각도: **minor**. 근거: S9(최대 55자, 45~50자 권장 — 라틴 기준, 한글 1음절 ≈ 라틴 2자로 환산), S14 Shin & Park 2003(한글 줄당 50자에서 읽기 빠름), S15 Dyson 2004(줄당 글자 수가 핵심 변수).

**[TY-12] 마지막 줄이 어절 하나만 남은 외톨이 줄이 없는가?** — 심각도 **minor**. 근거: S1 KLREQ §7.2.3.5.

## D. 정렬과 기준선

**[TY-13] 여러 줄 글이 왼끝 맞춤이고, 가운데 맞춤은 3줄 이하 캡션·제목에만 쓰였는가?** — 심각도 **minor**. 근거: S9("Do not center more than three lines"; "Justify the left margin and keep a ragged right"), S8 Centered text.

**[TY-14] 한 덩이(소제목 둘째 줄·밑줄·본문, 제목·키커·설명) 안의 왼끝 잉크 위치 차가 1 pt 이하인가?** (번호 원판 때문에 들여 쓴 첫 줄은 제외) — 심각도 **minor**. 근거: S9, S8.

**[TY-15] 반복 모듈 CORE ①~⑤의 내부 치수가 같은가?**
- 측정: (a) 원판 → 제목 1줄 들여쓰기, (b) 제목 둘째 줄 잉크 아래끝 → 밑줄, (c) 밑줄 → 본문 첫 줄 잉크 위끝, (d) 밑줄 길이 규칙(제목 둘째 줄 잉크 폭 ±2 pt, 또는 다섯 곳 같은 고정 길이 ±2 pt).
- 합격: (a)(b)(c) 다섯 곳 차 ≤ 1 pt, (d) 규칙 하나를 다섯 곳 모두 따름.
- 심각도: **minor**(모듈 소속이 헷갈릴 정도면 **major**). 근거: S9(consistent spacing), S8(Headings — 공간으로 위계), S16.

## E. 한국어 줄바꿈과 오독

**[TY-16] 모든 줄바꿈이 어절 사이에서 일어나는가?(어절 안 끊김 0)** — 심각도 **major**. 근거: S1 KLREQ §7.1.1, S2 CSS Text 3 `word-break: keep-all`("the other common behavior for Korean"), S13 Baek·Choi·Gordon 2023(띄어쓰기·조사가 어절 분절 단서).

**[TY-17] 줄 끝 오독이 없는가?** — 앞 줄 끝 어절이 다음 줄 첫 어절과 떨어져 다른 뜻으로 먼저 읽히는 끊기(예: '보통 / 온도'), 수식어·피수식어, 수·단위, 부정어·서술어 분리가 0. 2줄 이상 글 전부를 하나씩 읽는다. — 심각도 **major**. 근거: BRIEF §6, S13.

**[TY-18] 줄머리·줄끝 금칙과 분리 금지를 지키는가?** — 닫는 괄호·따옴표, 마침표·쉼표, 가운뎃점, 물음표가 줄머리에 없고, 여는 괄호·따옴표가 줄끝에 없으며, 숫자·단위·연속 숫자가 갈리지 않음. — 심각도 **major**. 근거: S1 KLREQ §7.1.2~7.1.4, 부록 B(cl1, cl2, cl5~cl9).

## F. 문장부호

**[TY-19] 가운뎃점이 한 글자(U+00B7)로 통일되고, 열거는 붙여 쓰며, 띄운 가운뎃점은 '항목 구분자' 역할에만 일관되게 쓰였는가?** — 심각도 **minor**. 근거: S3 국립국어원 「문장 부호」 제5항("가운뎃점은 앞말과 뒷말에 붙여 쓴다"), S1 KLREQ cl7·§7.3.3.

**[TY-20] 따옴표는 둥근 따옴표(U+2018/2019, U+201C/201D)이고, 쉼표·괄호·따옴표의 붙여 쓰기가 규정대로인가?** — 심각도 **minor**. 근거: S3 제4·9·10·18항, S1 §6.1.3.

**[TY-21] 같은 역할 안에서 끝맺음(문장형 + 마침표 / 명사형 개조식 + 마침표 없음)이 섞이지 않는가?** — 심각도 **minor**. 근거: S3 제1항(마침표), S8(consistent role).

## G. 서체 조화

**[TY-22] 글꼴 가족이 2개 이하이고, 획 대비가 큰 명조는 40 pt 이상 제목에만 쓰이며, 두 가족이 같은 설계 계열인가?**
- 심각도: 명조가 12 pt 이하 글에 쓰이면 **major**, 그 밖 불합격 **minor**.
- 근거: S8 Mixing fonts("Most documents can tolerate a second font"; 같은 디자이너 짝), S12 Minakata et al. 2023(획 대비가 작은 글꼴이 작은 크기에서 유리), S11 Wallace et al. 2022(글꼴에 따라 읽기 속도 35% 차 — 본문 글꼴은 검증된 것 하나로).

## H. 인쇄 최소 크기(한국어 CPS)

**[TY-23] 모든 글이 0.5 m에서 잉크 높이 ≥ 0.226°(1.97 mm, Noto Sans KR ≥ 6.2 pt)인가?** — 심각도 **blocker**(가장 관대한 거리에서도 기준 미달). 근거: K2·K3, S4, S5, S6 Kim et al. 2024(한국어 MNREAD — 한국어도 CPS 개념이 성립).

**[TY-24] CORE 본문이 1.0 m에서 잉크 높이 ≥ 0.226°(3.94 mm, Noto Sans KR ≥ 12.35 pt)인가?**
- 심각도: 모자란 정도 ≤ 15%(유창 거리 ≥ 0.85 m)면 **minor**, 그보다 크면 **major**.
- 근거: K2·K3·K5, S4("sizes below the critical print size are not found in running text in books or newspapers"), S5.

**[TY-25] 제목·질문·CORE 소제목이 1.5 m에서 잉크 높이 ≥ 0.226°(5.92 mm, Bold ≥ 18.0 pt)인가?** — 심각도 **major**. 근거: K2·K3·K5, S4, S5.

## I. 회전 지명과 글 바탕

**[TY-26] 회전 지명이 |θ| ≤ 45°이고, 평탄화하면 정상 글자로 왼→오른 읽히며(뒤집힘·거울상 없음), 같은 방향 지명끼리 같은 땅 축 변환을 쓰는가?**
- 심각도: 뒤집힘·거울상 **major**, 각도 초과·변환 불일치 **minor**.
- 근거: S7 Wigdor & Balakrishnan 2005(−45°, 0°, 45°에서 짧은 낱말·구 읽기 시간 유의차 없음), S16(회전도 시각 속성).

**[TY-27] 회전 지명이 12 pt 이상이고, 국소 최저 대비 ≥ 4.5:1이며, 다른 지도 요소(해안선·길·물·건물)와 잉크 간격 ≥ 2 pt인가?** — 심각도 **minor**(간격 0 = 겹침이면 TY-28로 판정). 근거: S7, S9("Print only on a solid background"), S4(대비가 낮으면 CPS 상승).

**[TY-28] 모든 수평 글의 글자 밑이 민바탕인가?(3D 물체·길·밭·물결 무늬가 글자 잉크 상자 + 2 pt 안에 들어오지 않는가)**
- 측정: 낱말 단위 바탕 L 표준편차 ≤ **6**(민바탕 2~3.5), 국소 최저 대비 ≥ **4.5:1**, 무늬와 잉크 간격 ≥ **2 pt**.
- 심각도: 무늬가 글자 밑을 지나거나 대비 < 4.5:1이면 **blocker**(BRIEF '겹침'·'기준 수치 미달'), 간격만 0~2 pt면 **minor**.
- 근거: S9 Smithsonian("Print only on a solid background. Overprinting (type on an imaged background) is unreadable…"; 인쇄물 기준 P "No type … printed over other designs, photographs, graphics"), S4(대비·CPS).

## 출처 (모두 직접 열어 확인함, 2022~2026 = 6건)

- S1. W3C Internationalization WG (2026). *Requirements for Hangul Text Layout and Typography (KLREQ)*, Group Note Draft, 21 March 2026. https://www.w3.org/TR/klreq/ (§6.1.3, §7.1.1~7.1.4, §7.2.2, §7.2.3.5, §7.3.1, §7.3.3, §7.4.1, 부록 B)
- S2. W3C CSS WG (2026). *CSS Text Module Level 3*, Candidate Recommendation Draft, 14 August 2026, `word-break: keep-all`. https://www.w3.org/TR/css-text-3/
- S3. 국립국어원 (2017 시행, 2014 개정). 「한글 맞춤법」 부록 「문장 부호」 제4·5·9·10·18항. https://korean.go.kr/kornorms/regltn/regltnView.do?regltn_code=0001&regltn_no=270
- S4. Legge, G. E., & Bigelow, C. A. (2011). Does print size matter for reading? A review of findings from vision science and typography. *Journal of Vision*, 11(5):8. https://pmc.ncbi.nlm.nih.gov/articles/PMC3428264/
- S5. He, Y., Baek, S., & Legge, G. E. (2018). Korean reading speed: Effects of print size and retinal eccentricity. *Vision Research*, 150, 8–14. https://doi.org/10.1016/j.visres.2018.06.013 (PDF: https://legge.dl8.umn.edu/sites/legge.psych.umn.edu/files/files/media/he18_korean_reading_speed-_effects_of_print_size_and_retinal_eccentricity.pdf)
- S6. Kim, U. S., Kim, K. S., & Kim, Y. S. (2024). Korean version of the MNREAD acuity chart. *Scientific Reports*, 14, 7429. https://pmc.ncbi.nlm.nih.gov/articles/PMC10978959/
- S7. Wigdor, D., & Balakrishnan, R. (2005). Empirical investigation into the effect of orientation on text readability in tabletop displays. *ECSCW 2005*. https://www.dgp.toronto.edu/public_user/ravin/papers/ecscw2005_textorientation.pdf
- S8. Butterick, M. *Practical Typography* (온라인판): Line length, Line spacing, Point size, Headings, Mixing fonts, Centered text. https://practicaltypography.com/
- S9. Smithsonian Accessibility Program. *Smithsonian Guidelines for Accessible Exhibition Design* (Fig. 12, leading, ragged right, solid background, 45~55자). https://www.sifacilities.si.edu/sites/default/files/Files/Accessibility/accessible-exhibition-design1.pdf
- S10. Brown, T. (2011). More Meaningful Typography. *A List Apart*, 3 May 2011. https://alistapart.com/article/more-meaningful-typography/
- S11. Wallace, S., Bylinskii, Z., Dobres, J., Kerr, B., Berlow, S., Treitman, R., Kumawat, N., Arpin, K., Miller, D. B., Huang, J., & Sawyer, B. D. (2022). Towards Individuated Reading Experiences: Different Fonts Increase Reading Speed for Different Individuals. *ACM TOCHI*, 29(4), Article 38. https://doi.org/10.1145/3502222
- S12. Minakata, K., Eckmann-Hansen, C., Larsen, M., Bek, T., & Beier, S. (2023). The effect of serifs and stroke contrast on low vision reading. *Acta Psychologica*, 232, 103810. https://doi.org/10.1016/j.actpsy.2022.103810
- S13. Baek, H., Choi, W., & Gordon, P. C. (2023). Reading spaced and unspaced Korean text: Evidence from eye-tracking during reading. *Quarterly Journal of Experimental Psychology*, 76(5), 1072–1085. https://doi.org/10.1177/17470218221104736 (https://scholar.gist.ac.kr/handle/local/10234)
- S14. Shin, J.-H., & Park, M.-Y. (2003). The influences of reading type, line length, and interlinear spacing on the legibility of Korean web documents. *대한산업공학회지*, 29(3), 197–205. https://koreascience.or.kr/article/JAKO200310103403108.pub?orgId=kiie
- S15. Dyson, M. C. (2004). How physical text layout affects reading from screen. *Behaviour & Information Technology*, 23(6), 377–393. https://stu.westga.edu/~ssynan1/literacy/Dyson.pdf
- S16. Brath, R. (2021). *Visualizing with Text*. A K Peters/CRC Press. https://www.routledge.com/Visualizing-with-Text/Brath/p/book/9780367259266 (목차·설명만 확인)
