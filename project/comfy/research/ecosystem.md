# Ecosystem scout: Figma infographic / poster design (2026-10-07)

Use case: A2 portrait Korean infographic poster in Figma (isometric Rome map), next stage = color, isometric illustration style, Korean typography, texture, hierarchy, automated critique loop (supervisor + workers + blind VLM judges).

Status: DONE -- see RANKED SHORTLIST at bottom

## Raw findings (appended progressively)

### 1. Official Figma plugin (figma/mcp-server-guide) -- VERIFIED
- Repo: https://github.com/figma/mcp-server-guide  ★2051, pushed 2026-10-05, no LICENSE file (Figma Developer Terms apply), plugin.json v2.2.127.
- In claude-plugins-official marketplace (already configured locally) as `figma`, pinned sha 1729207.
- Install: `claude plugin install figma@claude-plugins-official` (README's own command).
- Contents: skills/ figma-use (+ references: api-reference, gotchas, text-style-patterns, variable-patterns, effect-style-patterns, validation-and-recovery, plugin-api-standalone.d.ts), figma-generate-design (+ discover-product-font.md), figma-generate-library (+ JS helper scripts run inside use_figma), figma-generate-diagram, figma-use-figjam, figma-use-slides, figma-use-motion, figma-implement-motion, figma-shaders, figma-generative-plugins, figma-create-new-file, figma-design-to-code, figma-code-connect, figma-swiftui. Also workflow-skills/ (generate-project-plan, video-interaction-mapper with python scripts) -- NOT referenced by plugin.json? (plugin.json has no skills field -> default `skills/` dir only).
- .mcp.json: http server `figma` -> https://mcp.figma.com/mcp with X-Figma-Plugin-Bundle header. SAME upstream as claude.ai Figma connector.
- Risk: duplicate MCP server. Claude Code changelog: "MCP servers configured both locally and via claude.ai connectors are now deduplicated — the local config wins" (2.1.83) and "Plugin MCP servers that duplicate an org-managed connector are now suppressed" ; "Fixed plugin MCP servers stuck connecting ... when they duplicate a claude.ai connector that is unauthenticated". => After install, check `/mcp`; plugin server may win and need its own OAuth (`/mcp` -> figma -> authenticate), or be suppressed. Either way tool names change prefix (mcp__plugin_figma_figma__* vs mcp__claude_ai_Figma__*) -> any scripts/prompts that hardcode mcp__claude_ai_Figma__ names must be checked. Clean alternative: skills-only copy (`gh` download skills/* into ~/.claude/skills/`) without .mcp.json.
- Value: the MCP server's own instructions say "Prefer the skills shipped with the Figma plugin"; plugin skills are newest (generate_image guidance released 2026-10-05) and load as real skills (auto-trigger, /figma-use). Content is the same family as the MCP-resource fallback, so incremental gain is moderate; main gain = up-to-date gotchas/text-style/variable/effect-style references and the shaders/generative-plugins skills (texture!).
- No API keys besides Figma OAuth. Seat limits: Starter/View/Collab seats = 6 tool calls/month; Dev/Full seat = Tier-1 REST limits. Write-to-canvas free during beta, will become usage-based paid. generate_image consumes Figma AI credits.

### 2. anthropics/skills (marketplace `anthropic-agent-skills`) -- VERIFIED
- Repo: https://github.com/anthropics/skills ★179,916, pushed 2026-10-05. Per-skill LICENSE.txt (canvas-design: Apache-2.0).
- Marketplace plugins: document-skills (xlsx/docx/pptx/pdf), example-skills (algorithmic-art, brand-guidelines, canvas-design, doc-coauthoring, frontend-design, internal-comms, mcp-builder, skill-creator, slack-gif-creator, theme-factory, web-artifacts-builder, webapp-testing), claude-api, academy-guide, discernment-nudge.
- Install: `claude plugin marketplace add anthropics/skills` then `claude plugin install example-skills@anthropic-agent-skills` (brings 12 skills, several duplicate already-installed anthropic-skills:*). Or copy only canvas-design dir to ~/.claude/skills/canvas-design.
- canvas-design (NOT in the user's installed anthropic-skills list): two-step "design philosophy manifesto (.md) -> express on canvas as PNG/PDF via code". Ships ~80 OFL TTF fonts (Latin only, no Hangul). Output is raster/PDF from Python, not Figma. Useful only as a prompt pattern for art-direction ("name a movement, 4-6 paragraphs") before applying in Figma. Fonts download instruction ("Download and use whatever fonts are needed") = network.
- theme-factory / brand-guidelines / algorithmic-art already installed via anthropic-skills.

### 3. pbakaus/impeccable -- VERIFIED
- https://github.com/pbakaus/impeccable ★77,697, pushed 2026-10-07, Apache-2.0, plugin v4.5.0. Own marketplace `impeccable` (source ./plugin).
- Install: `claude plugin marketplace add pbakaus/impeccable` + `claude plugin install impeccable@impeccable` (or `npx impeccable install`).
- What: 1 skill `/impeccable` with 24 commands (critique, audit, polish, colorize, typeset, layout, bolder, quieter, distill...), 60 deterministic detector rules over HTML/CSS/JSX + live-browser variant mode. critique = two isolated sub-agent assessments (design review + detector/browser) then synthesis -- nice pattern, but Assessment B requires code/URL target and Nielsen heuristics (web UI).
- Risk: plugin hooks.json runs `scripts/impeccable hook` on SessionStart, every PostToolUse Edit|Write, and Stop (30s). Launcher execs a platform binary; if absent it DOWNLOADS a binary into ~/.impeccable/bin on first run. Writes PRODUCT.md / DESIGN.md / .impeccable/ into project. Global hooks on every edit = noise for non-web work.
- Fit: web UI only. Figma poster -> SKIP (could read reference/colorize.md, typeset.md, critique.md as text for vocabulary).

### 4. nextlevelbuilder/ui-ux-pro-max-skill -- VERIFIED
- https://github.com/nextlevelbuilder/ui-ux-pro-max-skill ★133,601, pushed 2026-10-03, MIT, v2.13.0. Own marketplace `ui-ux-pro-max-skill`.
- Install: `claude plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill` + `claude plugin install ui-ux-pro-max@ui-ux-pro-max-skill`.
- Skills (8): ui-ux-pro-max (core: offline BM25 search over CSVs -- 89 styles, 192 palettes, 74 font pairings, 1,934 Google fonts incl. 38 tagged korean/hangul e.g. Black Han Sans, Do Hyeon, Diphylleia, Dokdo, Bagel Fat One), design (logo/CIP/icon/banner/social -- generate.py calls GEMINI_API_KEY / ATLASCLOUD_API_KEY / MUAPI_API_KEY and auto-loads .env files), design-system (tokens + slide scripts; fetch-background.py pulls Pexels URLs), brand (node .cjs scripts), banner-design, slides, ui-styling (shadcn/Tailwind, copy of Anthropic canvas fonts).
- Core search.py: no network. Python3 required.
- Fit: palette/font lookup is generic UI; styles skew to app UI (Brutalism, Swiss Modernism 2.0, E-Ink/Paper, Anti-Polish/Raw). No isometric/infographic/print entries. Overlaps heavily with ecc design-system, design:design-system, theme-factory. -> OPTIONAL at best (Korean font lookup is the one unique bit).

### 5. Leonxlnx/taste-skill -- VERIFIED
- https://github.com/Leonxlnx/taste-skill ★93,140, pushed 2026-10-06, MIT. Own marketplace `taste-skill`, plugin `taste-skill` v1.0.0 (source ./).
- Skills: taste-skill (+v1), gpt-tasteskill, brutalist, minimalist, soft, redesign, stitch (Google Stitch DESIGN.md), output-skill, image-to-code, imagegen-frontend-web/mobile, brandkit. All landing-page / web frontend focused ("one horizontal image PER website section").
- NOTE: the user's installed `ecc:taste` is unrelated (ECC video creative-direction skill, angelcore/hyperpop music videos).
- Fit: web UI -> SKIP.

### 6. superdesign (claude-plugins-official `superdesign`, repo superdesigndev/superdesign-skill) -- VERIFIED
- ★628, pushed 2026-08-21, MIT, plugin v0.6.0. In official marketplace: `claude plugin install superdesign@claude-plugins-official`.
- Runs everything via `npx --yes @superdesign/cli@latest` (unpinned npm package executed each run), browser login to superdesign.dev, designs live on Superdesign's hosted infinite canvas, model/credit usage on their service. GRAPHIC.md covers posters (brief -> 3 divergent directions -> branch variants). Zero Figma integration (grep 'figma' = 0).
- Fit: SaaS canvas outside Figma; duplicates Figma generate_image for moodboards. -> SKIP.

### 7. JimLiu/baoyu-skills (baoyu-infographic, baoyu-cover-image, baoyu-image-gen...) -- VERIFIED
- https://github.com/JimLiu/baoyu-skills ★26,374, pushed 2026-09-10, MIT. Marketplace `baoyu-skills` (one plugin `baoyu-skills`, strict:false, 21 skills, v2.5.2).
- Install whole: `claude plugin marketplace add JimLiu/baoyu-skills` + `claude plugin install baoyu-skills@baoyu-skills`. Safer: copy only `skills/baoyu-infographic` (pure markdown: SKILL.md + references/layouts/*.md + styles/*.md) into ~/.claude/skills/.
- baoyu-infographic v1.117.4: layout (21) x style (22) matrix. Relevant entries: layouts `isometric-map` (30deg isometric, labels floating above objects, path labels along routes, legend, scale), `winding-roadmap`, `linear-progression`, `structural-breakdown`; styles `aged-academia` (sepia #704214 on parchment #F4E4BC, faded red annotations, cross-hatching, specimen-plate numbering), `technical-schematic`, `storybook-watercolor`, `morandi-journal`, `subway-map`. Output = RASTER image via a backend (Codex imagegen / Cursor GenerateImage / "other runtime-native tools" / baoyu-image-gen). Hard rule: never fake with SVG/HTML, never paint over generated text. Writes prompts/ files + EXTEND.md preference file (~/.baoyu-skills or ~/.config/baoyu-skills).
- baoyu-image-gen: bun/npx TS script, providers OpenAI/Azure/Google/OpenRouter/DashScope/Z.AI/MiniMax/Jimeng/Seedream/Replicate/Agnes (API keys) or `codex-cli` (uses logged-in Codex subscription).
- RISK in full plugin: `baoyu-danger-gemini-web` (reverse-engineered Gemini Web API using browser cookies), `baoyu-danger-x-to-markdown`, `baoyu-post-to-x/wechat/weibo` (browser automation posting under your accounts). Do NOT install the whole plugin for this use; copy just baoyu-infographic (and optionally baoyu-cover-image) as reference.
- Fit: art-direction vocabulary for isometric map + aged-academia/archaeology look is directly on-topic; generated rasters can be moodboards (could route to Figma generate_image as "runtime-native tool"). Chinese-first but --lang any. -> OPTIONAL (copy single skill).

### 8. antvis/Infographic (marketplace `antv-infographic`) -- VERIFIED
- https://github.com/antvis/Infographic ★6,957, pushed 2026-08-21, MIT. Plugin `antv-infographic-skills` v0.2.14: infographic-creator / -item-creator / -structure-creator / -syntax-creator / -template-updater (SKILL.md in Chinese).
- Install: `claude plugin marketplace add antvis/Infographic` + `claude plugin install antv-infographic-skills@antv-infographic`.
- What: emits AntV Infographic DSL (`infographic <template>` + data + theme palette) rendered to SVG by the @antv/infographic JS lib (template-driven lists/sequences/compare/hierarchy cards with icons). Not illustration, not isometric, not Figma.
- Fit: maybe a timeline strip as SVG to paste into Figma; otherwise template look clashes with hand-built isometric poster. -> SKIP.

### 9. antvis/mcp-server-chart -- VERIFIED
- ★4,391, pushed 2026-08-27, MIT. npx @antv/mcp-server-chart; renders charts via AntV's remote render service by default (VIS_REQUEST_SERVER for private deploy); geo maps China-only (AMap). Companion skill antvis/chart-visualization-skills via `npx skills add`.
- Fit: poster has no quantitative charts; data leaves machine. -> SKIP.

### 10. Paper2Poster/Paper2Poster (PosterAgent, NeurIPS 2025) -- VERIFIED
- https://github.com/Paper2Poster/Paper2Poster ★3,978, pushed 2026-06-08, MIT. Python research pipeline (CAMEL-based, LibreOffice, poppler, OPENAI_API_KEY or vLLM). Paper PDF -> PPTX poster. Not a Claude Code skill/plugin.
- Reusable asset: VLM-as-Judge prompt templates, 5-point anchored scales, "uncompromising judge, resist high scores": utils/prompt_templates/aesthetic_layout_judge.yaml, aesthetic_element_judge.yaml, aesthetic_engagement_judge.yaml, information_content_judge.yaml, information_logic_judge.yaml, information_low_level_judge.yaml; plus critic_overlap_agent_v3.yaml (painter-commenter overflow/overlap loop). Copies saved to scratchpad research/p2p/.
- Fit: DON'T install; BORROW the six judge rubrics (MIT) for the blind VLM judge prompts. -> SKIP install / REUSE rubric.

### 11. meodai/skill.color-expert -- VERIFIED (strong fit)
- https://github.com/meodai/skill.color-expert ★605, pushed 2026-10-06, CC-BY-4.0. Single skill `color-expert`: SKILL.md + references/INDEX.md + 173 markdown refs (historical/, contemporary/, techniques/) + evals/. NO scripts, no network, no keys.
- Content: OKLCH/OKLAB ramps, print vs screen (CIELAB D50 for print/ICC), CAM16 cross-media matching, APCA/WCAG contrast, Kubelka-Munk pigment mixing, "character (pale/muted/vivid/deep/dark) beats hue harmony", Gage "Colour and Culture" (antiquity, Apelles' four-pigment palette), Albers, Munsell, Itten critique. Has explicit mode "Concrete design or art project: poster/illustration -> ask medium (print), mood, existing colors, then propose".
- Install: `npx skills add meodai/skill.color-expert` (vercel skills CLI, network npm) OR manual `git clone https://github.com/meodai/skill.color-expert ~/.claude/skills/color-expert` (plain markdown; also visible to ~/.agents/skills users if cloned there per ECC convention).
- Overlap: theme-factory / ecc design-system give canned themes; none cover color science or print. -> INSTALL.

### 1b. Figma plugin vs MCP-resource parity (checked live)
- `get_figma_skill skill://index.json` on the already-connected claude.ai Figma connector lists 14 skills: figma-code-connect, figma-create-new-file, figma-design-to-code, figma-generate-design, figma-generate-diagram, figma-generate-library, figma-generative-plugins, figma-implement-motion, figma-shaders, figma-swiftui, figma-use, figma-use-figjam, figma-use-motion, figma-use-slides == exactly the plugin's skills/ dir. So the plugin adds NO new content; only native Skill auto-trigger + local reference files (cheaper than many get_figma_skill calls).
- Changelog evidence on duplicates: L807 "Fixed the same MCP server being connected twice when a plugin or claude.ai connector and a configured server spell its URL differently"; 2.1.83 "local config wins"; 2.1.92 "Plugin MCP servers that duplicate an org-managed connector are now suppressed". Exact winner for plugin-vs-personal-connector is not documented -> verify with `/mcp` after install. If plugin server wins: one-time OAuth + tool prefix changes from mcp__claude_ai_Figma__* to mcp__plugin_figma_figma__* (breaks any supervisor/worker prompts hardcoding names).
- Verdict: OPTIONAL. Content-equivalent alternative already available: `get_figma_skill skill://figma/figma-shaders/SKILL.md` etc. (figma-shaders + generative-plugins are the texture-relevant ones).

### 12. okou-ai/okou-skills (formerly vm0-ai/vm0-skills) illustration-template/iso-scene -- VERIFIED
- https://github.com/okou-ai/okou-skills ★77, pushed 2026-09-28, NO LICENSE (all rights reserved by default). 33 illustration-template skills (iso-scene, riso-relic, grain-poster, flat-poster, grainy-duotone, op-ed-cover, folk-storybook...).
- iso-scene: locked-style prompt template for raster isometric editorial illustration (hairline uniform strokes, flat fills no gradients, one flat saturated BG, 4 colour roles BG/BODY/FOLIAGE/ACCENT, complexity L1-L3, "the scene IS the metaphor"), renders via text-to-image (gpt-image-2 suggested). Markdown only + 4 reference PNGs.
- Fit: good art-direction pattern ("locked axes vs varied axes") for keeping isometric models consistent; raster output; no license. -> SKIP install, read for ideas only.

### 13. cathrynlavery/diagram-design -- VERIFIED (relevant subset)
- https://github.com/cathrynlavery/diagram-design ★44,034, pushed 2026-10-06, MIT, plugin v2.6.64. Own marketplace `diagram-design`.
- Install: `claude plugin marketplace add cathrynlavery/diagram-design` + `claude plugin install diagram-design@diagram-design`.
- 42 editorial diagram types as self-contained HTML+SVG. Relevant: `axonometric plan` (site/campus with buildings, one projection function `iso(x,y,z)` 2:1 dimetric, topological paint order, horizontal roof tags never tilted onto floor, one focal accent, no gradients/shadows) and `exploded axonometric`; `timeline`. Scripts: export_svg.py, self_check.py, drawio/mermaid/excalidraw extractors; verify-axonometric-plan.py reprojects geometry from data-attrs (geometry linting!). PRIVACY.md: no server/telemetry; generated HTML pulls Google Fonts; brand profiles in ~/.diagram-design/profiles/.
- Fit: produces SVG that can be imported into Figma (use_figma figma.createNodeFromSvg) for magnified isometric models/timeline; its axonometric rules match the user's own lesson (floating labels horizontal). 2:1 dimetric != true 30deg isometric -> check projection matches the map. Latin fonts (Geist) -> swap for Korean. -> OPTIONAL.

### 14. uxKero/anydesign -- VERIFIED
- https://github.com/uxKero/anydesign ★215, pushed 2026-09-15, MIT. Single skill; install = `git clone https://github.com/uxKero/anydesign.git && cp -r anydesign ~/.claude/skills/` (no marketplace).
- Analyzes image / URL / Figma file -> design.md (+ DTCG design-tokens.json importable as Figma Variables, design-a11y.md). Element mode "asset" -> token-grounded image prompt for 3D/illustration. 8 local Python scripts (extract_colors.py Pillow, check_contrast.py stdlib, build_tokens_json.py, lint_design_md.py; capture_site.py needs playwright+chromium ~300MB). pip install -r requirements.txt optional. No keys.
- Fit: reverse-engineer palette/type scale from reference posters (e.g. the 203 award winners already downloaded) into tokens -> Figma variables. -> OPTIONAL.

### 15. revfactory/harness -- VERIFIED
- https://github.com/revfactory/harness ★9,127, pushed 2026-09-28, Apache-2.0, v2.1.0, Korean author (README_KO.md). Marketplace `harness-marketplace`.
- Install: `claude plugin marketplace add revfactory/harness` + `claude plugin install harness@harness-marketplace`.
- Meta-skill: domain sentence ("하네스 구성해줘") -> agent team + skills; 6 patterns incl. Producer-Reviewer, Supervisor; quality patterns: adversarial verification, judge panels, loop-until-dry; targets native Workflow scripts / named agents + SendMessage / sub-agents. Skills: harness, evolve. No hooks seen.
- Fit: could formalize the existing supervisor + workers + blind-judge loop. Overlaps ECC gan-design / santa-loop / council / autonomous-loops / team-agent-orchestration, already installed. -> OPTIONAL (only if current loop needs re-architecting).

### Rejected quickly
- bitjaru/styleseed ★969 MIT: web-screen design rules + render/score loop (npx skills add). Web UI only.
- dembrandt/dembrandt-skills ★66 MIT: UX/design-system rules for apps.
- gregorymm/design-review-plugin ★6: UI review (16px body text, CTA dominance) -- UI only, overlaps design:design-critique.
- S-jooyoung/oh-my-joy ★1: code<->Figma frontend loop.
- southleft/figma-console-mcp ★2,443 MIT: alternate Figma MCP via Desktop Bridge plugin + PAT; duplicates official use_figma; adds credential surface.
- garrytan/gstack ★135k: design-review / plan-design-review are web-app (browse) oriented.
- Korean: no vetted Korean poster-typography skill exists (search hits: RexRenatus/deck-streak cjk-typography = web app pack AGPL ★0; kez-lab/korean-presentation-skill ★2 HTML decks; epoko77-ai/design-diversity ★191 PPT/web packs). Authoritative source to feed instead: W3C KLREQ (Requirements for Hangul Text Layout and Typography).

### More rejected (checked)
- nexu-io/open-design ★99,718 Apache-2.0: local desktop app + `od mcp install claude`; magazine-poster/poster-hero/image-poster skills output HTML; paid "Go" plan for models. Not Figma.
- K-Dense-AI/scientific-agent-skills `infographics` ★47,790 MIT: Nano Banana 2 raster via OPENROUTER_API_KEY + Gemini review loop (rubric: hierarchy, typography, data viz, color/accessibility, overall impact, 0-2 each). Raster only; rubric idea noted.
- 0xheycat/isometric-game-skills ★26 MIT: isometric-art-direction = write STYLE.md (projection, single light direction, 8-12 swatch palette, one shading style, 3 test assets before scaling). Good idea, trivial skill; write your own.
- Wcc723/claude-skill-design-gallery ★7 (no license), LaurentiuGabriel/learnscape isometric-explainer ★136, phoroth/AGENTIC ★3: low trust/low value.
- canva (official marketplace): Canva MCP, Canva-only. adobe-for-creativity (official): Adobe Firefly/Photoshop API actions (bg removal, vectorize) -- needs Adobe account; could vectorize raster textures but not needed.
- anthropics canvas-design: not in the installed anthropic-skills set; python->PNG/PDF; no Hangul fonts. Prompt pattern only.

### Already-available capabilities worth using (no install)
- Figma connector exposes texture tools: create_shader/update_shader/list_shaders (load `get_figma_skill skill://figma/figma-shaders/SKILL.md` first), create_generative_plugin (skill figma-generative-plugins), generate_image (Figma AI credits), weave_* (Figma Weave model runs; credits). These cover paper grain / stone / parchment texture without new installs.
- ECC: gan-design, santa-method (dual independent reviewers), council, loop-design-check (judge independence + Goodhart checks) already cover the critique-loop mechanism.

## RANKED SHORTLIST (for Figma A2 Korean infographic poster)
| # | Item | Verdict |
|---|------|---------|
| 1 | meodai/skill.color-expert | INSTALL (git clone to ~/.claude/skills/color-expert) |
| 2 | Paper2Poster judge rubrics (6 YAML, MIT) | REUSE in blind-judge prompts (copies in research/p2p/) |
| 3 | figma@claude-plugins-official | OPTIONAL (content == get_figma_skill; check /mcp dedup) |
| 4 | cathrynlavery/diagram-design | OPTIONAL (axonometric plan/exploded SVG + label rules) |
| 5 | baoyu-infographic (single dir copy) | OPTIONAL (isometric-map x aged-academia vocabulary; raster moodboards) |
| 6 | uxKero/anydesign | OPTIONAL (reference posters -> DTCG tokens -> Figma variables) |
| 7 | nextlevelbuilder/ui-ux-pro-max | OPTIONAL-low (offline Korean Google-font list) |
| 8 | revfactory/harness | OPTIONAL-low (judge-panel/supervisor patterns; overlaps ECC) |
| - | impeccable, taste-skill, superdesign, AntV x2, open-design, K-Dense infographics, StyleSeed, figma-console-mcp | SKIP |

Status: DONE (2026-10-07)
