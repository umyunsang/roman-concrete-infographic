# 고정 지도에 새 서사 에셋 통합

기본 소스는 본 폴더 바깥의 `roman_concrete_map.blend`다. 저장 후보 A/B는 확정본이라는 근거가 없어 기본 소스로 사용하지 않는다. 2026-10-07 19:22:26 저장, SHA-256 `28d49f93c6edaf89bcbcc54ff1dfb94b0089cc2a0e43496032d46717c1a14cb3`를 다시 확인했다.

## 보존 범위

원본 모든 물체의 메시 좌표·연결 구조·transform·parent·collection·색, camera/constraints, 기존 collection visibility, 렌더 규격을 fingerprint로 확인한다. terrain/fields/roads/water/trees/arena/site 재생성 스크립트는 실행하지 않는다. 허용된 CORE 또는 기존 항구 mole의 visibility만 manifest에서 명시하여 숨길 수 있다. 원본은 계속 남아 있다. 물체 이동/삭제는 하지 않는다. 새 .blend는 `narrative_benchmark_20261007/out/`의 새 파일명으로만 저장한다.

## 정확한 CORE 앵커 — 카메라 투영 bbox, pt

| 기존 물체 | bbox [x0,y0,x1,y1] | 새 역할 후보 |
|---|---|---|
| C1_pozzolana_quarry | [695.24,384.01,816.79,478.01] | 새 철근 콘크리트 건물, 기존 채석 장면만 숨김 |
| C2_hot_mixing | [93.51,852.00,194.41,950.00] | 유지: hot-mixing 설명 |
| C3_arch_building | [450.82,1127.99,555.23,1245.99] | 새 석회 알갱이 절개 모형, 기존 아치 작업 장면만 숨김 |
| C4_crack_repair | [684.66,1130.00,769.33,1228.00] | 필요 시 visibility만 숨김; 기존 D4 3단계 균열 도식은 유지 |
| C5_researchers | [1015.99,708.01,1115.99,812.01] | 유지: 현재 연구와 관찰 |

건물/절개 새 모델은 우선 기존 해당 bbox 안에 fit-contain한다. 성분과 알갱이의 식별성이 부족하면 모델 자체 yaw, short caption, Figma 설명을 조절하고 지도를 옮기지 않는다. 기존 `layout_big.py`의 C1 설계 슬롯은 [680,384,832,478]로 조금 넓다. 이 확대 슬롯을 선택할 경우 고정 원본 주변 물체와 실제 이미지에서 한 번 확인한다.

root의 넓은 후보 슬롯 감사: C1 [688,365,836,501]은 고정 봉우리 `L01_velino`의 bbox [693.64,268.42,856.84,378.61]와 위쪽 13.6pt가 겹치며, 수도교 bbox가 x830.6부터 시작한다. C1은 [688,384,826,491]처럼 위를 384 이하로 올리지 않는 편이 안전하다. 수도교는 대각선으로 길어 bbox 경고가 실제 교각 충돌인지 새 렌더로 확인한다. C3 [438,1132,581,1260]은 다른 높은 원본 CORE/지역 물체 bbox 및 고정 글 bbox와 겹치지 않는다. mole [110,1428,226,1523]은 기존 항구 핀 지시선 [197.67,1496.62,240.33,1533.38]과 겹치는데 기존 mole에서도 같은 연결이 있어 지시선이 새 모델을 올바르게 가리키는지 확인하면 된다.

직접 읽은 월드 최소 z: C1=0, C3=0, C4=0, mole=-0.01585594, 등대=0.00893331, 코사 교각=-0.00400194. C1 원본 yaw0°, C3/C4 원본 yaw45°다. 지상 새 모델은 ground_z0이 가장 일관되고 새 해상 방파제는 수면 아래 -0.75를 선택할 수 있다. 카메라의 XY 방위는 (+X,-Y), 즉 -45° 방향이다. 모델의 드러낼 정면/절개가 local -Y일 때 yaw45°가 카메라를 향하고, local +Y일 때 yaw-135°가 향한다. Meshy 실제 front는 모델별로 달라 45°를 확정하지 않고 preview로 확인한다.

## 항구는 이미 있다

파일 `assets/meshy/L09_harbor_breakwater.glb`가 존재하지만 현재 scene에서 이름은 `L09_portus_mole`다. "아직 방파제가 없다"는 전제는 틀리다.

| SUPPORT 장면/물체 | bbox |
|---|---|
| L09_portus_lighthouse | [43.34,1389.72,106.29,1524.38] |
| L09_portus_mole | [115.17,1432.03,224.84,1521.38] |
| L12_harbor_pilae | [312.74,1438.32,387.25,1517.73] |
| L11_privernum_wall | [1022.21,1004.66,1124.52,1102.75] |
| L08_pompeii_site | [652.54,1419.95,749.44,1524.98] |
| S_lab_island | [556.26,1505.13,623.70,1581.85] |

선택지는 두 개다. 기존 SUPPORT 위치를 모두 그대로 보이게 유지하려면 새 Meshy 방파제를 **해수 반응 절개 모형**으로 인접 빈 바다 [398,1504,490,1595]에 추가한다. 이 슬롯은 기존 텍스트 bbox/콜로세움 bbox와 겹치지 않으며 r16 이미지에서 하단 바다의 여백이다. 새 에셋 ground_z는 약 -0.75(수면 -0.7보다 아래)를 권장한다. 최종 원근/물결 가림은 새 출력 육안 확인이 필요하다.

기존 mole 자체를 정교한 새 방파제로 바꾸려면 해당 bbox에 배치하고 `replace_objects: ["L09_portus_mole"]`를 명시한다. 이는 기존 SUPPORT geometry/transform을 유지하지만 visibility를 바꾸는 선택이다. root가 사용자 요구와 맞춰 선택한다. 등대/코사 교각은 두 선택 모두 그대로 둔다.

## 현재 SUPPORT 글 보호 bbox

- 항구: [232.4,1537.4,339.2,1593.3]
- 폼페이: [719,1548.9,832.8,1591.8]
- 프리베르눔: [826.4,1021.9,892.4,1092.7]
- 실험실: [506.9,1437.9,638.1,1493.8]
- 연표: [47.9,1619.4,837.4,1659.3]
- 중앙 COL_ruined: [353.21,568.29,835.37,996.98]

기존 글 snapshot은 `loop/figma_texts.json`이다. root가 CORE 문안을 바꾸고 bbox도 바꾸면 새 snapshot을 manifest `text_zones_path`로 넘긴다. script는 새 물체 bbox가 글 bbox +2pt, 중앙 경기장 bbox +2pt, 프레임 safe8pt와 겹치는지 보수적으로 검사한다.

## 실행·검증

`integrate_assets.py`는 기본 dry-run이다. import 후 새 물체만 평가하고 report를 쓰지만 저장하지 않는다. `--audit-only`는 import/render/save 없이 소스 읽기/anchors/fingerprints만 확인한다. `--save-draft`를 root가 명시해야 새 output을 저장한다. 이미 존재하는 output은 덮어쓰지 않는다.

직접 수행한 검증은 Python 구문 검사와 Blender 5.2.2의 audit-only 로드(종료 0)다. `out/source-anchors-audit.json`은 canonical source의 geometry/transform/camera 보존 확인과 앵커 값을 담는다. 아직 Meshy 모델 import/fit/render/save는 실행하지 않았다.

`--render-passes <new-draft-path.png>`은 기존 방식의 지도/그림자 없는 도형 2패스를 새 폴더에 출력하고 기존 collection/렌더 설정을 되돌린다. 두 PNG를 alpha 합성한 후 새 Figma RGBA 글을 합친다. 주된 새 모델은 map-pass collection `46_NARRATIVE_ASSETS`에 들어가고, 고정 평면 확대 모형처럼 그림자가 없어야 할 경우 manifest `shadow_pass: "overlay"`로 기존 `81_NOSHADOW`에 넣을 수 있다.

## CORE4: 기존 3단계 모델 복사

새 외부 모델 생성 없이 D4의 원본 **복사본**을 CORE4 [642,1133,811,1227]에 둔다. 원본 DETAIL D4는 그 자리에 그대로 남는다. manifest asset은 `reuse_object_prefixes: ["D4_"]`, `replace_objects: ["C4_crack_repair"]`, `rotation_z_degrees: 0`, `shadow_pass: "overlay"`를 사용한다. 일반 GLB `path`와 동시에 지정하면 거부한다.

포함되는 렌더 가능한 원본 MESH는 13개, 약 770 triangles다: `D4_cube0/1/2`, `D4_crack0/1/2`, `D4_lime0/1`, `D4_drop0/1/2`, `D4_arrow0/1`. `D4_crack` EMPTY는 제외한다. 해당 prefix에 FONT/label 객체는 없다. drop은 기존 `81_NOSHADOW`, 나머지는 기존 `50_DETAIL_MODEL`에서 읽는다. 원본 object/data를 수정하거나 이동하지 않고 평가 mesh의 사본을 world matrix로 굽고 새 mesh에 합친 **숨김 fit proxy**를 만든다.

root의 후속 결정에 따라 **원본 object-gray별 새 copy mesh 그룹**도 함께 만든다. fit proxy만 bbox에 맞춘 뒤 그 matrix를 새 Empty 부모에 전달하여 copy 그룹의 배치를 일치시킨다. proxy는 제거하고 원본 회색 대비가 유지되는 새 그룹만 저장·렌더한다. Workbench global OBJECT shading은 바꾸지 않는다. report의 bbox는 배치 완료한 copy 그룹 합집합으로 확인하고 triangles는 실제 보이는 copy 그룹 합계이며 proxy 수치와 일치하는지 확인한다. 원본 DETAIL D4 및 모든 원본 mesh/transform은 fingerprint 검증 대상 그대로다. 현재 변경의 검증 범위는 함수 구현 및 Python 구문 검사이며 모델 복사/fit/render/save는 root가 실행한다.

## 최종 실행 결과
최종은 out/roman_concrete_narrative_v4.blend. 기존mole유지, 새방파제[398,1510,500,1600] ground_z0으로해안바다에추가. C1/C3/C4와원본D4 13meshes숨김, geometry/transform보존. 원본302objects의live검사및freshcanonical/draft재로드검사통과. 이전배치제안과미실행표현은준비단계기록이다. 최종권위는placement_manifest_v4.json, integration-report-v4.json,saved-draft-validation.json.
