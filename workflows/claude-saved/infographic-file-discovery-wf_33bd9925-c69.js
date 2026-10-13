export const meta = {
  name: 'infographic-file-discovery',
  description: 'Read-only sweep of the Mac for files/folders belonging to the Roman-concrete infographic poster project',
  phases: [{ title: 'Sweep', detail: 'one read-only finder per location group' }, { title: 'Completeness', detail: 'one critic looks for missed places' }],
}
const KNOWN = `이미 알고 있는 위치(다시 보고하지 말고, 있으면 '확인됨'으로만): ~/Documents/로마콘크리트_3D (iCloud, 대부분 dataless), /private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work (작업 사본).`
const COMMON = `너는 읽기 전용 탐색 에이전트다. 파일을 만들거나 옮기거나 지우지 않는다(임시 파일도 쓰지 않음). 목적: 사용자의 '로마 콘크리트 인포그래픽 포스터' 작업(A2 포스터, Blender 3D 지도, Figma, Meshy 3D 모델, ComfyUI 생성, 콜로세움·판테온·로마 지도, 수상작 참고 자료 '203' 어워드 보드, 심사 루프 BRIEF/STATE/rubric/judge, 인쇄 PDF/X-4, 교수 피드백·스케치·마인드맵)과 관련된 파일·폴더를 빠짐없이 찾는 것.
${KNOWN}
방법: du/find/ls/stat/mdfind(Spotlight)/grep -l로 이름·내용·수정 시각(2026-09-20 이후)으로 찾는다. iCloud dataless 파일은 열지 말고(읽으면 내려받기가 시작됨) 이름·크기(stat -f %z)·dataless 여부(find -flags +dataless)만 본다. 큰 폴더는 du -sh로 크기만.
판정: 각 후보마다 relevance(certain/likely/unsure)와 근거(이름·내용 일치), 크기(논리 MB, 로컬 MB), 성격(source/deliverable/reference/temp/cache)을 적는다. 시스템·앱 캐시는 temp/cache로 표시. 관계없는 것은 보고하지 않는다.`
const SCHEMA = { type: 'object', properties: {
  area: { type: 'string' }, summary: { type: 'string' },
  items: { type: 'array', items: { type: 'object', properties: {
    path: { type: 'string' }, kind: { type: 'string', enum: ['file', 'dir'] }, relevance: { type: 'string', enum: ['certain', 'likely', 'unsure'] },
    nature: { type: 'string', enum: ['source', 'deliverable', 'reference', 'temp', 'cache', 'config'] },
    logical_mb: { type: 'number' }, local_mb: { type: 'number' }, reason: { type: 'string' } },
    required: ['path', 'kind', 'relevance', 'nature', 'logical_mb', 'reason'] } } },
  required: ['area', 'summary', 'items'] }
const AREAS = [
  { key: 'user-folders', where: '~/Downloads, ~/Desktop, ~/Pictures, ~/Movies, ~/Documents(로마콘크리트_3D 제외한 나머지 전부: Comfyworkflow, Codex, Zoom 등)' },
  { key: 'work-and-icloud', where: '~/work, ~/Library/Mobile Documents(iCloud Drive 전체, Obsidian/OpenKnowledge 볼트 포함), ~/.planning, ~/.aside, ~/.ok, ~/.omp, ~/.prime, ~/.gjc' },
  { key: 'claude-and-tmp', where: '~/.claude(projects/*/workflows/scripts, plans, todos, 메모리 폴더 ~/.claude/projects/-Users-um-yunsang/memory 는 위치만), /private/tmp/claude-501 아래 다른 세션 폴더(73df8d3b… 의 nb_work 제외), /private/tmp 의 blender·meshy·figma 관련 임시, ~/.remember' },
  { key: 'tools-and-caches', where: '~/Library/Application Support(Blender, ComfyUI, Figma, Meshy, Claude), ~/Library/Caches, ~/.cache, ~/.local, ~/.venvs, ~/.codex, ~/ComfyUI 또는 ComfyUI 설치 폴더, Blender 애드온·스크립트 폴더. 그리고 ~ 바로 아래 프로젝트 폴더들 중 이름·내용으로 관련 있어 보이는 곳(CHOOGuard·argo-paper-orx 같은 다른 프로젝트는 관련 파일이 있는지만 grep/mdfind로 확인)' },
]
phase('Sweep')
const found = await parallel(AREAS.map(a => () => agent(`${COMMON}\n\n네 구역: ${a.where}`, { label: `sweep:${a.key}`, phase: 'Sweep', schema: SCHEMA })))
const all = found.filter(Boolean)
phase('Completeness')
const crit = await agent(`${COMMON}\n\n다른 탐색 에이전트 4명이 찾은 결과가 아래 JSON이다. 빠진 장소(다른 경로·이름 규칙·Spotlight로만 찾히는 것·외장 볼륨·/Volumes)가 있는지 mdfind와 find로 확인하고, 새로 찾은 것만 items에 넣는다(area="completeness").\n${JSON.stringify(all.map(r => ({ area: r.area, items: r.items.map(i => i.path) })))}`, { label: 'completeness', phase: 'Completeness', schema: SCHEMA })
return [...all, crit].filter(Boolean)