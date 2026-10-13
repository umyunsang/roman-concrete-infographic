# v8 부위 재질 저장본 검증

결과: PASS

v7와 v8를 fresh background open으로 각각 읽고 비교했다. 씬·가시성·재질·UI를 수정하지 않았고 저장·렌더하지 않았다.

317객체/255메시, 실제 재질 51개, 렌더 표시 메시 227개, 2개 이상 색을 쓰는 메시 36개.
공유 mesh data 분리는 실제 18개이며 production 리포트 목록과 대조했다.

## 체크

- PASS: fresh_v7_v8_files_opened
- PASS: exact_317_objects_255_meshes_preserved
- PASS: all_geometry_basis_parent_inverse_transforms_collections_constraints_camera_visibility_object_colors_preserved
- PASS: only_applied_material_slots_changed
- PASS: saved_before_report_exact_match
- PASS: saved_after_report_exact_match
- PASS: exact_51_materials_227_assigned_visible_meshes_36_multicolor_meshes
- PASS: all_reported_face_counts_slot_roles_and_assignment_sha_exact
- PASS: all_diffuse_and_principled_colors_match_srgb_linear_float32_palette
- PASS: only_18_reported_shared_mesh_data_isolations
- PASS: only_workbench_material_scene_shading_change
- PASS: only_existing_view3d_material_color_changes
- PASS: v7_source_sha_preserved
- PASS: canonical_sha_preserved

## 검증 범위

- vertices/edges/loops/polygon topology 해시, basis/world/parent inverse, 부모·컬렉션·제약·카메라·가시성·object color를 비교했다.
- material slots와 polygon material_index만 메시별 허용 변경이다. 분리된 공유 mesh data도 이름 변경 외 geometry가 같은지 확인했다.
- 모든 227메시의 material role 순서, 슬롯 이름, role별 면 수, 원본 순서의 uint16 material_index SHA를 적용 리포트와 대조했다.
- 모든 51재질의 HEX를 독립적으로 linear float32로 변환하여 diffuse_color와 Principled Base Color 및 메타데이터를 대조했다.
- Studio/shadow/cavity/outline/exposure/world/background/resolution은 보존 비교 대상이다. Scene Workbench OBJECT→MATERIAL 및 기존 VIEW_3D color_type→MATERIAL만 표시 방식의 허용 변경이다.
- 숨김 원본 16개의 identity world cache는 basis/parent inverse에서 읽기 계산했다. raw cache와 persistent parent inverse도 v7/v8 사이에서 비교했다.

## SHA256

- v7: `2c22462b8cd9f169f6eb12822befa415c9c42a256eca86ae4e5ead5820d1b4b8`
- v8: `d179c5abdce8a9b0b48cf3f34cad9331b61e048f2e8edef504f430cee172ef3c`
- canonical: `28d49f93c6edaf89bcbcc54ff1dfb94b0089cc2a0e43496032d46717c1a14cb3`

## 검증 스크립트 점검 기록

첫 실행의 JSON 출력에서 VIEW_3D clip_planes의 중첩 bpy_prop_array 직렬화가 실패했다. RNA 배열을 재귀적으로 일반 목록으로 변환한 뒤 다시 비교했다. 제작 파일이나 UI를 변경하지 않았다.
World/Material.use_nodes 제거 예정과 wireframe_color_type enum0 경고는 읽기 중 출력됐으며 허용 변경과 구분했다.
