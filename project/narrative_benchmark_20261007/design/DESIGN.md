# 로마 콘크리트 · 컬러와 타이포 v11

이 문서는 전체 배색·타이포의 기반인 v11 기록이다. 최신 부위별 재질 적용은 [v12 기준](PART-MATERIALS.md), [현재 포스터](https://www.figma.com/design/jQPriO85F6wtPy1NPo752p/?node-id=737-78)를 참고한다.

현재 결과: [편집형 포스터](https://www.figma.com/design/jQPriO85F6wtPy1NPo752p/?node-id=728-241), [편집형 배색 가이드](https://www.figma.com/design/jQPriO85F6wtPy1NPo752p/?node-id=728-360), [실제 Figma PNG](../out/figma_poster_v11_color_2x.png).

전체는 석회·트래버틴의 따뜻한 바탕으로 묶고, 중앙 콜로세움의 갈색을 주변 유적보다 진하게 두었다. 제작·발열의 적갈색과 물·연구의 청록색은 코어 장면과 강조 문장에서 반복된다. 현대 골조는 청회색으로 구분하고 나무·산·농경지는 낮은 채도의 보조색으로 정리했다.

| 역할 | 모형과 바탕 색 | 글자용 강조 색 |
| --- | --- | --- |
| 바탕·지형 | #F3E8D4 · #EDE1CB | 제목 #2E2A22 · 본문 #3E3A31 |
| 중앙 콜로세움·주변 유적 | #CDA477 · #D3BE9E | 보조 글 #615A4E |
| 현대 골조·현대 실험 | #657B88 · #527882 | #365864 |
| 배합·발열 | #D15B36 | #983821 |
| 석회 시편·칼슘·충전 결정 | 모재 #97614B · 흰 부분 #FFF4DD | #784C26 |
| 물의 작용·바다와 강 | #3F9DAA · #82B9BC | #195B61 |

석회 알갱이, 칼슘, 최종 충전 결정의 흰색을 통일해 같은 재료가 이어진다는 단서를 유지했다. 장면 색은 실제 재료의 측정 색이 아니라 서사 역할을 표현한다. 작은 글은 모형과 같은 계열의 더 짙은 색을 쓴다. 하단 바다 위의 사례·연대는 본문 색으로 읽힌다.

큰 제목은 **Noto Serif KR Bold, 70px / 행간80px / 자간−1%**이다. 고전 건축물 헤더와 어울리는 명조 계열을 사용했고, 실제 Figma에서 자연 너비419px가 기존455px 상자에 들어감을 확인했다. 질문은 Noto Sans KR Bold20px를 유지한다. 코어 제목은 Noto Sans KR Bold21px / 행간26px, 코어 본문은 Regular11.5px / 행간15.5px이다. 나머지 지명·보조 글은 현재 크기와 모든 상자 위치를 유지했다.

Figma에는 포스터 전용 **38개 원색 + 38개 의미 변수, 4개 텍스트 스타일**을 만들었다. 의미 변수는 원색 변수의 alias이며 95개 포스터 TEXT의 fill이 변수에 연결되어 있다. 기존 마인드맵 변수 컬렉션은 유지했다. [JSON](design-tokens.json)과 [CSS](design-tokens.css)에도 같은 값을 기록했다. 편집형 가이드는 포스터 밖의 별도 프레임이다.

Blender v7은 기존 Workbench OBJECT 색 모드를 유지해 보이는227개 모형의 object.color를 배색했다. sRGB HEX를 scene-linear로 변환했고, Standard·기존Studio·shadow·cavity를 유지하면서 노출을+.7, World 배경을 크림색으로 조정했다. **317개 객체의 형상·변환·배치·가시성·카메라는 v6와 동일**하다. v6와 원본 파일도 보존했다. 색상은 Workbench 렌더용이며 재질을 새로 생성한 것은 아니다.

실제 2382×3368 Figma 출력, 전체1x, 코어·바다 확대와 가이드를 검토했다. 새 작은 강조색의 렌더 배경 사각형 p10 대비는 약4.9–5.7이며, 하단 본문은 약4.8이다. 회전 지명·실제 글리프·안티앨리어싱을 계산하지 않은 진단값이므로 공식 WCAG 인증으로 해석하지 않는다. 폰트 누락·범위 밖 글·alias 오류는0, 현재95개 문구와 모든 텍스트 경계는 동일하다. 이는 시각·파일 검증이며 독자 이해도 실험은 아니다.

사용 도구: design-system·brand·figma-use·figma-generate-library 스킬, 공식 Figma MCP의 Plugin API·변수·타입 스타일·에셋 업로드/내보내기, Blender 렌더. 기존 Meshy 모형을 그대로 사용했다. 새 모델 생성 작업은 없다.

재현 근거: [Blender 저장본 검증](../out/v7-color-saved-validation.md), [최종 시각 검토](../out/v11-final-color-qa.md), [Figma 실제 검증](../out/figma-v11-color-final-validation.json), [전달 기록](../out/delivery-receipt-v11.json).
