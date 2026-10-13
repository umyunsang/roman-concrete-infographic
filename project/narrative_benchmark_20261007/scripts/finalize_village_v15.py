"""Promote the actual village poster only after saved-file and native QA pass."""
import datetime
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'out'
PLAN = Path('/Users/um-yunsang/.planning/roman-concrete-narrative-20261007')
URL = 'https://www.figma.com/design/jQPriO85F6wtPy1NPo752p/?node-id=764-78'

def read(path):
    return json.loads(path.read_text())

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

report = read(OUT / 'construction-detail-v12.json')
saved = read(PLAN / 'village-qa/v12-saved-validation.json')
native = read(OUT / 'figma-v15-village-native-validation.json')
upload = read(OUT / 'figma-v15-village-upload.json')
visual = read(OUT / 'v15-final-visual-review.json')
assert saved['pass'] and saved['output_sha256'] == sha(OUT / 'roman_concrete_narrative_v12.blend')
assert native['nativeTextCount'] == 84 and native['coreActualLines'] == [2, 3, 2, 2, 3]
assert native['detailActualLines'] == [2, 2, 2] and not native['problems']
assert native['backgroundHash'] == upload['imageHash']
assert upload['scene_sha256'] == saved['output_sha256']
assert visual['pass'] and visual['backgroundHash'] == native['backgroundHash']
assert visual['poster_sha256'] == sha(OUT / 'figma_poster_v15_village_2x.png')

for name in ['v12-saved-validation.json', 'v12-saved-validation.md', 'source-v9-drift-validation.json', 'source-v9-drift-validation.md']:
    shutil.copy2(PLAN / 'village-qa' / name, OUT / name)
for name in ['verify_v12_saved.py', 'v12_physical_geometry.py', 'v12_expected_names.py']:
    shutil.copy2(PLAN / 'village-qa' / name, ROOT / 'scripts' / name)

texts = []
for rid, text, x, y, w, h, fs, lh, missing, family, style in native['rows']:
    texts.append({'id': rid, 'text': text, 'x': x, 'y': y, 'width': w, 'height': h,
                  'fontSize': fs, 'liveLineHeightValue': lh, 'missingFont': missing,
                  'fontFamily': family, 'fontStyle': style})
write(ROOT / 'copy/narrative_v15.json', {
    'frameId': native['frameId'], 'question': read(ROOT / 'copy/narrative_v13.json')['question'],
    'copy_source': 'live Figma v15; integrated Roman village and material workyards',
    'titleFont': native['titleFont'], 'bodyFont': native['bodyFont'], 'texts': texts,
    'core_actual_lines': native['coreActualLines'], 'detail_actual_lines': native['detailActualLines'],
    'nativeEditableTexts': native['nativeTextCount']})
palette = read(ROOT / 'copy/village_material_palette_v15.json')
write(ROOT / 'design/village-tokens.json', palette)
(ROOT / 'design/village-tokens.css').write_text(':root {\n' + ''.join(
    '  --roman-' + key.replace('_', '-') + ': ' + value + ';\n'
    for key, value in palette['part_colors'].items()) + '}\n')

total = report['total_objects']
new = len(report['new_objects'])
hidden = len(report['hidden_objects'])
materials = report['total_materials']
houses = len(report['village']['house_objects'])
citizens = len(report['village']['citizen_groups'])
checks = len(saved['checks'])
doc = f'''# 실제 월드맵의 로마 마을 · v15

최신은 [편집형 Figma v15]({URL}), [Blender v12](../out/roman_concrete_narrative_v12.blend), [오버레이 포함 포스터](../out/figma_poster_v15_village_2x.png)다.

## 공간과 행동

지도·지형·카메라를 보존하고 중앙 콜로세움을 균일 축소했다. 도로 위의 제작 행렬 대신 주택 {houses}채, 장터, 생활 인물 {citizens}군집, 석회 가마·배합장과 회랑·벽체 작업장을 빈 지면에 분산했다. 사람은 약 2.4–2.5 world units, 주택은 약 4–5.2 units로 배치했다. 실제 건축물에 맞춘 장면의 비례이며 축척 지도나 고증된 로마 시가지 복원은 아니다.

콜로세움 표면을 카메라 ray/BVH로 찾아 두 목재 비계와 작업자를 붙였다. 비계 기둥은 지형에 닿고 작업자는 작업 발판 위에 놓인다. 주택의 기초·마당과 지면 인물은 도로·물의 실제 저부 투영을 피한다. 아레나의 목재·모래 바닥을 콘크리트로 부었다고 표현하지 않는다.

## 개념 모형의 마이그레이션

큰 흰 알갱이 표본, 균열 3단 모형, 확대 큐브와 연구소 암석 받침을 맵에서 숨겼다. 석회 원료 더미, 굳은 모르타르·석재 잔재, 실제 작업장의 작은 벽으로 바꾸었다. CORE3 DETAIL은 굳은 반죽의 석회 알갱이, CORE4 DETAIL은 물·칼슘·결정을 설명한다. 연결선은 해당 작업장 벽에 붙으며 콜로세움 자체를 자가치유의 입증 사례로 가리키지 않는다. 연구소의 받침은 새 복사본에서만 제거했다. 원본 객체들은 삭제하지 않았다.

## 실제 모델과 부위별 색

새 주택·장터·생활 인물은 Meshy AI MCP 표준 작업 3건으로 생성했다(60 credits). 기존 단계의 회랑 2개·작업자 3개도 재사용한다. 이 건축/마을 범위의 누적 작업은 8건, 160 credits다. 원본 GLB 8개와 작업 journal을 보존했다.

생활 인물의 빠진 머리는 같은 실제 모델의 머리를 복사했고, 잘못 붙은 항아리는 실제 손 위치로 옮겼다. 운반자와 회랑의 이전 보정도 유지한다. 석회 가마는 외벽·기단·내부·연기, 마을은 기와·회벽·돌·목재·차양·항아리·바구니, 인물은 피부·옷·신발·도구를 구분했다. Workbench MATERIAL과 Principled Base Color에 같은 scene-linear 색이 저장돼 있다. [역할별 색](../copy/village_material_palette_v15.json), [JSON 토큰](village-tokens.json), [CSS 토큰](village-tokens.css)을 사용한다. Solid 뷰포트에서는 Color를 Material로 설정한다.

## 서사·타이포·근거

중심 질문은 “철근도 없는 로마 건축물이 어떻게 2천 년을 버텼을까?”다. 메인 CORE는 현대 대비 → 뜨거운 배합과 흰 알갱이 → 불량 혼합이라는 해석의 반전 → 물·칼슘·결정 → 대조 재현 실험이며 반시계 방향을 유지한다. 본문은 2·3·2·2·3줄, DETAIL3/4와 한계 문구는 각각 2줄이다. {native['nativeTextCount']}개 글은 Figma TEXT다. 제목은 Noto Serif KR Bold, 본문은 Noto Sans KR이며, 본문11.5px/행간15.5px를 유지한다. 약0.5mm·수 주·생석회 없는 비교군과 직접 입증 범위를 유지했다.

콜로세움은 돌·벽돌·콘크리트를 함께 사용한 구조다. 장면은 기초·회랑·볼트 시공과 생활을 설명하기 위한 교육용 재구성이다. 역사 근거는 [콜로세움 남쪽 회랑](https://colosseo.it/en/southern-ambulatories/), [지보공·거푸집 연구](https://www.cambridge.org/core/books/abs/concrete-vaulted-construction-in-imperial-rome/centering-and-formwork/8EBABDACD4705DC49B63734AB1FE68C3), [지하 구조 안내](https://colosseo.it/en/marvels/the-underground-levels-of-the-colosseum/)다. 재료·실험 근거는 [2023년 논문](https://pmc.ncbi.nlm.nih.gov/articles/9821858/)과 [2025년 폼페이 배합 연구](https://www.nature.com/articles/s41467-025-66634-7)다.

## 보존과 검증

원본317개 객체의 local geometry와 지도·지형·카메라·기존 재질을 보존했다. 가마 재질과 허용된 크기·배치·가시성·CORE2/3 표시는 조정했다. 과거 설명과 이번에 퇴역한 모형 {hidden}개는 숨겼다. 새 객체 {new}개를 더해 총 {total}개, 저장된 재질 {materials}개다. 사용자 저장본 v9의 가마 이름이 control character로 바뀐 한 건은 mesh/index SHA 일치를 확인한 뒤 새 v12 안에서만 D2_lime_kiln으로 정규화했다. 원본 v9와 canonical 파일은 수정하지 않았다.

[저장본 독립 검증](../out/v12-saved-validation.md) {checks}개 항목과 [실제 Figma 측정](../out/figma-v15-village-native-validation.json), [최종 실제 이미지 검토](../out/v15-final-visual-review.json)를 통과했다. 검증은 원본 보존·부위 재질·GLB provenance·도로/물 접촉·독립 객체와 콜로세움의 표면 충돌·비계 접촉을 다룬다. Blender에는 Figma 글이 포함되지 않으며 포스터 PNG에는 오버레이가 포함된다.
'''
(ROOT / 'design/VILLAGE.md').write_text(doc)
(ROOT / 'README.md').write_text(f'''# 로마 콘크리트 포스터

최신은 **[Figma v15 · 로마 마을과 실제 시공]({URL})**과 **[Blender v12](out/roman_concrete_narrative_v12.blend)**다. 지도·카메라와 중앙 콜로세움을 유지하고, 주택·장터·생활 인물·배합 및 시공 작업장을 실제 지면에 분산했다. 콜로세움 벽면에도 목재 비계와 작업자를 붙였다. 도로 위 행렬과 큰 개념 모형은 마을·자재·작업장 벽으로 마이그레이션했다.

- [오버레이 포함 포스터 · 2382×3368](out/figma_poster_v15_village_2x.png)
- [빠른 미리보기 · 1191×1684](out/figma_poster_v15_village_1x.png)
- [콜로세움 시공 확대](out/figma-v15-colosseum-construction-detail.png)
- [마을·CORE3/4 확대](out/figma-v15-core34-detail.png)
- [편집·배색·역사·검증 기준](design/VILLAGE.md)
- [릴스 분석과 서사 근거](분석과_재구성안.md)

중심 질문은 **“철근도 없는 로마 건축물이 어떻게 2천 년을 버텼을까?”**다. 현대 대비 → 배합 → 흰 알갱이의 반전 → 물·칼슘·결정 → 대조 실험이라는 CORE의 반시계 흐름을 유지했다. 본문2·3·2·2·3줄, DETAIL 각2줄, {native['nativeTextCount']}개 편집형 TEXT다. 주택 {houses}채·생활 인물 {citizens}군집의 비례와 시야를 검토했고, 벽·기와·목재·피부·옷·도구를 부위별 채색했다.

원본317개 객체의 기하와 원본 파일을 보존하며 신규 {new}개를 더해 {total}개 객체·{materials}개 재질이다. 새 주택/장터/생활 인물3개 Meshy 모델과 기존 건설5개 모델을 사용했다. [새로 연 저장본의 독립 검증](out/v12-saved-validation.md), 실제 native PNG와 편집형 텍스트 검증을 완료했다. 장면은 일반적인 교육용 재구성이며 콜로세움의 자가치유를 직접 입증하는 사례가 아니다.

현재 문구·좌표는 `copy/narrative_v15.json`, 새 역할별 색은 `copy/village_material_palette_v15.json`, 전달 SHA는 `out/delivery-receipt-v15.json`이다. 포스터에는 Figma 오버레이가 포함되고 Blender 파일에는 Figma TEXT가 포함되지 않는다. 이전 버전과 Meshy 원본도 보존했다.
''')
history = ROOT / '분석과_재구성안.md'
text = history.read_text()
start = text.index('\n\n')
end = text.index('\n\n확인일:')
latest = f'''

최신 결과는 **[Figma v15 · 로마 마을과 실제 시공]({URL})**과 **[Blender v12](out/roman_concrete_narrative_v12.blend)**다. [오버레이 포함 포스터](out/figma_poster_v15_village_2x.png)를 실제 크기로 검토했다. 기존 도로 행렬을 실제 주택·장터·생활 인물·배합/벽체 작업장으로 바꾸고, 콜로세움에는 비계·작업자를 붙였다. 큰 개념 모형은 자재와 실제 작업장 벽으로 마이그레이션했다. 본문2·3·2·2·3줄, DETAIL3/4 각2줄을 유지한다. [현재 제작·편집 기준](design/VILLAGE.md)을 참고한다.

아래 분석은 서사·과학 근거와 비교 이력이다. 최신 상태는 README, 문구/좌표는 `copy/narrative_v15.json`, 독립 저장본 검증은 `out/v12-saved-validation.json`이다. 지도·카메라·원본317개 객체의 기하와 원본 파일을 보존했다. 사용자 캔버스에서 삭제한 마지막3문구는 복원하지 않았다.
'''
history.write_text(text[:start] + latest + text[end:])
for name in ['DESIGN.md', 'PART-MATERIALS.md', 'SEA-VOLCANO.md']:
    path = ROOT / 'design' / name
    content = path.read_text()
    i = content.index('\n\n')
    note = '\n\n이 문서는 이전 단계의 기록이다. 최신 실제 마을 구성·부위별 배색·포스터는 [v15 제작 기준](VILLAGE.md)을 참고한다.'
    path.write_text(content[:i] + note + content[i:])

files = ['out/roman_concrete_narrative_v12.blend', 'out/figma_poster_v15_village_2x.png',
         'out/figma_poster_v15_village_1x.png', 'out/figma-v15-colosseum-construction-detail.png',
         'out/figma-v15-core34-detail.png', 'out/construction-detail-v12.json',
         'out/figma-v15-village-native-validation.json', 'out/figma-v15-village-upload.json',
         'out/v12-saved-validation.json', 'out/v12-saved-validation.md', 'out/v15-final-visual-review.json',
         'copy/narrative_v15.json', 'copy/village_layout_v15.json', 'copy/village_material_palette_v15.json',
         'design/VILLAGE.md', 'design/village-tokens.json', 'design/village-tokens.css',
         'scripts/integrate_village_v12.py', 'scripts/village_geometry_v15.py', 'scripts/village_parts_v15.py',
         'scripts/worker_geometry_v14.py', 'scripts/worker_parts_v14.py', 'scripts/construction_parts.py',
         'scripts/hearth_object_parts.py', 'scripts/compose_village_map_v12.py', 'scripts/figma_village_v15.js',
         'scripts/verify_v12_saved.py', 'scripts/v12_physical_geometry.py', 'scripts/v12_expected_names.py',
         'meshy_construction_jobs_v14.json', 'meshy_construction_workers_v14.json', 'meshy_village_jobs_v15.json',
         'README.md', '분석과_재구성안.md']
files += [str(path.relative_to(ROOT)) for folder in ['construction_v14', 'workers_v14', 'village_v15']
          for path in sorted((ROOT / 'models' / folder).glob('*.glb'))]
artifacts = {name: {'bytes': (ROOT / name).stat().st_size, 'sha256': sha(ROOT / name)} for name in files}
write(OUT / 'delivery-receipt-v15.json', {
    'createdAtLocal': datetime.datetime.now().isoformat(timespec='seconds'), 'figmaUrl': URL,
    'frameId': '764:78', 'backgroundId': '764:79', 'pageId': '19:4',
    'backgroundHash': native['backgroundHash'], 'nativeEditableTexts': native['nativeTextCount'],
    'actualCoreBodyLines': native['coreActualLines'], 'detailBodyLines': native['detailActualLines'],
    'existingObjectsPreserved': 317, 'newObjects': new, 'objectsTotal': total, 'savedMaterials': materials,
    'sourceNameAliases': report['source_name_aliases'], 'sourceSHA': report['source_sha256'],
    'mapCameraTerrainLocalGeometryPreserved': True, 'newVillageMeshyJobs': 3, 'villageCredits': 60,
    'constructionAndVillageMeshyJobs': 8, 'constructionAndVillageCredits': 160,
    'newGLBsPreserved': True, 'savedSceneReview': 'PASS', 'nativeVisualReview': 'PASS',
    'direction': 'balanced village and workyards off roads; core counterclockwise; direct Colosseum scaffolds',
    'artifacts': artifacts})
print('FINALIZED_V15', len(artifacts), 'artifacts')
