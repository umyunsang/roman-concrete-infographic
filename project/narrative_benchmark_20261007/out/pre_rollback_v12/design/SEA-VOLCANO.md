# 바다·화산 부위별 배색과 본문 압축 · v13

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
