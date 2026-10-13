export const meta = {
  name: 'poster-critic-round9-full',
  description: 'Round 9: fresh blind critics for all 7 visual fields on v8_11, plus an independent print-master (PDF/X-4 CMYK) critic',
  phases: [{ title: 'Review', detail: 'one fresh critic per field, fixed rubric' }, { title: 'Print review', detail: 'PDF/X-4 CMYK print master' }],
}
const L = args.loopDir, R = args.round, P = args.printDir
const FIELDS = [
  { key: 'color', name: '컬러그래픽(색채)' },
  { key: 'infographic', name: '인포그래픽(정보 설계·서사)' },
  { key: 'typography', name: '타이포그래피(한글 조판)' },
  { key: 'layout', name: '레이아웃·구성' },
  { key: 'illustration3d', name: '3D 일러스트·이미지 표현' },
  { key: 'hierarchy_access', name: '시각 위계·가독성·접근성·인쇄' },
  { key: 'value', name: '명암·명도 구성(톤 구조)' },
]
const SCHEMA = {
  type: 'object',
  properties: {
    field: { type: 'string' }, grade: { type: 'string', enum: ['AAA', 'AA', 'A', 'B', 'C'] },
    summary: { type: 'string' },
    checks_total: { type: 'integer' }, checks_failed: { type: 'integer' },
    checks: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, pass: { type: 'boolean' }, evidence: { type: 'string' } }, required: ['id', 'pass', 'evidence'] } },
    findings: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, severity: { type: 'string', enum: ['blocker', 'major', 'minor'] },
      title: { type: 'string' }, location: { type: 'string' }, evidence: { type: 'string' },
      rubric_check: { type: 'string' }, fix_tool: { type: 'string', enum: ['figma', 'blender', 'copy', 'figma+blender', 'print'] }, fix: { type: 'string' } },
      required: ['id', 'severity', 'title', 'location', 'evidence', 'fix_tool', 'fix'] } },
    strengths: { type: 'array', items: { type: 'string' } },
  },
  required: ['field', 'grade', 'summary', 'findings', 'checks', 'checks_total', 'checks_failed'],
}
const prompt = f => `너는 '${f.name}' 분야의 혹독한 비평가다. 이 포스터를 처음 보는 독립 심사관이다. 수상작 수준(AAA)인지 적대적으로 정밀 검증한다. 결함을 찾는 것이 임무지만, 측정으로 증명할 수 없는 지적은 내지 않는다.

작업 폴더: ${L}
1) ${L}/BRIEF.md 를 끝까지 읽는다(고정 조건·수정 수단·등급·심사 규칙). 이어 ${L}/STATE.md 의 '결정·기각' 절을 읽는다. 기각·보류 항목은 새 근거가 없으면 다시 내지 않는다. 고정 조건 자체를 감점하지 않는다.
2) 판정 기준은 ${L}/rubrics/${f.key}.md 다. 항목을 바꾸거나 빼지 말고 그대로 적용한다. 루브릭 밖의 결함은 blocker급(가림·겹침·판독 불가·사실 오류)일 때만 'NEW-' 접두 ID로 보고한다.
3) 자료: ${L}/r${R}/poster_1x.png(전체), ${L}/r${R}/tiles/*.png(2배 확대, 파일 이름에 pt 범위), ${L}/r${R}/poster_2x.png, ${L}/r${R}/map_only_2x.png(글 없는 지도), ${L}/text_spec_r${R}.json(글 크기·색 실제값), ${L}/palette_*.json. 이전 라운드 리포트는 읽지 않는다(블라인드 심사).
4) 측정은 직접 한다. 필요하면 Python(uv run --no-project --with pillow --with numpy python -I …)으로 픽셀을 잰다(대비, 색, 간격, 겹침). 측정용 임시 파일은 너의 스크래치패드에만 쓴다. 이미지에서 확인하지 않은 상태를 단정하지 않는다. 한국어 줄바꿈 오독도 본다.
5) 파일을 쓰지 않는다. 루브릭 항목마다 판정과 증거를 결과의 checks 배열에 모두 담는다.
6) 등급은 BRIEF 기준(AAA = blocker 0 · major 0 · minor ≤ 2)을 그대로 적용한다. 지적마다 수치가 있는 해법을 준다. 같은 결함을 쪼개 부풀리지 않는다.
읽기 전용: Figma·Blender·포스터 파일을 고치지 않는다.
최종 출력은 스키마에 맞춘 구조화 결과다(field="${f.key}").`
const printPrompt = `너는 '시각 위계·가독성·접근성·인쇄' 분야의 혹독한 비평가이고, 이번 임무는 최종 인쇄 원고만 판정하는 독립 심사관이다(다른 비평가가 같은 시간에 화면용 디자인을 분야별로 심사한다). 이전 인쇄 심사 보고서는 없다고 생각하고 블라인드로 본다.
1) ${L}/BRIEF.md, ${L}/STATE.md의 결정·기각 절(특히 R4·R8·R9와 D31), ${L}/rubrics/hierarchy_access.md 를 읽는다. 루브릭 중 인쇄 관련 항목(해상도, 재단 여분, 안전 영역, 인쇄 판독, 인쇄 색)을 기준으로 쓴다.
2) 자료(${P}): 인쇄소용 원고 로마콘크리트_A2_재단3mm_인쇄원고_PDFX4_CMYK.pdf, 화면·공유용 로마콘크리트_A2_재단3mm_화면용_RGB.pdf, 같은 프레임의 Figma 4배 PNG print_frame_4x.png(RGB), 배경 원본 v8_11_map_print_bleed_5033x7087.png, 조각 v8_11_tile_*.jpg, 사양서 PRINT_SPEC.md, 출력 조건 프로파일 PSOcoated_v3.icc. 화면용 디자인은 ${L}/r${R}/poster_2x.png, 글 사양은 ${L}/text_spec_r${R}.json.
3) 직접 측정한다(uv run --no-project --with pillow --with numpy --with pypdf python -I …, 임시 파일은 너의 스크래치패드에만). Ghostscript는 /opt/homebrew/bin/gs 전체 경로로 부른다(셸의 gs는 다른 명령의 별칭이다). pdfinfo·pdfimages·pdffonts·transicc도 있다. 볼 것: PDF/X-4 요건(버전, OutputIntent와 ICC, 페이지 박스: TrimBox = A2 420×594mm, BleedBox, 색공간에 RGB가 남았는지), 배경 실제 유효 ppi(≥ 240, 목표 300), 조각 경계 틈·이음, 재단 여분 안 그림 연속성과 가장자리 띠, 안전 영역, 글꼴 의존, 안쪽 재단 영역이 화면용 디자인과 같은지(위치·내용 누락 없음), 분판 값이 사양서와 맞는지, 인쇄 모의 뒤 글 대비(특히 작은 색 글, 4.5:1), 총잉크량(≤ 300%), 사양서 서술이 실제 파일과 맞는지.
4) 파일을 쓰지 않는다. 항목마다 판정과 증거를 checks에 담는다. 등급은 BRIEF 기준(AAA = blocker 0 · major 0 · minor ≤ 2). 지적마다 수치가 있는 해법을 준다. 최종 출력은 스키마에 맞춘 구조화 결과다(field="print").`
const jobs = FIELDS.map(f => () => agent(prompt(f), { label: `r${R}:${f.key}`, phase: 'Review', schema: SCHEMA }))
jobs.push(() => agent(printPrompt, { label: `r${R}:print`, phase: 'Print review', schema: SCHEMA }))
const results = await parallel(jobs)
const ok = results.filter(Boolean)
log(ok.map(r => `${r.field}: ${r.grade} (${r.findings.length})`).join(' · '))
return ok