"""Package verified saved materials and native editable poster delivery."""
from pathlib import Path
import datetime, hashlib, json, shutil

ROOT=Path(__file__).resolve().parents[1]
PLAN=Path('/Users/um-yunsang/.planning/roman-concrete-narrative-20261007/sea-volcano-copy')
OUT=ROOT/'out'
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
saved=read(PLAN/'v9-saved-material-validation.json')
native=read(OUT/'figma-v13-sea-volcano-validation.json')
assert saved['pass'] and not native['problems'] and not native['aliasErrors']
visual=(PLAN/'v13-final-visual-review.md').read_text()
assert 'PASS' in visual
for n in ['v9-saved-material-validation.json','v9-saved-material-validation.md','v13-final-visual-review.md']:shutil.copy2(PLAN/n,OUT/n)
shutil.copy2(PLAN/'verify_v9_saved_materials.py',ROOT/'scripts/verify_v9_saved_materials.py')
palette=read(ROOT/'copy/sea_volcano_palette_v13.json')
old=read(ROOT/'copy/narrative_v12.json');mutation=read(OUT/'figma-v13-copy-mutation.json')
inverse={v:k for k,v in mutation['idMap'].items()};previous={t['id']:t for t in old['texts']}
texts=[]
for id,text,x,y,w,h in native['texts']:
 item=previous[inverse[id]].copy();item.update(sourceId=inverse[id],id=id,text=text,x=x,y=y,width=w,height=h);texts.append(item)
write(ROOT/'copy/narrative_v13.json',{'frameId':'743:78','question':old['question'],'copy_source':'live v12; five CORE bodies and modern/Rome comparison caption shortened; other 89 texts preserved','titleFont':old['titleFont'],'bodyFont':old['bodyFont'],'texts':texts,'core_actual_lines':[r[-1]for r in native['bodies']]})
write(ROOT/'design/sea-volcano-tokens.json',palette)
(ROOT/'design/sea-volcano-tokens.css').write_text(':root {\n'+''.join('  --rc-'+role.replace('_','-')+': '+hex+';\n'for role,hex in palette['part_colors'].items())+'}\n')
doc='''# 바다·화산 부위별 배색과 본문 압축 · v13

최신 결과는 [Figma v13](https://www.figma.com/design/jQPriO85F6wtPy1NPo752p/?node-id=743-78), [Blender v9](../out/roman_concrete_narrative_v9.blend), [실제 포스터 PNG](../out/figma_poster_v13_sea_volcano_2x.png), [편집형 재질 가이드](https://www.figma.com/design/jQPriO85F6wtPy1NPo752p/?node-id=744-99)다.

| 기존 모형 | 채색한 부위 |
| --- | --- |
| 포르투스 등대 | 석재 벽체 / 기단 / 정상부·발코니 상면 / 기존 창 오목면 |
| 항구 구조물 | 벽체 / 기초 / 기존 상판·보행면 / 높은 모서리 상면 |
| 항구 교각 | 기둥 옆면 / 기단 / 슬래브 상면 / 기둥 정상부 |
| 로마 방파제 개념 모형 | 콘크리트 블록 벽 / 기단 / 슬래브 상면 / 벽체 상면 |
| 베수비오 | 주 사면 / 기존 분화구 안쪽 / 높은 테두리 / 낮은 사면 |

바다 쪽은 따뜻한 석재·모래색과 청회색 오목면, 화산은 낮은 채도의 흙색 4역할로 구분했다. 분화구 안쪽만 어두운 색으로 두어 중앙 콜로세움과 CORE 강조색의 우선순위를 유지했다. 방파제에는 독립된 노출 골재 형상이 없어 골재 면을 만들지 않았다. 용암이나 폭발 형상도 추가하지 않았다. 5개 기존 메시의 원래 polygon index에 실제 재질을 배정했다.

본문은 ①2줄 ②3줄 ③2줄 ④2줄 ⑤3줄이다. 기존 Noto Sans KR Regular11.5px, 행간15.5px와 폭을 유지했다. 마지막 실험에는 현대 재현 시편·약0.5mm 균열·수 주·생석회 유무의 비교를 남겼다. 현대/로마 재료 대비 캡션도2줄로 줄였다. 95개 편집형 TEXT 중6개 문구만 바꾸고 다른89개 문구와 모든 글의 폰트·색·폭·상단 위치는 유지했다.

317개 객체의 기하·변환·배치·카메라·가시성·씬·저장된 뷰포트 설정은 v8과 같다. 대상 외250메시의 재질 슬롯과 면별 인덱스는 동일하다. 기존51재질의 색·Principled 상태를 보존하고 새10재질을 추가해 총61재질이다. 현재 Workbench MATERIAL 출력에서는 Material Properties → Viewport Display → Color를 편집한다. Principled Base Color에도 같은 scene-linear 색이 저장돼 있다. [팔레트 JSON](../copy/sea_volcano_palette_v13.json)과 [재사용 토큰](sea-volcano-tokens.json), [CSS](sea-volcano-tokens.css)에 역할과 HEX가 있다.

[저장본 검증](../out/v9-saved-material-validation.md), [Figma 검증](../out/figma-v13-sea-volcano-validation.json), [최종 시각 검토](../out/v13-final-visual-review.md)를 통과했다. 모든 CORE 줄수는 Figma 실제 높이와 native PNG에서 확인했다. brand·design-system·figma-use·figma-generate-library, Blender Python API와 공식 Figma MCP를 사용했다. 새 Meshy 작업은 없다.
'''
(ROOT/'design/SEA-VOLCANO.md').write_text(doc)
parts=ROOT/'design/PART-MATERIALS.md';s=parts.read_text()
prefix='최신 후속 작업은 **[v13 바다·화산 배색과 본문 압축](SEA-VOLCANO.md)**이다. 아래 v12 기록은 이전 제작 단계다.\n\n'
if not s.startswith(prefix):parts.write_text(prefix+s)
(ROOT/'README.md').write_text('''# 로마 콘크리트 포스터

최신 편집형 결과는 **[Figma v13 · 바다·화산 배색과 본문 압축](https://www.figma.com/design/jQPriO85F6wtPy1NPo752p/?node-id=743-78)**이다. 기반 지도는 **[Blender v9](out/roman_concrete_narrative_v9.blend)**이다. 원본과 이전 v8/v12도 보존했다.

- [최종 포스터 PNG · 2382×3368](out/figma_poster_v13_sea_volcano_2x.png)
- [빠른 미리보기 · 1191×1684](out/figma_poster_v13_sea_volcano_1x.png)
- [편집형 바다·화산 재질 가이드](https://www.figma.com/design/jQPriO85F6wtPy1NPo752p/?node-id=744-99)
- [새 배색·본문·편집 기준](design/SEA-VOLCANO.md)
- [앞선 부위별 재질 배색](design/PART-MATERIALS.md)
- [릴스 분석과 서사 재구성 근거](분석과_재구성안.md)

중심 질문은 **“철근도 없는 로마 건축물이 어떻게 2천 년을 버텼을까?”**이다. 현대와 로마 대비 → 제조가 남긴 흰 알갱이 → 불량 혼합이라는 해석의 반전 → 물·칼슘 이동·결정 충전 → 대조 시편이 있는 현대 재현 실험을 유지한다. 코어 본문은 각각2·3·2·2·3줄로 압축했다. 글자 크기·폭을 줄이지 않았으며 마지막 실험의 약0.5mm와수 주·생석회 유무 비교를 유지한다. 재료 비교 캡션도2줄이다.

바다 쪽 등대·항구 구조물·교각·방파제의 벽/정상부/상판/기단/창을 기존 부위에 맞춰 채색했다. 베수비오는 분화구·테두리·주 사면·낮은 사면을 저채도 흙색으로 구분했다. 중앙 콜로세움과 지도 배치, 다른 모형의 색은 그대로다.

저장본을 새로 열어317개 객체의 기하·변환·배치·카메라·가시성·씬·뷰포트 동일, 대상 외250메시 재질 동일, 기존51재질 유지+새10재질=61재질을 검증했다. Workbench MATERIAL과 저장된 Solid 뷰포트의 MATERIAL 색상 모드를 사용한다. 95개 글은 모두 Figma TEXT로 편집 가능하고,6개 문구만 바꿨다. 기존 제목 Noto Serif KR Bold70/80과 본문 Noto Sans KR Regular11.5/15.5, 모든 글의 폰트·fill·폭·상단 위치는 유지했다.

최신문구는 `copy/narrative_v13.json`, 재질은 `copy/sea_volcano_palette_v13.json`, 검증은 `out/v9-saved-material-validation.json`과 `out/figma-v13-sea-volcano-validation.json`, 전달 기록은 `out/delivery-receipt-v13.json`이다. 실제1x/2x 포스터와 부위 확대를 검토했다. 배경 지도에는 글이 없고 Blender에는 Figma 오버레이가 포함되지 않는다. 이번 단계에 새 Meshy 생성 작업은 없다.
''')
report=ROOT/'분석과_재구성안.md';s=report.read_text();idx=s.index('\n\n');end=s.index('\n\n확인일:')
current='''

최신 결과는 **[Figma v13 · 바다·화산 배색과 본문 압축](https://www.figma.com/design/jQPriO85F6wtPy1NPo752p/?node-id=743-78)**과 **[Blender v9](out/roman_concrete_narrative_v9.blend)**이다. [실제 포스터 PNG](out/figma_poster_v13_sea_volcano_2x.png)에서 오버레이를 포함해 검토했다. 항구 4모형과 화산의 기존 부위에 새10재질을 추가했고 총61재질이다. CORE 본문은2·3·2·2·3줄이며 기존 글 크기·폭을 유지했다. 현대/로마 비교 캡션도2줄로 축약했다. [최신 제작 기준](design/SEA-VOLCANO.md)을 참고한다.

아래 제작·과학 분석은 이전 단계의 근거와 비교 이력이다. 최신 보존 범위는 README와 `out/v9-saved-material-validation.json`, 현재 문구·좌표는 `copy/narrative_v13.json`, native 글 검증은 `out/figma-v13-sea-volcano-validation.json`을 기준으로 한다. 기존317개 객체형상·배치·씬·카메라와 대상 외 재질은 유지했고95개 편집형 글 중6개 문구만 압축했다. 사용자 캔버스에서 삭제한 마지막3문구는 복원하지 않았다.
'''
report.write_text(s[:idx]+current+s[end:])
files=['out/roman_concrete_narrative_v9.blend','out/figma_poster_v13_sea_volcano_2x.png','out/figma_poster_v13_sea_volcano_1x.png','out/figma_sea_volcano_guide_v13_2x.png','out/figma_import/map_v9_sea_volcano_without_text_2x.png','out/poster-sea-volcano-v9.json','out/figma-v13-copy-mutation.json','out/figma-v13-material-guide-mutation.json','out/figma-v13-sea-volcano-validation.json','out/figma-v13-sea-volcano-upload.json','out/v9-saved-material-validation.json','out/v9-saved-material-validation.md','out/v13-final-visual-review.md','copy/narrative_v13.json','copy/sea_volcano_palette_v13.json','design/SEA-VOLCANO.md','design/sea-volcano-tokens.json','design/sea-volcano-tokens.css','scripts/sea_object_parts.py','scripts/volcano_parts.py','scripts/apply_sea_volcano_v9.py','scripts/compose_sea_volcano_map_v9.py','scripts/figma_sea_volcano_v13.js','scripts/figma_sea_volcano_guide_v13.js','README.md','분석과_재구성안.md']
artifacts=[{'path':n,'bytes':(ROOT/n).stat().st_size,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()}for n in files]
write(OUT/'delivery-receipt-v13.json',{'createdAtLocal':datetime.datetime.now().isoformat(timespec='seconds'),'figmaUrl':'https://www.figma.com/design/jQPriO85F6wtPy1NPo752p/?node-id=743-78','guideUrl':'https://www.figma.com/design/jQPriO85F6wtPy1NPo752p/?node-id=744-99','frameId':'743:78','backgroundId':'743:79','pageId':'19:4','backgroundHash':native['imageHash'],'nativeEditableTexts':95,'changedTexts':6,'otherTextsPreserved':89,'actualCoreBodyLines':[2,3,2,2,3],'fontSizesWidthsAndTopPositionsPreserved':True,'geometryPlacementCameraSceneVisibilityPreservedObjects':317,'nontargetMeshMaterialAssignmentsPreserved':250,'newMaterials':10,'totalMaterials':61,'newMaterialVariables':20,'savedSceneReview':'PASS','nativeVisualReview':'PASS','newMeshyJobs':0,'artifacts':artifacts})
print('V13_DELIVERY_COMPLETE',len(artifacts),'artifacts')
