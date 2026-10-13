# Final saved Blender v6 validation

Status: **PASS**. Fresh saved-scene fingerprint, preserved objects, modern/specimen terrain crossings, and the corrected C2 badge/rule bounds all pass.

## Current generation

- File: `roman_concrete_narrative_v6.blend`
- SHA256: `d71533920ebd305c41e92db718b527647c8b9655aee87cbb3b656c3afde257cd`
- Read-only fresh background Blender with `--disable-autoexec`; no save, production edit, render, GUI interaction, or model job.
- Audit output writes are confined to this folder. Temporary in-memory visibility evaluation was restored before process exit.

## Preservation

- 317 objects, no additions or removals.
- All 286 objects outside the production report allowed-change list match source v5 fingerprints.
- Saved v6 matches the report after-snapshot; no differences at Float32 transform tolerance 1e-5.
- `COL_ruined`, `T_land`, `CAM_iso`, sea, river, and all roads remain preserved.
- Canonical original and v5 SHA256 remain unchanged.

## Final terrain surface test

| Object | Vertices tested | Negative vertex gaps | Terrain BVH polygon pairs | Minimum terrain gap |
|---|---:|---:|---:|---:|
| NB_modern_building | 28609 | 0 | 0 | 0.01996949 |
| NB_lime_clast_specimen | 20297 | 0 | 0 | 0.01997700 |

The earlier broad-face curvature intersections are **resolved**. Root locally subdivided the affected lower surfaces and conformed new lower vertices to terrain+0.02. Frame pairs reduced 267→0 and specimen pairs 72→0. Existing upper geometry, projected bounds, and terrain remain unchanged. New base vertices: frame 4536; specimen 1584. All final model vertices were independently ray-cast against terrain; negative counts use tolerance 1e-4.

Current projected bounds:

- Frame: [709.8780,355.3104,885.1173,550.3783]
- Specimen: [441.9939,1132.4068,566.0061,1288.0873]

## Corrected C2 shapes

- `S_core2_badge`: [69.49989,746.50063,89.50007,766.50021], matching [69.5,746.5,89.5,766.5].
- `S_core2_underline`: [69.49952,797.10008,213.60031,797.90040], matching requested Y[797.1,797.9].

Both checks pass within 0.02 poster pixels.

## Unchanged placement checks reused

Root confirms tree/site/marine transforms and geometry algorithms are unchanged by the lower-surface and C2-shape correction. Their prior actual saved-v6 checks remain valid and are preserved under `prior_unchanged_placement_checks` in the current JSON:

- Nine relocated trees are supported on land: minimum trunk-base gap about 0.01, maximum 0.0814 across local slopes; no negative gaps or off-land base vertices.
- No moved tree physically intersects visible core models, hero, mechanism objects, or historical/regional sites.
- `S_lab_island` and `C5_researchers` have no terrain or other site/core/tree crossings. The lab is at [1012.89,698.99,1117.11,811.00]; ruin at [868.88,1128.06,963.11,1240.88]. `L08_pompeii_site` remains the Pompeii construction-site illustration.
- Marine base=-0.85, water=-0.7, top=0.176435: base 0.15 below water, top 0.876435 above water; 222 sea-plane and 37 shoreline crossings confirm immersion/bank embedding. No modeled seabed exists, so no seabed-contact claim is made.

## Artifacts and history

- `v6-validation.json`: current final PASS, exact saved-scene SHA, fingerprint differences, both model terrain tests, corrected shape bounds, and preserved placement checks.
- `v6-validation-depth.json`: historical pre-refinement face crossings and depths, retained unchanged for provenance. Its unresolved counts do **not** describe the final saved v6.
- `v6-validation-baseline.json`: original v5 bottom-band indices used for the earlier contact check, retained as baseline history. Later local subdivision changes vertex indexing, so it must not be reapplied directly to final meshes.

No unresolved geometry finding remains in this verification scope.
