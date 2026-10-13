# Blender v6 배색 구현 감사

상태: 완료. 저장본을 백그라운드에서 읽고 JSON만 생성했다. Blender 데이터 변경, 저장, 렌더, UI 또는 MCP 호출을 하지 않았다. root가 최종 색을 선택하고 r7 저장·렌더를 수행한다.

## 직접 확인한 현재 상태

- 소스: `out/roman_concrete_narrative_v6.blend`
- SHA256: `d71533920ebd305c41e92db718b527647c8b9655aee87cbb3b656c3afde257cd`
- Blender 5.2.2 LTS, 317 객체: MESH 255, FONT 47, EMPTY 13, CAMERA 1, LIGHT 1.
- 현재 저장본에서 보이는 메시 227개. 숨김 글 컬렉션 70_LABELS_TEST는 그대로 유지한다.
- Workbench / SOLID / STUDIO / `roman_poster.sl` / OBJECT 색 방식. 재질 데이터는 **0개**.
- 색 관리: Standard, Look None, sRGB 디스플레이, exposure +0.35, gamma 1.0.
- 그림자 true, intensity .28. 외곽선 true / RGB .10. cavity BOTH, ridge1.2 / valley1.4, curvature0 / 0.
- 배경 방식 THEME, viewport background RGB0. World.color .050876, 월드 Background RGBA .844944/.847438/.960488/1 및 Strength .35. `use_scene_world`와 `use_scene_world_render`는 false.
- 합성 헬퍼는 지도 패스에서 오버레이 80_SHAPES/81_NOSHADOW/85_HEADER를 숨기고 opaque + shadow로 렌더한다. 오버레이 패스는 해당 컬렉션만 투명 배경 + no shadow로 렌더한다. 배색 후에도 이 분리가 필요하다.

## 핵심 모형의 정확한 색 역할

| 객체 | 실제 의미 | 현재 그레이 | 권장 역할 |
|---|---|---|---|
| NB_modern_building | 철근을 포함한 현대 골조, 합쳐진 단일 메시 | .78 | 차가운 회청색 |
| C2_hot_mixing | 제조 장면, 합쳐진 단일 메시 | 1 | 따뜻한 석재색 |
| NB_lime_clast_specimen | 고체 매트릭스 | .58 | 중간 갈색 석재 |
| ..._LIME00–05 | 기존 D2 석회 형상 복제 | 1 | 밝은 분필색, 반드시 흰 알갱이로 읽혀야 함 |
| NB_core4_sequence_GRAY00 | D4_arrow0/1 | .15 | 흐름 화살표, 청록 회색 |
| ..._GRAY01 | D4_crack0/1 | .08 | 열린 금, 짙은 중성색 |
| ..._GRAY02 | D4_crack2 + D4_lime0/1 | 1 | 석회 및 최종 충전부, 같은 밝은 분필색 |
| ..._GRAY03 | D4_cube0/1/2 | .60 | 3개 콘크리트 매트릭스, 동일한 갈색 |
| ..._GRAY04 | D4_drop0/1/2 | .35 | 물방울, 선명한 청록 |
| S_lab_island | 실험실 장면 | 1 | 현대 골조와 같은 차가운 계열 |
| C5_researchers | 일반 유적 관찰 장면 | 1 | 로마 유적의 따뜻한 계열 |

JSON에는 모든 317 객체에 의미 범주·색·가시성·재질·원본 재사용 메타데이터·화면 경계 상자가 있다. `suggested_object_color_dictionary`에는 보이는 227 메시의 **개별 객체 이름 → 의미 역할 → 제안 sRGB HEX**가 있다. 이 제안은 root 최종 배색의 입력이고 적용 완료 결과가 아니다.

## 구현 제약과 권장 선택

1. 현재 OBJECT 방식이면 객체 전체가 한 색이다. 현대 골조와 C2 제조 장면 안의 개별 재료를 서로 다르게 칠하려면 객체 분리 또는 재질 인덱스 설계가 추가로 필요하다. 이번 작업에서는 합쳐진 장면의 냉색/난색 구분만 적용해도 구조 보존과 대비 목적을 함께 달성할 수 있다.
2. GRAY02는 석회와 충전된 마지막 금이 이미 같은 메시다. 둘 다 밝은 석회색을 쓰는 것이 현재 서사와 데이터 구조에 맞는다. GRAY04를 바다와 같은 색 계열로 두면 물의 행동을 연결하기 쉽다.
3. terrain과 물은 매우 큰 영역이다. 낮은 채도·높은 명도로 유지하고, 콜로세움에는 따뜻한 중간톤을 주어 중심을 유지한다. 수목·농경지는 저채도 세이지 계열로 제한한다. CORE 5개 배지와 밑줄은 같은 테라코타 색으로 일관성을 유지한다.
4. 팔레트 HEX는 sRGB 제안값이다. Blender float 색 작업 공간과 Figma 색을 동일 숫자로 취급하면 결과가 달라질 수 있다. root의 적용 스크립트에서 HEX→scene linear 변환을 명시한다. 현재 +.35 노출이 밝기를 더 올리므로, flat 색 일치가 필요하면 exposure0을 선택하거나 변환 후 노출을 보정한다. 실제 스튜디오 음영·cavity·outline을 포함한 렌더 확인이 최종 기준이다.
5. 현재 world node 색을 바꿔도 사용하지 않는 월드 조명 플래그 때문에 원하는 팔레트를 보장할 수 없다. 큰 배경은 실제 T_land/sea 색을 우선 맞춘다. 배경 설정을 바꾸는 경우 root가 별도로 렌더에서 확인한다.
6. 기존 `D4_crack`는 화면에 보이는 MESH이지만 과거 절차 모형의 EMPTY 부모 이름과 비슷하다. NB_core4_sequence와 혼동해 숨김·삭제하지 않는다. 모든 변환·메시·가시성은 그대로 두고 색만 바꾸는 것이 이 작업의 검증 경계다.

## 출처와 점검 기록

- 기술 문서: [Workbench Object Color](https://docs.blender.org/manual/en/5.1/render/workbench/color.html), [Blender GPU Color Management](https://developer.blender.org/docs/features/gpu/color_management/). 공식 검색 결과는 Workbench의 객체별 Display 색과 scene-linear 렌더 파이프라인을 지원한다. 상세 문서 open는 접근 오류/402여서, 그 이상 문서로 확인했다고 주장하지 않는다.
- `World.use_nodes`의 Blender6.0 제거 예정 경고와 `wireframe_color_type` enum0 경고는 읽기 중 출력됐다. scene 데이터와 파일은 쓰지 않았고 소스 SHA를 확인했다.
- 첫 감사에서 L02_tiber/W_water_marks/숨김 글 메시 분류가 불완전했다. 객체 이름과 컬렉션을 확인해 분류를 수정한 두 번째 감사에서 **unclassified 0**을 확인했다.
- 감사 스크립트 `scene_color_audit.py`; 제안 추가 스크립트 `scene_color_recommendations.py`. 두 스크립트는 저장본을 수정하지 않는다.
