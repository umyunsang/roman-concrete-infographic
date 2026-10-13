# ComfyUI 생성 단계 — 상태 기록

## 결정 (2026-10-07)
- Blender 직접 모델링 취소 → 스케치 기반 생성형 이미지(ComfyUI).
- 실행 환경: **Comfy Cloud + comfy-skills 플러그인**(`comfy-cloud@comfy-skills`, 커밋 d50722a, MCP `https://cloud.comfy.org/mcp`).
  - 사용자 할 일: Comfy Cloud 요금제(Standard ≈$20/월 API, Civitai LoRA는 Creator ≈$35/월) → `/mcp`에서 comfy-cloud 로그인 → 필요하면 세션 재시작.
  - 플러그인의 `/comfy-cloud:rickroll` 명령은 볼륨 최대+유튜브 열기 장난 — 쓰지 말 것.
- 스타일: 미니어처 디오라마(클레이) + 약간 플랫, 로마 안료 팔레트(`scripts/palette.py`).
- 글·지시선·범례·연표는 Figma에 남긴다. 생성 이미지는 글 없는 바탕 지도이고 스케치 기하와 겹쳐야 한다.

## 입력(inputs/) — `python3 scripts/make_controls.py`로 재생성
| 파일 | 내용 |
|---|---|
| `map_textless_2x.png` | 글 없는 스케치 지도 2382×3368(Figma 지도 그룹 6개를 배경색 마스크로 합성) |
| `start_color.png` | 1216×1728, SVG 면을 의미별로 팔레트 색칠 + 스케치 회색 → 3단 음영(img2img 시작점, denoise 0.6~0.75) |
| `edges.png` | 1216×1728, 보이는 면 경계만(면 ID 지도에서 추출) — Fun ControlNet Canny 입력 0.65~0.9 |
| `gray.png` | 1216×1728, 회색 다이어그램 — Fun ControlNet Gray 대안 |
| `masks/*.png` | 18종(colosseum, aqueduct, harbor, volcano, smoke, lab, house, wall, hill, mountain, river, sea, coast, roads, fields, plaza, kiln, tree) — CropAndStitch 인페인트용 |
| `controls_meta.json` | 캔버스 1216×1728, 배율 1.02099 px/pt, 아래 여백 8.65px(늘이지 않음) |

좌표: 캔버스 px = Figma pt × 1.02099. 최종 A2(4962×7016)로 올릴 때 같은 균일 배율로 되돌린다.

## 계획
1. comfy-cloud MCP로 템플릿 `image_z_image_turbo_fun_union_controlnet` 확인·API 형식으로 받기.
2. 기본 생성: Z-Image-Turbo + Fun ControlNet Union 2.1(edges, 0.65~0.9) + start_color img2img(0.6~0.75) + 스타일 LoRA(3DRenderStyle-REDMOND-ZIMAGE / ClayAnimationRedmond).
3. 물체별 인페인트(CropAndStitch + 마스크 + 물체 프롬프트): 콜로세움 절개면, 항구·등대, 수도교, 베수비오·연기, 실험실 섬.
4. 전체 조화 img2img 0.15~0.25.
5. 업스케일: UltimateSDUpscale ×2(Z-Image 0.2~0.3) → SeedVR2 → 4962×7016.
6. Figma: 2×2 타일(한 변 4096px 제한) 글 층 아래, 스케치와 Difference로 정렬 확인.

## 조사 원문
`research/comfyui.md`(Comfy API·워크플로우·LoRA·라이선스), `research/academic.md`, `research/ecosystem.md`, `research/pipeline3d.md`.
