# Phase13 seaside part selections

Final helper: `sea_object_parts.py`; public API `build_assignments(bpy)` and `PALETTE`.

Fresh Blender 5.2.2 read of source v8 passed. Source SHA before/after: `d179c5abdce8a9b0b48cf3f34cad9331b61e048f2e8edef504f430cee172ef3c`. Original local geometry is read only; no production save/render, material, geometry, transform, camera, or UI writes were used.

| Object | Default | Original polygon role counts |
|---|---|---|
| L09_portus_lighthouse | sea_stone | stone 5565; base 449; cap 438; recess 327 |
| L09_portus_mole | sea_stone | stone 2815; base 664; deck 1965; cap 45 |
| L12_harbor_pilae | sea_stone | stone 4612; base 252; deck 361; cap 164 |
| NB_marine_breakwater | sea_concrete | concrete 12135; base 127; deck 843; cap 4225 |

The lighthouse mask selects its existing lowest foot, summit and balcony upper surfaces, and small inset shaft-window faces. Window masks use original local depth/position, measured height bands, and face-area bounds; the broad outer wall polygons remain stone. Lantern-body openings remain default stone because their inset geometry is less unambiguous.

The quay has an existing recessed flat floor and perimeter walking surfaces. Its walls and irregular ruins remain stone; the elevated corner-block top alone receives the darker cap color. The harbor pilae have six pillar forms on a shared slab, with original slab upward faces and pillar cap upward faces identified by normal and local height. Decorative lower panels retain the stone color.

The added breakwater is a low slab with two masonry/block wall sections. Slab top, underside/lowest sides, wall body, and upper block faces are separately identified. There is no independently recognizable exposed aggregate geometry, so the helper has no aggregate role.

`sea-object-parts-audit.png` is drawn directly from exported original mesh faces with the selected labels. It is an inspection preview, not a production render. `sea-object-part-validation.json` records source/helper/assignment SHA and original topology/counts; `sea-object-part-assignments.json` records exact original polygon indices. Face lists are disjoint and in range. Existing sea/wave objects are outside the helper scope.
