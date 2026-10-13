---
name: roman-poster-v12-color-pipeline
description: "로마 콘크리트 컬러 포스터(v12→v12.1) 현재 작업본 위치, Blender 2패스→Figma 배경 교체 절차, Meshy 화살표·WebP 업로드 함정"
metadata:
  node_type: memory
  type: project
  originSessionId: 73df8d3b-73af-481e-9f8b-64064c56fc53
  modified: 2026-10-12T04:38:21.982Z
---

컬러 디자인 단계(10/8~)는 `~/Documents/로마콘크리트_3D/narrative_benchmark_20261007/`에서 진행됐다([[blender-3d-pipeline]]의 후속). README.md가 항상 현재 작업본을 가리킨다.

- **현재 작업본(2026-10-12)**: Figma `790:78` "v12.1"(페이지 19:4, x −5418) + Blender `out/roman_concrete_narrative_v8_2.blend`(v8_1 = 평평한 화살표안, 폐기). v12(`737:78`)·Blender v8은 보존. v13~v15는 사용자가 되돌려 폐기한 안.
- 구조: Figma 프레임 = 배경 사각형(Blender 렌더 이미지) + 편집형 글. 번호 원판·밑줄·지시선·연표 선은 Blender `80_SHAPES`(오버레이 패스), 글만 Figma. 글 색은 변수에 바인딩(코어 ②색 = `semantic/type_heat` #983821).
- 갱신 절차: 백그라운드 Blender로 v8을 열어 수정 → 새 파일로 저장(원본 덮어쓰기 금지) → `integrate_assets.py`의 `render_two_pass`(48% = 2381×3367) → 합성 스크립트로 2382×3368 PNG → Figma 프레임 복제 후 배경 노드에 `upload_assets`(nodeIds, FIT).
- **10/12 사용자 결정**: 코어 ①~⑤ 색을 ②번 색 하나로 통일, 읽는 방향 표시 3개(①→②, ②→③④, ③④→⑤), 맨 아래 연표 제거. '소제목 배경 깔기'는 사용자가 취소함. 방향 표시는 평평한 화살표가 거절되고 **로마 가도 이정표(석회암 기둥+받침+②색 화살표 판)** 로 확정 — [[roman-poster-diegetic-objects]].

**Why:** 다음 세션이 옛 v12나 Blender v8을 고치면 이번 변경이 사라진다. 아래 함정은 각각 한 번씩 시간을 잃은 것이다.

**How to apply:**
- Figma에 **무손실 WebP를 올리면 업로드는 성공해도 이미지가 비어 보인다**(`getSizeAsync` 실패). PNG(10 MiB 이하)로 올리고, 올린 뒤 `getImageByHash().getSizeAsync()`로 확인한다.
- Meshy text-to-3d는 화살표 같은 추상 아이콘에 약하다(창 모양, 3D 십자가 나옴, 2회 40크레딧). **이미지 경유가 한 번에 맞았다**: nano-banana-2 시안(6) 확인 → image_to_3d meshy-7.1 메시만(20). 비용은 매번 먼저 확인받는다.
- Meshy 메시는 한 덩어리(연결 성분 1)라 부위 색은 형상으로 나눈다: 정규 좌표계(기둥 축 원점, 판 +X, 판 −Y 쪽)에서 '기둥 원통 밖 또는 기둥 앞면보다 튀어나온 면 = 판'. 평면 거리로 나누면 기둥 앞면이 판으로 잡힌다. 판만 키울 때 기둥과 공유하는 꼭짓점은 고정(`scripts/milestone_signs_v8_2.py`).
- 세운 판은 카메라 쪽(화면 아래쪽 방향)을 가리키면 납작해진다. 회전각은 '화면 방향 오차 + 판 정면 보임(n·카메라)'으로 고르고, 좌우 반전 메시를 함께 후보로 둔다(①→② 판은 반전해야 보임).
- 회전된 Figma 글(지명, 30°)은 `node.y`가 경계 상자 위쪽이 아니다. 옮긴 뒤 `absoluteBoundingBox`로 다시 잰다.
- 화면 pt → 땅 좌표는 카메라 `view_frame` 광선을 지형+길 BVH에 쏴서 구한다(오버레이 평면이 카메라 앞에 있어 `scene.ray_cast`를 쓰면 먼저 맞는다).

- **적대적 리뷰 루프(2026-10-12 사용자 요청: 분야별 독립 혹독한 비평가 → AAA까지)**: `narrative_benchmark_20261007/review_loop/`. BRIEF.md(고정 조건·등급), STATE.md(라운드 표·결정 D·기각 R), rubrics/<6분야>.md(1라운드 비평가가 최신 문헌으로 만든 고정 기준), r<N>/(poster·tiles·report_*), text_spec_r<N>.json. 분야 6 = 컬러·인포그래픽·타이포·레이아웃·3D·위계접근성. 1라운드 B/A/B/B/B/A → Figma 790:78 수정 + Blender v8_4(`scripts/review_r1_fixes_v8_3.py`, `review_r1_addendum_v8_4.py`). 2라운드는 같은 루브릭으로 새 비평가 블라인드 심사(Workflow `poster-critic-round`, args {loopDir, round}). 종료 = 분야마다 다른 비평가 연속 2라운드 AAA. **인쇄 원고(300ppi·재단 3mm)는 수렴 뒤 별도 프레임으로 만들어야 함(STATE R4).**
- 루프 운영 함정: Figma `saveVersionHistoryAsync`는 MCP에서 미지원. 회전 글·자동 레이아웃 프레임(CORE 묶음 VERTICAL, '단계 제목' 높이 고정)은 줄 높이를 바꾼 뒤 `primaryAxisSizingMode='AUTO'`로 감싸야 줄어든다. CORE 번호 원판·밑줄은 Blender 카메라 앞 평면이라 화면 pt 좌표로 광선-평면 교차해 다시 만든다.
- **루프 진행(2026-10-12 18시)**: r1 B/A/B/B/B/A → r5 컬러·위계·인포 연속 AAA로 수렴, 타이포 r5 AAA, 레이아웃·3D AA. Blender 최신 `out/roman_concrete_narrative_v8_8.blend`(라운드마다 `scripts/review_r<N>_fixes_v8_<M>.py`, 합성 `compose_r<N>_map_v8_<M>.py`). r6은 남은 3분야만(Workflow args.fields). 수렴 뒤 할 일: `scripts/render_print_bleed.py`(5033×7087, 3mm 재단 여분, 안쪽 35.5px 정렬 검증됨)로 인쇄용 프레임 1208×1701pt 제작 — Figma 4096px 한계로 2×2 타일 JPEG, 강조색·단계 라벨은 CMYK 직접 지정 메모(R8·R9), 그 뒤 위계·접근성 비평가로 인쇄 원고 판정(R4).
- 3D 수정 교훈: 콜로세움 스캔 잔해는 하나의 타원이 아니라 '각도별 서 있는 벽선(높이 3.2 이상 면의 반경 98백분위)' 바깥 낮은 면으로 골라야 지워짐. Meshy 모델(철근 골조)의 작은 섬은 구조 일부일 수 있어 지우지 말 것. 땅 지명을 옮길 땐 map_only와 겹침·4pt 여유를 먼저 잴 것(2라운드 '수도교' 이동이 3라운드 blocker를 만듦).
- **상태(2026-10-12 19:30)**: 컬러·위계·인포·타이포·레이아웃 5분야 연속 AAA 수렴. 3D는 r7 AAA → r8(3D만) 심사 중(Workflow task w1fr6glfy, journal wf_9ee4d6c4-72e). Blender 최신 v8_10, 화면 프레임 790:78. **인쇄용 프레임 `810:78`**(1208×1701pt, 2×2 300ppi JPEG 타일, 내용 +8.5pt) → `out/print/로마콘크리트_A2_재단3mm_인쇄원고.pdf`(426×600mm, Type3 글꼴, 이미지 원본 크기) + `PRINT_SPEC.md`(CMYK 권장값). 인쇄 원고 단독 판정 Workflow task w4asck92u(journal wf_6a9a7fbf-024). 사용자: "AAA 품질을 위해 3D 모델을 Meshy로 새로 생성해도 됨" — 3D가 r8에서 AAA 못 받으면 해당 모델(유력: 베수비오 스캔 지느러미 R11) 재생성. 3D가 r8 AAA면 전체 수렴 → STATE·README 정리, 인쇄 프레임은 디자인이 바뀌면 다시 만들 것.
- 7번째 분야 '명암·명도 구성'(value) 추가(2026-10-12 19:3x, 사용자 질문: 컬러 검토에 명암 포함됐나 → 글 대비·3D 음영은 봤지만 포스터 전체 명도 설계는 없었음). 첫 심사 Workflow task wswwuexix(journal wf_60d828aa-a37), 루브릭 rubrics/value.md. 이 분야도 다른 비평가 연속 2회 AAA까지.
- **State as of 2026-10-12 20:40.** Round-8 results came back:
  - 3D: B (the Pantheon was a peripteral temple, not its real form; the step 1/2 cracks in ④ were invisible).
  - Value (first review): AA.
  - Print master: AA (sRGB, no TrimBox).
- **v8_11 fixes:**
  - Pantheon replaced with a Meshy 7.1 image-route model (concept 6 + mesh 20 credits): `models/pantheon_v1`.
  - ④ cracks redrawn as camera-facing per-segment quads (a ribbon on the shaded side face renders white as grey).
  - Material colours rescaled by linear reflectance to fix value.
  - Print master is now PDF/X-4 CMYK: `scripts/make_print_pdfx.py` — Ghostscript `-dPDFX=4`, PSO v3, `-dBlackPtComp=0`. Afterwards pypdf sets TrimBox, removes stray `h` closepaths and the invisible Type3 text layer, and forces a 1.6 header.
- **Work copy:** because of iCloud eviction ([[roman-poster-icloud-eviction]]), the working copy lives in the session scratchpad `nb_work/`; results are copied back to Documents.
- **Round 9:** all 7 fields plus print, Workflow wf_f955cfc0-52a, loopDir = `scratchpad/nb_work/review_loop`.
