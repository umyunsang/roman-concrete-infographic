# Rebar/modern-frame enlargement placement review

## Scope
Read-only placement recommendation from current native v9 1x PNG, figma-poster-v9-validation.json CORE1 coordinates, and placement_manifest_v4.json. Root reports live user edits removed some text; preserve the current live95texts rather than restoring any historical receipt. Current CORE1 coordinates/background remain unchanged by root's live read. No model/Figma/production writes.

## Primary bbox
**[710,356,885,549]**, dimensions175×193 pt. Compared with actual visible model97.3×107 pt, about1.80× both dimensions and3.24× area. This is a fit-contain target for the existing NB_modern_building transform, not regeneration or a different asset.
- C1 protected text/caption extends to approximatelyx702, leaving8pt horizontal gap.
- New topy356 sits just below the northern mountain feet rather than pushing farther into them at proposedy350.
- New bottom549 remains19pt above the central Colosseum global bbox top568. The tall arena wall's actual top is farther left, so the visual arena separation is stronger than that global-box margin alone suggests.
- Right edge885/bottom549 stops short of the large aqueduct's nearest rising/curving visible segment. A full rectangular intersection against the aqueduct's global bbox would overestimate actual conflict; inspect the visible silhouette after transform.

## Fallback bbox
**[710,366,875,548]**, dimensions165×182 pt. About1.70× width/height and2.89× area. Prefer this if primary roof or posts visually merge with mountain edge/aqueduct. Narrower right edge and lower roof leave more skyline clearance while remaining clearly larger.

## Concrete visual risks
1. At this scale, a strictly empty rectangle does not exist around the fixed C1 position with every map object and text position unchanged. Orchard crowns aroundx715–795/y495–540 are the unavoidable local tradeoff: some may appear behind or through the frame's lower bays, and feet/shadows may cover their edge. Neither proposed bbox guarantees every small tree remains fully visible. Preserve those tree objects rather than moving/deleting them.
2. Primary top is still near mountain feet, although not mountain peaks. A roof strut may share an edge with a pale ridge; fallback lowers the roof another10pt.
3. The dark open frame can merge with background cultivation marks through its bays. Enlarging improves line legibility, but inspect whether thin steel lines read separately from field rows/tree branches.
4. Bbox excludes cast-shadow extent. Keep any longer shadow away from C1 caption and major aqueduct; root's actual render is required for that check.
5. Do not expand right past about885 or down beyond549 without another visual check. That would approach the aqueduct or central scene and reduce the clear distinction from surrounding historical structures.

## On root's suggested box
[710,350,890,545] is roughly1.8× and clears text/arena. Its roof is tighter against northern mountain feet, so the primary suggestion nudges it6pt lower and5pt narrower. This is a visual recommendation, not a collision-validated rendered result.

## Final enlarged native export visual check — PASS
Viewed actual figma_poster_v9_enlarged_frame_1x.png once, with scope limited to enlarged frame silhouette and adjacent fixed composition.
Reviewed1x SHA-256: `e75379c8d8597c71ff9872c5c557c43a999610baa633b786b8ac01ca75177027`
- The approximately1.8× enlarged modern frame is clearly more prominent; multistory silhouette and internal bars are distinguishable at1x.
- C1 headings/body/comparison caption remain unobstructed with a visible horizontal gap to the frame.
- Enlarged footprint does not conflict with the central Colosseum silhouette.
- Major aqueduct remains visible and separate; no bridge segment is hidden by the enlarged frame.
- Fixed small orchard crowns show through/below the lower frame. They do not obscure the enlarged frame silhouette, and no map changes are requested.
No remaining failure in this bounded visual check. Object preservation, exact text equality and saved-file reload assertions remain root's independently reported validation surface.
