export const meta = {
  name: 'poster-v8_13-workers',
  description: 'Worker agents build the v8.13 changes in parallel: Colosseum/Pantheon/road layout, field colouring, road colouring, object inventory + per-object render tool',
  phases: [{ title: 'Workers', detail: 'four independent workers, each delivers a step script + verification' }],
}
const W = args.work
const BL = '/Applications/Blender.app/Contents/MacOS/Blender'
const COMMON = `공통 조건(반드시 지킬 것):
- 작업 루트: ${W} (iCloud가 아닌 로컬 사본이다. ~/Documents 쪽 파일은 iCloud가 비워 둘 수 있으니 읽지 말고 이 루트만 쓴다.)
- Blender: ${BL} -b <입력.blend> --factory-startup --python <스크립트> -- <인자> (헤드리스). 기준 파일 ${W}/out/roman_concrete_narrative_v8_11.blend 는 절대 덮어쓰지 않는다. 다른 .blend도 덮어쓰지 말고 네 폴더 안에 새 파일로 저장한다.
- 화면 좌표는 포스터 프레임 1191×1684pt(카메라 기준). 좌표 변환·광선·지형 높이 함수는 ${W}/scripts/user_v8_13.py 와 ${W}/scripts/review_r8_fixes_v8_11.py 의 to_pt, ray, bvh_of, tz, ground, world_per_pt 를 그대로 쓰면 된다.
- 렌더: runpy로 ${W}/scripts/integrate_assets.py 를 불러 H['render_two_pass'](경로.png) (지도 패스 + 겹침 패스 두 장). 합성·확대 크롭은 uv run -q --no-project --with pillow python -I ${W}/scripts/crop.py <렌더접두사> <출력.png> x0,x1,y0,y1,배율 ... (pt 좌표).
- Workbench MATERIAL 렌더라 색은 material.diffuse_color(선형)로 정해진다.
- 네 결과물은 오직 네 폴더에만 쓴다: 다른 워커 폴더·scripts·out·Figma는 건드리지 않는다.
- 결과 단계 스크립트(step.py)는 '어떤 입력 blend든 열어서 자기 변경만 적용하고 -- 뒤 첫 인자 경로로 저장, 둘째 인자(선택)가 있으면 그 접두사로 시험 렌더'하는 형태로 만든다. 같은 입력에 두 번 돌려도 결과가 같아야 한다(멱등). 물체 이름으로 대상을 찾고, 없으면 분명한 오류를 낸다.
- 측정으로 확인한 것만 보고한다. 확대 크롭을 직접 보고(Read로 이미지 열기) 결함이 없는지 눈으로도 확인한다.
- 최종 출력은 스키마에 맞춘 구조화 결과다.`
const SCHEMA = { type: 'object', properties: {
  worker: { type: 'string' }, summary: { type: 'string' },
  step_script: { type: 'string' }, output_blend: { type: 'string' },
  files: { type: 'array', items: { type: 'string' } },
  verification: { type: 'array', items: { type: 'object', properties: { check: { type: 'string' }, pass: { type: 'boolean' }, evidence: { type: 'string' } }, required: ['check', 'pass', 'evidence'] } },
  open_issues: { type: 'array', items: { type: 'string' } } },
  required: ['worker', 'summary', 'step_script', 'files', 'verification', 'open_issues'] }
const TASKS = [
  { key: 'layout', prompt: `너는 '배치 워커'다. 폴더: ${W}/workers/layout
사용자 요청: "콜로세움이랑 도로랑 너무 가까워서 콜로세움을 위쪽으로 조금 이동". 이전 요청(유지해야 함): 콜로세움 둘레 길이 가려지면 안 된다.
출발점: ${W}/scripts/user_v8_13.py 의 0~4절(콜로세움 무리 COL_ruined·R3_colosseum_podium·R4_arena_skin 를 화면 위로 14pt, 판테온 R8_pantheon 을 왼쪽 34·위 30pt, ①→② 북서쪽 길 R_core_road 를 새 중심선으로 다시 깔기(돌 상자 0.45 간격·0.49 폭, 경계석), 기단을 길에서 4pt 떨어지게 줄이기, 카메라 광선 가림 검사). 이 스크립트를 v8_11에 시험으로 돌린 결과: 길 가림 정점 0, 판테온-길 최소 간격 13.3pt, 기단 줄임 0각도였다. 5절(채색)은 다른 워커 몫이니 너의 step.py에서는 빼라.
할 일: 이 배치 변경을 step.py로 정리하고 검증·보완한다. 합격 조건(모두 측정):
1) 콜로세움 무리가 남쪽 길(R_core_road 남쪽 구간, x 330~800pt)과 화면에서 12pt 이상, 기단 바깥 가장자리는 4pt 이상 떨어진다.
2) R_core_road·R_via_appia·R_via_ostiensis 정점 중 콜로세움·기단·판테온·다른 물체에 가려지는 것 0 (카메라 광선 검사).
3) 옮긴 콜로세움·기단이 다른 물체(밭 F_centuriatio, 수도교, 나무, 이정표 MS1~3, ① 골조 NB_modern_building 등)와 화면에서 겹치거나 4pt 안으로 붙지 않는다. 겹치면 그 물체를 옮기지 말고 보고하거나, 꼭 필요하면 최소한으로 해결하고 근거를 남긴다.
4) 판테온: ①→② 이정표 MS1_core1_to_2 와 5pt 이상, 다시 깐 길과 8pt 이상, 밭과 4pt 이상.
5) 다시 깐 길: 돌 줄이 끊기거나 쐐기 틈·단차가 없고 양 끝(서쪽 다리 B_pons1, 동쪽 착지 R1_road_landing1)과 이음새가 자연스럽다(6배 확대 크롭으로 확인).
6) 콜로세움이 땅에 떠 있거나 묻혀 보이지 않는다(밑동·기단 이음 확대 확인).
결과: step.py(입력 v8_11 → 출력 ${W}/workers/layout/layout_v8_13a.blend), 시험 렌더와 전후 크롭(콜로세움 둘레 전체, 판테온·북서 길, 남쪽 길), 그리고 Figma 이름표를 옮겨야 할 양(콜로세움 지명 802:78은 현재 (730.5, 633.2) −30° 회전 글; 판테온 이름표 797:79 의 새 자리 후보: 판테온 왼쪽 8pt·세로 가운데, 지도 잉크와 4pt 이상 떨어진 자리 — 지도 패스 이미지에서 종이가 아닌 픽셀까지 거리를 재서 고른다)을 report.json에 수치로 남겨라.` },
  { key: 'fields', prompt: `너는 '밭 채색 워커'다. 폴더: ${W}/workers/fields
사용자 요청: "논 이랑이랑 밭 오브젝트도 채색이 필요". 대상: F_centuriatio (재질 하나 RC.v12.base_field #C8BBA0, 섬 1,824개).
이미 알아낸 것: 섬 종류는 (a) 판(4~42면, 가로세로 1~6.5, 두께 0.16~1.0), (b) 12면짜리 작은 말뚝 약 1,443개(0.14×0.16×0.43), (c) 18면짜리 둥근 더미 약 166개(0.55×0.64×0.52). 판 윗면에 줄무늬(이랑)가 보이는데, '윗면(법선 z>0.3) 면 중심 높이 차'로는 이랑이 하나도 잡히지 않았다(높이 차 0.03 이하). 즉 이랑이 어떻게 모델링됐는지(면 기울기? 얕은 홈? 법선? 별도 얇은 면?) 직접 조사해서 이랑 등/고랑을 가를 방법을 찾아야 한다.
할 일: 밭을 로마 시대 농지답게 채색하는 step.py.
- 판마다 작물 유형을 정해(같은 유형이 이웃에 몰리지 않게, 결과가 늘 같도록 고정 시드) 이랑 등은 작물색, 고랑·옆면은 흙색. 이랑 없는 평평한 판은 목초지/그루터기 색. 말뚝(포도나무·과수 지주)은 잎 녹색 계열, 둥근 더미는 짚색.
- 색 제약(이 포스터의 컬러 규칙): 모두 저채도(Oklch C ≤ 0.09), 색상각 60~130° 안, 강조색 계열(색상각 20~48°, #983821)은 쓰지 않는다, 명도 L* 62~84(종이 L* 약 88보다 어둡게, CORE 그림보다는 밝게). 기존 잎색 RC.v12.foliage #75865C·foliage_light #8D9A70, 흙길 #C0AF90, 땅 #F4E8D1와 어울리게.
- 새 재질 이름은 RC.v12_13.field_* 로. F_centuriatio 외 물체는 건드리지 않는다.
검증: 시험 렌더에서 밭 구역(예: x 0~300·y 380~620, x 640~1191·y 380~720, x 700~900·y 1300~1480 등)을 3배 크롭해 직접 보고, 이랑 줄무늬가 작물색/흙색으로 읽히는지, 얼룩·잘못 칠한 면이 없는지 확인. 렌더 픽셀로 각 색의 Oklch(L, C, h)를 재서 제약 충족을 표로 남긴다.
결과: step.py(어떤 blend든 → 출력), 입력 v8_11로 시험한 출력 ${W}/workers/fields/fields_test.blend, 크롭들, report.json.` },
  { key: 'roads', prompt: `너는 '도로 채색 워커'다. 폴더: ${W}/workers/roads
사용자 요청: "도로도 채색이 필요해 보인다". 대상: R_core_road, R_via_appia, R_via_ostiensis (모두 재질 RC.v12.base_road_foundation #C0AF90 하나), 착지 원판 R1_road_landing1·R1_road_landing5. 다리 B_pons1·B_pons2 와 그 난간, R4_bridge_west_bed, R1_road5_bed 는 석재 다리/바닥이니 따로 판단(근거 남김).
이미 알아낸 것: 길은 '돌 상자'(섬 하나당 5면 안팎, 0.43×0.49, 위 0.094) 수백 개 + 양쪽 '경계석' 긴 띠(섬 하나 수백 면)로 되어 있다. ①→② 길 일부는 다른 워커가 같은 치수의 새 돌 상자와 경계석 띠로 다시 깔 것이므로, 섬 크기(면 수 ≤ 40 = 돌 상자)로 가르는 방식이어야 어느 판에서도 통한다.
할 일: 로마 가도답게(아피아 가도의 현무암 포장 selce + 밝은 경계석 crepidines/umbones) 포장 돌은 차분한 회색 현무암 계열, 경계석은 밝은 석회암 계열로 칠하는 step.py. 근거(로마 도로 포장 재료)를 짧게 report에 적는다.
색 제약: 저채도(Oklch C ≤ 0.04), 포장 명도 L* 55~68(종이 L* 약 88, 콜로세움 약 60과 구별), 경계석은 L* 75~85, 강조색 계열 금지. 길 위 글자는 없지만 길 옆 지명·이정표 판(#983821)이 묻히지 않아야 한다.
검증: 시험 렌더에서 길 구간(예: x 200~960·y 480~1060, 아피아 가도 x 840~1191·y 930~1000, 오스티아 가도 x 70~400·y 1000~1460)을 3배 크롭해 직접 보고 칠이 빠진 돌·다리 칠 오류가 없는지, 이정표와 대비가 충분한지(이정표 판 vs 길 WCAG 3:1 이상) 측정한다.
결과: step.py, 입력 v8_11로 시험한 출력 ${W}/workers/roads/roads_test.blend, 크롭, report.json.` },
  { key: 'inventory', prompt: `너는 '물체 목록·렌더 워커'다. 폴더: ${W}/workers/inventory
사용자 요구: "블렌더에 배치된 모든 오브젝트 각각을 분야별 혹독한 비평가가 정밀검토해 AAA까지 루프". 그 심사에 쓸 자료를 만드는 것이 네 임무다(심사는 하지 않는다).
할 일:
1) inventory.py: blend를 열어 렌더에 보이는 모든 메시 물체를 나열(이름, 컬렉션, 면 수, 재질과 diffuse 색 hex, 화면 경계 상자 pt, 화면 면적). 이를 '심사 단위 자산'으로 묶는다(예: 콜로세움 = COL_ruined+기단+경기장 흙, 판테온, 이정표 3개 각각, CORE ①~⑤ 그림, DETAIL 모형들(구조 탑·단면, ③ 큰 시편, ④ 세 큐브, 제작 주사위, 재료/해수 큐브 등), SUPPORT 사례(폼페이, 항구·등대·방파제, 프리베르눔, 유적 관찰 장면, 실험실 시편), BASIC 재료(원뿔·벽돌·틀 등), 지물(수도교, 베수비오, 아펜니노 산들, 석회 가마, 나무 무리, 밭, 길·다리, 강·바다·물결, 땅), 카메라 앞 평면 도형(번호 원판·밑줄·지시선 등 80_SHAPES/81_NOSHADOW/85_HEADER)). 자산마다 id, 이름(한국어), 역할(CORE/DETAIL/SUPPORT/BASIC/지물/배경/도형), 구성 물체 목록, 화면 상자. 숨김(hide_render) 물체는 빼되 목록에 '숨김'으로 따로 적는다. 결과 inventory.json.
2) render_assets.py: blend 하나를 받아 자산마다 (a) 포스터 카메라 그대로의 전체 렌더에서 그 자산 상자 +여백 12pt 를 3배로 키운 '맥락 크롭', (b) 그 자산만 보이게(다른 물체 hide_render) 같은 카메라로 렌더해 같은 상자를 3배로 자른 '단독 크롭'을 만든다. 렌더는 integrate_assets.render_two_pass를 쓰되 필요한 영역만 border 렌더(render.use_border/use_crop_to_border)로 잘라 빠르게 한다. 출력 assets/<id>/context.png, assets/<id>/isolated.png, 그리고 전체 목록 contact_sheet.png 와 assets_index.json(자산별 파일 경로·상자·역할).
3) 입력 ${W}/out/roman_concrete_narrative_v8_12.blend 로 한 번 돌려 도구가 동작함을 보이고(자산 수, 걸린 시간), 크롭 몇 개를 직접 열어 맞게 잘렸는지 확인한다. 자산이 너무 잘게 쪼개지면(예: 밭 판 수백 개) 구역 단위로 묶는다. 목표 자산 수 30~60.
결과: inventory.py, render_assets.py, inventory.json, assets_index.json, contact_sheet.png, report.json.` },
]
phase('Workers')
const results = await parallel(TASKS.map(t => () => agent(`${t.prompt}\n\n${COMMON}`, { label: `worker:${t.key}`, phase: 'Workers', schema: SCHEMA })))
const ok = results.filter(Boolean)
log(ok.map(r => `${r.worker}: ${r.verification.filter(v => v.pass).length}/${r.verification.length} checks, issues ${r.open_issues.length}`).join(' · '))
return ok