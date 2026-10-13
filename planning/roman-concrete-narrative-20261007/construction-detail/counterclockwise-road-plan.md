# Counterclockwise construction road plan

Status: concrete proposal complete. Production edits belong to root.

Six main slots use the final controller targets; the kiln and Palatine are ancillary. One caption-frame overlap remains: the142px maker caption atx177,y947 intersects the carrier slot by26px horizontally. Narrow its frame to106px (endsx283); all six body rectangles then clear the retained native text frames. CORE3/4 titles can stay at1028/1032.

| Stage | Body bbox | Bottom-centre proxy | Nearest road pixel | Distance |
|---|---|---|---|---|
| maker | [177, 831, 319, 940] | [248, 940] | [248, 940] (R_core_road) | 0.0 px |
| carrier | [293, 913, 352, 1005] | [322.5, 1005] | [328, 1003] (B_pons2) | 5.852 px |
| vault_construction | [351, 920, 463, 1008] | [407, 1008] | [407, 1006] (R_core_road) | 2.0 px |
| builder | [465, 920, 548, 1008] | [506.5, 1008] | [506, 1008] (R_core_road) | 0.5 px |
| pair | [557, 902, 673, 1008] | [615, 1008] | [615, 1008] (R_core_road) | 0.0 px |
| vault_complete | [804, 887, 917, 970] | [860.5, 970] | [860, 970] (R_core_road) | 0.5 px |

CCW route: maker → carrier across B_pons2 → timber-supported vault → kneeling wall builder → paired mortar delivery facing north to COL → finished cutaway vault on SE R_core_road.

Exact sole/platform contact is not proved by body-bbox bottom points. Root final ground planting uses T_land/R_core_road/B_pons1/2 BVH. Foreground heads may overlap the lower facade in projection; actual 3D penetration must be checked in the saved controller output.

Virtual uniform COL scaling about its existing object origin: .88 projects to approximately [381.71,598.93,805.98,976.36]. The controller target [395,592,791,965] is more compact; final fitted world scale should be recorded. Source local geometry and camera/terrain remain unchanged.

Maker caption should move from937 to947 after its body bottom changed to940, and narrow from142 to106px to clear the carrier by10px. Other label row y1012 height12 ends1024 before CORE3 title1028. Current temporary v10 Vesta is in the old mixer area; a v11 controller starting from v9 naturally restores both upper temples once construction models leave that upper row.

Full raw projection arrays moved from the temporary33MB JSON into counterclockwise-road-geometry.npz. Final JSON contains compact slots, route, evidence hashes and native text rectangles.
