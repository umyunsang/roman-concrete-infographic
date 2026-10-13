# 로컬 서사 문안과 글 오버레이

합성에는 `text_overlay_narrative_rgba_2x.png`를 사용한다. 캔버스는 1191×1684, 이미지 파일은 2382×3368 RGBA다. 확정 문안·좌표·패치 영역은 `narrative_copy.json`, 합성 배치 검사용 글 영역은 `text_zones_narrative.json`에 있다.

`build_overlay.py`는 기존 `team/text_overlay_rgba_2x.png`를 복제하고 승인된 질문·CORE·작은 과학/역사 문구와 새 모형 캡션만 바꾼다. D4 제목과 근거 주의 문구는 큰 CORE④ 시퀀스 바로 아래로 옮긴다. CORE 숫자의 기존 픽셀은 복원하며 패치 밖 픽셀 변화가 0인지 검사한다. 원본 Figma·Blender·원본 JSON·원본 오버레이를 수정하지 않는다.

`figma_text_narrative.json`은 과거 글 목록에 패치를 더한 참고 자료다. 유지된 항목의 모든 좌표가 현재 Figma와 같다는 뜻은 아니므로, 전체 목록을 다시 그리는 방식보다 위 RGBA와 패치 명세를 사용한다.

`overlay_validation.json`은 글 너비, 새 글과 유지한 글의 겹침, 모델 투영 상자와의 겹침, 지정 영역 밖 픽셀 변화를 기록한다. 실제 합성 렌더의 명암·가독성·물체 인식, 독자 이해도는 이 기하 검사의 범위에 포함되지 않는다.

재생성: `python3 copy/build_overlay.py` (프로젝트의 `narrative_benchmark_20261007/`에서 실행). `out/integration-report-v*.json` 중 가장 높은 버전의 실제 모델 상자와 지정한 최종 방파제 상자를 검사한다. 검사에 사용한 보고서 경로는 `overlay_validation.json`에 남긴다.
