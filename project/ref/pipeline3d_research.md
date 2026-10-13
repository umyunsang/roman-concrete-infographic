# 3D pipeline research (2026-10-07)

## Local Unity facts (verified 2026-10-07)
- `unity` = Unity CLI 1.0.0-beta.12 at ~/.unity/bin/unity (Hub-less CLI; replaces Unity Hub).
- Installed editor: 6000.3.23f1 (Unity 6.3 LTS) at /Applications/Unity/Unity-6000.3.23f1/Unity.app (upgrade 6000.3.25f1 available).
- MCP `unity-editor-mcp` = `unity mcp --project-path /Users/um-yunsang/CHOOGuard` (user scope) -> pinned to an unrelated project (CHOOGuard). For poster need a new project + re-pin.
- `unity status`: no instances (no Editor open with com.unity.pipeline). Requires `unity pipeline install` in project.
- MCP exposes Editor commands: eval (arbitrary C#), screenshot (--output --width --height), create_gameobject etc. Tools = whatever Pipeline package registers.
- Plugin unity@claude-plugins-official 0.1.6-beta: skills only (game dev: UI, URP postprocessing, tilemap, IAP, multiplayer...) — nothing for offline still render/NPR. Works with Unity 6+. Unity Companion License.
- Analytics status: false (opted out / no consent).

## ahujasid/blender-mcp (now ahujasid/mcp-for-blender) — verified via gh api
- 30.1k stars, MIT, pushed 2026-10-06 (very active). PyPI `mcp-for-blender` 2.1.9 (old name `blender-mcp` still works). requires-python >=3.10.
- Addon bl_info blender (3,0,0) min; addon v1.8. Socket server localhost:9876, NO auth.
- 9 tools: execute_blender_code (arbitrary Python), look (viewport/camera/angles/wireframe/xray/render), get_scene_info, generate_3d (Tripo/Hunyuan3D/Hyper3D Rodin; "premium" = paid hosted credits via their Supabase fn), search_assets/import_asset (Poly Haven CC0 no key; Sketchfab key; Poly Pizza free key, ~69% CC-BY), get_addon_status, disable_telemetry, record_trajectory_feedback.
- Ships guides: bpy.md, scene.md, level-design.md, materials.md ... (src/blender_mcp/guides)
- Telemetry: default minimal anonymous usage record (install ID, tool name, success, duration, versions, OS) -> Supabase. Content (prompts/code/screenshots) only with opt-in. Full off: env DISABLE_TELEMETRY=true (also BLENDER_MCP_DISABLE_TELEMETRY / MCP_DISABLE_TELEMETRY). Opt-in data "may be used to train AI models".
- Safe mode: BLENDER_MCP_SAFE_MODE=1 blocks file/network/subprocess in scripts (but blocks writing renders? says rendering/saving/import/export still work).
- Install (Claude Code): `claude mcp add blender -e DISABLE_TELEMETRY=true -- uvx --python 3.11 mcp-for-blender` ; addon: `uvx mcp-for-blender install-addon` then enable "Interface: MCP for Blender", N-panel > Start MCP Server. Avoid `curl | sh` installer (auto-edits all client configs).
- Blender 5.2 issues: #299 (closed) & #357 (open) are Windows-only command-timeout; #309 macOS M-series: uvx picked x86_64 python -> cryptography wheel fail; fix `--python 3.11-aarch64`.

## Blender Lab official MCP (projects.blender.org/lab/blender_mcp) — verified via Gitea API
- Blender Foundation "Blender Lab"; docs https://www.blender.org/lab/mcp-server/ ; GPL-3.0-or-later (LICENSE added 2026-09-29); 26 stars; releases v1.0.0 (2026-04-27), v1.0.2, v1.0.3 (2026-09-11: blender-1.0.3.mcpb + mcp-1.0.3.zip). Last commit 2026-09-29 ("Update 5.2: manual & API").
- Addon = extension id "mcp", blender_version_min 5.1.0, permission network (local TCP). Default localhost:9876 (SAME port as ahujasid -> run only one, or change port).
- Tools: execute_blender_code (+ _for_cli background Blender), blendfile summaries, object summaries, get_python_api_docs / search_api_docs / search_manual_docs (bundled 5.2 API+manual RST — great for correct bpy on 5.x), screenshots of area/window, render_thumbnail_to_path, render_viewport_to_path, jump_to_*.
- No asset library / no generator integration. No telemetry code seen (deliberately minimal). Security: "executes LLM code without guards".
- Install: drag-drop addon zip in Blender (or Install from Disk) ; `git clone https://projects.blender.org/lab/blender_mcp.git ~/blender_mcp` ; `claude mcp add blender-lab -- uv --directory ~/blender_mcp/mcp run blender-mcp` (wiki Setup page uses uv --directory .../mcp run blender-mcp). Python pkg name "blender-mcp" 1.0.2 (name collides with ahujasid's old PyPI name — do NOT `uvx blender-mcp` expecting this one).

## Meshy official MCP (meshy-dev/meshy-mcp-server) — verified gh api
- MIT, 49 stars, pushed 2026-10-05; npm @meshy-ai/meshy-mcp-server; 24 tools (text/image/multi-image-to-3d, refine, remesh, retexture, convert, resize, uv_unwrap, text_to_image (nano-banana/gpt-image-2), task mgmt, check_balance, 3D printing).
- Models: meshy-7.1 (latest), meshy-6, meshy-6-lite (5cr mesh), meshy-t2 smart-topology (clean low-poly 100-15k faces, 5cr mesh/15 textured). `model_type: lowpoly` retires 2026-10-30.
- Credits: 7.1 mesh 20 / +tex 30; 6-lite 5/15; t2 5/15; remesh 5; convert/resize 1.
- API key requires **Pro plan or above** (msy_...). Auto-saves to meshy_output/.
- Claude Code: `claude mcp add-json meshy '{"command":"npx","args":["-y","@meshy-ai/meshy-mcp-server"],"env":{"MESHY_API_KEY":"msy_..."}}'` (Bun pref: could use bunx). Avoid `npx add-mcp` (writes to all clients).

## Generators — other
- Meshy plans (meshy.ai/pricing): Free 100 cr/mo, outputs CC BY 4.0 (public; attribution); Pro 1,000 cr/mo, API access, private ownership; ~$20/mo per 3rd-party (costbench) — confirm on page. API = prepaid credits bought in subscription settings. Has Education Program (/education).
- Tripo official MCP VAST-AI-Research/tripo-mcp: MIT, 210 stars, last push 2025-04-14 (STALE) -> SKIP. In ahujasid blender-mcp Tripo only via paid "Premium".
- Hyper3D Rodin in ahujasid addon: own key (hyperhuman.deemos.com) or fal key (queue.fal.run/fal-ai/hyper3d/rodin); shared free-trial key "vibecoding" button (rate-limited shared).
- Hunyuan3D: open weights LICENSE "DOES NOT APPLY IN THE EU, UK AND SOUTH KOREA"; outputs may not be used/displayed outside Territory -> user in Korea: AVOID the open model/derivatives (cloud API = separate Tencent Cloud terms; avoid anyway). On M1 local impractical regardless.
- TRELLIS.2 (microsoft/TRELLIS.2, MIT, 11.5k stars): hosted fal-ai/trellis-2 $0.25 (512)/$0.30 (1024)/$0.35 (1536) per gen, GLB out, commercial OK.
- fal official MCP: `claude mcp add --transport http --scope user fal https://mcp.fal.ai/mcp-relay` (OAuth browser sign-in, no key) — tools search_models/get_model_schema/get_pricing/run_model/submit_job/check_job/get_job_result/upload_file. MCP free; pay per model run. Gives TRELLIS.2, Rodin 2.5, Tripo H3.1, Hunyuan3D Pro, SF3D ($0.07) pay-as-you-go.
- ECC fal-ai-media skill references 3rd-party `fal-ai-mcp-server` npm (derekalia, last 2025-10) — prefer official relay.

## Blender 5.2.2 local probe (background, factory-startup) — VERIFIED
- Freestyle present (render.use_freestyle), Line Art object modifier LINEART (GP v3) present, ShaderNodeShaderToRGB (EEVEE toon) present, CompositorNodeKuwahara present.
- True isometric ortho cam: rotation_euler = (54.7356°, 0, 45°) -> world X/Y axes project at exactly -30°/+30°, all axes equal length (0.8165 x). 
- 2:1 dimetric ("game iso"): (60°, 0, 45°) -> axes at ±26.565°, NOT 30°. So a sketch with 30° axes = TRUE isometric.
- ortho_scale with sensor_fit AUTO spans the LARGER render dimension: A2 portrait 4961x7016 (300dpi) and ortho_scale=10 -> 701.6 px per BU vertically. Set sensor_fit='VERTICAL' explicitly to avoid ambiguity.
- Placement: unproject Figma (u,v) -> ray along camera forward from cam plane point -> intersect ground z=0 (or object's base height). Verify with bpy_extras.object_utils.world_to_camera_view.

## Research (arXiv IDs verified via export.arxiv.org API)
- SceneCraft 2403.01248 — LLM agent writes Blender code; scene graph -> constraints -> layout; VLM critiques render, iterates (render-and-compare).
- BlenderAlchemy 2404.17672 — VLM edits Blender programs, visual-state search vs target.
- BlenderGym 2504.01786 — benchmark of VLM systems for Blender graphics editing (placement, lighting, material...), reports gaps vs humans; inference scaling for verifiers.
- BlenderLLM 2412.14203 — CAD-oriented LLM finetune for bpy (not layout).
- LayoutGPT 2305.15393 — LLM produces CSS-like numeric layouts (2D and 3D indoor).
- Holodeck 2312.09067 — LLM spatial-relational constraints + solver for 3D environments (Objaverse assets).
- 3D-GPT 2310.12945 — LLM agents drive procedural Infinigen code.
- LL3M 2508.08228 — multi-agent LLM writes Blender code to model assets (BlenderRAG).
- SceneWeaver 2509.20414 — self-reflective agent, tool-based scene synthesis with evaluate/refine loop.
- Code-as-Room 2605.18451 — top-down image -> agentic Blender code (closest analog to "match a 2D layout").
- Thinking in Blender / SEIG 2606.02580 — staged executable inverse graphics from a single image: geometry -> materials -> composition -> lighting.
- SceneActBench 2607.22393 — agents act on 3D scenes via MCP-driven headless Blender.
Practical takeaway: numeric anchors (not VLM eyeballing) for placement; VLM render-compare only for final critique; overlay diff metrics (IoU of per-object masks vs sketch regions, anchor-point px error).

## Asset sources (verified via public APIs 2026-10-07)
- Sketchfab (downloadable=true; needs free account API token for download):
  - Colosseum (11.8k faces, CC-BY) https://sketchfab.com/3d-models/e749705838044be78ced42205f9f9dda
  - Previz-Lowpoly Colosseum w/ concept texture (198k, CC-BY) https://sketchfab.com/3d-models/c1c2391478a34ba9a4c5f254c662fb30
  - Colosseo (Flavian Amphitheatre) - Drone (13.8k, CC-BY) https://sketchfab.com/3d-models/73c497e1f4954da0aaa54bf2918bc3c9
  - Roman Colosseum 3d Section (9.3M faces, CC-BY; cutaway ref, decimate) https://sketchfab.com/3d-models/87a0d66a92c1427eb4d16f3805bf87d6
  - Aquaeduct (6.6k, CC-BY) https://sketchfab.com/3d-models/d1b68f033efc486a98389676b37f6064
  - (FREE) Volcano Low poly (15k, CC-BY) https://sketchfab.com/3d-models/516e0bd4e78d4f5caed3f00f056e2e3a
  - Low Poly Roman Temple (WIP) (748, CC-BY) https://sketchfab.com/3d-models/5953273cfe5346cbacf704809a404c83 ; Ancient Temple Modular Kit (25k CC-BY) https://sketchfab.com/3d-models/89243c2c9fe2409e9297fbbe58ba32e3
  - Toorlectra lime kiln (CC0) https://sketchfab.com/3d-models/0da9d13dae774ccfa732b888a8f0d990
  - Avoid NC/ND ones (Mt. Vesuvius NC-SA, Medieval Lime Kiln & Roman Wall NC-ND).
- Poly Haven: 521 models, CC0, mostly realistic props/rocks/coastal cliffs, Dutch ships; little Roman. Use for HDRI only / rocks.
- Quaternius: CC0 ("without the need for attribution in commercial, educational, personal"). Kenney CC0.
- Ancient Greece 3D Low Poly Asset Pack (aitordsgn.itch.io) 350+ assets, CC0, $4.99+, FBX, single 32px palette material — style-consistent temples/houses/ships.
- Unity Asset Store: renders OK; non-Unity use allowed for standard assets but must download via Unity; Unity-published assets under Unity Companion License = Unity-only.

## Blender 5.2.2 probe 2
- Engines EEVEE/WORKBENCH/CYCLES OK; Freestyle as_render_pass True; Cryptomatte True; Workbench object outline + cavity True; resolution hard max 65536; camera background_images True.
- Local: arm64, uv arm64 (/opt/homebrew/bin/uv), uv-managed cpython 3.12.11 present. Blender user dirs 4.5 and 5.2 (no addons yet) -> install-addon may write to both; target 5.2 with BLENDERMCP_ADDONS_DIR.
- Blender Lab server env: BLENDER_MCP_HOST/BLENDER_MCP_PORT (default 9876); ahujasid: BLENDER_HOST/BLENDER_PORT or --port.
