# 루브릭 · 인포그래픽(정보 설계·서사)

- 대상: 로마 콘크리트 A2 세로 포스터(Figma 1191×1684pt, 1pt = 1px).
- 작성: 라운드 1 인포그래픽 비평가. 다음 라운드 비평가도 이 루브릭을 그대로 쓴다.
- 판정 규칙: 항목마다 예/아니오만 판정하고, 증거(pt 좌표, text_spec 값, 측정값)를 남긴다. 한 결함이 여러 항목에서 걸리더라도 지적(finding)은 하나로 묶는다(BRIEF 6절).
- 고정 조건(BRIEF 3절)은 판정 대상이 아니다. 고정 조건을 깨는 해법은 쓰지 않는다.
- 공통 측정 도구: `text_spec_r<N>.json`(글 위치·크기·색), `r<N>/poster_2x.png` 픽셀 측정. 거리는 글 상자 왼쪽 위 기준 유클리드 거리(pt)이고, 물체 경계 상자는 배경 #E4D9C4 근처(RGB 차 합 > 28)로 잰다.
- 용어: CORE ①~⑤, BASIC(전제 2개), DETAIL(원리 모형+설명), SUPPORT(사례·근거). 역할 구분은 BRIEF 2절을 따른다.

## A. 질문 → 답 서사

**[INF-01] 포스터 질문이 맨 위에서 질문 문장으로 보이는가?**
- 측정: text_spec에서 물음표로 끝나는 제목급 문장의 크기와 y.
- 합격: 크기 ≥ 18pt, 상자 y ≤ 253pt(높이의 15%).
- 실패 시: major.
- 근거: Erren & Bourne 2007 규칙 2·3(10초 안에 붙잡는 제목). Borkin et al. 2016(제목은 위에 있을 때 더 많이 응시되고, 제목과 글이 메시지를 전해야 함).

**[INF-02] 제목 질문에 대한 답이 결과형 문장 하나로 명시되어 있는가?**
- 측정: 80개 글 전체에서 질문의 핵심어(금·메움·버팀 가운데 둘 이상)를 쓴 결과형(완료·단정) 문장을 찾는다. 이 문장은 CORE 제목이나 ⑤ 본문에 있어야 한다.
- 합격: 그런 문장이 1개 이상, 길이 ≤ 30자.
- 실패 시: major.
- 근거: Borkin et al. 2016. Kim, Setlur & Agrawala 2021(글이 강조한 내용이 독자의 결론이 됨). Stokes et al. 2022(어떤 정보는 제목에 둘 때 가장 잘 전달됨).

**[INF-03] CORE 제목(두 줄)만 차례로 읽어도 원인 → 기제 → 검증 결과가 재구성되는가?**
- 측정: CORE 제목 10줄에 다음 명제가 들어 있는지 센다. (p1) 생석회와 물이 열을 냄. (p2) 흰 알갱이는 칼슘 공급원. (p3) 물이 칼슘을 옮겨 금을 메움. (p4) 실험에서 금이 실제로 메워짐.
- 합격: 4개 가운데 3개 이상.
- 실패 시: major. INF-02와 같은 결함이면 지적은 하나로 묶는다.
- 근거: Borkin et al. 2016. Paper2Poster 2025(포스터가 핵심 내용을 전하는지 퀴즈로 잼). Erren & Bourne 2007 규칙 2.

**[INF-04] CORE ①이 대비(현대 철근 콘크리트)로 문제를 세우고, 질문을 재료로 좁히는가?**
- 측정: ① 제목과 본문 문장 확인.
- 합격: 대비 문장 1개와 좁힌 질문 1개가 있음.
- 실패 시: minor.
- 근거: Segel & Heer 2010(작가 주도 서사의 도입). Bach et al. 2018(서사 설계 패턴: 흐름과 몰입).

**[INF-05] 이웃한 CORE 본문끼리 앞 단계에서 나온 핵심어를 이어받는가?**
- 측정: ①→②, ②→③, ③→④, ④→⑤ 네 전이마다 공통 핵심어가 있는지 본다.
- 합격: 4/4.
- 실패 시: major.
- 근거: Segel & Heer 2010. Lu et al. 2020(시각 정보 흐름 VIF는 요소를 차례로 잇는 의미 구조).

**[INF-06] 어떤 CORE의 '반전'이나 결론을, 읽는 순서상 그보다 먼저 오는 비CORE 글이 미리 말하지 않는가?**
- 측정: 각 CORE의 결론 명제가 다른 역할의 글에 있는지 찾는다. 있으면 위치를 비교한다. 같은 가로 띠(±40pt)에서 더 왼쪽에 있거나, 경로상 앞 CORE와 그 CORE 사이에 있으면 '먼저 읽힘'으로 본다.
- 합격: 0건.
- 실패 시: minor.
- 근거: Bach et al. 2018. Segel & Heer 2010(작가 주도 순서).

## B. 읽는 순서 신호

**[INF-07] CORE에 1~5 번호 원판이 하나씩 있고, 지름 ≥ 14pt이며, 제목 첫 줄 바로 왼쪽(간격 ≤ 8pt)에 있는가?**
- 측정: 원판 경계 상자를 픽셀로 잼.
- 합격: 5/5.
- 실패 시: major.
- 근거: Erren & Bourne 2007 규칙 7(화살표·번호로 시선을 처음부터 끝까지 이끔). Lu et al. 2020.

**[INF-08] 붙어 있지 않은 CORE 전이(①→②, ②→③, ④→⑤)마다 방향 표시가 있고, 다음 CORE를 ±30° 안으로 가리키는가?**
- 측정: 이정표 화살 판의 방향과 다음 CORE 제목 쪽 벡터의 각도 차. ③→④는 같은 가로 띠(제목 y 차 ≤ 60pt)에서 왼쪽→오른쪽이면 표시가 없어도 합격.
- 합격: 3/3.
- 실패 시: major.
- 근거: Erren & Bourne 2007 규칙 7. Lu et al. 2020.

**[INF-09] 이웃한 CORE 제목 사이 거리가 모두 ≤ 600pt이고, 경로가 스스로 교차하지 않는가?**
- 측정: text_spec 제목 상자 좌표.
- 합격: 4/4이고 교차 0.
- 실패 시: minor.
- 근거: Lu et al. 2020. Schroeder & Cenkci 2018(관련 정보 사이의 거리는 학습 비용).

**[INF-10] CORE 제목 크기가 DETAIL·SUPPORT 제목 가운데 가장 큰 것의 1.5배 이상인가?**
- 측정: text_spec 크기 비.
- 합격: ≥ 1.5.
- 실패 시: major.
- 근거: Schneider et al. 2018(구조를 드러내는 신호의 효과 g = 0.53). Mayer 2005(신호 원리).

## C. 정보 역할 구분

**[INF-11] 역할마다 제목 양식(크기·굵기·색·머리말)이 역할 안에서 같고, 다른 역할과 위치 말고도 한 가지 이상 다른가?**
- 측정: text_spec에서 DETAIL 제목 4개와 SUPPORT 제목 전부의 크기·굵기·hex·머리말을 표로 만든다.
- 합격: 역할 안 불일치 0, 역할 사이 구분 속성 ≥ 1.
- 실패 시: major.
- 근거: Qu & Hullman 2018(같은 대상은 같은 부호, 다른 대상은 다른 부호). Schneider et al. 2018.

**[INF-12] CORE 색 #983821이 글 노드 가운데 CORE에만 쓰이는가?**
- 측정: text_spec에서 hex가 #983821인 노드 목록.
- 합격: CORE(제목 둘째 줄) 말고는 0개.
- 실패 시: major. INF-11과 같은 결함이면 묶는다.
- 근거: Qu & Hullman 2018(C2.3·C2.4: 서로 다른 필드는 색이 겹치면 안 됨).

**[INF-13] DETAIL이 자기가 설명하는 대상 가까이에 있는가?**
- 측정: CORE 본문의 핵심 개념(생석회·열·석회 알갱이·칼슘·금 메움)을 설명하는 DETAIL은 그 CORE 제목과의 거리를 잰다. CORE에 없는 개념을 다루는 DETAIL은 같은 현상을 보여 주는 SUPPORT와의 거리를 잰다. 대응 CORE와 SUPPORT가 모두 없는 DETAIL은 판정에서 뺀다.
- 합격: 해당 DETAIL 모두 ≤ 350pt이거나 리더선·번호로 연결됨.
- 실패 시: major.
- 근거: Mayer 2005(공간 근접 8/8 시험, 중앙 효과 크기 1.11). Schroeder & Cenkci 2018(58개 비교, g = 0.63).

**[INF-14] SUPPORT 이름표마다 대상 물체와 리더선으로 이어져 있거나 20pt 안에 있고, 이름표의 명사(조각·장면·모형)가 물체 종류와 맞는가?**
- 측정: 리더선 유무, 간격, 명사와 물체를 대조.
- 합격: 전부.
- 실패 시: minor.
- 근거: Mayer 2005. IGenBench 2026(주석·콜아웃이 맞는지 원자 문항으로 확인).

## D. 글과 그림의 통합

**[INF-15] CORE마다 60pt 안에 그림이 있고, 그 그림이 제목 둘째 줄의 핵심 대상이나 사건을 보여 주는가?**
- 측정: ① 금(균열), ② 열, ③ 흰 알갱이, ④ 칼슘 이동·금 메움, ⑤ 생석회 있음/없음 비교. 각각이 그림에 보이는지 확대해서 확인한다.
- 합격: 5/5.
- 실패 시: major.
- 근거: Mayer 2005. Borkin et al. 2016(글과 그림이 같은 메시지를 되풀이할 때 전달이 잘 됨). Kim et al. 2021.

**[INF-16] 단계 모형에서 단계 이름표마다, 그 단계 그림에 이름표가 말하는 변화가 보이는가?**
- 측정: 이름표와 그 아래 그림의 상태를 짝지어 비교한다(물 표시 유무, 흰 알갱이 크기, 금 채움). 이름표 중심 x와 해당 그림 표시의 x를 픽셀로 잰다.
- 합격: 모든 단계에서 일치.
- 실패 시: major. 그림이 글과 반대로 말하면 blocker.
- 근거: Heiser & Tversky 2006(화살표·변화 표시가 있어야 그림이 구조 대신 기능·인과로 읽힘). Mayer 2005.

**[INF-17] 과정·인과 모형의 단계 사이에 방향 화살표가 있는가?**
- 측정: 모형마다 확인.
- 합격: 과정 모형 전부.
- 실패 시: minor.
- 근거: Heiser & Tversky 2006.

**[INF-18] CORE·DETAIL 글 상자에서 60pt 안에 있는 3D 건물·장치 가운데, 이름표가 없거나 그 글에 나오지 않는 것이 하나도 없는가?**
- 측정: 물체 경계 상자와 글 상자의 거리. 나무·밭·길·물결 같은 바탕 요소는 뺀다.
- 합격: 0개.
- 실패 시: minor.
- 근거: Mayer 2005(일관성 원리: 군더더기를 빼면 학습이 깊어짐, 중앙 효과 크기 1.32). IGenBench 2026(장식 요소 문항). Lu et al. 2020.

## E. 정확성·과장

**[INF-19] 사실 문장(수치·연대·기제)이 1차 연구나 기관 발표와 어긋나지 않는가?**
- 측정: 문장마다 출처와 대조해 모순·부정확·확인 불가로 분류한다.
- 합격: 모순 0, 부정확 ≤ 1.
- 실패 시: 모순이면 blocker, 부정확이 2건 이상이면 minor.
- 근거: MIT News 2023(Seymour et al. 2023, Science Advances). MIT News 2025(Nature Communications 2025). Utah News 2017(Jackson et al. 2017, American Mineralogist). Song et al. 2025(신뢰는 정보 신뢰성에 좌우됨).

**[INF-20] 대표 건물(콜로세움)에서 직접 입증되지 않은 기제와 개념 모형이 그렇다고 표시되어 있는가?**
- 측정: '직접 입증 안 됨', '개념 모형' 같은 표시가 있는지 본다.
- 합격: 있음.
- 실패 시: major.
- 근거: Song et al. 2025. Liu et al. 2026(가정을 명시하라는 권고).

**[INF-21] 모호한 연도에 기원(서기·기원전)이 붙어 있고, 지도가 담겠다고 한 실제 장소가 고유명으로 표시되어 있는가?**
- 측정: 연도 글과 지명 글 목록. 대상 장소는 BRIEF 고정 조건 4(아펜니노·티베르강·티레니아해·베수비오·폼페이·아피아 가도·수도교).
- 합격: 모호한 연도 0, 고유명 누락 ≤ 1.
- 실패 시: minor.
- 근거: IGenBench 2026(제목·주석 정확성 문항). Erren & Bourne 2007 규칙 8.

## F. 정보량·인지 부하

**[INF-22] 같은 사실 명제를 두 글 상자에서 되풀이하지 않는가?**
- 측정: 두 글 상자의 내용어가 60% 이상 겹치고 같은 명제를 말하면 중복으로 센다.
- 합격: 0쌍.
- 실패 시: major.
- 근거: Mayer 2005(일관성 원리). Sweller et al. 1998(작업 기억 용량 한계). Schroeder & Cenkci 2018(글과 그림이 서로 보완할 때 g = 0.72).

**[INF-23] 한 개념을 한 용어로 쓰고, 서로 다른 두 개념에 같은 용어를 쓰지 않는가?**
- 측정: 같은 대상을 부르는 이름 수와, 다른 대상을 같은 이름으로 부르는 경우를 센다.
- 합격: 같은 대상의 동의어 ≤ 1쌍(본문에서 이어 줌), 다른 대상의 같은 이름 0.
- 실패 시: minor.
- 근거: Qu & Hullman 2018(부호 일관성). Sweller et al. 1998.

**[INF-24] 부가 설명(DETAIL·SUPPORT 본문)은 2줄 이하, CORE 본문은 3줄 이하인가?**
- 측정: text_spec의 줄바꿈 수.
- 합격: 전부.
- 실패 시: minor.
- 근거: Erren & Bourne 2007 규칙 8(말을 아끼라는 권고). Paper2Poster 2025(글이 지저분하면 퀴즈 점수가 낮음).

**[INF-25] 포스터만 보고 다음 다섯 문항에 답할 수 있는가?**
- 문항: (q1) 왜 열이 나는가? (q2) 흰 알갱이는 무엇인가? (q3) 금은 어떻게 메워지는가? (q4) 효과를 보여 준 증거는 무엇인가? (q5) 어디서 관찰했는가?
- 측정: 문항마다 답이 되는 글 상자를 찾는다.
- 합격: 5/5.
- 실패 시: 3/5 이하면 major, 4/5면 minor.
- 근거: Paper2Poster 2025(PaperQuiz). IGenBench 2026(원자적 예/아니오 문항). BizGenEval 2026(사람이 검증한 체크리스트 문항).

## G. 기억성

**[INF-26] 사람이 알아보는 물체·사람 모형과 색이 있고, 흔한 차트 형식이 아닌가?**
- 측정: 눈으로 확인.
- 합격: 세 조건 모두.
- 실패 시: minor.
- 근거: Borkin et al. 2013(색과 사람이 알아보는 물체가 기억성을 높이고, 흔한 그래프는 덜 기억됨).

**[INF-27] 핵심 기제(금이 메워지는 원리)가 글과 그림 양쪽에 다 있는가?**
- 측정: CORE 글과 원리 모형이 둘 다 있는지 본다.
- 합격: 둘 다 있음.
- 실패 시: major.
- 근거: Borkin et al. 2016(메시지를 여러 경로로 되풀이하면 전달에 유리).

## 출처(실제로 열어 본 자료)

1. Borkin, M. A., Vo, A. A., Bylinskii, Z., Isola, P., Sunkavalli, S., Oliva, A., Pfister, H. (2013). What Makes a Visualization Memorable? IEEE TVCG (InfoVis 2013). https://vcg.seas.harvard.edu/publications/20130101-what-makes-a-visualization-memorable
2. Borkin, M., Bylinskii, Z., Kim, N., Bainbridge, C., Yeh, C., Borkin, D., Pfister, H., Oliva, A. (2016, 온라인 2015). Beyond Memorability: Visualization Recognition and Recall. IEEE TVCG 22(1). https://vcg.seas.harvard.edu/publications/20150101-beyond-memorability-visualization-recognition-and-recall
3. Segel, E., Heer, J. (2010). Narrative Visualization: Telling Stories with Data. IEEE TVCG (InfoVis). https://idl.uw.edu/papers/narrative
4. Lu, M., Wang, C., Lanir, J., Zhao, N., Pfister, H., Cohen-Or, D., Huang, H. (2020). Exploring Visual Information Flows in Infographics. CHI 2020. https://vcg.seas.harvard.edu/publications/20200301-exploring-visual-information-flows-in-infographics
5. Bach, B., Stefaner, M., Boy, J., Drucker, S., Bartram, L., Wood, J., Ciuccarelli, P., Engelhardt, Y., Koeppen, U., Tversky, B. (2018). Narrative Design Patterns for Data-Driven Storytelling. In Data-Driven Storytelling (CRC Press), 5장. https://www.microsoft.com/en-us/research/publication/narrative-design-patterns-for-data-driven-storytelling/
6. Mayer, R. E. (2005). Principles for Reducing Extraneous Processing in Multimedia Learning: Coherence, Signaling, Redundancy, Spatial Contiguity, and Temporal Contiguity Principles. Cambridge Handbook of Multimedia Learning, 12장. 일관성 10/11 시험·중앙 효과 크기 1.32, 신호 3/3·0.60, 공간 근접 8/8·1.11. https://www.cambridge.org/core/books/abs/cambridge-handbook-of-multimedia-learning/principles-for-reducing-extraneous-processing-in-multimedia-learning-coherence-signaling-redundancy-spatial-contiguity-and-temporal-contiguity-principles/C98AB3A6CE760DD63C048936EA0B3B44
7. Schroeder, N. L., Cenkci, A. T. (2018). Spatial Contiguity and Spatial Split-Attention Effects in Multimedia Learning Environments: a Meta-Analysis. Educational Psychology Review 30(3), 679–701. 58개 비교, g = 0.63, 보완형 정보 g = 0.72. TUM Clearinghouse 요약으로 확인: https://www.clearinghouse.edu.tum.de/wp-content/uploads/2019/06/CHU_KR-23_Schroeder-2018_Lernmaterial.pdf
8. Schneider, S., Beege, M., Nebel, S., Rey, G. D. (2018). A meta-analysis of how signaling affects learning with media. Educational Research Review 23, 1–24. 회상 g = 0.53, 전이 g = 0.33, 인지 부하 g = 0.25. TUM Clearinghouse 요약으로 확인: https://www.clearinghouse.edu.tum.de/wp-content/uploads/2018/12/CHU_KR-22_-Schneider_2017_Lernmaterial_Hervorhebungen.pdf
9. Sweller, J., van Merriënboer, J. J. G., Paas, F. G. W. C. (1998). Cognitive Architecture and Instructional Design. Educational Psychology Review 10(3), 251–296. https://research.utwente.nl/en/publications/cognitive-architecture-and-instructional-design/
10. Heiser, J., Tversky, B. (2006). Arrows in Comprehending and Producing Mechanical Diagrams. Cognitive Science 30(3), 581–592. https://www.tc.columbia.edu/faculty/bt2158/faculty-profile/files/sincomprehendingandproducingmechanicaldiagrams.PDF
11. Qu, Z., Hullman, J. (2018). Keeping Multiple Views Consistent: Constraints, Validations, and Exceptions in Visualization Authoring. IEEE TVCG 24(1). https://idl.uw.edu/papers/consistency
12. Kim, D. H., Setlur, V., Agrawala, M. (2021). Towards Understanding How Readers Integrate Charts and Captions: A Case Study with Line Charts. CHI 2021. https://hci.stanford.edu/publications/paper.php?id=429
13. Erren, T. C., Bourne, P. E. (2007). Ten Simple Rules for a Good Poster Presentation. PLoS Computational Biology 3(5), e102. https://pmc.ncbi.nlm.nih.gov/articles/PMC1876493/
14. Stokes, C., Setlur, V., Cogley, B., Satyanarayan, A., Hearst, M. (2022). Striking a Balance: Reader Takeaways and Preferences when Integrating Text and Charts. IEEE TVCG (VIS 2022). https://arxiv.org/abs/2208.01780
15. Pang, W., Lin, K. Q., Jian, X., He, X., Torr, P. (2025). Paper2Poster: Towards Multimodal Poster Automation from Scientific Papers. arXiv 2505.21497. https://arxiv.org/abs/2505.21497
16. Tang, Y. 외 (2026). IGenBench: Benchmarking the Reliability of Text-to-Infographic Generation. arXiv 2601.04498. 원자적 예/아니오 문항, 10개 문항 유형. https://arxiv.org/html/2601.04498v1
17. Li, Y., Zeng, Z. 외 (2026). BizGenEval: A Systematic Benchmark for Commercial Visual Content Generation. arXiv 2603.25732. https://arxiv.org/abs/2603.25732
18. Song, H., Cho, A., Bearfield, C. X., Stasko, J. (2025). Visualizing Trust: How Chart Embellishments Influence Perceptions of Credibility. IEEE VIS 2025. https://aa.ieeevis.org/year/2025/program/paper_de570d65-b80f-4e25-9d54-88f11281e2c5.html
19. Liu, X., Sreekanth, V., Patel, V., Muzumdar, S., Lopez, D., Yang, F., Liu, Z. (2026). What Do We Mean When We Talk About Infographics? IEEE VIS 2026 단편 논문, arXiv 2608.12370. https://arxiv.org/abs/2608.12370
20. MIT News (2023-01-06). Riddle solved: Why was Roman concrete so durable? Seymour, L. M. 외 (2023), Hot mixing: Mechanistic insights into the durability of ancient Roman concrete, Science Advances 9, eadd1602 소개 기사. https://news.mit.edu/2023/roman-concrete-durability-lime-casts-0106
21. MIT News (2025-12-09). An unfinished Pompeian construction site reveals ancient Roman building technology, Nature Communications 2025 소개 기사. https://news.mit.edu/2025/pompeii-offers-insights-ancient-roman-building-technology-1209
22. University of Utah News (2017). Jackson, M. D. 외 (2017), Phillipsite and Al-tobermorite mineral cements produced through low-temperature water-rock reactions in Roman marine concrete, American Mineralogist 102(7) 소개 기사. https://unews.utah.edu/articles/roman-concrete/

- 2022~2026년 자료: 14, 15, 16, 17, 18, 19, 20, 21번(8개).
- 주: 과제에서 예로 든 Mayer 3판(2021)은 열어 보지 못했다. 그래서 실제로 연 2005년 장(같은 원리와 효과 크기)을 인용한다.
