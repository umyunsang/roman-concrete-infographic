# Pair loaded-trough visibility — bounded yaw choice

Recommendation: apply **current yaw −35 degrees**, absolute Z rotation **221.4250477 degrees** (equivalent to −138.5749523 degrees). This temporary candidate is the only one of the three requested angles that visibly exposes a continuous wooden trough side and a pale mortar top in the space between the two real workers, while their walking direction remains upward toward the Colosseum.

| Temporary candidate | Actual native camera observation | Choice |
|---|---|---|
| +30 degrees | Bodies overlap along the view; the shared trough is hidden. | Reject |
| +55 degrees | More side view, but one body still covers the load and the two workers stack. | Reject |
| −35 degrees | Workers remain separated; wood trough wall and pale filled top are visible between the bodies. | Recommend |

Use the current scale **4.3996696472** uniformly and current location **[19.4147663116, -17.0482254028, 0.2492889464]**. This winner required no uniform refit or translation. Ground bottom Z remains 0.2492889464. Projected model bbox is **[581.3596, 908.0884, 645.5801, 1006.0984]**. Its projected forward vector is **[+2.6990, -28.1650]**, maintaining the inward approach to the Colosseum. No trough extension or new local geometry is needed for the demonstrated winner.

Source: actual latest `out/roman_concrete_narrative_v11.blend`, SHA256 `f58d958eee5db375a76779f337681be96f8b7b6f0f0d4ba562f7d9aa3f79f528`. Loaded read-only; three temporary yaw previews rendered with the existing native Camera and MATERIAL Workbench shading, crop x550..710/y890..1020 at 3x pixel density. Colosseum background and actual body occlusion remain present. Each candidate starts from the source transform; plus30/plus55 only shrink uniformly if their height exceeds the allowed region. Minus35 preserves source scale and anchor.

Evidence files:

- `pair_yaw_minus35_native.png`: recommended actual crop.
- `pair_yaw_plus30_native.png`, `pair_yaw_plus55_native.png`: rejected actual crops.
- `pair-yaw-candidates.json`: exact transforms, forward directions, foot bounds and source checks.
- `audit_pair_yaw_candidates.py`: bounded temporary preview script; it never saves a blend.

PASS: source blend bytes, every mesh geometry hash and native Camera matrix preserved. No production writes, helper changes, paid jobs or new geometry. This is a demonstrated temporary choice; root owns production application and final export.
