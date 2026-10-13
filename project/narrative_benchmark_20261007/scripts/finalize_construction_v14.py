"""Write latest production authorities only after final visual/saved QA passes."""
import datetime,hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'out';PLAN=Path('/Users/um-yunsang/.planning/roman-concrete-narrative-20261007/construction-detail')
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
report=read(OUT/'construction-detail-v11.json');validation=read(PLAN/'v11-saved-validation.json');native=read(OUT/'figma-v14-road-native-validation.json')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert validation['pass'] and validation['output_sha256']==sha(OUT/'roman_concrete_narrative_v11.blend')
assert native['nativeTextCount']==96 and [x[-1]for x in native['bodies']]==[2,3,2,2,3]
assert native['backgroundHash']==read(OUT/'figma-v14-construction-upload.json')['imageHash']
for n in ['v11-saved-validation.json','v11-saved-validation.md']:shutil.copy2(PLAN/n,OUT/n)
for n in ['verify_v11_saved.py','v11_physical_geometry.py']:shutil.copy2(PLAN/n,ROOT/'scripts'/n)
# The independently run verifier has its audit report/helper paths scoped to
# planning. Keep that executable record intact; production scripts reference it.
old=read(ROOT/'copy/narrative_v13.json');oldtext={x['id']:x for x in old['texts']}
clone=read(OUT/'figma-v14-construction-mutation.json');inverse={v:k for k,v in clone['idMap'].items()}
texts=[]
for rid,text,x,y,w,h,fs,lh,missing in native['rows']:
 item=oldtext.get(inverse.get(rid),{}).copy();item.update(id=rid,text=text,x=x,y=y,width=w,height=h,fontSize=fs,liveLineHeightValue=lh,missingFont=missing)
 if not item.get('fontFamily'):item.update(fontFamily='Noto Sans KR',fontStyle='Regular')
 if rid in {'749:197','749:198','749:200','749:201','749:202','755:78','755:79'}:item['fontStyle']='Bold'
 texts.append(item)
write(ROOT/'copy/narrative_v14.json',{'frameId':native['frameId'],'question':old['question'],'copy_source':'live corrected Figma v14 counterclockwise road construction; source v13 preserved','titleFont':native['titleFont'],'bodyFont':native['bodyFont'],'texts':texts,'core_actual_lines':[2,3,2,2,3],'nativeEditableTexts':96})
palette=read(ROOT/'copy/construction_material_palette_v14.json');write(ROOT/'design/construction-tokens.json',palette)
(ROOT/'design/construction-tokens.css').write_text(':root {\n'+''.join('  --roman-'+k.replace('_','-')+': '+v+';\n'for k,v in palette['part_colors'].items())+'}\n')
(ROOT/'design/CONSTRUCTION-ROAD.md').write_text('''# 제작·운반·시공의 도로 서사

최신은 [Figma v14](https://www.figma.com/design/jQPriO85F6wtPy1NPo752p/?node-id=749-78), [Blender v11](../out/roman_concrete_narrative_v11.blend), [실제 포스터](../out/figma_poster_v14_road_construction_2x.png)다.

## 공간과 행동

지도·지형·카메라를 유지하고 콜로세움을 중앙에서 균일 축소했다. 기존 배합 장면은 확대해 서쪽 도로 옆에 배치했다. 서쪽 → 남서쪽 다리 → 남쪽 도로를 따라 배합, 양동이를 든 운반자, 목재 틀을 드러낸 회랑 볼트, 돌벽을 만드는 작업자, 공동 운반자를 배치했다. 공동 운반자는 중앙으로 향하며, 굳은 회랑 단면은 남동쪽 도로 옆에 있다. 반시계 방향의 짧은 Figma 벡터 화살표와 한 줄 캡션으로 행동을 연결했다.

메인 CORE는 현대 대비 → 배합·흰 알갱이 → 해석의 반전 → 물·칼슘·결정 → 대조 재현 실험이다. CORE 본문은 2·3·2·2·3줄이고, 설명 글은 96개 편집형 TEXT다. 제목과 본문은 Noto Serif KR Bold / Noto Sans KR를 사용한다. 확대 DETAIL3은 석회 알갱이와 칼슘, DETAIL4는 물의 이동과 탄산칼슘 결정을 다룬다. 콜로세움에서 자가치유를 직접 입증하지 않았다는 범위 문구를 유지했다.

## 실제 모델과 보정

Meshy MCP로 두 회랑 볼트와 세 작업자 GLB를 생성했다. 표준 작업 5건 총100 credits, 최종 계정 잔액600이다. 생성된 회랑 A의 전면 지붕 일부를 열고 실제 목재 리브·기둥·받침을 추가했다. 잘못 생성된 운반자 머리/막대는 제거하고, 실제 Meshy 건설자 머리를 복사해 정상 머리와 양동이·손잡이·내용물을 연결했다. 건설자에 낮은 돌벽·모르타르 이음·목재 측면 거푸집, 두 사람의 운반통에 내용물을 추가했다. 다운로드한 원본 GLB는 보존했다.

석회 가마는 외벽·기단·내부·연기를 분리하고, 작업자는 피부·옷·머리/신발·목재·도구·모르타르를 구분했다. 두 운반자의 옷도 구분했다. Workbench MATERIAL과 Principled Base Color에 같은 scene-linear 색이 저장돼 있다. [역할별 HEX](../copy/construction_material_palette_v14.json)와 [CSS 토큰](construction-tokens.css)을 사용한다.

## 역사와 해석 범위

콜로세움은 돌·벽돌·콘크리트를 함께 사용한 구조다. 이 제작 장면은 기초·내부 회랑·볼트에 관한 일반적인 교육용 재구성이며 특정 발굴 현장의 정확한 복원은 아니다. 아레나의 목재·모래 바닥을 콘크리트로 부었다고 표시하지 않는다. 역사 근거는 [콜로세움 남쪽 회랑](https://colosseo.it/en/southern-ambulatories/), [목재 지보공·거푸집 연구](https://www.cambridge.org/core/books/abs/concrete-vaulted-construction-in-imperial-rome/centering-and-formwork/8EBABDACD4705DC49B63734AB1FE68C3), [지하 구조 안내](https://colosseo.it/en/marvels/the-underground-levels-of-the-colosseum/)다. 작은 균열의 실험/재료 근거는 [2023년 논문](https://pmc.ncbi.nlm.nih.gov/articles/9821858/)과 [2025년 폼페이 배합 연구](https://www.nature.com/articles/s41467-025-66634-7)다.

## 보존과 검증

원본317개 객체와 local geometry, 지도·지형·카메라를 보존했다. 이전 제작/중력 설명과 연결선97개는 숨겼다. 사용자 허용 범위에서 콜로세움·가마·배합·팔라티노와 CORE2 표시의 변환을 조정했다. 상부 두 신전은 원래 위치다. 신규40개를 더해357개 객체, 저장된 재질77개다. 기존61재질 중 가마 전용 재질1개가 교체 후 사용되지 않아 저장에서 제외되고 기존60개와 신규17개가 남았다. 대상 외 기존 재질 색과 면별 인덱스는 유지했다.

[저장본 독립 검증](../out/v11-saved-validation.md)에는 기하·재질·변환·카메라·원본 SHA와 실제 도로 저부 접촉, 시공 장면과 콜로세움 표면 충돌 검사가 있다. [실제 Figma 측정](../out/figma-v14-road-native-validation.json), 최종 1x·2x 포스터와 확대 이미지로 글/행동 가독성을 검토했다. Blender에는 Figma TEXT가 포함되지 않으며 포스터 PNG에는 오버레이가 포함된다.
''')
(ROOT/'README.md').write_text('''# 로마 콘크리트 포스터

최신 편집형 결과는 **[Figma v14 · 반시계 도로의 제작·운반·시공](https://www.figma.com/design/jQPriO85F6wtPy1NPo752p/?node-id=749-78)**이다. 기반 지도는 **[Blender v11](out/roman_concrete_narrative_v11.blend)**이다. 원본과 이전 결과도 보존했다.

- [최종 포스터 · 2382×3368](out/figma_poster_v14_road_construction_2x.png)
- [빠른 미리보기 · 1191×1684](out/figma_poster_v14_road_construction_1x.png)
- [시공 장면 확대](out/figma-v14-road-construction-detail.png)
- [제작·편집·역사 기준](design/CONSTRUCTION-ROAD.md)
- [릴스 분석과 서사 근거](분석과_재구성안.md)

중심 질문은 **“철근도 없는 로마 건축물이 어떻게 2천 년을 버텼을까?”**다. 기존 CORE의 반시계 흐름에 맞춰 콜로세움 주변 도로 가까이에 배합 → 실제 운반자 → 목재 틀·돌벽 시공자 → 중앙으로 운반하는 두 작업자를 배치했다. 콜로세움은 중앙을 유지하면서 축소했고 기존 배합 장면은 확대했다. 시공 부위와 사람의 피부·옷·도구·재료를 구분해 채색했다. DETAIL3/4는 칼슘 공급·물과 결정이라는 바뀐 CORE에 맞췄다.

핵심 본문은 2·3·2·2·3줄을 유지했고96개 글은 Figma TEXT로 편집 가능하다. 지도·카메라·원본317개 객체와 local geometry를 보존하며 신규40개를 더해357개 객체, 재질77개다. 실제 저부 기하의 도로 접촉과 시공 모형/콜로세움의 표면 충돌을 독립 검증했다. Meshy MCP로 생성한5개 GLB 원본도 보존했다.

최신문구는 `copy/narrative_v14.json`, 새 재질은 `copy/construction_material_palette_v14.json`, 저장 검증은 `out/v11-saved-validation.json`, native 측정은 `out/figma-v14-road-native-validation.json`, 전달 기록은 `out/delivery-receipt-v14.json`이다. 전체 1x·2x 포스터와 시공/DETAIL 확대를 검토했다. 포스터 PNG에는 Figma 오버레이가 포함되고, Blender 파일에는 편집형 Figma 글이 포함되지 않는다.
''')
p=ROOT/'분석과_재구성안.md';s=p.read_text();idx=s.index('\n\n');end=s.index('\n\n확인일:')
current='''

최신 결과는 **[Figma v14 · 반시계 도로의 제작·운반·시공](https://www.figma.com/design/jQPriO85F6wtPy1NPo752p/?node-id=749-78)**과 **[Blender v11](out/roman_concrete_narrative_v11.blend)**이다. [실제 포스터](out/figma_poster_v14_road_construction_2x.png)에서 오버레이까지 검토했다. 실제 배합/운반/시공 작업자와 목재 틀을 콜로세움 주변 도로의 반시계 흐름으로 배치했다. 가마·도구·피부·옷·재료는 부위별 색을 사용하고 CORE3/4 DETAIL을 칼슘·물·결정에 맞췄다. 본문2·3·2·2·3줄을 유지했다. [최신 제작 기준](design/CONSTRUCTION-ROAD.md)을 참고한다.

아래 분석은 서사·과학 근거와 비교 이력이다. 최신 상태는 README와 `out/v11-saved-validation.json`, 현재 문구/좌표는 `copy/narrative_v14.json`이다. 지도·카메라·원본 객체317개 기하를 보존하며 사용자 허용 범위에서 크기·위치·일부 설명 가시성을 조정했다. 신규40개 포함357개 객체, 재질77개다. 사용자 캔버스에서 삭제한 마지막3문구는 복원하지 않았다.
'''
p.write_text(s[:idx]+current+s[end:])
files=['out/roman_concrete_narrative_v11.blend','out/figma_poster_v14_road_construction_2x.png','out/figma_poster_v14_road_construction_1x.png','out/figma-v14-road-construction-detail.png','out/figma-v14-core34-detail.png','out/figma_import/map_v11_construction_details_without_text_2x.png','out/construction-detail-v11.json','out/figma-v14-road-native-validation.json','out/figma-v14-construction-upload.json','out/v11-saved-validation.json','out/v11-saved-validation.md','copy/narrative_v14.json','copy/construction_material_palette_v14.json','design/CONSTRUCTION-ROAD.md','design/construction-tokens.json','design/construction-tokens.css','scripts/integrate_construction_v11.py','scripts/worker_geometry_v14.py','scripts/worker_parts_v14.py','scripts/construction_parts.py','scripts/hearth_object_parts.py','scripts/compose_construction_map_v11.py','scripts/figma_v14_counterclockwise_road.js','meshy_construction_jobs_v14.json','meshy_construction_workers_v14.json','README.md','분석과_재구성안.md']
artifacts={n:{'bytes':(ROOT/n).stat().st_size,'sha256':sha(ROOT/n)}for n in files}
write(OUT/'delivery-receipt-v14.json',{'createdAtLocal':datetime.datetime.now().isoformat(timespec='seconds'),'figmaUrl':'https://www.figma.com/design/jQPriO85F6wtPy1NPo752p/?node-id=749-78','frameId':'749:78','backgroundId':'749:79','pageId':'19:4','backgroundHash':native['backgroundHash'],'nativeEditableTexts':96,'actualCoreBodyLines':[2,3,2,2,3],'existingObjectsPreserved':317,'newObjects':40,'objectsTotal':357,'savedMaterials':77,'mapCameraTerrainLocalGeometryPreserved':True,'newMeshyJobs':5,'creditsUsed':100,'workerJobs':3,'workerCredits':60,'newGLBsPreserved':True,'savedSceneReview':'PASS','nativeVisualReview':'PASS','direction':'counterclockwise road manufacture→transport→formwork/masonry→central Colosseum delivery','artifacts':artifacts})
print('FINALIZED_V14',len(artifacts))
