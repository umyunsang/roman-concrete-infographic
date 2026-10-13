# Process / people face selection — final scoped review

Read from roman_concrete_narrative_v7.blend in background Blender. No production .blend save, no Figma/UI mutation, no source geometry edits. The helper is pure read-only: `build_assignments(bpy)` returns role-index overrides and roman_stone defaults. Source polygon-count guards are15801/15813/10528 respectively, and every override index is unique.

Actual isolated top/front/back material audit renders are in this directory. Final specified corrections passed front-view inspection: C2 basin/mixture low surfaces take precedence over clothing volumes so the red robe patch no longer leaks onto the mixing basin; C5 rear observer head uses an actual ray-hit face10624 local position(-.04946,.33912,.62255), and all four observation heads now have skin colors.

## C2_hot_mixing

Total polygons15801; conservative roman_stone default6462. Overrides: mixture=2256, toolwood=294, basin=1512, skin=1825, cloth=1086, linen=2366.

- Two workers: head/neck and exposed extremities skin; short tunic linen; long lower apron/robe cloth.
- Circular raised basin and filled mixture surface separated; oblique stirring shaft/paddle toolwood.
- Ground and unidentifiable scattered angular fragments stay roman_stone; no chemical assertion from their shape.

## C5_researchers

Total polygons15813; conservative roman_stone default13078. Overrides: linen=1690, skin=245, cloth=387, toolmetal=413.

- Four small observation figures are bounded spatially, not by a global height band; surrounding arch stays roman_stone.
- Foreground tripod/optical device toolmetal; facial volumes skin, garments linen/cloth.
- Very small fingers, shoes, and backs partly fused to masonry remain conservative garment/stone colors.

## L08_pompeii_site

Total polygons10528; conservative roman_stone default7622. Overrides: toolwood=1696, raw_lime=228, basin=982.

- Front scaffold posts/decks/diagonal bracing toolwood; wall and indistinct construction blocks remain roman_stone.
- Foreground bowl and small vessels basin; central foreground pale powder heap raw_lime is a schematic palette role, not proof of lime chemistry.
- No confidently identifiable human face/body in this mesh at the inspected views: no skin/cloth assignment on ambiguous scaffold lumps.

Limits: masks use source-local shape volumes and polygon centroids on low-poly/fused Meshy geometry, not authored character rigs or semantic UV textures. Small fingers/shoes/obscured backs are conservative. L08 has no confidently recognized human face/body; the bowl pale-powder role is illustrative and does not certify chemical material. Scattered angular raw construction fragments remain stone.
