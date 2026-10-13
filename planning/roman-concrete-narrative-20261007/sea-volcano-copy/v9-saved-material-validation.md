# v9 바다·화산 부위 재질 저장본 검증

결과: PASS

v8/v9 저장본을 각각 fresh background open으로 읽었다. 씬·가시성·재질·UI를 수정하지 않았고 저장·렌더하지 않았다.

317객체/255메시, 기존51재질 유지 + 새10재질 =61재질. target5개, nontarget250메시.

## 체크

- PASS: fresh_v8_v9_files_opened
- PASS: exact_317_objects_255_meshes_preserved
- PASS: all_geometry_transforms_camera_visibility_object_colors_parent_inverse_custom_properties_preserved
- PASS: only_exact_five_target_object_material_slots_changed
- PASS: exact_250_nontarget_mesh_data_names_material_slots_roles_indices_counts_preserved
- PASS: all_scene_render_display_shading_world_exposure_settings_exact
- PASS: all_saved_viewport_settings_exact
- PASS: existing_51_materials_colors_principled_nodes_links_metadata_exact_except_users
- PASS: exact_10_new_61_total_reported_materials
- PASS: all_five_target_slot_roles_face_counts_uint16_assignment_shas_exact
- PASS: all_255_reported_before_after_index_shas_exact
- PASS: new_10_material_hex_linear_float32_diffuse_principled_roughness_correct
- PASS: only_reported_shared_mesh_data_isolations
- PASS: production_before_report_matches_fresh_v8
- PASS: production_after_report_matches_fresh_v9
- PASS: v8_source_sha_preserved
- PASS: canonical_sha_preserved

## 범위

- 모든317객체의 geometry/basis/world/parent/constraint/collection/camera/visibility/object color와255메시의 topology/UV/color attribute를 비교했다.
- 기존51재질의 diffuse/Principled base color/roughness와 node properties/inputs/links/role/HEX를 대조했다. material users만 허용한다.
- nontarget250메시는 mesh data name, material slot order/role/face count/material_index uint16 SHA를 포함해 전체 snapshot이 같아야 한다.
- 다섯 target은 production report의 role 순서, polygon count, 실제 role별 face count, material slot 이름, index SHA를 대조했다.
- 새10재질의 HEX를 독립 linear float32로 변환해 diffuse_color/Principled Base Color와 roughness .85를 확인했다.
- 숨김 객체의 identity world cache는 basis/parent inverse를 읽어 계산하며 viewport를 일시 켜지 않는다. raw cache와 parent inverse도 별도로 보존 비교한다.

## SHA256

- v8: `d179c5abdce8a9b0b48cf3f34cad9331b61e048f2e8edef504f430cee172ef3c`
- v9: `8125d6cf8ec2da6cf09125472aa603afd1debcd88910ff8ed0893b174a2288fe`
- canonical: `28d49f93c6edaf89bcbcc54ff1dfb94b0089cc2a0e43496032d46717c1a14cb3`
