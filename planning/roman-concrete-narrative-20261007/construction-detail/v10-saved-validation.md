# Saved v10 independent read-only validation

Result: PASS

Original objects 317; output objects 332; new objects 15; changed originals 103.

- PASS: fresh_v9_v10_opened_read_only
- PASS: source_v9_original317_objects_all_retained
- PASS: new_objects_exactly_match_production_report
- PASS: allowed_existing_names_within_independent_user_scope
- PASS: existing_object_changes_only_authorized_fields
- PASS: newly_hidden_objects_exactly_reported_and_scoped
- PASS: original_geometry_topology_exact_except_two_baked_shape_translations
- PASS: existing_slots_and_indices_exact_except_kiln
- PASS: original_mesh_datablock_names_exact_except_optional_kiln_isolation
- PASS: all_original_materials_preserved_except_unused_replaced_kiln_slot
- PASS: new_material_HEX_linear_diffuse_and_principled_match
- PASS: kiln_exact_original_faces_match_independent_helper_and_palette
- PASS: new_meshes_visible_material_indices_valid_inside_safe_poster_bounds
- PASS: scene_camera_render_world_exposure_studio_and_old_collections_preserved
- PASS: all_saved_viewport_settings_preserved
- PASS: all_original_parent_inverse_and_narrative_properties_preserved
- PASS: production_before_matches_fresh_v9
- PASS: production_after_matches_fresh_v10
- PASS: fresh_mover_bboxes_and_reported_bboxes_valid
- PASS: all_original_and_new_face_index_SHAs_match_report
- PASS: applied_roles_face_counts_material_slot_order_polygon_count_match_report
- PASS: material_roles_HEX_and_linear_values_match_report
- PASS: downloaded_Meshy_GLB_provenance_SHA_preserved
- PASS: report_object_material_totals_match_fresh_saved
- PASS: source_v9_SHA_exact_preserved
- PASS: canonical_SHA_exact_preserved

Source v9 SHA `8125d6cf8ec2da6cf09125472aa603afd1debcd88910ff8ed0893b174a2288fe`
Output v10 SHA `05be502a28c650dd0bbbbc8132f63c49c09c997cc2be4d62f7a754016b4d5f78`
Canonical SHA `28d49f93c6edaf89bcbcc54ff1dfb94b0089cc2a0e43496032d46717c1a14cb3`

Two fresh background file opens. No save, render, object/material/visibility/UI writes. Hidden matrix_world cache normalized read-only from persistent basis/parent inverse. Existing geometry/slots/indices/property and material-node snapshots compared outside independent authorized scope.

Final micro fill revision independently confirmed: crack/fill local geometry SHA is identical, projected bbox maximum difference 0.001317 px, fill is slightly toward the camera and uses base_lime_calcium_crystal. See v10-final-micro-fill-validation.json.

Final saved material count: 69. The unused old kiln-only material omission remains scoped and reported.
