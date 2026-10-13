# ComfyUI research for Rome A2 poster (started 2026-10-07)
Status legend: [V]=verified by fetching page/repo, [S]=from search snippet only, [U]=unverified

## 1. ComfyUI API options
### "Recent update" = Comfy API (blog 2026-09-30) [V]
- https://blog.comfy.org/p/comfy-api-is-live-deploy-comfyui : "Comfy API is live for everyone on a paid Comfy plan". Package workflow + custom nodes + LoRAs + models + pinned deps as a Build -> immutable Release -> Deployment (autoscaling endpoint https://<deployment>.run.comfy.app). CLI: `comfy build init`, `comfy build push --release`, `comfy build release create --target linux/nvidia --watch`, `comfy deploy scale --deployment dep_x --min 0 --max N`. Console platform.comfy.org. Billed per second GPU; storage $0.20/GB-mo.
- Docs: https://docs.comfy.org/development/serverless/overview ; SDKs https://docs.comfy.org/development/api-development/sdks (pip comfy-sdk 0.4.0 / npm @comfyorg/sdk 0.4.0 — verified on PyPI/npm). SDK targets: Comfy Cloud (default https://cloud.comfy.org), Comfy API deployments, self-hosted via comfy-api-proxy (github Comfy-Org/comfy-api-proxy, MIT).
- Comfy API GPU prices (comfy.org/pricing) [V]: RTX PRO 6000 96GB $4.54/hr; H100 $6.23/hr; H200 $7.71/hr; B200 $11.23/hr; flex workers 30s idle window; min 0 => cold start.
- Limits: Standard/Creator 5 releases, 2 deployments, 2 max workers; Pro 10/5/10.
### Comfy Cloud (hosted ComfyUI UI + Cloud API) [V]
- Base https://cloud.comfy.org, header X-API-Key, key from platform.comfy.org (keys start `comfyui-`). v1 cloud API deprecated in favor of "Comfy API v2" (SDK). Experimental label.
- API access: Standard, Creator, Pro (docs api-reference/cloud/overview says Standard+; an older page said Creator/Pro only -> conflicting; pricing page lists API concurrency Standard 1, Creator 3, Pro 5).
- Plans (pricing page, garbled monthly/annual): Standard ~$16-20/mo 4,200 cr/mo; Creator ~$28-35/mo 7,400 cr/mo **custom LoRA/model import**; Pro ~$80-100/mo 21,100 cr/mo. Free: 5 runs. GPU: RTX 6000 Pro Blackwell 96GB; 30 min max run (Pro 1h). Custom nodes "supported" = preinstalled set (900+ models preinstalled).
- Credit burn [S]: 0.39 credits/s GPU (~1,400 cr/h). 211 cr ≈ $1 (from 957.94 cr = $4.54) => ~$0.0018/s ≈ $6.6/h effective.
### MCP servers [V]
- Comfy Cloud MCP: remote https://cloud.comfy.org/mcp, OAuth. Claude Code: `/plugin marketplace add Comfy-Org/comfy-skills` -> `/plugin install comfy-cloud@comfy-skills` -> `/mcp` authenticate. Tools: search_templates, search_models, search_nodes, run_template, submit_workflow, partner_generate, upload_file, get_job_status, wait_for_job, get_output, submit_batch, save_workflow... Needs active subscription for generation. Docs https://docs.comfy.org/development/cloud/mcp-server . Repo Comfy-Org/comfy-skills (MIT, 219★, pushed 2026-10-06).
- Local: comfy-mcp (PyPI 0.10.0, repo Comfy-Org/comfy-mcp, AGPL-3.0 or commercial, beta, 40 tools), formerly comfy-local-mcp. `pip install comfy-mcp "comfy-cli>=1.14.0"`; `claude mcp add comfy-mcp -e COMFY_BIN=/path/venv/bin/comfy -- comfy-mcp`. COMFYUI_URL can point at remote ComfyUI (e.g., a RunPod pod). comfy-cli 1.22.0.
- Docs https://docs.comfy.org/agent-tools/local
### Partner model catalog (docs llms.txt router schemas, Oct 2026): flux-3-image, flux-2-pro/max, flux-kontext-pro/max, qwen-image-3.0(-pro), seedream-5-0(-pro/flash), gpt-image-2/2.5, nano-banana-2/pro/2.1, gemini-3-pro-image, ideogram-4-5, recraftv4_1(vector), krea-2, hunyuan image 3.5, topaz bloom 2, seedvr2, ultimate-image-upscaler (wavespeed), freepik precision upscaler v2.


## 2. Layout-locked workflows
### Open models w/ structure control (HF API verified 2026-10-07)
- Qwen-Image-2.1 (Qwen/Qwen-Image-2.1, released ~2026-09-14/20): unified T2I+edit, 7B DiT, 10 ref images, RGBA, native 2K. LICENSE = **Qwen Research License (non-commercial, "research or evaluation purposes only")**. ComfyUI native (Comfy-Org/Qwen-Image-2.1; templates image_qwen_image_2_1_t2i / _image_edit).
  - ControlNet: alibaba-pai/Qwen-Image-2.1-Fun-Controlnet-Union (2026-09-24, 7GB, 8 conds incl. Lineart/Scribble/Canny/Depth/Gray + inpaint; same research license). Card shows only VideoX-Fun inference; no official Comfy template yet (community t8star/Qwen-Image-2.1-Fun-Controlnet-Union-Comfy, 0 dl). [ComfyUI native support UNVERIFIED]
- Qwen-Image-2512 (Apache-2.0) + alibaba-pai/Qwen-Image-2512-Fun-Controlnet-Union (Apache-2.0; 2602 version) -> official template image_qwen_Image_2512_controlnet.json (ControlNetLoader + ControlNetApplyAdvanced, Canny preproc, Lightning 4-step LoRA option). Files from Comfy-Org/Qwen-Image_ComfyUI.
- Qwen-Image (orig) + DiffSynth union control LoRA (canny/depth/lineart/softedge/normal/openpose) template image_qwen_image_union_control_lora.json; InstantX union controlnet template image_qwen_image_instantx_controlnet.json (+inpainting variant).
- Qwen-Image-Edit-2509 / 2511 (Apache-2.0), template image_qwen_image_edit_2511.json.
- Z-Image-Turbo (Apache-2.0, 6B) + alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union-2.1 (Apache; 2602 adds Gray; Canny/HED/Depth/Pose/MLSD/Scribble/Gray; 8-step; Tile model for SR; lite variants for low-spec). Template image_z_image_turbo_fun_union_controlnet.json uses native ModelPatchLoader + QwenImageDiffsynthControlnet. Also Z-Image (Base) + Z-Image-Fun-Controlnet-Union-2.1 (Apache).
- FLUX.2-dev (non-commercial FLUX dev license, gated) + alibaba-pai/FLUX.2-dev-Fun-Controlnet-Union (2.38GB) via custom node JLC Flux2 ControlNet (comfyui-wiki news 2026-07-19) [S].
- FLUX.2-klein-4B (Apache-2.0) / 9B (non-commercial) — multi-reference edit (ReferenceLatent), templates image_flux2_klein_image_edit_*.json. No official ControlNet found.
- Krea-2 open (Raw/Turbo, 2026-06, Krea-2 community license — check), Comfy-Org/Krea-2, style-reference LoRA (ostris/krea2_turbo_style_reference), template image_krea2_turbo_int8_image_style_reference.json. Only community pose controlnet.
### Upscale templates (Comfy-Org/workflow_templates, 692 templates)
- utility_seedvr2_image_upscale.json (numz/ComfyUI-SeedVR2_VideoUpscaler; seedvr2_ema_7b_fp16), seedvr2 3b/7b int8 variants
- utility_z_image_turbo_2k_upscaler.app.json (RealESRGAN x4 + Z-Image-Turbo img2img denoise 0.15-0.35)
- utility_pid_latent_upscale_dit.json (PiD pixel diffusion decoder, Z-Image latent 1024 -> 4096 px in 4 steps; Comfy-Org/PixelDiT)
- utility_image_upscale_supir.json
- Partner: api_wavespeed_seedvr2_ai_image_fix, api_magnific_image_upscale_precise/creative, topaz bloom2/wonder3.5, recraft crisp.
### Iso miniature templates: templates-2x2_grid-iso_miniatures.json & api_from_photo_2_miniature.json both use GeminiImage2Node (Nano Banana partner node).


## 3. Style models (civitai.com blocked by local DNS filter -> used civitai.red API mirror; HF API)
Civitai (page = https://civitai.com/models/<id>):
- 2420163 ISOMETRIC REDMOND (artificialguybr) — versions Z-Image-Turbo / Qwen-Image(2512) / Flux.2 Klein 9B (2026-02-25); trig "ISOMETRIC, ISOMETRICREDM"; HF mirrors artificialguybr/ISOMETRIC-REDMOND-ZIMAGE (apache-2.0), -QWENIMAGE (apache, base Qwen-Image-2512), -FLUXKLEIN9B. Civitai perms: Image(outputs) ok.
- 143769 ClayAnimationRedmond — ZIT / Qwen / Klein9B / SDXL; trig "Clay animation, Clay"; 3.2k dl 189👍
- 194138 3D.Redmond 3D Render Style — ZIT/Qwen/Klein9B/SDXL; trig "3D Render Style, 3DRenderAF"; 5.5k dl; HF artificialguybr/3DRenderStyle-REDMOND-ZIMAGE/-QWENIMAGE
- 1492159 Clay Art - CE — Z-Image Base & Turbo, Qwen, Klein9B-base, Flux.1D, SDXL; trig (Flux/SDXL) "clyartCE_style, textured clay art"
- 685433 Handpainted Miniature (Estylon) — Krea 2, ZIT, Flux Kontext, Flux.1D; trig "Handpainted Miniature"; 2.1k dl 166👍
- 2294777 British Claymation — Klein 9B/4B, ZIT; trig "Claymation"
- 2244737 isometric 2d art style — ZIT; trig isometric_art_style (14 imgs, small)
- 2786400 Isometric Diorama (Tranchillo) — Krea 2 only; trig "isometric_diorama" first; 651 dl 80👍
- 2740221 miniature diorama — Krea 2; weight 0.5–0.9
- 1431818 Tilt Shift/Miniature Diorama [F1D/Illu]; 1200408 Isometric Concept IlluXL (Illustrious, trig diorama, isometric); 302122 Miniature XL (SDXL)
- 1342716 Low Poly Papercraft (ZIT), 2204336 Low Poly Style (ZIT, trig l0wp0ly)
HF:
- linoyts/krea2-isometric-3d-lora (Krea-2-Raw, apache tag; trig "isometric skeuomorphic 3D", 2026-06-23)
- ilkerzgi/krea-2-handmade-clay-diorama-lora (Krea-2-Turbo; trig "handmade clay diorama style"), ilkerzgi/krea-2-clay-folk-miniature-lora ("clay folk miniature style"), krea-2-miniature-diorama-figurine-lora, krea-2-mint-peach-diorama-lora
- multimodalart/isometric-skeumorphic-3d-bnb (Flux.1-dev, NC; trig RBNBICN) — icon style, not maps
- Shakker-Labs/FLUX.1-dev-LoRA-Miniature-World (Flux.1-dev NC; "a meticulously crafted miniature scene")
- strangerzonehf/Flux-Isometric-3D-LoRA ("Isometric 3D")
- Quorlen/Qwen_Image_Tilt_Shift_Photography-lora (Qwen-Image; "Tilt Shift Photograph")
- Krea-2 style reference LoRA: ostris/krea2_turbo_style_reference (Krea community license) + template image_krea2_turbo_int8_image_style_reference.json -> feed a clay-diorama reference image instead of a style LoRA.


## 4. Licenses (verified from HF cards/LICENSE files unless noted)
- Qwen-Image-2.1 + its Fun ControlNet Union: Qwen RESEARCH License (2026-09-20) — "NON-COMMERCIAL ... research or evaluation purposes only". Student assignment = non-commercial but definition is narrow; acceptable-ish for coursework, not for any sale/print-for-profit. 
- Qwen-Image / 2512 / Edit-2509 / Edit-2511 + Qwen-2512 Fun ControlNet, DiffSynth & InstantX controlnets: Apache-2.0.
- Z-Image, Z-Image-Turbo, Z-Image Fun ControlNet Union 2.1 (+Tile): Apache-2.0.
- FLUX.2-dev, FLUX.2-klein-9B, FLUX.2-dev Fun ControlNet: FLUX Non-Commercial license (gated). FLUX.2-klein-4B: Apache-2.0. FLUX.1-dev: non-commercial (outputs usable commercially per BFL FAQ [S]).
- Krea-2 Raw/Turbo (12B, open 2026-06-22/23): Krea 2 Community License — commercial OK if company revenue < $1M [S: krea.ai/krea-2-licensing]; gated auto on HF.
- Ideogram-4 open weights (Comfy-Org/Ideogram-4, 2026-06): "ideogram-non-commercial-model-agreement".
- Tencent HunyuanImage-3.0 (and Hunyuan community licenses generally): "DOES NOT APPLY IN THE EUROPEAN UNION, UNITED KINGDOM AND SOUTH KOREA" -> user in Korea: do NOT use Hunyuan open weights. (Partner API 'Hunyuan Image 3.5 Preview' governed by API ToS — avoid anyway.)
- SDXL base: CreativeML Open RAIL++-M (commercial OK). xinsir controlnet-union-sdxl: Apache-2.0.


## 5. M1 16GB feasibility
(pending)

## Extra findings (batch 2)
- Qwen-Image-2.1 Fun ControlNet: native ComfyUI support merged PR Comfy-Org/ComfyUI#16519 (kijai, merged 2026-09-28; comfy_extras/nodes_model_patch.py) -> in ComfyUI v0.38.0 (2026-09-29)+; latest v0.39.0 (2026-10-05). Test weights Kijai/QwenImage_experimental/model_patches. Community alt: T8mars/Comfyui-Qwen-Image-2.1-Fun-Controlnet-Union-T8 (MIT).
- Regional prompting for DiTs: no dominant maintained node for Qwen/Z-Image. RES4LYF (ClownsharkBatwing, 1.35k★) regional cond supports Flux, HiDream, Chroma, SD3.5, SDXL, AuraFlow, WAN (not Qwen/Z-Image per README). ZIT: bbc-s/ZIT-Ideogram (1★, box regions). Krea2: januspluto/ComfyUI-Krea2-Regional (15★). Core ComfyUI ConditioningSetMask is model-agnostic (blends per-cond predictions) [my knowledge, not re-verified]. Ideogram-4 open model has native JSON bbox per-object prompts but NC license.
- Ideogram-4 open weights: Comfy-Org/Ideogram-4 (2026-06), ideogram NON-COMMERCIAL agreement, 13.8GB DiT.
- Krea-2: 12B; Krea 2 Community License; commercial ok < $1M revenue [S].
- Comfy credits: 211 credits = $1 [S support.comfy.org]. Partner prices (credits): Nano Banana Pro 30.38 (~$0.144), NB2 15.19 (~$0.072), Flux.2 pro 6.33+3.17/MP (~$0.03+0.015/MP), Flux.2 max 14.77+6.33/MP, Kontext pro 8.44 (~$0.04)/max 16.88, Seedream 5 Pro 9.50 1K/18.99 2K, Qwen Image 3 9.05, Qwen 3 Pro 2K 22.63 (~$0.107), Ideogram V4 9.05-30.17, Recraft V4.1 10.56, Topaz Bloom 2 96.55/8MP (~$0.46/8MP), Wonder 3.5 24.14/8MP, Magnific Precise V2 35.91-430.88, WaveSpeed SeedVR2 2.11/run (~$0.01), Ultimate upscaler 12.66/run.
- SeedVR2 native in ComfyUI core (PR #14424); 3B/7B; fp16/fp8/int8/nvfp4; "conservative upscaling preserves structure".
- Alternatives: RunComfy (pay-go L40S $2.99/h, A100 $4.99/h, H100 $7.49/h, per-second; serverless API docs.runcomfy.com/serverless) [S]; RunPod serverless (runpod-workers/worker-comfyui 746★, pushed 2026-09-21; 4090 ~$0.72/h serverless, pods 4090 $0.34/h, L40S $0.79/h) [S]; Replicate comfyui/any-comfyui-workflow (~$0.024/run, fixed model/node set; cog-comfyui last push 2025-11) ; ComfyDeploy OSS repos stale (2025). fal: not verified.
- mflux (mflux-community/mflux, MIT, 2.45k★) MLX on Apple Silicon: Z-Image (+Union ControlNet), FLUX.2 Klein, Krea 2, Qwen-Image-2.1 (+ref edit, masks), SeedVR2 upscaling, LoRA, float16 compute for M1. mflux-community HF has z-image-turbo-controlnet-union-2-1 quantized q3..q8.
- Comfy Desktop macOS: macOS 13+, Apple Silicon M1+.
- Trainers: OneTrainer supports Z-Image, Qwen Image, Flux.2 Dev/Klein, Ernie, Chroma, SDXL. ai-toolkit supports Z-Image(+Turbo/De-Turbo), Qwen-Image/2512/2.1, Krea 2 Raw/Turbo, Klein 4B/9B; EDIT training (paired control images) for Qwen-Image-Edit-2511, Qwen-Image-2.1, Krea 2. Mac experimental. Ostris Cloud.
- Custom node repos verified alive: ssitu/ComfyUI_UltimateSDUpscale (2026-06), lquesada/ComfyUI-Inpaint-CropAndStitch (2026-09), Fannovel16/comfyui_controlnet_aux (2026-09), city96/ComfyUI-GGUF (2026-01), TTPlanetPig/Comfyui_TTP_Toolset (2026-09), kijai/ComfyUI-SUPIR (2026-04), Impact-Pack (2026-04).

## USER CLARIFICATION (mid-task): sketch is a DIAGRAM sketch (filled grayscale regions/blocks), NOT lineart.
=> re-rank: lineart/scribble controls less central; prefer (a) Gray/Grayscale control (Z-Image Fun CN 2602 "Gray", Qwen-2.1 Fun CN "Grayscale"), (b) canny/MLSD of region boundaries from SVG at moderate strength, (c) color-blocked img2img (fill SVG regions with Roman palette -> denoise 0.55-0.75), (d) edit models that understand diagrams (Qwen-Image-Edit-2511 / Qwen-2.1 edit / Nano Banana Pro / Flux.2 Klein edit), (e) per-region masks for regional prompts & crop-stitch inpaint. Krea2 lineart-edit LoRA (Cierpliwy/krea2_lineart_edit, needs ostris/ComfyUI-Krea2-Ostris-Edit) downgraded.

## API mechanics (verified)
- Comfy API v2 OpenAPI: https://docs.comfy.org/openapi-v2.yaml . Servers: http://127.0.0.1:8189 (comfy-api-proxy self-host), https://cloud.comfy.org, https://{deployment}.run.comfy.app. Auth: `Authorization: Bearer comfyui-...` (API key) or OAuth/session.
  - POST /api/v2/assets (multipart upload) -> asset UUID; reference in workflow as {"__type":"core/ASSET","info":{"id":"<uuid>"}} where a filename would go.
  - POST /api/v2/jobs {"workflow": <API-format JSON>, "extra_data": {"api_key_comfy_org": "..."} (only for partner nodes)} -> 201 Job; UI-format rejected (workflow_format_ui). Idempotency-Key header.
  - GET /api/v2/jobs/{id}, /events (SSE), /logs, /cancel; outputs via /api/v2/assets/{id}/content. 402 insufficient_credits.
- comfy-cli 1.22: `comfy cloud login` (OAuth PKCE) ; `comfy run --workflow wf_api.json --where cloud` ; `comfy jobs wait <id> --where cloud` ; `comfy download <id> --where cloud -o ./outputs` ; `comfy upload` ; `comfy generate` for partner models without JSON ; `comfy set-default --where cloud`. UI-format JSON auto-converted.
- Local ComfyUI server API [known, not re-fetched]: POST /prompt {"prompt":wf,"client_id"}, POST /upload/image (multipart), GET /history/{prompt_id}, GET /view?filename=..&type=output, WS /ws?clientId=.
- Comfy Cloud custom nodes: cannot install own; ~preinstalled list https://comfy.org/cloud/supported-nodes includes ssitu/ComfyUI_UltimateSDUpscale, lquesada/Inpaint-CropAndStitch, Fannovel16/controlnet_aux, KJNodes, Impact-Pack(+RegionalSampler/RegionalPrompt), RES4LYF (ClownRegionalConditioning), kijai/SUPIR, cubiq essentials & IPAdapter_plus, LayerStyle, Advanced-ControlNet, SAM2/SAM3, Florence2. NOT: Inspire-Pack, GGUF, TTP_Toolset, Easy-Use, Krea2-Regional, ostris Krea2 edit nodes(?), T8 Qwen2.1 CN. BYO LoRA (Creator+): Civitai import (HF 'coming soon' as of 2025-12; cloud docs now say Civitai & HF import).
- Arbitrary custom nodes => Comfy API Builds (serverless, paid plan) or RunPod/RunComfy.
- xinsir/controlnet-union-sdxl-1.0 (+promax): Openpose, Depth, Canny, Lineart, AnimeLineart, MLSD, Scribble, HED, Softedge, TEED, **Segment**, Normal + tile/inpaint/outpaint (promax). Segment control = good fit for diagram->render on SDXL.
- Qwen-Image-Edit-2509 card: "Native Support for ControlNet: depth maps, edge maps, keypoint maps". 2511: less drift, stronger geometric reasoning, industrial design.
- GPT Image 2.5 partner node: custom size 16px steps up to 3840 (exact A-ratio e.g. 2704x3824 possible), up to 16 refs, mask inpaint w/ one ref. Nano Banana Pro: native 4K, 14 refs (aspect presets — not exact A-ratio [U]).
- M1 perf [S]: M2 Pro 16GB SDXL 1024² 25–40 s in ComfyUI; ComfyUI MPS 2-4x slower than CUDA; Draw Things ~3x faster than ComfyUI on Mac; use --force-fp16. Z-Image Turbo GGUF Q8 works on M4 16GB "slow". => M1 estimate (mine): SDXL 1MP ~60–120 s; ZIT 1–2MP+CN several min; 35MP upscale = hours. Cloud recommended.

## Figma constraint (verified via Figma help/forum search)
- Figma downsizes any image >4096 px on a side to longest edge 4096 (A2 7016 px -> 4096 = ~175 dpi). Workaround: place 2x2 tiles (each 2481x3508) edge-to-edge, or composite final print outside Figma (Figma text layer as vector PDF over the full-res image).

## Ex/est cost notes [E = my estimate]
- Comfy Cloud: 0.39 cr/s, 211 cr/$ => ~$0.0018/GPU-s (~$6.7/h on RTX 6000 Pro 96GB). ZIT+CN 2MP ~10–30 s => $0.02–0.06 [E]; Qwen-2512+CN 2MP 60–120 s => $0.11–0.22 [E]; USDU+ZIT to 35MP 5–15 min => $0.55–1.65 [E].
- Partner upscalers: WaveSpeed SeedVR2 2.11 cr/run (~$0.01); Topaz Wonder 3.5 24.14 cr/8MP (35MP ≈ $0.50); Bloom 2 96.55 cr/8MP (≈ $2.0); Magnific Precise V2 35.9–430.9 cr.
- Plans: Standard ~$20/mo (4,200 cr) API yes, no LoRA import; Creator ~$35/mo (7,400 cr) LoRA import + API concurrency 3.

## Core node detail (verified from ComfyUI source comfy_extras/nodes_model_patch.py, main @ 2026-10-07)
- `ModelPatchLoader` + `ZImageFunControlnet` (inputs: model, model_patch, vae, strength; optional image, inpaint_image, mask, start/end_percent). SEARCH_ALIASES include "qwen image 2.1 controlnet": same node drives Z-Image Fun CN AND Qwen-Image-2.1 Fun CN, control + inpaint in one node. `QwenImageDiffsynthControlnet` for Qwen-Image(2512) diffsynth/union patches. Marked EXPERIMENTAL.
- Caution [inference]: model-patch control images are full-frame; inside Ultimate SD Upscale tiles they will not be cropped per tile -> don't use model-patch tile CN inside USDU; use low-denoise img2img in USDU instead, or SeedVR2.
STATUS: research complete; final report delivered to caller.
