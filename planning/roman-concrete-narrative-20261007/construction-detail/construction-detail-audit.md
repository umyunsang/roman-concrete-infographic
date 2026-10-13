# Phase14 construction/detail read-only findings

Source v9 SHA: `8125d6cf8ec2da6cf09125472aa603afd1debcd88910ff8ed0893b174a2288fe`. Actual visible mesh count: **227**. Camera/terrain/hero and all production objects are read only.

## Object identification

`D2_lime_kiln` is the domed hearth/lime-kiln-shaped model above CORE2. Its current bbox is `[80.02, 594.91, 200.36, 738.38]`; original mesh has 4442 vertices / 6494 polygons. It currently has one material, `RC.v12.base_roman_support_stone` (#D3BE9E), on all faces. Its geometry includes a concave arched chamber, low ground platform and raised curling plume. These are visible in the original-geometry audit, independent of its name.

`L04_palatine` is the small stepped tower to the left of CORE3, bbox `[338.72, 1106.01, 401.31, 1170.01]`, with `L04_palatine_arch` child. It is separate from the hearth. `D3_structure` is the much lower stack with arrows and density/weight labels.

The two temple models in the proposed new construction row are `L03_forum_vesta` `[304.25, 470.42, 395.12, 585.43]` and `L03_forum_temple` `[414.28, 454.90, 495.43, 558.11]`. They have no current native historical SUPPORT heading in the v13 poster. Root has selected hiding them in the new draft.

## Current DETAIL groups

### D1_material

Root type `EMPTY`; 33 children; 33 render-visible meshes; union bbox `[73.74, 332.0, 160.31, 406.0]`.

Names: `D1_material`, `D1_concrete`, `D1_crystal00`, `D1_crystal01`, `D1_crystal02`, `D1_crystal03`, `D1_crystal04`, `D1_crystal05`, `D1_crystal06`, `D1_crystal07`, `D1_crystal08`, `D1_crystal09`, `D1_crystal10`, `D1_crystal11`, `D1_crystal12`, `D1_crystal13`, `D1_crystal14`, `D1_crystal15`, `D1_crystal16`, `D1_crystal17`, `D1_crystal18`, `D1_crystal19`, `D1_crystal20`, `D1_crystal21`, `D1_crystal22`, `D1_crystal23`, `D1_crystal24`, `D1_crystal25`, `D1_seawater`, `D1_tank_floor`, `D1_tank_wall0`, `D1_tank_wall1`, `D1_tank_wall2`, `D1_tank_wall3`.

Face colors: `RC.v12.base_lime_specimen_matrix` #97614B (6 faces); `RC.v12.base_lime_calcium_crystal` #FFF4DD (208 faces); `RC.v12.base_water_process` #3F9DAA (6 faces); `RC.v12.base_modern_concrete` #657B88 (30 faces).

### D2_making

Root type `EMPTY`; 20 children; 20 render-visible meshes; union bbox `[69.28, 951.99, 130.7, 1031.99]`.

Names: `D2_making`, `D2_cube`, `D2_heat0`, `D2_heat1`, `D2_heat2`, `D2_lime00`, `D2_lime01`, `D2_lime02`, `D2_lime03`, `D2_lime04`, `D2_lime05`, `D2_lime06`, `D2_lime07`, `D2_lime08`, `D2_lime09`, `D2_lime10`, `D2_lime11`, `D2_lime12`, `D2_lime13`, `D2_lime14`, `D2_lime15`.

Face colors: `RC.v12.base_lime_specimen_matrix` #97614B (6 faces); `RC.v12.base_hot_mixing` #D15B36 (414 faces); `RC.v12.base_lime_calcium_crystal` #FFF4DD (1280 faces).

### D3_structure

Root type `EMPTY`; 11 children; 11 render-visible meshes; union bbox `[262.26, 1187.98, 317.74, 1337.98]`.

Names: `D3_structure`, `D3_brick_course1`, `D3_brick_course2`, `D3_brick_course3`, `D3_foundation`, `D3_heavy`, `D3_light`, `D3_middle`, `D3_press0`, `D3_press1`, `D3_press_tip0`, `D3_press_tip1`.

Face colors: `RC.v12.base_pozzolan` #A4876D (18 faces); `RC.v12.base_concrete_dense` #6B6254 (6 faces); `RC.v12.base_road_foundation` #C0AF90 (6 faces); `RC.v12.base_stone_light` #EBDDCA (6 faces); `RC.v12.base_stone_middle` #B7A584 (6 faces); `RC.v12.base_type_secondary_on_light_ground` #615A4E (54 faces).

### D4_crack

Root type `EMPTY`; 13 children; 0 render-visible meshes; union bbox `None`.

Names: `D4_crack`, `D4_arrow0`, `D4_arrow1`, `D4_crack0`, `D4_crack1`, `D4_crack2`, `D4_cube0`, `D4_cube1`, `D4_cube2`, `D4_drop0`, `D4_drop1`, `D4_drop2`, `D4_lime0`, `D4_lime1`.

Face colors: Original D4 children are all hidden; visible replacement is NB_core4_sequence..

### NB_core4_sequence

Root type `EMPTY`; 5 children; 5 render-visible meshes; union bbox `[625.0, 1153.36, 840.0, 1250.0]`.

Names: `NB_core4_sequence`, `NB_core4_sequence_GRAY00`, `NB_core4_sequence_GRAY01`, `NB_core4_sequence_GRAY02`, `NB_core4_sequence_GRAY03`, `NB_core4_sequence_GRAY04`.

Face colors: `RC.v12.base_type_secondary_on_light_ground` #615A4E (2 faces); `RC.v12.base_type_heading` #2E2A22 (12 faces); `RC.v12.base_lime_calcium_crystal` #FFF4DD (166 faces); `RC.v12.base_lime_specimen_matrix` #97614B (162 faces); `RC.v12.base_water_process` #3F9DAA (240 faces).

## Leader ownership and current bboxes

| DETAIL | Object | Current bbox |
|---|---|---|
| D1 | `S_lead00` | `[51.9, 347.06, 95.97, 357.69]` |
| D1 | `S_lead01` | `[60.98, 385.68, 86.9, 387.95]` |
| D2 | `S_lead02` | `[128.0, 1006.55, 140.0, 1007.45]` |
| D3 | `S_lead03` | `[298.9, 1231.45, 315.8, 1232.35]` |
| D3 | `S_lead04` | `[373.8, 1231.45, 390.7, 1232.35]` |
| D3 | `S_lead05` | `[300.8, 1258.05, 324.1, 1258.95]` |
| D3 | `S_lead06` | `[365.1, 1258.05, 388.4, 1258.95]` |
| D3 | `S_lead07` | `[303.4, 1286.55, 319.8, 1287.45]` |
| D3 | `S_lead08` | `[369.8, 1286.55, 386.2, 1287.45]` |
| D3 | `S_lead09` | `[309.5, 1307.55, 318.6, 1308.45]` |
| D3 | `S_lead10` | `[375.6, 1307.55, 384.7, 1308.45]` |
| D1 | `S_lead_dot0` | `[94.27, 355.65, 97.47, 358.85]` |
| D1 | `S_lead_dot1` | `[85.28, 384.53, 88.48, 387.73]` |
| D2 | `S_lead_dot2` | `[126.4, 1005.4, 129.6, 1008.6]` |

The entire `S_sect*` section graphic also belongs to old D3: `S_sect0`, `S_sect0_edge`, `S_sect1`, `S_sect1_edge`, `S_sect2`, `S_sect2_edge`, `S_sect3`, `S_sect3_edge`, `S_sect_brick1227`, `S_sect_brick1233`, `S_sect_brick1239`, `S_sect_dot0`, `S_sect_dot1`, `S_sect_dot2`, `S_sect_dot3`, `S_sect_ground`.

D4 has no standalone S_lead line; arrows are part of its current NB sequence geometry. The legacy L_D*_h/b FONT objects in 70_LABELS_TEST are not the editable native Figma text layer; their freshly loaded screen bounds are runtime legacy data and are not used for proposed poster placement.

## Selected new layout and geometry checks

| Element | Proposed bbox | River overlap | Colosseum overlap |
|---|---|---|---|
| kiln | `[40, 358, 160, 502]` | 0 px | 0 px |
| mixer | `[45, 624, 190, 742]` | 0 px | 0 px |
| unfinished_vault_slot | `[300, 470, 410, 556]` | 0 px | 0 px |
| completed_vault_slot | `[420, 470, 515, 556]` | 0 px | 0 px |
| white_clast_zoom_slot | `[300, 1170, 400, 1260]` | 0 px | 0 px |

Checks use current projected original face silhouettes for the existing kiln/mixer and full conservative rectangles for future model slots at 1191×1684. They prove screen-space clearance only; root will validate actual imported geometry and ground contact in the new draft. All targets remain within the poster. The construction-row bottom y556 leaves at least 12 px before the current Colosseum minimum y568.29. CORE1 lower caption begins at x528, leaving 13 px beyond the completed-vault slot end x515.

The mixer slot is 145×118; fitting the current near-square silhouette uniformly within it yields about 122×118 rather than stretching geometry. CORE2 text at x36/y510/height102 ends y612, leaving 12 px before the mixer slot.

## Final hearth helper

`hearth_object_parts.py` exposes PALETTE and build_assignments(bpy), with original polygon-index lists: kiln_shell 3671 / kiln_foundation 1278 / kiln_interior 930 / kiln_smoke 615. The interior uses actual inward-facing chamber surfaces, bounded by local coordinates, rather than a painted front rectangle.

Fresh Blender helper verification PASS: source SHA before/after identical, topology SHA identical, material slots/indices and matrix_basis unchanged, all selected indices unique and in range. See `hearth-part-validation.json` and `kiln-parts-audit.png`. No production file save/render, UI, Figma, material or geometry write was performed.
