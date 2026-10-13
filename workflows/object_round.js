export const meta = {
  name: 'poster-object-critics',
  description: 'Per-object review: for each visual-design field a harsh critic builds/uses an object rubric and judges every placed Blender asset (batched), blind to earlier rounds',
  phases: [{ title: 'Rubrics', detail: 'one rubric author per field (first round only)' }, { title: 'Object review', detail: 'field x asset-batch critics' }],
}
// args: { loopDir, objDir, round, fields?: [keys], batches: [[assetId,...],...], makeRubrics: bool }
const L = args.loopDir, D = args.objDir, R = args.round
const FIELDS = [
  { key: 'obj_color', name: '물체 컬러(재질 색·팔레트)', focus: '재질 색이 역할·재료·시대에 맞는지, 포스터 팔레트(STATE·palette_*.json)와 일관된지, 강조색 #983821이 CORE 밖에 새지 않는지, 같은 재료는 같은 색인지, 색이 얼룩·잘못 칠한 면 없이 깨끗한지' },
  { key: 'obj_value', name: '물체 명암·명도', focus: '면(윗면/왼면/오른면) 명도 단계, 주변 배경과의 그림-바탕 명도 차, 그림자·접지 어둠, 물체 안 디테일(금·알갱이·이랑 등)의 명도 대비가 읽히는지' },
  { key: 'obj_form', name: '물체 3D 형태·조형', focus: '실루엣이 무엇인지 바로 읽히는지, 실제 대상(로마 시대 실제 장소·건물·도구)과 형태·비례가 맞는지(사실 오류는 blocker), 메시 결함(떠 있는 조각, 구멍, 찢김, 스캔 지느러미, 각진 패싯, z-fighting), 축척 일관성' },
  { key: 'obj_info', name: '물체 인포그래픽(의미 전달)', focus: '그 물체가 포스터 서사에서 맡은 개념을 전하는지(이름표·본문과 일치), 단계 그림(④ 큐브 등)의 변화가 읽히는지, 같은 개념은 같은 시각 부호인지, 오해를 부르는 요소가 없는지' },
  { key: 'obj_hier', name: '물체 시각 위계', focus: '역할(CORE > DETAIL > SUPPORT > BASIC > 지물 > 배경)에 맞는 크기·대비·채도·디테일 밀도인지, 배경 지물이 CORE보다 눈을 끌지 않는지' },
  { key: 'obj_place', name: '물체 배치·구성', focus: '땅에 제대로 서 있는지(떠 있음·묻힘), 이웃 물체·길·강·이름표와의 간격(겹침·4pt 미만 근접), 방향(정면·현관 방향 등), 이웃과의 축척 관계, 길·이정표와의 관계, 장면 전체 구성 속 자리의 타당성' },
]
const SCHEMA = { type: 'object', properties: {
  field: { type: 'string' }, batch: { type: 'integer' }, summary: { type: 'string' },
  assets: { type: 'array', items: { type: 'object', properties: {
    id: { type: 'string' }, grade: { type: 'string', enum: ['AAA', 'AA', 'A', 'B', 'C'] },
    checks: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, pass: { type: 'boolean' }, evidence: { type: 'string' } }, required: ['id', 'pass', 'evidence'] } },
    findings: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, severity: { type: 'string', enum: ['blocker', 'major', 'minor'] }, title: { type: 'string' },
      evidence: { type: 'string' }, fix_tool: { type: 'string', enum: ['blender', 'figma', 'meshy', 'copy'] }, fix: { type: 'string' } },
      required: ['id', 'severity', 'title', 'evidence', 'fix_tool', 'fix'] } } },
    required: ['id', 'grade', 'checks', 'findings'] } } },
  required: ['field', 'batch', 'summary', 'assets'] }
const RUBRIC_SCHEMA = { type: 'object', properties: { field: { type: 'string' }, rubric_file: { type: 'string' }, items: { type: 'integer' }, sources: { type: 'integer' }, summary: { type: 'string' } }, required: ['field', 'rubric_file', 'items', 'summary'] }
const RUN = args.fields ? FIELDS.filter(f => args.fields.includes(f.key)) : FIELDS

const rubricPrompt = f => `너는 '${f.name}' 분야의 혹독한 비평가이자 루브릭 저자다. 이 포스터(로마 콘크리트 A2 인포그래픽 지도, Blender 3D 지도 + Figma 글)의 '물체 하나하나'를 심사할 원자적 예/아니오 기준을 만든다.
1) ${L}/BRIEF.md, ${L}/STATE.md(결정·기각), 기존 포스터 단위 루브릭 ${L}/rubrics/*.md 를 읽어 이미 정해진 것과 충돌하지 않게 한다.
2) 최신 시각디자인·지도학·3D 일러스트·지각 연구와 SOTA 실무 자료를 찾아 근거로 쓴다(웹 검색 가능. 출처를 항목마다 단다).
3) 초점: ${f.focus}.
4) 기준은 물체 단위로 측정 가능해야 한다(맥락 크롭·단독 크롭 픽셀, 화면 pt, 명도 L*, Oklch, ΔE00 등 수치 문턱). 15~30개 항목, 항목마다 id(${f.key.toUpperCase()}-NN)·판정 방법·문턱·심각도 기준(blocker/major/minor)·출처.
5) 등급 규칙은 BRIEF와 같게: AAA = blocker 0 · major 0 · minor ≤ 2 (자산 단위).
결과 파일: ${L}/rubrics/${f.key}.md 에 쓴다(이 파일만 쓴다). 최종 출력은 스키마에 맞춘 구조화 결과.`

const reviewPrompt = (f, b, ids) => `너는 '${f.name}' 분야의 혹독한 비평가다. 이 포스터를 처음 보는 독립 심사관이고, 이번 임무는 Blender에 배치된 물체(자산) 하나하나를 판정하는 것이다. 결함을 찾는 것이 임무지만, 측정으로 증명할 수 없는 지적은 내지 않는다.
1) ${L}/BRIEF.md 와 ${L}/STATE.md 의 결정·기각 절을 읽는다. 기각·보류 항목은 새 근거가 없으면 다시 내지 않는다. 고정 조건 자체를 감점하지 않는다.
2) 판정 기준은 ${L}/rubrics/${f.key}.md 다. 항목을 바꾸거나 빼지 말고 그대로 적용한다. 루브릭 밖 결함은 blocker급(사실 오류·가림·겹침·판독 불가)일 때만 'NEW-' 접두 ID로.
   판정 단위는 ${D}/assets_index.json의 자산 id다. 루브릭이 자기 자산 번호·목록(A01, r10 상자 등)을 쓰면 이름·역할·물체로 이 id에 대응시켜 적용한다. 루브릭이 명시적으로 판정에서 뺀 자산(고정 조건 등)은 그 분야에서 grade AAA, checks에 제외 근거를 적는다. 루브릭의 다른 분야 경계표를 지켜 다른 분야 결함은 내지 않는다.
3) 네가 맡은 자산(묶음 ${b}): ${ids.join(', ')}.
   자료: ${D}/assets_index.json(자산별 역할·구성 물체·화면 상자·파일), ${D}/assets/<id>/context.png(포스터 그대로 3배 맥락 크롭), ${D}/assets/<id>/isolated.png(그 자산만 렌더한 3배 크롭), 전체 맥락 ${L}/r${R}/poster_1x.png·poster_2x.png·map_only_2x.png, 글 사양 ${L}/text_spec_r${R}.json, 팔레트 ${L}/palette_*.json, 물체 목록 ${D}/inventory.json(재질 hex 포함).
4) 자산마다 루브릭 항목을 모두 적용해 checks에 판정과 증거(수치)를 남기고, 지적마다 수치가 있는 해법과 수단(blender/figma/meshy/copy)을 준다. 이미지를 직접 열어 보고, 필요하면 Python(uv run --no-project --with pillow --with numpy python -I …)으로 잰다. 임시 파일은 너의 스크래치패드에만. 이전 라운드 리포트는 읽지 않는다(블라인드).
5) 파일을 쓰지 않는다. 읽기 전용: Figma·Blender·포스터 파일을 고치지 않는다.
6) 자산별 등급: AAA = blocker 0 · major 0 · minor ≤ 2. 같은 결함을 쪼개 부풀리지 않는다.
최종 출력은 스키마에 맞춘 구조화 결과(field="${f.key}", batch=${b}).`

if (args.makeRubrics) {
  phase('Rubrics')
  await parallel(RUN.map(f => () => agent(rubricPrompt(f), { label: `rubric:${f.key}`, phase: 'Rubrics', schema: RUBRIC_SCHEMA })))
}
phase('Object review')
const jobs = []
for (const f of RUN) args.batches.forEach((ids, b) => jobs.push(() => agent(reviewPrompt(f, b, ids), { label: `r${R}:${f.key}:b${b}`, phase: 'Object review', schema: SCHEMA })))
const out = (await parallel(jobs)).filter(Boolean)
const tally = {}
for (const r of out) for (const a of r.assets) { tally[r.field] = tally[r.field] || { AAA: 0, other: 0 }; tally[r.field][a.grade === 'AAA' ? 'AAA' : 'other']++ }
log(Object.entries(tally).map(([k, v]) => `${k}: AAA ${v.AAA} / not ${v.other}`).join(' · '))
return out
