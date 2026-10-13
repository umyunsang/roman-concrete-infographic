# 물체 심사 1라운드 수정 워커 공통 규칙 (wave 1, 입력 v8_14)

- 작업 폴더 W = /private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work (iCloud Documents 폴더는 열지 말 것)
- Blender: /Applications/Blender.app/Contents/MacOS/Blender (헤드리스 -b --factory-startup). Blender MCP의 look 도구는 쓰지 않는다.
- 입력: $W/out/roman_concrete_narrative_v8_14.blend — 읽기 전용, 절대 덮어쓰지 않음.
- 산출: $W/workers/<이름>/step.py 와 시험 출력 $W/workers/<이름>/<이름>_test.blend.
  실행 규약: Blender -b <in.blend> --factory-startup --python step.py -- <out.blend> [render_prefix]
  입력 경로나 $W/out/의 기존 파일 이름으로는 저장을 거부한다. 멱등(같은 입력 두 번, 자기 출력에 다시 = 같은 결과).
- **물체 소유권:** 프롬프트에 적힌 '네 물체'만 바꾼다. 다른 워커가 같은 시각에 다른 물체를 고친다. 저장 전에 소유 밖 물체의 메시·행렬·재질 해시가 입력과 같은지 확인하고, 다르면 저장하지 않는다.
- **공유 재질:** 소유 물체만 쓰는 재질만 고친다. 다른 물체도 쓰는 재질(예: RC.v12.linen, RC.v12.toolwood, RC.v12.roman_stone)은 복제해 네 물체에만 지정한다. 단 예외로 명시된 토큰은 소유 워커만 바꾼다.
- **땅에 앉히기:** 물체를 지형 위에 놓을 때는 step 실행 시점의 T_land 높이를 광선으로 다시 재서 앉힌다(지형 워커의 step이 먼저 실행된다). 고정 z 값을 박지 않는다.
- **순서:** 최종 조립 순서는 지형·길·밭(WE) → 큰 지물(WD1) → 작은 지물·항구(WD2) → ② 장면(WB) → ③④⑤(WC) → 머리 띠·도형(WA) → 이정표(WM). 네 step은 앞 워커들의 변경 뒤에도 같은 의도로 돌아야 한다(이름으로 찾기, 실행 시점 재계산).
- **지적 원본:** $W/review_loop/obj_r11/findings_by_asset.md(.json) — 네 자산 절의 모든 지적(blocker·major·minor). 판정 기준은 $W/review_loop/rubrics/obj_*.md(항목 번호로 찾기). 결정·기각은 $W/review_loop/STATE.md.
  자산 → 물체 대응: $W/review_loop/obj_r11/assets_index.json, 재질 hex: inventory.json. 맥락·단독 크롭: $W/review_loop/obj_r11/assets/<id>/context.png·isolated.png. 포스터: $W/review_loop/r11/poster_2x.png. 글 상자: $W/review_loop/text_spec_r11.json(화면 pt 1191×1684).
- **검증 먼저:** 각 지적을 먼저 재현한다(비평가 수치를 다시 잼). 재현되지 않거나 STATE 결정·기각과 충돌하면 고치지 말고 rejected에 근거와 함께 남긴다. blocker·major는 반드시 처리(수정 또는 근거 있는 기각), minor는 2개 이하로 남겨도 되지만 쉬운 것은 고친다.
- **도구:** 화면 좌표·지형·가림은 $W/workers/layout/common.py(Screen, to_pt 등), 렌더는 $W/scripts/integrate_assets.py의 render_two_pass(Path) → 48% 두 패스 PNG(2381×3367, 1pt=2px). 자산만 다시 렌더: $W/workers/inventory/render_assets.py(--only id1,id2, 출력 폴더 인자). 대비는 $W/workers/roads/contrast.py(python3 -P). Python: uv run --no-project --with pillow --with numpy --with scipy python -I.
- **Meshy:** 사용자가 AAA 품질을 위해 Meshy AI 새 생성을 허락했다(Hunyuan 금지). 꼭 필요할 때만, 워커당 생성 3회(약 60크레딧) 이내. 흐름: meshy_text_to_image(nano-banana-2) → meshy_image_to_3d(meshy-7.1, should_texture false, glb) → Blender에서 크기·위치·재질(포스터 토큰) 맞춤. 먼저 meshy_check_balance.
- **확인:** 전후 3배·6배 크롭을 $W/workers/<이름>/crops/에 만들고 직접 열어 본다. 수치는 비평가와 같은 방법으로 다시 잰다.
- **최종 출력(JSON):** {worker, summary, step_script, output_blend, owned_objects, files, fixed:[{asset, finding_id, severity, before, after}], rejected:[{asset, finding_id, reason}], verification:[{check, pass, evidence}], open_issues}
