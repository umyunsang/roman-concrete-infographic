export const meta = {
  name: 'poster-critic-value-field',
  description: 'New 7th field: an independent harsh critic researches value/tonal-structure evidence, builds a rubric, and reviews the poster',
  phases: [{ title: 'Research+Review' }],
}
const L = args.loopDir, R = args.round
const SCHEMA = { type: 'object', properties: {
  field: { type: 'string' }, grade: { type: 'string', enum: ['AAA', 'AA', 'A', 'B', 'C'] }, summary: { type: 'string' },
  rubric_file: { type: 'string' }, sources_count: { type: 'integer' }, checks_total: { type: 'integer' }, checks_failed: { type: 'integer' },
  checks: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, pass: { type: 'boolean' }, evidence: { type: 'string' } }, required: ['id', 'pass', 'evidence'] } },
  findings: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, severity: { type: 'string', enum: ['blocker', 'major', 'minor'] }, title: { type: 'string' }, location: { type: 'string' }, evidence: { type: 'string' }, fix_tool: { type: 'string', enum: ['figma', 'blender', 'copy', 'figma+blender'] }, fix: { type: 'string' } }, required: ['id', 'severity', 'title', 'location', 'evidence', 'fix_tool', 'fix'] } },
  strengths: { type: 'array', items: { type: 'string' } } },
  required: ['field', 'grade', 'summary', 'rubric_file', 'checks', 'findings', 'checks_total', 'checks_failed', 'sources_count'] }
phase('Research+Review')
const r = await agent(`너는 '명암·명도 구성(value / tonal structure)' 분야의 혹독한 비평가다. 이 분야는 이번에 새로 추가됐고, 다른 6개 분야(컬러·인포그래픽·타이포·레이아웃·3D·위계접근성)와 독립적으로 일한다. 수상작 수준(AAA)인지 적대적으로 정밀 검증하되, 측정으로 증명할 수 없는 지적은 내지 않는다.

작업 폴더: ${L}
1) ${L}/BRIEF.md 와 ${L}/STATE.md 의 결정·기각 절을 끝까지 읽는다. 고정 조건 자체는 감점하지 않는다. 기존 루브릭 ${L}/rubrics/color.md(글 대비 CL-13~18 등), illustration3d.md(광원·실루엣·그림자 I3-09~13, I3-25), hierarchy_access.md(H·C 항목)를 훑어 이미 다룬 항목과 겹치지 않게 한다. 네 분야는 '포스터 전체의 명도 설계'다.
2) 근거 조사: WebSearch/WebFetch(지연 로딩이면 ToolSearch로 불러옴)로 명도 구조·명암 위계에 관한 최신 학술·연구·SOTA 자료를 찾는다. 출처 10개 이상, 그중 4개 이상은 2022~2026년. 출발점 예시: 노탄(Arthur Wesley Dow)과 명도 단계(value grouping) 조형 이론, Livingstone 'Vision and Art'의 휘도 채널, Ware 'Information Visualization'의 휘도 대 색상 채널, Itti–Koch 주목도·Bylinskii UMSI/주목도 예측 연구, 흑백·블러(squint) 시험을 쓴 그래픽 위계 연구, 2022~2026 주목도·시각 위계 예측 모델과 포스터·인포그래픽 평가 연구. 실제로 열어 본 자료만 인용한다.
3) 루브릭 작성: ${L}/rubrics/value.md 에 원자적 예/아니오 검사 15~25개를 쓴다. 범위 예: 흑백(휘도만) 변환에서의 위계 보존(콜로세움·제목·CORE가 먼저 잡히는가), 가우시안 블러(squint) 뒤에도 초점이 남는가, 명도 단계 수와 분포(중간 톤 쏠림·평평함), 가장 어두운 곳·가장 밝은 곳이 초점에 모이는가, 주요 물체와 바탕의 명도 대비(그림-바탕 분리), 영역별 명도 균형, DETAIL 모형과 SUPPORT 장면의 명도 위계가 CORE보다 낮은가, 바다·땅·하늘(종이) 큰 면의 명도 관계, 인쇄 시 중간 톤 붕괴 위험 등. 항목마다 [ID] 질문형 기준 · 측정 방법과 합격 수치 · 실패 시 심각도 · 근거 출처. 다음 라운드의 다른 비평가가 그대로 재현할 수 있게 쓴다.
4) 심사: 자료는 ${L}/r${R}/poster_1x.png, ${L}/r${R}/poster_2x.png, ${L}/r${R}/map_only_2x.png(글 없는 지도), ${L}/r${R}/tiles/*.png, ${L}/text_spec_r${R}.json. Python(uv run --no-project --with pillow --with numpy --with scipy python -I …)으로 CIELAB L*, 블러, 히스토그램, 주목도 근사 등을 직접 잰다. 측정용 임시 파일은 너의 스크래치패드에만 쓴다.
5) 파일은 rubrics/value.md 하나만 쓴다. 항목별 판정과 증거는 결과의 checks 배열에 담는다. 등급은 BRIEF 기준(AAA = blocker 0 · major 0 · minor ≤ 2)을 그대로 적용하고, 지적마다 수치가 있는 해법(Blender 재질·조명·노출, Figma 색 등)을 준다.
읽기 전용: Figma·Blender·포스터 파일을 고치지 않는다. 최종 출력은 스키마에 맞춘 구조화 결과다(field="value").`, { label: 'critic:value', phase: 'Research+Review', schema: SCHEMA })
return r
