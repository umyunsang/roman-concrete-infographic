최신 후속 작업은 **[v13 바다·화산 배색과 본문 압축](SEA-VOLCANO.md)**이다. 아래 v12 기록은 이전 제작 단계다.

# 부위별 Blender 배색 · v12

현재 결과는 [Figma v12](https://www.figma.com/design/jQPriO85F6wtPy1NPo752p/?node-id=737-78), [부위별 재질 가이드](https://www.figma.com/design/jQPriO85F6wtPy1NPo752p/?node-id=737-246), [Blender v8](../out/roman_concrete_narrative_v8.blend), [실제 Figma PNG](../out/figma_poster_v12_part_materials_2x.png)이다.

이전 v11의 큰 색 체계를 유지하면서, 같은 모형 안의 의미가 다른 부위를 실제 재질로 나눴다. 지형과 콜로세움 중심 배치, 현대 골조 크기, 인물과 유적의 위치는 유지한다. 전체는 따뜻한 석회·석재 계열로 묶고, 현대 콘크리트·철근과 실험 장면에는 차가운 계열을 사용한다. 의복과 흙·목재에는 낮은 채도의 적갈색·갈색을 사용한다.

| 모형 | 구분한 기존 부위 | 대표 색 |
| --- | --- | --- |
| 현대 골조 | 두꺼운 콘크리트 기둥·보 / 노출된 가는 cage·bar | #B9BEC0 / #344E5A |
| 제작 장면 | 피부 / 밝은 의복 / 적갈색 의복 / 목제 도구 / 배합 용기 / 반죽 | #C99C78 / #DED1AF / #9C5C43 / #8D6C49 / #B9976F / #8B6950 |
| 실험실 모형 | 기초 / 벽체 / 창호로 해석한 오목한 면 / 지붕 | #9FACA6 / #B9C7C5 / #3F9DAA / #527882 |
| 유적 관찰 | 석재 / 관찰자의 피부·의복 / 삼각대 도구 | #D3BE9E / 인물 팔레트 / #526873 |
| 폼페이 공사 장면 | 벽 / 비계 / 용기 / 기존 분말 더미 | #D3BE9E / #8D6C49 / #B9976F / #FFF4DD |
| 콜로세움 | 외벽 / 내부 좌석·벽 / 중앙의 기존 낮은 표면 | #CDA477 / #B89D78 / #B5A07B |
| 주변 유적 | 석재 / 기단 / 실제 돔이 있는 두 모형의 상부 | #D3BE9E / #B5A68B / #A88565 |
| 소나무 | 잎·일부 수관 / 줄기 | #75865C·#8D9A70 / #8D6C49 |

실제 재질은 **51개**이며 보이는 **227개 메시**에 재질을 배정했다. **36개 메시에는 둘 이상의 재질 색**이 배정돼 있다. 별도 객체로 이미 나뉜 석회·결정 등은 기존 부위색을 재질로 옮겼다. 사이프러스 모형은 잎 모양의 단일 메시로 별도 줄기가 없어 줄기색을 창작하지 않았다. 같은 석재 덩어리나 지형처럼 하나의 재료를 표현하는 부분은 한 재질을 유지한다.

Meshy 모형은 seam 정점 중복 때문에 연결 성분이 실제 부품 수와 다르다. 현대 골조·인물·실험실은 실제 전후·상부 뷰에 대조한 위치와 면 방향으로 원래 polygon index를 선택했다. 소나무는 실제 1개 목제 연결체와7개 수관 연결체를 사용했다. 콜로세움은 기존 타원 형태와 면 방향으로 내부·외부 표면을 구분했다. 새로운 아레나 바닥·철근·지붕 형상은 추가하지 않았다. 이 색은 설명용 그래픽이며 재료의 고고학적 실측 결과를 뜻하지 않는다.

현재 렌더와 저장된 Solid 뷰포트는 **Workbench MATERIAL**이다. 색을 직접 조정하려면 해당 모형의 Material Properties에서 `RC.v12.concrete`, `RC.v12.steel` 등 재질을 선택하고 **Viewport Display → Color**를 바꾼다. Shader Editor의 Principled Base Color도 같은 색으로 저장했지만, 현재 Workbench 출력의 색 기준은 Viewport Display Color이다. 각 재질을 따로 선택할 수 있고 메시를 다시 생성할 필요가 없다.

24개 부위 팔레트는 Figma에서24개 원색·24개 의미 alias로 기록했다. [재질 팔레트 JSON](../copy/part_material_palette_v12.json), [재사용 토큰](part-material-tokens.json), [CSS](part-material-tokens.css), 편집형 가이드에서 같은 역할 이름과 색을 확인할 수 있다. 기존 제목 Noto Serif KR, 설명 Noto Sans KR 및95개 네이티브 문구·폰트·fill·텍스트 경계는 그대로 유지했다.

v7와v8을 새로 열어317개 객체와 각 메시의 정점·변·루프·면 구조, 변환·부모·컬렉션·카메라·가시성·object color 보존을 확인했다. 공유 메시18개만 동일한 형상의 데이터 복사본으로 분리해 재질이 다른 객체에 번지지 않게 했다. 실제 슬롯 순서·면별 index SHA·face counts·51개 diffuse/Principled 색은 적용 리포트와 일치한다. MATERIAL 표시 모드 외 Studio·shadow·cavity·배경·노출·해상도는 동일하다. [저장본 검증](../out/v8-saved-material-validation.md)과 [Figma 검증](../out/figma-v12-part-material-validation.json)을 참고한다.

사용 도구는 brand·design-system·figma-use·figma-generate-library 스킬, Blender Python API와 실제 렌더, 공식 Figma MCP이다. 기존 모형을 사용했고 새 Meshy 생성 작업은 없다. 실제1x/2x 포스터와 부위 확대를 검토했으며 독자 이해도 실험은 수행하지 않았다.
