# 로마 콘크리트 인포그래픽 (A2 포스터)

핵심 질문: **철근도 없는 로마 건축물이 어떻게 2천 년을 버텼을까?**
Blender 3D 지도(아이소 원근, Workbench 렌더) 위에 Figma로 글을 얹은 A2(420×594mm) 인포그래픽 포스터 작업 전체를 모은 저장소입니다.

- 디자인 원본(글·레이아웃): Figma 파일 `jQPriO85F6wtPy1NPo752p`, 페이지 `19:4`
  - 디자인 프레임 `790:78`(1191×1684pt), 지도 이미지 노드 `790:79`
  - 인쇄 프레임 `810:78`(재단 여분 3mm, 디자인 +8.5pt), 지도 조각 `810:184`~`810:187`
- 3D 지도: `project/narrative_benchmark_20261007/out/roman_concrete_narrative_v8_*.blend` (Blender 5.2)

## 폴더

| 폴더 | 내용 |
|---|---|
| `project/` | 원래 `~/Documents/로마콘크리트_3D` 전체. 초기 지도·에셋(Meshy GLB, Sketchfab CC-BY 출처는 `assets/ATTRIBUTION.md`)·스케치·초기 심사 루프(`loop/`, `team/`) |
| `project/narrative_benchmark_20261007/` | 현재 작업 트리. `scripts/`(렌더·합성·인쇄 파이프라인), `review_loop/`(BRIEF·STATE·루브릭·라운드 기록), `workers/`(물체별 수정 단계 스크립트), `out/`(blend·인쇄 원고), `renders/` |
| `planning/` | 조사·기획 단계(9/23 근거 마인드맵, 10/1 W3 참고 보드, 10/2 교수 피드백, 10/7 내러티브 감사, 배색 승인안) |
| `deliverables/` | v12 포스터 4배 PNG(Figma `737:78` 내보내기) |
| `feedback/` | 사용자 표시 피드백 이미지(10/12, 빨간 화살표 3개) |
| `workflows/` | 다중 에이전트 블라인드 심사 워크플로 스크립트(물체 단위·포스터 단위·인쇄 원고) |
| `notes/` | 작업 중 남긴 결정·교훈 메모(Claude 메모리, Codex 요약) |

## 현재 상태 (2026-10-13)

- 포스터 단위 7분야(컬러·인포그래픽·타이포·레이아웃·3D·위계/접근성·명암): 라운드 10에서 5분야 연속 AAA 수렴, 레이아웃 AA·3D B. 인쇄 원고 AAA(라운드 10).
- 사용자 변경(콜로세움 위로 이동, 도로·밭 채색, 이정표 MS3 이동, 길 형상 정리) 반영본이 v8_13 → v8_14. 결정은 `review_loop/STATE.md`의 D34~D38.
- 물체 단위 심사 라운드 11(자산 58개 × 6분야, 루브릭 `review_loop/rubrics/obj_*.md`) 완료. blocker·major 75건 → 수정 워커 단계 스크립트(`workers/WA`·`WB`·`WC`·`WD1`·`WE` 등) 작성 중 중단. `workers/WA`(머리 띠·표지 도형)만 완료, 나머지는 미완성.
- Figma 후속 작업: `workers/FIGMA_FOLLOWUPS.md`.

## 복구 메모

작업 사본(세션 임시 폴더)이 10/13에 지워져, 텍스트 파일은 작업 기록에서 복구했습니다. 그래서 아래는 이 저장소에 없습니다.

- `roman_concrete_narrative_v8_13.blend`, `v8_14.blend`. 다시 만드는 방법: v8_11에서 `workers/layout/step.py` → `workers/fields/step.py` → `workers/roads/step.py`(= v8_13) → `workers/roadgeo/step.py` → `workers/ms3/step.py`(= v8_14). 각 단계는 `Blender -b <in.blend> --factory-startup --python step.py -- <out.blend>`. 복구한 스크립트는 실제로 실행된 판과 조금 다를 수 있으니, 다시 만든 뒤 지도 렌더를 Figma `790:79`의 v8_14 지도와 비교하세요.
- v8_14 렌더·인쇄 PDF(최종 판), 라운드 11 자산별 크롭. 인쇄 원고는 `scripts/build_print_master.sh`로 다시 만듭니다.

## 저장소에 넣지 않은 것

- 라이선스가 불분명한 외부 논문 원문 2개(`jackson-2017-paper.pdf`, `vaserman-2025.xml`). 출처: Jackson et al. 2017 *American Mineralogist*, Vaserman 2025.

## 다시 실행하려면

- Blender 5.2(헤드리스), Python 3.12 + `uv`(pillow, numpy, scipy, pypdf), Ghostscript 10, lcms2(`transicc`), poppler.
- 렌더 조명: `project/narrative_benchmark_20261007/roman_poster_studiolight.sl` 파일을 Blender `datafiles/studiolights/studio/`에 넣습니다.
- 100MB가 넘는 옛 blend 2개(`project/roman_concrete_map_pre_opt.blend`, `project/roman_concrete_map_ortho_backup.blend`)는 Git LFS로 올렸습니다.
