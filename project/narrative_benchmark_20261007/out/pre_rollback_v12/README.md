# 로마 콘크리트 포스터

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
