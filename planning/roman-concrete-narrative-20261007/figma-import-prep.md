# Figma editable poster import preparation

## Plan
1. [complete] Inspect render composition and authoritative narrative patch copy.
2. [complete] Recover all visible retained text with current transforms and source provenance.
3. [complete] Write no-text base image, editable text manifest, and composition audit.
4. [complete] Verify exact composite reconstruction and image file size; hand off to root.

## Findings
- Map and overlay render inputs are 2381 x 3367; existing poster is 2382 x 3368. Pad one white pixel on map right/bottom and one transparent pixel on overlay right/bottom.
- copy/figma_text_narrative.json has 51 entries, 27 with measured patchNodes. It omits title, BASIC labels, DETAIL model labels, and most timeline text.
- copy/README.md warns old retained positions may differ from current Figma. Live v7 audit has 89 original text entries but only content/size; root asked to provide current transforms and typography.
- Older memory registry entries classify as near_match_only; no historic facts used for current assets.

## Ownership
Local only. Writes restricted to scripts/prepare_figma_poster.py, out/figma_import/map_without_text_2x.png, out/figma_import/text_manifest.json or SVG, out/figma_import/audit.json, and this file. Root owns Figma writes.

## Progress
- Read planning-with-files and existing root task state. No AGENTS.md exists in the project path.
- No Blender, Meshy, or remote mutation attempted.

## Errors
- Read-only rg included absent team/README.md; authoritative copy README inspected instead.

- Visual audit of poster and overlays confirms no visible text in Blender passes. Top +/+/→ are text glyphs and need editable nodes.
- Exact reconstruction established: no-text base plus current RGBA overlay equals poster_2x.png at every pixel. Background: 6,264,341 bytes, SHA256 8c63e11dcc9175a438554a8f8ce37930fb9fb8d70d42a25947405d2147361434.
- Complete target count is 90: original89 minus oldquestionlabel and oldquestion, plus newquestion and 2captions.
- Retained PLACE positions diverge strongly from older narrative JSON; root asked for live full transform inventory.

## Final handoff
- `out/figma_import/map_without_text_2x.png`: 2382 x 3368 RGB, 6,264,341 bytes. Figma placement is exactly 1191 x 1684 at x0/y0, with no offset.
- `out/figma_import/text_manifest.json`: entries90, patches27, retained63; complete=true. All original89 source IDs mapped or retained except removed634:722, no unresolved geometry or narrative fallback coordinates.
- `out/figma_import/audit.json`: exact current poster reconstruction mismatchingPixels0; hashes for all inputs/outputs.
- `scripts/prepare_figma_poster.py`: executable via python3; AST parsed; actual run with root's live inventory passed all reconstruction and size assertions.
- Source inventory is `.planning/roman-concrete-narrative-20261007/evidence/figma-texts-import-live.json`, root-owned live read of frame634:78.

## Text placement details
- All patch x/y/w/h/s are in 1x Figma pixels. Patch `targetInkBboxes` were measured at 2x then divided by2.
- Native patch `lineHeight` uses PIXELS: CORE bold25/body14, DETAIL14 except D3_h15, SUPPORT/TIMELINE13, question24.
- Raster ink start offsets: CORE bold3.5/body2.5 below node y; D3_h1.9; other patched DETAIL/SUPPORT/TIMELINE2.1; question0. Keep node y and inspect final native font export against these target ink boxes.
- Retained PLACE transforms have skewed basis vectors; preserve full relativeTransform rather than just rotation. Frame origin is x3048/y56.
- All circles/underlines are already in Blender base. Do not generate duplicate shapes from narrative `ul` metadata, which predates some actual line transforms.
- Clone source native text when available to preserve rich BASIC headings and current Medium PLACE faces. Patched texts use Noto Sans KR Bold/Regular with explicit lineHeight; root verifies font availability.

## Verification limits
Pixel equality proves local raster decomposition only. Native Figma text/font fidelity requires root's final export and visual review. No reader/acceptance test was performed in this lane.
