# V12 actual village visual review

Read-only review of the actual 1191×1684 map and native 2382×3368 map. No scene, geometry, Figma, helper, or paid-job changes. This review records the inspected render; root corrections reported below are pending and not visually verified here.

## Confirmed acceptable

- Central Colosseum remains dominant. Two timber scaffolds are physically attached to its outer wall; their small workers contact their platforms and fit the building scale.
- Five low houses have readable terracotta tiled roofs, plaster/stone walls, doorways and jars. Sizes are credible relative to the market and visible people. House earth patches appear flat and grounded; no clear floating foundations were observed.
- Market canopy, posts, containers and nearby citizens form a compact daily-life cluster. Skin, tunic, vessel, roof and timber colors show no conspicuous leakage at native 2×.
- The visible eastern citizen pair has two complete heads and readable basket/amphora silhouettes. The root's repaired head does not show an obvious seam at this rendered scale. The north and south citizen clones cannot receive the same action-readability pass because they are hidden behind houses.
- Western making zone fits a small working court; kiln/basin no longer compete in scale with the central architecture.

## Real issues in this inspected render

1. **Citizen visibility:** north anchor approximately (631,606) and south (599,1199) are substantially/fully occluded by house roofs and walls. Only the eastern clone is visibly validated. Root reported planned moves to (658,613) and (637,1220), respectively; those positions require the root's final rendered check.
2. **Research island:** near (1040,776), a large jagged gray rock support remains below the blue lab, creating an isolated display-model appearance. Trim/remove the rock support in the copied asset or sink it flush with terrain. Root reports this cut is implemented pending rebuild.
3. **South construction surfaces:** near (454,1227), the wall behind the unfinished vault reads as a plain gray vertical panel, with the builder hidden. The wall near the completed vault at (827,1223) is also mostly obscured and does not convey active stone construction. Root reports changing stone-facing direction and exposing the builder at (476,1222), plus moving the second wall forward to (849,1273).
4. **Isolated green form:** near (875,882), a narrow leaf/diamond shape has no visible trunk or ground contact in native 2×. Its silhouette reads as an abstract marker. Retire this isolated source object or use an existing visibly grounded tree. No new asset is needed.

## Balance

New houses currently occupy north, east and south. The west is a narrow river/Colosseum strip with a making court, so no extra house is mandatory for equal visual area. A small western house may improve settlement continuity if it fits without river/foundation collision or hiding the central wall; root is evaluating that placement. This is a composition choice, not a confirmed rendering defect.

## Evidence

Owned native-resolution crops (2× source, no resampling):
- `v12-qa-hero_scaffolds.png`
- `v12-qa-market_east_lab.png`
- `v12-qa-makers_west.png`
- `v12-qa-north_citizens.png`
- `v12-qa-south_citizens_occlusion.png`
- `v12-qa-south_wall.png`
- `v12-qa-vault_wall.png`

Inspected image hashes:
- `map_v12_construction_details_without_text_1x.png`: `eb893f0934b1dae0e4dba444d68e3f2289d6420181d318ee21bc6fc7aa71dc21`
- `map_v12_construction_details_without_text_2x.png`: `7d29669480fae53d14d257c637f1482ee0a30cb42a70e41d09fb8b3d529b4421`

Outcome: geometry scale, scaffold attachment, material parts and hero hierarchy acceptable. Four concrete visibility/grounding findings above were sent to the production owner. No further image iteration or new alternatives in this lane.
