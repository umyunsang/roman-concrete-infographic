export const meta = {
  name: 'poster-print-master-check',
  description: 'Independent hierarchy/legibility/print critic judges the print master (300ppi, 3mm bleed) for the deferred print items',
  phases: [{ title: 'Print review' }],
}
const L = args.loopDir, P = args.printDir
const SCHEMA = { type: 'object', properties: {
  grade: { type: 'string', enum: ['AAA', 'AA', 'A', 'B', 'C'] }, summary: { type: 'string' },
  checks: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, pass: { type: 'boolean' }, evidence: { type: 'string' } }, required: ['id', 'pass', 'evidence'] } },
  findings: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, severity: { type: 'string', enum: ['blocker', 'major', 'minor'] }, title: { type: 'string' }, evidence: { type: 'string' }, fix: { type: 'string' } }, required: ['id', 'severity', 'title', 'evidence', 'fix'] } } },
  required: ['grade', 'summary', 'checks', 'findings'] }
phase('Print review')
const r = await agent(`너는 '시각 위계·가독성·접근성·인쇄' 분야의 혹독한 비평가다. 이번 임무는 최종 인쇄 원고만 판정하는 것이다. 디자인 자체(글·배치·색)는 이미 다른 비평가들이 연속 AAA로 판정을 끝냈다. 이번에는 STATE.md의 R4(인쇄 해상도·재단 여분), R8·R9(인쇄 색 왕복)처럼 '최종 인쇄 원고 단계에서 판정'하기로 미뤄 둔 항목만 본다.
1) ${L}/BRIEF.md와 ${L}/STATE.md의 결정·기각 절, ${L}/rubrics/hierarchy_access.md 를 읽는다. 루브릭 중 인쇄 관련 항목(해상도, 재단 여분, 안전 영역, 인쇄 판독)과 R4·R8·R9를 기준으로 쓴다.
2) 자료: 인쇄 원고 PDF ${P}/로마콘크리트_A2_재단3mm_인쇄원고.pdf, 같은 프레임의 4배 PNG ${P}/print_frame_4x.png(4832×6804), 배경 원본 ${P}/v8_10_map_print_bleed_5033x7087.png, 조각 ${P}/v8_10_tile_*.jpg, 사양서 ${P}/PRINT_SPEC.md, 화면용 디자인 ${L}/r8/poster_2x.png.
3) 직접 측정한다(uv run --no-project --with pillow --with numpy --with pypdf python -I …, 임시 파일은 너의 스크래치패드에만). 볼 것: PDF 문서 크기와 재단 여분(A2 420×594mm + 사방 3mm), 배경 이미지의 실제 유효 ppi(≥ 240, 목표 300), 2×2 조각 경계의 틈·이음 자국, 재단 여분 안의 그림 연속성(재단선에서 잘려도 흰 띠가 생기지 않는지), 안전 영역(글이 재단선에서 충분히 안쪽인지), 글꼴 포함 여부, 안쪽 재단 영역이 화면용 디자인과 같은지, 인쇄 색 지정(사양서의 CMYK 권장값)이 R8·R9를 해소하는지.
4) 파일을 쓰지 않는다. 항목마다 판정과 증거를 checks에 담는다. 등급은 BRIEF 기준(AAA = blocker 0 · major 0 · minor ≤ 2).`, { label: 'print:hierarchy_access', phase: 'Print review', schema: SCHEMA })
return r
