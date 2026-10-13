# v9 narrative and visual QA

## Result
FAIL pending one readability correction; rhetorical sequence and written evidence scope PASS. One additional recommended visual-source qualifier for C5.

Viewed actual native 1x PNG, read logical narrative_v9.json and actual figma-poster-v9-validation.json. No Figma or production writes.
Image SHA-256: `934bf706a08f4b7d7334e5baecd7333730a7210f500b1d062acde629849b2419`

## Required correction — C1 comparison caption
The three small lines at x528/y496–535 overlap patterned field/ground graphics. The first modern-binder line and last steel line compete with map marks at 1x. This is not text-frame clipping, but it weakens the key comparison that should carry the opening question into manufacture.
Bounded overlay fix: keep story/C1 coordinates, add a quiet neutral backing or halo only behind the existing three-line caption. Candidate backing [524,492,704,539], subtle fill matching nearby light ground; avoid a heavy card border. It does not touch the modern frame bbox starting near x708. Root should inspect the actual result once after applying it. The background image/model/terrain remain unchanged.

## Recommended correction — separate the fixed ruin image from C5 experiment
C5's body explicitly says modern recreated specimens, so the text does not label the ruin as an experimental specimen. Still, the ruin sits immediately above the headline 금을 내어 봤더니 and can be read as its illustration. Add a short visual-source label near the ruin, for example 유적 관찰 장면. Candidate x1016/y690, about120×13 pt, font9.5; model bbox starts y708, so the label sits above it with a small gap. Generic observational identification avoids inventing a site name. Keep the explicit modern-recreated-specimen first body line. No model relocation is required.

## Flow checks — PASS
1. C1 sets modern cracks against surviving Roman remains and asks what binder differed. It no longer asserts a universal 100-year modern lifetime.
2. C2 answers with dry mixing, then water/heat, then explicitly introduces the leftover white grains. This links to the next object.
3. C3 voices the apparent mixing defect, then reverses its meaning into calcium supply. It does not claim proven intentional self-healing design.
4. C4 says the same calcium moves into the crack, then new crystals fill small cracks. The three cubes have distinct water/calcium/crystal captions.
5. C5 asks whether filling really happens, then reports modern recreated specimens with a quicklime comparator and leakage results. It does not claim structural-strength recovery.
6. The closing returns to present-day study and the opening survival question, adding compression-friendly structure and continuing repair.

## Layout and evidence checks — PASS except C1 ground conflict
- No clipped title, full question, CORE body or final closure observed at1x.
- CORE numbers/badges align with headings; no visible duplicated old text.
- C4 single process row remains; state captions and D4 scope guard remain separate and readable.
- D4 explicitly says this was not directly proven at the Colosseum. C5 explicitly says modern recreated specimen. The central arena is not textually claimed to self-heal.
- White clasts remain visible; enlargement is identified as conceptual.
- Closing is readable in its blank gap and does not collide with D3 or today-lab text.
- Steel and breakwater labels remain present. Marine text remains marine-scoped.

## Validation boundary
Actual native PNG visual/story QA at1x, not measured reader acceptance or attention. Written causal continuity is now substantially clearer than v8. Root's structural image hash/node-preservation audit is independent of this lane's visual observations.

## Final bounded recheck — PASS
Viewed replaced actual 1x export once, inspecting only the two requested fixes.
Final reviewed1x SHA-256: `9f699b516acb9eba77fc74063f994fa1a32e85f15bd03541fd65fe5ae6ad504c`
- The subtle caption backing separates all three C1 comparison/steel lines from field patterns. Lines are readable at1x; no new overlap with C1 body or modern frame observed.
- 유적 관찰 장면 is readable above the fixed C5 ruin, separated from the model and C5 headline. It clarifies that the ruin image is contextual observation while the body identifies modern recreated experimental specimens.
Both requested corrections are resolved. Earlier FAIL is superseded by this final PASS. This is the two-fix digital visual recheck, not reader acceptance or broader revalidation.
