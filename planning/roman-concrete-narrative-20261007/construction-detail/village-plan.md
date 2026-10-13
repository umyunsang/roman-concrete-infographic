# Village layout proposal

Read-only plan for the latest user override. Source v11 SHA f58d958eee5db375a76779f337681be96f8b7b6f0f0d4ba562f7d9aa3f79f528.

Eight dominant neighborhood clusters, plus a second narrow scaffold base at the opposite COL facade. Every proposed primary floor rectangle has zero projected road/water intersection and is inside the terrain mask. The road is kept as circulation space.

| Cluster | Scene bbox | Land floor(s) |
|---|---|---|
| NW_heritage_neighborhood | [310, 475, 467, 567] | [[315, 543, 379, 566], [410, 526, 464, 548]] |
| N_house | [544, 538, 635, 615] | [[555, 590, 625, 615]] |
| NE_market | [813, 646, 901, 728] | [[824, 699, 898, 728]] |
| W_concrete_workspace | [54, 845, 207, 945] | [[68, 902, 206, 945]] |
| E_attached_construction | [772, 839, 838, 924] | [[798, 891, 827, 923]] |
| SW_masonry_workyard | [344, 1135, 468, 1235] | [[358, 1201, 464, 1234]] |
| S_daily_life | [547, 1133, 612, 1207] | [[551, 1182, 608, 1206]] |
| SE_repair_workyard | [737, 1135, 839, 1236] | [[746, 1208, 835, 1235]] |

Physical scale is the first constraint: human2.3–3world≈23–35nativepx; house4–6world; maker wholeheight~3.5world/~80px. A150px prep group combines several small objects. Do not fit people to80px.

Hide18 current abstract-object roots/children. Replace CORE3 clast/cube with SW mortar/rubble/actual masonry; replace CORE4 triptych/micro with SE cracked wall/finished vault. Main copy remains2body lines at11.5px. Detail callouts are2lines at9.5px in170/190px frames and point into real workyards. Retain the2line research limitation.

CORE3 main frame moves from408.5,1028 to330,1032; shift its bakedbadge/rule by−78.5,+4. CORE2/4/5 main positions can remain. The main/details frames clear all new yard bboxes.

West scaffold base[370,895,396,922], east base[798,891,827,923]. Human2.4world, beams3–5world wide, levels3/6world. Roof/head projection over facade is acceptable, but exact world contact/penetration needs final BVH QA.

The NPZ COL low2percent hull corresponds to arena pit floor and is not a valid exterior foundation mask; it was not used as a hard placement condition. Final footprint/attachment checks must use full world geometry.

Conservative text rectangle indications: 0. See JSON for exact IDs; use glyph/silhouette review rather than failing on rectangles alone.
