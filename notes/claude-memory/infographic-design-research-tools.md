---
name: infographic-design-research-tools
description: "인포그래픽 디자인 단계용 설치 스킬(color-expert 등)과 학술 근거 규칙 — 2026-10-07 조사·설치 결과, 미설치 사유 포함"
metadata:
  node_type: memory
  type: reference
  originSessionId: e6101edd-22a2-4787-95db-be2ff209cf5a
  modified: 2026-10-07T01:09:53.947Z
---

로마 콘크리트 포스터([[colosseum-poster-mindmap]])를 흑백 스케치에서 디자인 단계로 넘기려고 2026-10-07에 조사·설치한 것. **같은 날 사용자가 디자인을 3D 에셋 배치(Unity/Blender/Meshy)로 한다고 밝혀, 아래 2D용 스킬(diagram-design·baoyu)은 보조로 밀려남 — 3D 파이프라인 조사는 research/pipeline3d.md.** 조사 원문은 그날 세션 scratchpad `research/academic.md`·`ecosystem.md`(tmp라 재부팅 시 사라짐).

**설치함(모두 SKILL.md·스크립트 직접 검증 후)**
- `~/.claude/skills/color-expert`(meodai, 마크다운만): 인쇄 팔레트·OKLCH·APCA·고대 안료사(아펠레스 4색).
- 플러그인 `diagram-design@diagram-design`(cathrynlavery, 커밋 d137637, 훅·MCP 없음): 액소노메트릭·분해도 SVG → `createNodeFromSvg`로 Figma에. 2:1 투영이라 30° 아이소와 다름.
- `~/.claude/skills/anydesign`(uxKero d81bd89, examples 제외): 이미지·Figma에서 팔레트·타입 토큰 추출.
- `~/.claude/skills/baoyu-infographic`(JimLiu/baoyu-skills의 그 폴더만): **`disable-model-invocation: true`로 바꿔 설치** — 그대로 두면 '인포그래픽' 요청을 Codex 래스터 생성으로 끌고 감. 전체 플러그인은 쿠키 쓰는 비공식 Gemini·SNS 자동 게시 스킬이 있어 설치 금지.

**2차 설치(10/7 20시, 사용자 요청 "폰트·배색 작업용 OSS를 star 위주로 설치")** — 모두 얕은 clone 후 훅·원격 호출 grep 검사, 필요한 폴더만 `~/.claude/skills/`로 복사
- anthropics/skills(18만★) `canvas-design`(포스터·OFL 폰트 묶음)·`theme-factory`(색+글꼴 테마 10종)
- ui-ux-pro-max(13만★, v2.13.0, 477bcb2) — ECC 사본(~/.agents/skills)보다 최신. 글꼴 짝 DB는 쓸 만함, **색 DB는 웹 제품용이라 '고대·석재' 검색 0건** → 색은 color-expert 우선
- taste-skill(9.3만★) `design-taste-frontend`·`minimalist-ui`·`industrial-brutalist-ui`만(이미지 생성 계열 제외)
- impeccable(7.8만★, bbcb29d) **스킬 폴더만, 플러그인 훅 제외**(훅은 매 Edit/Write·Stop마다 바이너리 실행). 스킬 자체가 세션당 1회 런처로 GitHub 릴리스 바이너리를 sha256 검증 후 받음 — colorize·typeset·layout 명령
- hallmark(3만★), AntV `infographic-creator`·`infographic-syntax-creator`(7천★; 저장소 개발용 3개 제외)
- designer-skills(2.9천★) 마켓플레이스 플러그인 `ui-design`·`visual-critique`(훅·MCP 0) — critique-typography/color/composition/visual-hierarchy
- `typography`(danium/practicaltypography, 29★) — 별은 적지만 유일한 인쇄 타이포(Butterick) 기준이라 예외로 설치
- 2차 미설치: open-design(10만★, Node 24 데몬 앱 + `od` MCP, 스킬은 위와 중복), awesome-design-md(웹 브랜드 DESIGN.md 모음), huashu-design(영상·HTML 중심, ByteDance 클라우드 TTS·리뷰 API), Figma 비공식 MCP들(공식 커넥터와 중복), mcp-server-chart(원격 렌더 서비스로 데이터 전송). 한글 무료 글꼴 목록은 naen-nae/naen-nae(139★) 참고용

**1차 미설치(위 2차에서 일부 설치로 바뀜)**: 공식 Figma 플러그인(스킬 14개가 커넥터 `get_figma_skill`과 동일, 자체 `.mcp.json` 때문에 도구 이름이 `mcp__plugin_figma_figma__*`로 바뀌거나 OAuth 재요구 가능 → 루프 도중 설치 금지, 사용자 확인 대기). ui-ux-pro-max·impeccable(매 편집 바이너리 훅)·taste-skill·superdesign·AntV는 웹 UI용이거나 원격 의존. 한국어 타이포 스킬은 쓸 만한 것 없음 → 원천은 W3C KLREQ.

**바로 쓸 학술 근거**
- Lu et al. CHI 2020 시각 정보 흐름: 고리형은 기본이 **시계 방향**, 다른 방향이면 명시 신호 필요. 우리 ❶~❺는 10→9→6→3→12시 **반시계** → 디자인 단계에서 길에 방향 표시(화살촉·셰브런) 넣을 것.
- Wigdor & Balakrishnan 2005: ±45° 안 기운 글 6~8% 느림, 90°면 구절 54% 느림 → 교수님 '각도 최소화' 피드백의 수치 근거.
- Li·Agrawala SIGGRAPH 2007 절개도 규칙(축 정렬 절단, 계단식 절개, 단면 가장자리만 어둡게) → 확대 모형 그림 문법.
- Harrison CHI 2015: 첫인상 500ms, 복잡도보다 색이 호감 좌우. Song VIS 2025: 만화체·손글씨는 신뢰도 하락 → 근거·원리는 깔끔한 기술 도해체.
- 판정 루프 개선안: 1~5점 대신 원자적 예/아니오 체크리스트(IGenBench·BizGenEval), 짝 비교 유지, Paper2Poster PaperQuiz(포스터만 보고 문제 풀기), 생성 모델과 다른 계열 심사관(Codex 등).
- 한국어 글과 사실은 Figma에서 조판 — 이미지 생성 모델은 글 정확도가 낮음(문항 90% vs 작품 전체 49%).
