# Worker assets and material audit — final

Ready for root integration. All three Meshy GLBs are downloaded, valid GLB v2, single untextured mesh/primitive. Exactly three standard meshy-7.1 jobs, each task reports 20 consumed credits, total 60. Initial balance 660 and final download balance 600 agree with that total. A transient creation-time per-task balance observation of 40 was preserved in the journal; its cause is not established. No extra regeneration, refine, or texture job.

Actual gray geometry inspection precedes all material classification:

- Carrier needs root correction: generated bucket occupies the head and bars occupy the lower hands. Walking tunic body and lower hands are real. Do not display the source generation as a valid front bucket carrier.
- Builder is a kneeling worker with one stone block and mallet/punch-like tool, without the requested wall or wood form. Root owns adding explicit wall/form geometry.
- Pair has two walking workers and an actual shallow rectangular trough, without readable mortar fill. Root owns adding an inset fill.

Pure helper `../worker_parts.py` is locked. Call `build_assignments(bpy)` on original imported topology before surgery; call `build_correction_masks(bpy)` for root-owned carrier removal and builder head-copy selections. It mutates no geometry, materials or scene. Nine isolated material renders and source/mesh hashes verify this boundary. No production blend, Figma or source GLB was saved or modified.

Skin #C99C78, linen #DED1AF, left pair tunic #B77B60, hair/sandals #735A42, tools/trough #8D6C49, small tool metal #526873, block #D3BE9E. Root's separately created mortar fill token is #B5AD97; no original face is assigned a mortar role.

| Object | Polygons | Final roles and polygon counts |
|---|---:|---|
| NB_worker_carrier | 20669 | skin 3,067, toolwood 6,372, worker_dark 3,058, linen 8,172 |
| NB_worker_builder | 20601 | roman_stone 733, skin 8,717, toolmetal 121, toolwood 311, worker_dark 4,311, linen 6,408 |
| NB_worker_pair | 20763 | skin 5,252, toolwood 800, worker_cloth 5,721, worker_dark 2,948, linen 6,042 |

Final isolated audit confirms the block no longer receives knee skin, the trough side reads as a continuous wood surface, and the left/right tunics differ. Small fused sleeve/wrist and garment-hem transitions remain conservative. This is an isolated geometry/material check, not a final poster camera or layout approval; root will supply the actual composed crop for the follow-up.

Correction selections: carrier head region 5,831 faces, unwanted bars 541 faces, preserved lower-hand region 968 faces. Builder head-copy region 8,439 faces. The pair correction-mask trough box is an advisory search volume including fused end triangles; use the smaller inset-fill coordinates from `worker-coordinate-guides.json`, not that broad box as an exact trough model.

Evidence:

- Worker journal: `narrative_benchmark_20261007/meshy_construction_workers_v14.json`.
- Source gray views: `models/workers_v14/NB_worker_{carrier,builder,pair}_gray_view{0,1,2}.png`.
- Final material views: `construction-detail/workers/NB_worker_{carrier,builder,pair}_parts_view{0,1,2}.png`.
- Audit and exact correction indices: `worker-parts-audit.json`.
- Coordinates/counts/helper hash: `worker-coordinate-guides.json`.

Stop condition reached: bounded generation, actual geometry review, pure part masks, correction guides and isolated audit delivered. Root owns production adaptation and final poster QA.
