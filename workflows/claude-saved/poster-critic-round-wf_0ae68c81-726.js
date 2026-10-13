export const meta = {
  name: 'poster-critic-round',
  description: 'Fresh independent harsh critics re-review the revised poster with the fixed per-field rubrics (blind to earlier reports)',
  phases: [{ title: 'Review', detail: 'one fresh critic per field, fixed rubric' }],
}
const L = args.loopDir, R = args.round
const FIELDS = [
  { key: 'color', name: '컬러그래픽(색채)' },
  { key: 'infographic', name: '인포그래픽(정보 설계·서사)' },
  { key: 'typography', name: '타이포그래피(한글 조판)' },
  { key: 'layout', name: '레이아웃·구성' },
  { key: 'illustration3d', name: '3D 일러스트·이미지 표현' },
  { key: 'hierarchy_access', name: '시각 위계·가독성·접근성·인쇄' },
]
const SCHEMA = {
  type: 'object',
  properties: {
    field: { type: 'string' }, grade: { type: 'string', enum: ['AAA', 'AA', 'A', 'B', 'C'] },
    summary: { type: 'string' }, report_file: { type: 'string' },
    checks_total: { type: 'integer' }, checks_failed: { type: 'integer' },
    findings: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, severity: { type: 'string', enum: ['blocker', 'major', 'minor'] },
      title: { type: 'string' }, location: { type: 'string' }, evidence: { type: 'string' },
      rubric_check: { type: 'string' }, fix_tool: { type: 'string', enum: ['figma', 'blender', 'copy', 'figma+blender'] }, fix: { type: 'string' } },
      required: ['id', 'severity', 'title', 'location', 'evidence', 'fix_tool', 'fix'] } },
    strengths: { type: 'array', items: { type: 'string' } },
  },
  required: ['field', 'grade', 'summary', 'findings', 'checks_total', 'checks_failed'],
}
const prompt = f => `너는 '${f.name}' 분야의 혹독한 비평가다. 이 포스터를 처음 보는 독립 심사관이다. 수상작 수준(AAA)인지 적대적으로 정밀 검증한다. 결함을 찾는 것이 임무지만, 측정으로 증명할 수 없는 지적은 내지 않는다.

작업 폴더: ${L}
1) ${L}/BRIEF.md 를 끝까지 읽는다(고정 조건·수정 수단·등급·심사 규칙). 이어 ${L}/STATE.md 의 '결정·기각' 절을 읽는다. 기각·보류 항목은 새 근거가 없으면 다시 내지 않는다. 고정 조건 자체를 감점하지 않는다.
2) 판정 기준은 ${L}/rubrics/${f.key}.md 다. 항목을 바꾸거나 빼지 말고 그대로 적용한다. 루브릭 밖의 결함은 blocker급(가림·겹침·판독 불가·사실 오류)일 때만 'NEW-' 접두 ID로 보고한다.
3) 자료: ${L}/r${R}/poster_1x.png(전체), ${L}/r${R}/tiles/*.png(2배 확대, 파일 이름에 pt 범위), ${L}/r${R}/poster_2x.png, ${L}/text_spec_r${R}.json(글 크기·색 실제값), ${L}/palette_*.json. 이전 라운드 리포트(r1/ 등)는 읽지 않는다(블라인드 심사).
4) 측정은 직접 한다. 필요하면 Python(uv run --no-project --with pillow --with numpy python -I …)으로 픽셀을 잰다(대비, 색, 간격, 겹침). 이미지에서 확인하지 않은 상태를 단정하지 않는다. 한국어 줄바꿈 오독도 본다.
5) 항목 하나를 판정할 때마다 ${L}/r${R}/report_${f.key}.md 에 바로 덧붙인다(세션이 끊겨도 남도록). 마지막에 등급과 요약을 쓴다.
6) 등급은 BRIEF 기준(AAA = blocker 0 · major 0 · minor ≤ 2)을 그대로 적용한다. 지적마다 수치가 있는 해법을 준다. 같은 결함을 쪼개 부풀리지 않는다.
읽기 전용: Figma·Blender·포스터 파일을 고치지 않는다. 쓰는 파일은 리포트 하나뿐이다.
최종 출력은 스키마에 맞춘 구조화 결과다(field="${f.key}").`
phase('Review')
const results = await parallel(FIELDS.map(f => () => agent(prompt(f), { label: `r${R}:${f.key}`, phase: 'Review', schema: SCHEMA })))
const ok = results.filter(Boolean)
log(ok.map(r => `${r.field}: ${r.grade} (${r.findings.length})`).join(' · '))
return ok
