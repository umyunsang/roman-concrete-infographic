# 컬러 v7 저장본 검증

결과: PASS

v6와 v7를 별도로 새로 열어 비교했다. Blender 파일·UI·씬·가시성 변경과 저장·렌더를 수행하지 않았다.

## 체크

- PASS: fresh_v6_and_v7_opened
- PASS: all_317_object_names_and_types_preserved
- PASS: geometry_transforms_camera_visibility_modifiers_constraints_materials_preserved
- PASS: exact_227_only_color_changes
- PASS: saved_colors_exactly_match_declared_linear_rgb_float32
- PASS: source_report_before_matches_fresh_v6
- PASS: source_report_after_matches_fresh_v7
- PASS: all_other_render_shading_color_management_world_settings_preserved
- PASS: saved_exposure_matches_palette_float32
- PASS: saved_background_type_world
- PASS: world_color_matches_background_palette
- PASS: world_background_node_color_matches_background_palette
- PASS: v6_source_bytes_unchanged
- PASS: canonical_original_bytes_unchanged

## 저장본 비교

- 객체 317개와 메시 255개.
- 색만 변경된 객체 227개; 다른 90개 객체의 색은 동일.
- 카메라·지형·콜로세움과 모든 객체의 메시·변환·가시성·부모·컬렉션·모디파이어·제약·재질을 비교했다.
- 예외로 허용한 설정: view.exposure(+0.7), shading.background_type(WORLD), World.color와 World.Background node의 Color(동일 팔레트 배경색).
- Studio light, 그림자, cavity, outline, 해상도 및 기타 렌더 설정은 비교 대상이다.
- 숨김 원본 16개의 matrix_world는 새 로드에서 identity 캐시로 남는다. 씬을 수정하지 않고 persistent matrix_basis와 parent inverse로 world를 계산해 before/after 리포트와 비교했다. 이 16개의 raw 캐시도 v6/v7 사이에서 동일하고 basis·parent inverse·부모·실제 메시는 정확히 동일하다.

## 정정

`D4_crack`는 EMPTY 부모이며 메시가 아니다. 앞선 scene-color-inventory.md와 메시 전달에서 이를 visible MESH라고 쓴 부분을 정정한다. 기존 JSON의 type=EMPTY는 정확했다. 원본 균열 모델 자식 13개의 부모이며, 이번 배색 객체 227개 목록에 이 EMPTY는 포함되지 않는다.

## SHA256

- v6: `d71533920ebd305c41e92db718b527647c8b9655aee87cbb3b656c3afde257cd`
- v7: `2c22462b8cd9f169f6eb12822befa415c9c42a256eca86ae4e5ead5820d1b4b8`
- canonical original: `28d49f93c6edaf89bcbcc54ff1dfb94b0089cc2a0e43496032d46717c1a14cb3`

## 검증 스크립트 점검 기록

첫 실행에서 enum RNA에는 is_array가 없어서 background_type 추출이 누락되어 KeyError가 발생했다. getattr 기본값을 사용하는 수집기로 수정한 뒤 다시 실행했다. Blender 저장본은 쓰지 않았다.
World.use_nodes 제거 예정 경고와 wireframe_color_type enum0 경고는 읽기 과정에서 나타났다. 비교 결과의 허용 변경 목록과는 관계없다.
