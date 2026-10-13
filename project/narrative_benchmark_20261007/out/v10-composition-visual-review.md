# v10 native composition visual review

**Final verdict: PASS.** The sole observed C2 marker/rule defect was corrected and visually rechecked.

## Scope and artifact
Read actual figma_poster_v10_composition_1x.png and2x.png plus figma-v10-composition-mutation.json. Compare with previously reviewed nativev9. No production/Figma edits, new research, video work or direction changes. Current95text contents must remain; user-deleted closing is not restored.

Pre-fix1x SHA-256: `1dd94d3900484ea01f484c24bba9b26147e59731c20bba8807baf531e3288eea`
Pre-fix2x SHA-256: `915241ce926ff613375b55edd657559589d90825f7f470546a2084bf65aed638`

## Initial verdict
One concrete failure: C2 black badge and underline in the background do not align with correctly placed native number/title. Root independently found it and is fixing the background. No other blocking visual failure observed.

## C2 correction
Observed dark-circle pixel bbox approximately[77,724,96,742] in actual1x; its white native2 is nearx75.5/y750.5 and outside the circle. Underline is near the first heading line instead of below the two-line heading.
Root planned correction is appropriate:
- Badge bbox[69.5,746.5,89.5,766.5], keeping native numeralx75.5/y750.5.
- Underline[69.5,797.1,213.6,797.9], below title2 endingy796 and before body ink.
This is a background-marker placement correction; no text-content change or other object move needed. Await corrected native export for this bounded recheck only.

## Passed checks in actual1x/2x
- Header title72 has more breathing room while exact question remains dark, single-line and within the fixed band. No observed clipping.
- CORE21/body11.5 hierarchy is coherent; secondary context/case/place text is visibly lower in weight. Bodies remain readable at1x.
- Modern frame keeps its larger silhouette and now has clear lower bays/ground; the previous orchard interpenetration is resolved. C1 comparison caption remains readable without its old busy ground.
- C3 specimen and C4 three-state process have clearer prominence. Model-to-caption and state-label spacing remains legible; removed farm/particle clutter no longer resembles extra mechanism states.
- Clast conceptual caption remains separate from structural-model labels. D4 guard is readable and explicitly excludes direct Colosseum proof.
- Designated lab model and compact S4 metadata now sit with C5's modern-specimen proof. Generic ruin is separately labelled as an observation scene beside the Privernum evidence cluster. No source-case swap or Pompeii laboratory mislabelling observed.
- Five narrative steps are traceable: contrast/question → water/heat manufacture leaves grains → apparent-defect reversal → same calcium movement/crystal filling → controlled recreated-specimen comparison. The user-deleted closing block remains absent.
- Lower forest grouping, coastal cases and diagram area are less scattered thanv9. No observed tree/model interpenetration comparable to the previous modern-frame issue.
- Central hero, enlarged modern frame and major aqueduct remain visually distinct. No new hero/text/aqueduct obstruction observed.
- No other actual title/body/state/case caption clipping or overlap was observed. The lab's retained irregular rock base reads as a supporting model vignette, with its experimental identity defined by adjacent labels; no additional physical reinterpretation correction is required in this bounded review.

## Validation boundary
Digital native-export visual QA at1x/2x, not print proof, measured reader comprehension or physical contact/collision simulation. Exact95text-content equality and source-frame/Blender preservation are separate root-owned structural checks; this lane observed that deleted closing copy is absent rather than re-proving native content equality.

## Final corrected-export recheck — PASS
Viewed the replaced actual native1x export once, scoped only to corrected C2 badge/underline. The white numeral2 is centered inside the black circular marker beside the first heading. The rule is below both heading lines and above body ink, without crossing either. No new local overlap was observed.

Final1x SHA-256: `7d7bda505163e30a078f02713f9566ddcb5a2f3eb7b66629524dca64a27da20f`
Final2x SHA-256: `12f4c1cf7e4fe0e6e04f4ffd9192d97b11d38f9139a112f385377e5b9eb7afd2`
Root reports final background image hash`941c6dfe8fff1e17567f2413cb93c420b93e8517`; geometry/BVH and preservation results are root-owned checks and were not rerun by this lane.

The initial C2 failure is superseded. With the earlier full1x/2x composition checks and this bounded correction check, no remaining observed visual failure is reported. No deleted closing copy was added, and no new production edits or direction changes were requested.
