---
name: comfyui-generative-pipeline
description: 로마 콘크리트 포스터 생성형 단계 — Comfy API(2026-09-30) 실행 경로, Z-Image-Turbo+Fun ControlNet 추천안, 스타일 LoRA, 라이선스 함정(Qwen-2.1 연구용·Hunyuan 한국 제외)
metadata:
  type: reference
---

2026-10-07 Blender 모델링을 취소하고([[blender-3d-pipeline]]) 스케치→ComfyUI 생성형으로 전환하며 조사한 것. 원문: `~/Documents/로마콘크리트_3D/comfy/research/comfyui.md`.

- **"워크플로우 API 업데이트" = Comfy API(2026-09-30 발표)**: 워크플로우+노드+모델을 Build→Release→`https://<dep>.run.comfy.app` 엔드포인트로. API v2: `POST /api/v2/assets`(이미지 업로드, 워크플로우에서 `{"__type":"core/ASSET","info":{"id":…}}`), `POST /api/v2/jobs {"workflow": API 형식 JSON}`(UI 형식은 거부), `GET /api/v2/jobs/{id}`. 인증 `Bearer comfyui-…`.
- Claude Code에서 쓰는 길: ① comfy-cli 1.22.0 `comfy cloud login` → `comfy run --workflow wf_api.json --where cloud --wait` ② Claude 플러그인 `Comfy-Org/comfy-skills`(MIT, comfy-cloud MCP: submit_workflow·upload_file·wait_for_job) ③ RunPod 등 자기 GPU + `/prompt` 또는 comfy-mcp(AGPL 베타).
- Comfy Cloud: RTX 6000 Pro 96GB, 실행당 30분 제한, 커스텀 노드 설치 불가(UltimateSDUpscale·Inpaint-CropAndStitch·controlnet_aux·Impact RegionalSampler·SUPIR 등은 기본 포함). Standard 약 $20/월(API), Creator 약 $35/월(Civitai LoRA 가져오기).
- **추천 생성안**: Z-Image-Turbo + `alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union-2.1`(Apache, 기본 노드 ModelPatchLoader·ZImageFunControlnet, 공식 템플릿 있음) — 스케치는 선화가 아니라 **회색 면 도형**이라 영역 경계 맵+회색 도형+팔레트 색칠 시작 이미지(denoise 0.6~0.75)+물체별 SVG 마스크 인페인트(CropAndStitch)로. 고품질 대안 Qwen-Image-2512 Fun ControlNet(Apache). 업스케일: UltimateSDUpscale ×2 → SeedVR2. Figma는 한 변 4096px 넘는 이미지를 줄이므로 2×2 타일로 넣기.
- 스타일 LoRA 후보: ClayAnimationRedmond, 3DRenderStyle-REDMOND-ZIMAGE(HF Apache), ISOMETRIC REDMOND(낮은 가중치), Handpainted Miniature, Clay Art-CE. Civitai는 로컬 DNS 필터에 막힘(civitai.red API 미러로 조회됨).
- **라이선스**: Qwen-Image-2.1·그 ControlNet은 연구용(과제는 가능, 판매 불가). FLUX.2-dev/klein-9B·FLUX.1-dev 비상업. Hunyuan 계열은 한국 제외 — 사용 금지.
- M1 16GB: 제어 이미지·마스크 준비와 SDXL 미리보기만. 본 생성·35MP 업스케일은 클라우드.
