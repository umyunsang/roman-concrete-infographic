# 로마 콘크리트 포스터 · v12.1

현재 작업본은 **[Figma v12.1](https://www.figma.com/design/jQPriO85F6wtPy1NPo752p/?node-id=790-78)**(`790:78`)와 이에 연결된 **[Blender v8.2](out/roman_concrete_narrative_v8_2.blend)**이다. v12(`737:78`)와 Blender v8·v8.1(평평한 화살표안)은 그대로 두었다.

v12 → v12.1 변경(2026-10-12):
- 코어 ①~⑤의 번호 원판·밑줄(Blender)과 제목 둘째 줄(Figma `semantic/type_heat`)을 ②번 색으로 통일
- 읽는 방향 표시 3개 = 로마 가도 이정표: 석회암 기둥·받침 + ②번 색(#983821) 화살표 판. Meshy 시안 이미지 → 7.1 메시, 판만 1.45배 키움(`47_DIRECTION_ARROWS`, `scripts/milestone_signs_v8_2.py`)
  - v8.1의 평평한 화살표안은 사용자가 '로마 시대 오브젝트처럼' 요청해 교체
- 화살표와 겹치던 '아펜니노 산맥' 지명은 산기슭으로, ② 화살표 끝의 볏단 밭 조각은 강가 아래 빈 땅으로 옮김
- 맨 아래 연표(글 14개·선·점) 제거

- [포스터 · 2382×3368](out/figma_poster_v12_1_milestones_2x.png) · [미리보기](out/figma_poster_v12_1_milestones_1x.png)
- 제작 스크립트: `scripts/core_arrows_v8_1.py`(색·연표·밭 이동) → `scripts/milestone_signs_v8_2.py`(이정표), `scripts/compose_milestones_map_v8_2.py`(합성)
- 기록: `out/v12_1-milestones-receipt.json`, `out/v8_2-milestones-report.json`, `out/v12_1-core-arrows-receipt.json`
