# Phase15 village asset delivery

Three standard meshy-7.1 source GLBs are ready. Each task reports20 consumed credits, total60; account600→540 agrees. No regeneration, refinement or texture job. New canonical journal `meshy_village_jobs_v15.json` and all GLBs are under `models/village_v15/`. Previous journals/GLBs are unchanged.

Actual gray geometry inspected from three directions per model:

- **House:** pitched tiled roof, plaster/stone wall volume, doorway/window details, an actual amphora and small low front wall/bed fragments. No pedestal or floor slab. Side courtyard was not fully generated. Appropriate as an ordinary village house; archaeological authenticity is not independently verified.
- **Market:** four actual posts, sagging cloth canopy, counter, pottery/baskets and a standing full-body merchant. No pedestal or floor. High camera naturally hides the face beneath the canopy; low front view confirms a head exists.
- **Citizens:** basket bearer has a complete bald human head, arms and everyday stance. Right amphora bearer has no generated head and the vessel is at the hip without clear contact to the crossed hands. Root must graft the real source head and connect/move the vessel. No material mask pretends a missing head exists.

Pure helper `village_parts.py` is locked. PALETTE, `build_assignments(bpy)`, and `build_correction_masks(bpy)` only read original normalized H-import mesh data. Apply colors before citizen surgery or house duplication. Colors separate real roof/walls/door/stone/vessel, canopy/posts/counter/baskets/merchant, and citizen garments/skin/props. No dark hair is painted onto the actual bald heads.

| Production base name | Original polygons | Final palette counts |
|---|---:|---|
| NB_village_house | 20188 | plaster 634, roof 18,702, stone 576, terracotta 247, wood 29 |
| NB_village_market | 20448 | basket 3,181, canopy 3,906, linen 2,293, sandals 368, skin 1,048, terracotta 1,527, wood 8,125 |
| NB_village_citizens | 20661 | basket 2,710, cloth 6,757, linen 5,744, sandals 1,019, skin 3,579, terracotta 852 |

Citizen correction evidence:

- Source left head:657 faces, bbox[-.408360,-.359212,1.598537]..[-.162673,-.050751,1.901488], mean[-.303572,-.245771,1.737341].
- Empty right neck rim:345 faces, mean[.231305,.268044,1.638757], highest1.678535. Graft lower head edge nearZ1.65–1.67 and check the final camera.
- Actual right crossed hand hits:[.128667,-.035823,1.277058] / [.215977,-.014914,1.243411].
- Amphora:852-face cylinder selection now includes the full visible shoulder/back (earlier ellipsoid left a cream gap). Its contact edge includes thin fused garment triangles; root must inspect/trim the copied edge. The source body and neck guides are [.506,.365,.930] / [.470,.360,1.093], proposed moved neck near[.180,-.095,1.250]. Exact indices/bbox are in `village-parts-audit.json`.

Final isolated color views show continuous roof color, plaster wall with the actual low front stones, cream canopy with wood posts, warm pottery/baskets and two differentiated citizen garments. Large-wall/garment triangle intrusion was constrained with vertex-height and face-area checks. Small fused limb/hem transitions remain conservative; full final village placement, corrected citizen anatomy and native poster readability belong to root's production review.

Evidence: `NB_village_{house,market,citizens}_gray_view{0,1,2}.png` and `_parts_view{0,1,2}.png`, `village-source-audit.json`, `village-parts-audit.json`, `village-ray-probes.json`, `village-delivery-manifest.json`.

PASS: pure helper leaves geometry unchanged, each original source GLB hash preserved, audits used unsaved factory scenes only. No production Blender/Figma/UI writes, no nested agent. Stop condition reached: three assets, actual pose/geometry inspection, pure material/correction helper and audit evidence delivered.
