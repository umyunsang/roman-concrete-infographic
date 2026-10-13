# 루브릭 · 물체 단위 컬러 (재질 색·팔레트) — obj_color

- 작성: 라운드 11 물체 컬러 비평가(2026-10-13). STATE D37에 따라 Blender에 배치된 자산마다 따로 심사한다. 다음 라운드부터 이 문서를 고정하고, 다른 비평가가 블라인드로 같은 값을 재현한다.
- 판정 단위는 **자산 하나**다. 항목마다 예(합격)/아니오(불합격)/해당 없음으로 판정한다. 해당 없음은 합격으로 센다.
- 등급(자산 단위, BRIEF §6과 같음): **AAA** = blocker 0 · major 0 · minor ≤ 2 / **AA** = blocker 0 · major ≤ 2 / **A** = blocker 0 · major ≥ 3 / **B** = blocker 1~2 / **C** = blocker ≥ 3.
- 수치 표시: 문헌이 직접 준 값은 [문헌값], 문헌 원리를 이 포스터에서 재현할 수 있게 옮긴 값은 [운영값], 이 파이프라인을 실제로 재서 정한 값은 [보정값]이다(보정 근거는 부록 A).

## 고정 조건·결정 (감점하지 않음, 해법으로도 깨지 않음)
- BRIEF §3 전부. 특히 CORE ①~⑤의 번호 원판·밑줄·제목 둘째 줄이 모두 #983821인 것(고정 5), 이정표 3개 = 석회암 기둥 + ②색 화살 판(고정 6), 클레이 디오라마의 약간 플랫한 음영(고정 4).
- 역할 토큰으로 일부러 다르게 정한 색: 콜로세움 외벽 `colosseum`(design tokens), 이정표 기둥 #A79375(D24), 구조 탑·단면 돌 단계(D26·D29), 석회 콘크리트 큐브 공통 ×1.29와 ① 골조 ×0.53(D29), 나무 무리 A의 밝은 잎(D29), 땅 ×1.07(D30), 밭 4종·목초지·그루터기·포도·짚 색(D35), 포석 현무암 #A9A69F·연석/다리 석회암 #C7BEAA·다리 윗면 포석색(D36).
- 기각·보류 목록(STATE R1~R12)은 새 근거 없이 다시 내지 않는다. 특히 R12(②→③ 화살 머리 앞 가장자리와 그 그림자 대비 2.44:1), R10(밑동 접촉 어둠), R11(베수비오 능선 지느러미), R3·R5(그림자 세기)는 이 루브릭에서 재지 않는다.
- 포스터 단위 컬러 루브릭(`color.md`)의 CL-05 예외(의미가 같은 '열' 소품은 기호마다 1x 50px 이하)를 그대로 따른다.

## 다른 루브릭과의 경계 (겹치지 않게 뺀 것)
- 글 대비·포스터 전체 팔레트 통계·인쇄 색역 → `color.md` CL-01~04, CL-13~25. 이 루브릭은 **자산 하나의 재질 색**만 본다.
- 명도 위계·주목도·실루엣 ΔL*·그림-바탕 ΔL* → `value.md`, `illustration3d.md` I3-13·I3-15. 구조 탑의 무게별 명도 순서 → I3-25.
- 메시 구멍·파편·관통 → I3-21·I3-22와 물체 3D 형태 루브릭. 여기서는 그 결과가 **색 얼룩·이물 색**으로 보일 때만 잰다(OBJ_COLOR-24·25).
- 지시선·하중 화살의 대비 → CL-18. 여기서는 지시선이 무채색인지만 본다(부류 LINE).

---

## 0. 측정 규약 (모든 항목 공통 · 재현용)

**0-1 자료(자산마다).**
- **맥락 크롭**: `r<N>/map_only_2x.png`(글 없음)에서 자산 외곽 상자 + 사방 24pt. 글이 걸리는 판정(OBJ_COLOR-04 대상 확인)만 `poster_2x.png`를 쓴다. 1pt = 2px.
- **단독 크롭**: 그 자산만 보이게 같은 카메라·조명·노출로 렌더한 RGBA(바탕 투명). 없으면 맥락 크롭에 자산 마스크(아래 0-2)를 씌워 쓴다.
- **재질 ID 크롭**(권장): Workbench FLAT 조명, cavity·그림자·AA·디더 끔, 재질마다 고유 색을 준 ID 패스. 지도 패스와 오버레이 패스(`80_SHAPES`·`81_NOSHADOW`·`85_HEADER`)를 실제 합성 순서대로 따로 렌더해 겹친다. 원본 .blend는 저장하지 않는다. 참조 구현: 스크래치패드 `objcolor/idpass.py`(ID 렌더), `objcolor/measure_obj.py`·`objcolor/ramp_test.py`(측정), `objcolor/clib2.py`(색 공식).
- **재질 표**: 자산이 쓰는 재질 이름과 `material.diffuse_color`(sRGB hex). Workbench의 Material 색 모드는 재질의 Viewport Display 색을 쓴다(OC9). 따라서 **기준 색은 Principled Base Color가 아니라 diffuse_color**다. v8_13에서는 둘이 다른 재질이 8개 있다.

**0-2 마스크와 부위.**
- 자산 마스크 = 단독 크롭 알파 > 0.5. 부위 = 재질 ID 영역. 재질 ID가 없으면, 단독 크롭 화소를 각 재질의 **토큰 램프**(0-3)와의 ΔE00가 가장 작은 재질로 나눈다.
- **부위 안쪽** = 부위를 3px 깎은 영역. 남는 화소가 30px 미만이면 1px만 깎는다. 판정 대상은 면적 4pt²(2x 16px) 이상인 부위만이다.

**0-3 색 공식과 대표값.**
- CIELAB D65, ΔE00(CIEDE2000, `color.md` 규약 6), Oklab·Oklch(`color.md` S11). L*는 CIE L*이다.
- **밝은 면(lit)** = 부위 안쪽 화소 가운데 L* 60~90백분위 화소의 RGB 평균(`color.md` 규약 6과 같다).
- **흰 부위 대표값** = 부위 마스크 L*의 95백분위(p95). **금 대표값** = 25백분위(p25). 가는 부위에서는 안티앨리어싱이 평균을 끌어내리므로 이 백분위를 쓴다.
- **토큰 램프** = 토큰 diffuse를 선형 RGB로 바꿔 k ∈ [0.15, 1.8]배(60단계) 한 뒤 다시 sRGB로 바꾸고 0~255로 자른 색의 집합. 조명·노출·그림자는 반사율에 곱해지는 값이므로, 정상 화소는 이 램프 위에 놓인다.
- **L*_paper** = poster_1x에서 84 < L* < 92인 화소의 L* 중앙값(`value.md` 규약 3). v8_13 렌더 값은 89.9.

**0-4 크기와 구별 거리 D.** `color.md` 규약 8의 Szafir 2018 정규화 거리 D를 그대로 쓴다. D ≥ 1이면 믿을 만하게 구별되고, D ≤ 0.3이면 사실상 같은 색이다. 시각 크기는 비교하는 두 부위 중 **작은 쪽**으로 고른다. 1m에서 1° ≈ 49pt이므로 ≤ 12pt는 0.25°, 12~50pt는 0.5°, > 50pt는 2°다.

**0-5 강조색 계열.**
- **A1(강조색과 혼동)** = ΔE00(화소, #983821) ≤ 10. `color.md` CL-12의 구별 문턱 10을 따른다.
- **A2(강조 색상군)** = Oklch h 20~48° 그리고 C ≥ 0.10. `color.md` CL-04와 같다.

**0-6 CVD 모의.** `color.md` 규약 7과 같다. Machado 2009 행렬, 심각도 1.0, protan·deutan·tritan을 선형 sRGB에 곱한다.

**0-7 렌더 파이프라인 사실(v8_13 실측, 부록 A).** Workbench, Studio 조명 `roman_poster.sl`, 보기 변환 Standard, **노출 +0.7 EV**, cavity(ridge 1.2·valley 1.4), 그림자 0.28, AA 8. 지도 패스(그림자 있음)와 오버레이 패스(그림자 없음)를 알파 합성한다. 이 조명은 **명도만 바꾸고 색상각은 거의 바꾸지 않는다**. 측정해 보니 C ≥ 0.03인 재질은 렌더 밝은 면과 토큰의 색상각 차가 1.3° 이내였다. 그래서 렌더 색과 토큰을 비교할 때는 색상각·채도로 보고, 명도는 면 방향이 같을 때만 비교한다.

**0-8 자산 → 역할·시대·부위 재료 부류.** 오케스트레이터의 자산 목록을 아래 행에 맞춰 쓴다. 역할 등급은 심각도에 쓴다.
- **핵심** = CORE 표지, CORE 그림, 영웅(콜로세움).
- **보조** = DETAIL, SUPPORT, BASIC.
- **배경** = 배경 지물·지형·식생·밭·길·물·바탕.

| Blender 물체(접두어) | 역할 | 시대 | 부위 → 재료 부류(0-9) |
|---|---|---|---|
| S_core1~5_badge, S_core1~5_underline | 핵심(CORE 표지) | – | 전부 ACCENT |
| MS1_core1_to_2, MS2_core2_to_34, MS3_core34_to_5 | 핵심(CORE 길잡이) | 로마 | 화살 판 ACCENT · 기둥 STONE(D24) · 받침 STONE · 쇠붙이(toolmetal) IRON |
| NB_modern_building, R1_frame_rust, R3_frame_crack_col·col2 | 핵심(CORE ①) | 현대 | 콘크리트·철근 MODERN · 녹 얼룩 RUST · 금 CRACK |
| C2_hot_mixing | 핵심(CORE ②) | 로마 | 바닥 돌 STONE · 구덩이 테(basin) EARTH · 반죽(mixture) RCONC · 피부·옷(cloth·linen) PEOPLE · 도구 WOOD |
| NB_lime_clast_specimen(+_LIME00~05) | 핵심(CORE ③, DETAIL 겸) | 로마(확대 개념) | 몸체 RCONC · 알갱이 LIME |
| NB_core4_sequence_GRAY00·02·03·04, R8_crack_step1·2, R8_water_step1, R8_calcium_step2, R8_healed_step3 | 핵심(CORE ④) | 로마(개념) | 몸체 RCONC · 흰 알갱이·칼슘 줄·메움 LIME · 물 WATER-P · 금 CRACK · 연결선 LINE |
| R1_specimen_healed·leaking, R1_healed_clast0~2, R3_healed_fill, R3_leak_crack, R1_leak_drop0~2, R1_leak_puddle, R1_lab_bench | 핵심(CORE ⑤, '오늘의 실험실' 겸) | 현대 | 시편 RCONC · 알갱이·메움 LIME · 금 CRACK · 물방울·웅덩이 WATER-P · 실험대 MODERN |
| COL_ruined, R3_colosseum_podium, R4_arena_skin | 핵심(영웅) | 로마 | 외벽 STONE(역할 토큰 colosseum) · 안쪽 벽 STONE · 아레나 EARTH · 기단 광장 STONE |
| D1_tank_*, D1_seawater, D1_concrete, D1_crystal* | 보조(DETAIL 재료 원리) | 개념 | 수조 MODERN · 바닷물 WATER-P · 콘크리트 RCONC · 결정 CRYSTAL |
| D2_cube, D2_lime*, D2_heat* | 보조(DETAIL 제작 원리) | 로마(개념) | 주사위 RCONC · 알갱이 LIME · 열 물결 HEAT |
| D3_*, S_sect*, D3_press*, S_lead* | 보조(DETAIL 구조 원리) | 로마(개념) | 탑·단면 돌 STONE(D26·D29) · 벽돌 줄 TERRA · 기초 STONE · 하중 화살·지시선 LINE |
| NB_marine_breakwater, L09_portus_mole, L11_privernum_wall, L08_pompeii_site, C5_researchers | 보조(SUPPORT) | 로마(C5의 사람·삼각대는 현대) | 성벽·블록·유적 STONE · 원료 더미(raw_lime) LIME · 통(basin) EARTH · 비계 WOOD · 사람 PEOPLE · 삼각대 MODERN |
| H_gate_* | 보조(BASIC 머리판) | – | PAPER |
| H_lime_pile, H_ash_pile, H_stone0~2, H_mold_box·lime*·plank* | 보조(BASIC 재료 범례) | 로마 | 생석회 LIME · 화산재 POZZ · 깬 돌 STONE · 틀 안 콘크리트 RCONC · 알갱이 LIME · 거푸집 판 WOOD |
| H_book*, H_core_sample·band*, H_lens_*, H_colosseum_mini | 보조(BASIC 근거) | 로마 기록·현대 연구 | 책 WOOD·종이 LINEN · 시추 시료·띠·렌즈 MODERN · 작은 콜로세움 STONE(역할 토큰) |
| R8_pantheon | 배경 | 로마 | 벽 STONE · 돔·현관 지붕 ROOF · 기단 STONE |
| D2_lime_kiln, L05_aqua_claudia, L09_portus_lighthouse, L12_harbor_pilae, L08_pompeii | 배경 | 로마 | STONE |
| L07_vesuvius, L01_* | 배경(지형) | – | ROCK |
| T_* | 배경(식생) | – | 잎 VEG · 줄기 WOOD |
| F_centuriatio | 배경(밭) | 로마 | FIELD(D35) |
| R_*, R1_road_*, R4_bridge_west_bed, B_pons* | 배경(길·다리) | 로마 | 포석·다리 윗면 BASALT · 연석·다리 몸체·난간 STONE(D36) |
| L02_tiber, L10_sea, W_water_marks | 배경(물) | – | 바다·강 WATER-M · 물결 FOAM |
| T_land | 배경(바탕) | – | GROUND |
| S_pin_* | 배경(지시 표지) | – | LINE |

**0-9 재료 부류의 색 창.** 밝은 면(lit) 기준이다. 흰 부위는 p95, 금은 p25를 쓴다. 클레이 디오라마의 밝은 조(high key) 때문에 절대 명도는 실제보다 높게 둔다. 실제 재료와 맞춰 보는 것은 **색상각과 채도**, 그리고 OBJ_COLOR-02의 **명도 순서**다.

| 부류 | 실제 재료·근거 | 창 (Oklch h°, C / L*) |
|---|---|---|
| STONE 석재(트래버틴·석회암·응회암) | 로마 트래버틴은 옅은 노랑·흰색(OC14) | h 60~95, 0.015 ≤ C ≤ 0.08 |
| EARTH 흙·모래·흙 통 | 아레나 모래, 반죽 구덩이 테 | h 55~95, 0.03 ≤ C ≤ 0.09 |
| BASALT 포석 | 아피아 가도 포석은 짙은 회색 레우시타이트 용암(OC15) | C ≤ 0.02 (명도는 02-d) |
| TERRA 벽돌·기와 | 구운 점토 | h 35~70, 0.04 ≤ C ≤ 0.12 |
| ROOF 판테온 돔·현관 지붕 | 2세기에는 금박 청동 기와, 663년에 벗겨짐(OC17). 테라코타도 허용 | h 35~90, 0.04 ≤ C ≤ 0.12 |
| POZZ 화산재(포촐라나) | 로마의 Pozzolane Rosse(붉은)·Nere(검은)(OC16) | h 30~70 그리고 0.03 ≤ C ≤ 0.09, 또는 C ≤ 0.02 그리고 L* ≤ 50 |
| LIME 석회·석회 알갱이·칼슘 결정·금 메움(calcite) | "distinctive bright white", 고대·현대 시료 모두 흰 알갱이, 금 메움 = calcite(OC3) | p95 L* ≥ L*_paper − 2, C ≤ 0.04 |
| CRYSTAL 해수 광물 결정 | 흰 결정으로 표현(D4·D17) | LIME과 같음 |
| RCONC 로마식 석회 콘크리트 몸체(고대 시료·개념 모형·재현 시편·반죽) | 회갈색 몰탈 | h 40~65, 0.03 ≤ C ≤ 0.07, 40 ≤ L* ≤ 65 |
| WOOD 나무(비계·도구·책·거푸집·줄기) | – | h 55~80, 0.04 ≤ C ≤ 0.09, 35 ≤ L* ≤ 62 |
| LINEN 천·종이 | – | h 75~95, C ≤ 0.06, L* ≥ 70 |
| PEOPLE 피부 / 옷 | – | 피부 h 45~75, 0.04 ≤ C ≤ 0.09 / 옷 h 40~100, C ≤ 0.08, A2 화소 0 |
| VEG 잎 | 우산소나무·사이프러스 | h 105~140, 0.04 ≤ C ≤ 0.09 |
| FIELD 밭 | D35 | C ≤ 0.09, h 60~130, L* 62~84 |
| ROCK 산·화산 | – | h 75~110, C ≤ 0.05 |
| WATER-M 바다·강 | `color.md` CL-10 | h 180~250, 0.03 ≤ C ≤ 0.07 |
| FOAM 물결 | – | h 160~200, C ≤ 0.04, L* ≥ 88 |
| WATER-P 그림 속 물(물방울·웅덩이·수조) | `color.md` CL-09(물끼리 ±15°) | h 195~225, C ≥ 0.06 |
| CRACK 금(어두운 홈) | D11·D15·D28 | p25 L* ≤ 25, C ≤ 0.03 |
| HEAT 열 물결 | `color.md` CL-05·CL-12 | h 30~45, C ≥ 0.10, ΔE00(lit, #983821) ≥ 10 |
| RUST 녹 얼룩 | 산화철 | h 40~70, 0.03 ≤ C ≤ 0.09, A2 화소 0 |
| IRON 로마 쇠붙이 | – | C < 0.03, L* ≤ 60 (03의 로마 부호와 맞춤) |
| MODERN 현대 콘크리트·강철·실험대·용기·연구 도구 | `color.md` CL-08, I3-04 | h 180~260 또는 C ≤ 0.02 |
| PAPER 머리판 | – | h 75~92, C ≤ 0.06, L* ≥ 75 |
| GROUND 땅 바탕 | D30 | h 75~95, C ≤ 0.04 |
| LINE 지시선·연결선 | – | C ≤ 0.03 |
| ACCENT CORE 표지 | 고정 5·6 | OBJ_COLOR-18 |

**0-10 지적 묶기.** 한 원인이 여러 항목·자산에 걸리면 지적은 하나로 묶는다. 예를 들어 같은 부위가 04와 05에 모두 걸리면 04 하나로만 낸다. 등록부 파일 하나가 원인이면 가상 자산 `PALETTE`에 1건만 낸다. 취향은 minor를 넘지 않는다.

---

## A. 재료·시대·역할에 맞는 색

**[OBJ_COLOR-01] 부위마다 재료 부류의 색 창 안에 있는가?**
- 측정: 0-8 표로 부위의 부류를 정한다. 단독 크롭에서 밝은 면(흰 부위는 p95, 금은 p25)의 Oklch와 L*를 잰다.
- 합격: 4pt² 이상인 모든 부위가 0-9 창 안에 있다.
- 실패 시: 핵심 부위는 major, 보조·배경 부위는 minor. 단, 다른 부류의 창에 들어가 **재료를 바꿔 읽게 하면** 역할과 관계없이 major다(물색 땅, 돌색 물, 현대 슬레이트색 로마 벽, 나무가 돌로 보이는 경우 등).
- 근거: OC4(색의 주 기능은 물체·재료 식별), OC5(색 진단성 높은 물체는 색이 인식을 도움), OC6(사람은 개념과 색의 직접 연상으로 대응을 추론함), OC1(물=파랑·식생=초록 같은 지도 관례), OC3·OC14~17(실제 재료 색).

**[OBJ_COLOR-02] 실제 재료의 명도 순서가 지켜지는가?**
- 측정: 같은 자산 안 부위의 lit L*(흰 부위 p95, 금 p25). (d)는 맞닿은 자산 경계 20pt 안에서 잰다.
- 합격(해당하는 것 모두):
  - (a) LIME 부위가 자산 안에서 가장 밝고, 다른 모든 부위의 lit L*보다 5 이상 높다.
  - (b) RCONC lit L* ≤ LIME p95 − 30.
  - (c) POZZ lit L* ≤ LIME p95 − 20.
  - (d) BASALT lit L* ≤ 맞닿은 STONE(연석·광장) lit L* − 8.
  - (e) CRACK p25가 자산의 다른 모든 부위 lit L*보다 낮다.
  - (a)~(c)는 [운영값]이다. 명도 한 단계 ΔL* 10(`value.md` 규약 10)의 2~3단계로 정했다.
- 실패 시: 핵심은 major, 그 밖은 minor.
- 근거: OC3(석회 알갱이는 "bright white"이고 "conspicuous"), OC15(포석은 짙은 회색), OC16(포촐라나는 붉은·검은 화산재), OC8(가장 밝은 면이 흰색 기준).

**[OBJ_COLOR-03] 시대 색 부호가 자산 단위로 지켜지는가?**
- 측정: 0-8 표의 시대 열을 쓴다. 건축·도구 부위(4pt² 이상, lit C ≥ 0.03)의 색상각을 잰다.
- 합격: 로마 자산은 h 30~140° 또는 C < 0.03이다. 현대 자산은 h 180~260° 또는 C < 0.03이다. 재료 개념 부위(RCONC·LIME·CRYSTAL·WATER·CRACK)와 사람은 01에서 판정하므로 뺀다.
- 실패 시: 핵심은 major, 그 밖은 minor.
- 근거: `color.md` CL-08과 `illustration3d.md` I3-04의 부호를 자산 단위로 옮겼다. OC6, `color.md` S6(의미 판별성).

**[OBJ_COLOR-04] 글이 색 이름으로 부르는 부위가 정말 그 색으로 읽히는가?**
- 대상: text_spec 글이 색·물질 이름으로 가리키는 부위. '흰 (석회) 알갱이'(③ 큐브·제작 주사위·프리베르눔, 그리고 다른 자산에서도 알갱이를 그린 경우), '생석회'(BASIC 더미·폼페이 원료 더미), '물'·'바닷물'(④ 1단계·⑤ 물방울과 웅덩이·해수 수조), '열'(열 물결), '금'(어두운 홈).
- 글이 가리키는 부위가 그림에 **있을 때만** 판정한다. 부위가 아예 없으면 이 루브릭 소관이 아니다(물체 인포그래픽 의미 루브릭이 본다).
- 합격(이름 판정, [운영값]):
  - 흰 = p95 L* ≥ 80 그리고 lit C ≤ 0.05.
  - 물 = h 180~250°, C ≥ 0.03.
  - 열 = h 20~50°, C ≥ 0.08.
  - 금(어두운 홈) = p25 L* ≤ 35.
- 실패 시: **blocker**. 글과 그림이 서로 다른 것을 말하는 의미 오류다(BRIEF §6).
- 근거: OC7(색 이름 모형은 이름 경계로 색을 고르고 평가함), OC3, BRIEF §6.

**[OBJ_COLOR-05] 개념 부위가 개념색 띠 안에 있는가? (그림 언어 일관)**
- 측정: LIME·CRYSTAL·CRACK·WATER-P·HEAT 부위를 잰다.
- 합격:
  - 흰(석회·칼슘·결정·메움) = p95 L* ≥ L*_paper − 2, lit C ≤ 0.04.
  - 금 = p25 L* ≤ 25, 같은 자산 몸체에서 가장 어두운 면의 중앙값보다 10 이상 어둡고, lit C ≤ 0.03.
  - 그림 속 물 = h 195~225°, C ≥ 0.06이고, 지도 물(강·바다) 색상각과의 차 ≤ 15°.
  - 열 = h 30~45°, C ≥ 0.10, ΔE00(lit, #983821) ≥ 10.
- 실패 시: 핵심·DETAIL은 major, 그 밖은 minor. 04에도 걸리면 04로만 낸다.
- 근거: OC8. 포스터에서 가장 넓은 밝은 면은 종이(L* ≈ 90)이고, 이 면이 흰색의 기준이 된다. 그래서 종이보다 어두운 '흰'은 연회색으로 읽힌다. OC3(금 메움과 석회 알갱이는 같은 calcite), `color.md` CL-09·CL-12, D11·D15·D28.

**[OBJ_COLOR-06] 배경 자산의 채도가 가라앉아 있는가?**
- 대상: 역할이 배경인 자산.
- 측정: 부위별 lit C와, 자산 면적으로 가중한 C 중앙값.
- 합격: 모든 부위 C ≤ 0.09, 면적 가중 중앙 C ≤ 0.06, A2 화소 0.
- 실패 시: minor.
- 근거: OC1(Imhof: 강한 채도는 작은 면에만 쓰고 넓은 바탕색은 물러나야 함), D35(밭 C ≤ 0.09), `color.md` CL-03.

**[OBJ_COLOR-07] 개념색이 그 개념이 아닌 곳에 쓰이지 않는가? (개념색 예약)**
- 측정: 단독 크롭에서 개념색 화소 덩이(1pt² 이상)가 그 개념 부위 밖에 있는지 본다.
  - 그림 속 물색 = h 195~225, C ≥ 0.06.
  - 열색 = A2.
  - 석회 흰색 = L* ≥ 95, C ≤ 0.035, h 70~110.
  - 물결(FOAM)과 CORE 표지는 뺀다.
- 합격: 0개.
- 실패 시: 핵심 자산 안이거나 같은 개념 글 상자에서 60pt 안이면 major, 그 밖은 minor.
- 근거: `color.md` S6(같은 체계 안에서 서로 다른 개념은 판별돼야 함), OC6, `color.md` CL-05·CL-07.

## B. 팔레트 일관성

**[OBJ_COLOR-08] 자산의 재질이 팔레트 등록부와 맞는가? (가상 자산 `PALETTE`에서 한 번 판정)**
- 측정: 자산이 쓰는 재질 이름마다, Blender `diffuse_color`와 `palette_part_materials.json`(actual_materials)·`palette_design_tokens.json`의 hex를 비교해 ΔE00를 잰다.
- 합격: 모든 재질이 등록돼 있고 ΔE00 ≤ 1이다. STATE 결정으로 바뀐 값(D24·D26·D29·D30·D35·D36)도 등록부에 반영돼 있다.
- 실패 시: minor. 원인이 등록부 파일이면 `PALETTE`에 1건만 내고 자산마다 세지 않는다(0-10).
- 근거: OC11(디자인 토큰 = 도구 사이에서 디자인 결정을 나누는 단일 형식, 2025.10 첫 안정판), OC9(Workbench가 실제로 칠하는 색은 diffuse_color).

**[OBJ_COLOR-09] 렌더된 부위가 자기 토큰의 색상·채도를 지키는가?**
- 측정: 부위 lit와 그 토큰 diffuse의 Oklch를 비교한다(0-7: 조명은 명도만 바꾼다).
- 합격: 토큰 C ≥ 0.03이면 |Δh| ≤ 3°이고 C 비가 0.8~1.25다. 토큰 C < 0.03이면 lit C < 0.035다. 흰색 클리핑은 26에서 본다.
- 실패 시: minor. 개념 부위가 개념색 띠를 벗어나게 되면 05로 판정한다.
- 근거: 부록 A 보정(v8_13에서 C ≥ 0.03 재질 |Δh| ≤ 1.3°) [보정값], `color.md` S11.

**[OBJ_COLOR-10] 같은 재료는 자산이 달라도 같은 토큰인가?**
- 측정: 0-8 표에서 같은 부류인 부위 쌍(자산이 달라도)의 토큰 diffuse ΔE00와 D(2°). 특히 CORE 사슬의 같은 개념을 본다. ③④⑤·제작 주사위·해수 큐브·BASIC 틀의 RCONC, ③④⑤·제작 원리·BASIC의 LIME(알갱이·칼슘 줄·메움), ①④⑤의 CRACK, ④⑤·해수의 WATER-P.
- 합격: ΔE00 ≤ 3(D ≈ 0.3 이하로 사실상 같은 색)이다. 일부러 다르게 했다면 역할 토큰(0절 결정 목록)이고 D(2°) ≥ 1이거나 STATE 결정 번호가 있어야 한다.
- 불합격('어중간한 차이'): 3 < ΔE00이고, D(2°) < 1이고, 결정 기록도 없다. 같은 재료인데 다른 재료처럼 보일 만큼도 다르지 않고, 같게 보일 만큼도 같지 않다.
- 실패 시: minor. 두 부위가 CORE 사슬의 같은 개념이면 major다.
- 근거: `color.md` S4(Szafir 2018 구별 모형), OC3(고대·현대 시료의 흰 알갱이는 같은 색이고 금 메움은 알갱이와 같은 calcite), `color.md` S6.

**[OBJ_COLOR-11] 같은 토큰이 자산마다 같은 색으로 렌더되는가?**
- 측정: 같은 토큰을 쓰는 자산들의 lit Oklch를 비교한다. 두 자산 모두 카메라 쪽 윗면이 4pt² 이상 보이면 윗면 중앙값도 비교한다.
- 합격: (모두 C ≥ 0.03일 때) Δh ≤ 3°, ΔC ≤ 0.012. 윗면 비교는 ΔE00 ≤ 3.
- 실패 시: minor.
- 근거: `illustration3d.md` I3-01(같은 재질 = 같은 색), `color.md` S4.

**[OBJ_COLOR-12] 한 자산 안에서 같은 재료 부위가 같은 색인가?**
- 측정: 자산 안 같은 부류 부위들의 토큰과, 같은 방향 면끼리의 ΔE00. 예를 들어 수조 벽 4면, 나무 줄기, 다리 난간 두 줄, 큐브 3개.
- 합격: 토큰이 같고, 같은 방향 면끼리 ΔE00 ≤ 2.
- 실패 시: 핵심은 major, 그 밖은 minor.
- 근거: OC12(텍스처-형상 일관성은 3D 자산 평가 기준), `color.md` S4.

**[OBJ_COLOR-13] BASIC 재료 범례의 색이 본문 모형의 같은 재료 색과 맞는가?**
- 측정:
  - (a) BASIC 아이콘 가운데 글이 재료 이름을 붙인 것(생석회 더미 LIME, 화산재 더미 POZZ, 깬 돌·벽돌 STONE·TERRA, 틀 안 굳은 콘크리트 RCONC와 그 알갱이 LIME)과, 본문 모형에서 같은 재료를 그린 부위의 토큰 ΔE00. 본문에 그 재료를 그린 부위가 없으면 해당 없음이다. 거푸집 판처럼 이름이 붙지 않은 부위는 01로만 판정한다.
  - (b) 범례 아이콘끼리의 lit D(0.5°).
- 합격: (a) 같은 재료는 ΔE00 ≤ 3. (b) 서로 다른 재료끼리 D(0.5°) ≥ 1.
- 실패 시: (a)는 major다. 범례와 본문 색이 다르면 범례가 범례 구실을 못 한다. (b)는 모양·이름표로도 구별되므로 minor다.
- 근거: OC6(범례 없이도 색-개념 대응을 추론하므로 같은 대응이 반복돼야 함), `color.md` S6, `color.md` CL-07.

**[OBJ_COLOR-14] 자산 하나의 유채 색상군이 절제돼 있는가?**
- 측정: 4pt² 이상이고 lit C ≥ 0.03인 부위의 색상각을 정렬해, 이웃 차가 15° 이하면 한 군으로 묶는다.
- 합격: 단일 물체는 3군 이하, 사람이 있는 장면은 4군 이하. 밭·길·물·나무 무리 같은 망 자산은 제외한다(D35·D36).
- 실패 시: minor.
- 근거: `color.md` CL-02(포스터 단위 5군 이하), `color.md` S18(색 범주가 많을수록 즉시 구별이 무너짐), OC1.

**[OBJ_COLOR-15] 자산 부위가 포스터 색상군 안에 있는가?**
- 측정: lit C ≥ 0.03인 부위의 색상각.
- 합격: 다음 군 중 하나 안에 있다.
  - 흙·돌·나무: 30~110°.
  - 식생: 105~140°.
  - 물·물결: 160~250°.
  - 현대 슬레이트: 180~260°.
  - 강조: 20~48°. CORE 표지와 열 기호만 쓴다.
- 실패 시: minor.
- 근거: `color.md` CL-01·CL-02(바탕 저채도 한 색상군 + 소수 유채군), OC1.

## C. 강조색 #983821 보호

**[OBJ_COLOR-16] CORE 표지가 아닌 자산 안에 강조색과 혼동되는 화소가 없는가?**
- 측정: 단독 크롭의 자산 마스크 안에서 A1 화소를 센다. 열 기호는 17에서 따로 본다.
- 합격: A1 화소가 3px(2x) 이하다. 안티앨리어싱 잡음 정도만 허용한다.
- 실패 시: major.
- 근거: D2(강조색은 CORE 표지에만), `color.md` CL-05·CL-12, `color.md` S18(고유한 색 특징은 즉시 튀어 시선을 가져감), OC1.

**[OBJ_COLOR-17] 강조 색상군(A2)은 열 기호에만, 정해진 크기 안에서 쓰이는가?**
- 측정: 자산 마스크 안의 A2 화소 덩이.
- 합격: A2 덩이가 '열'을 뜻하는 기호(제작 원리 D2_heat*, 또는 CORE ② 장면의 열 표현)뿐이다. 기호마다 다음을 모두 만족한다.
  - poster_1x에서 A2 화소 ≤ 50. CL-05 예외와 같다.
  - lit ΔE00(#983821) ≥ 10.
  - 기호 안 A1 화소 ≤ 25%(그늘진 가장자리만 허용).
- 실패 시: major.
- 근거: `color.md` CL-05·CL-12, `color.md` S18, `color.md` S4.

**[OBJ_COLOR-18] CORE 표지 자산의 강조색이 지정색대로 렌더되는가?**
- 측정:
  - 번호 원판: 1px 깎은 마스크의 중앙값.
  - 밑줄: 가는 선이므로 가장 진한 30% 화소의 평균.
  - 이정표 화살 판: lit.
- 합격:
  - 원판·밑줄 ΔE00(#983821) ≤ 3.
  - 화살 판 lit ΔE00 ≤ 8, |Δh| ≤ 10°.
  - 화살 판 3개 lit의 서로 간 ΔE00 ≤ 6 [운영값]. 판 방향이 달라 생기는 음영 차를 허용한 값이다.
- 실패 시: minor.
- 근거: `color.md` CL-11, 고정 조건 5·6.

**[OBJ_COLOR-19] 이정표 안에서 강조색이 화살 판에만 있고, 판 앞면은 강조색으로 꽉 차 있는가?**
- 측정: 이정표 자산의 부위별 A2 화소.
- 합격: 기둥·받침·쇠붙이의 A2 화소가 0이고, 화살 판 앞면(카메라 쪽 큰 면)의 A2 비율이 90% 이상이다.
- 실패 시: minor.
- 근거: 고정 조건 6, OC12(텍스처-형상 일관성).

**[OBJ_COLOR-20] 강조 표지가 바로 뒤 바탕과 색으로 갈리는가?**
- 측정: 표지 바깥 2~8pt 고리(맥락 크롭, 글·다른 표지 제외)의 중앙값과 표지 대표값(18의 정의)을 비교한다. WCAG 대비비, 그리고 D(0.5°)를 정상 시각과 세 CVD 모의에서 잰다.
- 합격: WCAG ≥ 3:1이고, 네 조건 모두 D ≥ 1.
- 실패 시: major. R12(②→③ 화살 머리 앞 가장자리와 그 그림자)는 다시 내지 않는다.
- 근거: `color.md` S1(WCAG 1.4.11 비텍스트 3:1), `color.md` CL-22, `color.md` S9(Machado 2009), D36(화살 판과 길 대비 ≥ 3:1).

## D. 부위 색 구분

**[OBJ_COLOR-21] 의미를 가르는 부위 쌍이 색으로 믿을 만하게 구별되는가?**
- 대상 쌍(자산 안):
  - 알갱이/몸체, 금/몸체, 메움/몸체, 메움/금.
  - 물/몸체, 물/수조 벽, 웅덩이/실험대, 결정/콘크리트.
  - 열 기호/바닥, 화살 판/기둥, 사람/바닥, 지붕/벽, 포석/연석.
  - 범례 아이콘끼리는 13에서 본다.
- 측정: 두 부위 lit Lab의 D. 시각 크기는 0-4에 따라 작은 쪽 부위로 고른다.
- 합격: D ≥ 1.
- 실패 시:
  - 색 말고는 구별 단서(모양·위치·글)가 없으면 major, 있으면 minor.
  - CORE 그림의 개념 쌍(알갱이/몸체, 금/몸체, 메움/몸체, 물/몸체)은 단서가 있어도 major다.
- 근거: `color.md` S4, `color.md` CL-21·22, `color.md` S6.

**[OBJ_COLOR-22] 색각이상에서도 21의 부위 쌍이 구별되는가?**
- 측정: 21의 쌍을 protan·deutan·tritan으로 모의(0-6)한 뒤 D를 잰다.
- 합격: 세 모의 모두 D ≥ 1.
- 실패 시: 21과 같은 규칙. 색만으로 구별하면 major, 아니면 minor.
- 근거: `color.md` S9, `color.md` S10(논문 그림의 CVD 접근성 대규모 연구), `color.md` CL-21·22.

## E. 깨끗한 칠

**[OBJ_COLOR-23] 잘못 칠한 면이 없는가?**
- 측정: 재질 ID 크롭과 0-8 표의 부위→부류 대응을 대조한다. ID가 없으면 0-2의 토큰 램프 분류를 쓴다. 표에 없는 재질이나, 다른 부위의 재질로 칠해진 연결 영역 가운데 2pt² 이상인 것을 센다. 의도된 이음매·창·장식은 표에 적힌 것만 인정한다.
- 합격: 0개.
- 실패 시: 핵심은 major, 그 밖은 minor. 다른 재료로 오독하게 하면(물색 땅, 지붕색 벽, 돌색 잎 등) 역할과 관계없이 major다.
- 근거: OC12(GPTEval3D의 텍스처-형상 일관성 기준), OC13(3DGen-Bench 텍스처 품질 차원), OC2.

**[OBJ_COLOR-24] 팔레트 밖의 이물 색 반점이 없는가?**
- 측정: 부위 안쪽(경계 1pt 띠 제외)의 화소마다 그 부위 토큰 램프(0-3)와의 최소 ΔE00를 잰다. 8을 넘는 화소가 이어진 덩이 가운데 1pt²(2x 4px) 이상인 것을 센다.
- 합격: 0개.
- 실패 시: 핵심은 major, 그 밖은 minor.
- 근거: OC2(파노라마 지도에서 "undesired color variations"는 해석을 흐림, Patterson & Kelso 2004 인용). OC9: Material 색 모드는 재질마다 한 색이므로, 램프 밖의 색은 합성·경계 번짐·잘못된 재질에서만 생긴다. 보정: v8_13 정상 부위는 램프 ΔE00 p99 ≤ 4.3 [보정값].

**[OBJ_COLOR-25] 매끈해야 할 면에 얼룩(음영 잡음)이 없는가?**
- 측정:
  1. 선별: 부위 안쪽(경계 1.5pt 제외) 화소 가운데 |L* − 7px(3.5pt) 중앙값 필터| > 6인 비율 S를 잰다.
  2. 확대 검사: S > 2%면 4배 확대해 '얼룩 덩이'를 센다. 얼룩 덩이는 지름 1.5pt 이상(1m에서 약 1.8′, 보이는 크기)이고, 모델링된 모서리·이음매·개구부·기둥 사이와 나란하지 않은 불규칙한 어둡거나 밝은 반점·줄이다.
- 합격:
  - 단순 입체 부위(상자·원기둥·판·더미·받침 윗면·수조·원판): S ≤ 2%.
  - 복잡 부위: 얼룩 덩이가 핵심·DETAIL에서는 0개, 그 밖에서는 3개 이하.
- 실패 시: 핵심(영웅 포함)에서 1개 이상이면 major. DETAIL에서 1개 이상, 또는 배경·SUPPORT·BASIC에서 4개 이상이면 minor.
- 근거:
  - OC2(색 흔들림이 해석을 흐림), `illustration3d.md` I3-03(매끈한 클레이와 같은 추상 수준), OC12.
  - 보정: 매끈한 입체는 S 0.0~0.9%였다. 스캔·생성 메시는 부위에 따라 S 2~36%여서, 이음매·기둥 같은 의도된 디테일과 구별하려고 2단계를 둔다 [보정값].
- 경계: 메시 결함 자체(면 뒤집힘·잡음 정점)는 3D 형태 루브릭이 본다. 이 항목은 그것이 색 얼룩으로 보이는 결과만 판정한다.

**[OBJ_COLOR-26] 흰 재질이 렌더에서 하얗게 잘려(클리핑) 면이 사라지지 않는가?**
- 대상: LIME·CRYSTAL·FOAM 부위 가운데 면적이 100pt² 이상인 것. 알갱이 같은 작은 점은 제외한다.
- 측정: max(R,G,B) ≥ 254인 화소 비율, 그리고 보이는 두 면(윗면·옆면) 중앙값의 ΔL*.
- 합격: 클리핑 ≤ 25%이고 ΔL* ≥ 3.
- 실패 시: minor.
- 근거:
  - OC10(물리적으로 그럴듯한 반사율은 최대 채널 0.032~0.87, 그 위는 빛에 제대로 반응하지 않음).
  - 노출 +0.7 EV(0-7)가 밝은 토큰을 255로 밀어 올리면, 흰 더미가 입체감 없는 납작한 흰 판으로 보인다. 그래도 흰색은 가장 밝게 남겨야 한다(02-a). 해법은 토큰을 조금 낮추는 쪽이다.

**[OBJ_COLOR-27] 자산 경계에 후광·번짐 띠가 없는가?**
- 측정: 실루엣과 재질 경계의 1px(2x) 띠를 본다. 이 띠의 L*가 안쪽 2~4px 중앙값과 바깥 2~4px 중앙값 사이 범위를 5 넘게 벗어나거나, 띠의 색상각이 양쪽 어느 쪽과도 30° 넘게 다르면 후광 화소다.
- 합격: 후광 화소가 경계 길이의 5% 이하다.
- 실패 시: minor.
- 근거: OC2. 보정: v8_13의 오버레이·지도 패스 자산 8개는 경계 띠가 안팎 사이에 있었다(후광 없음) [보정값]. 두 패스 알파 합성(0-7)에서 생길 수 있는 결함을 감시한다.

---

## 판정 기록 형식 (자산마다)
```json
{"asset": "<자산 이름>", "role": "핵심|보조|배경", "grade": "AAA",
 "checks": [{"id": "OBJ_COLOR-05", "pass": true, "value": "p95 L* 94.4 ≥ 87.9", "note": ""}],
 "findings": [{"id": "OBJ_COLOR-xx", "severity": "blocker|major|minor", "title": "...",
   "evidence": "부위·좌표(pt)·측정값", "fix_tool": "blender|figma", "fix": "재질 이름·hex·배율 등 수치 해법"}]}
```
- 해법은 수치로 낸다. 재질 이름, diffuse hex 또는 선형 반사율 배율, 바꿀 부위를 적는다. 해법이 고정 조건이나 결정(0절)을 깨면 안 된다.
- 등록부(08) 지적은 `{"asset": "PALETTE"}`로 1건만 낸다.

## 부록 A. 보정 근거 (v8_13 렌더 실측 · 판정이 아니라 문턱의 근거)
- 장면: `nb_work/out/roman_concrete_narrative_v8_13.blend`. 2x 지도 패스와 오버레이 패스를 합성했다. ID 패스는 0-1의 방식으로 만들었다.
- 렌더 설정: Workbench, Studio `roman_poster.sl`, Standard, 노출 0.7, cavity BOTH(ridge 1.2·valley 1.4), 그림자 0.28·shift 0.1·focus 0.4, AA 8, color_type MATERIAL.
- diffuse와 Principled Base Color가 다른 재질은 8개다(lime_specimen_matrix, concrete, base_terrain, foliage_pale, sect_heavy, tower_foundation·heavy·middle). 그래서 기준 색을 diffuse로 정했다(0-1).
- 색상 보존: C ≥ 0.03이고 안쪽 화소가 200px 이상인 재질은 렌더 밝은 면과 diffuse의 |Δh|가 0.0~1.3°였다(최대는 밭 포도 1.3°). 예외는 255로 잘린 흰 재질(색상각이 85°에서 105°로 이동)과, 폭 1~2px의 가는 선·작은 부위의 안티앨리어싱이다(09·26의 근거).
- 토큰 램프 거리: 부위 10개(판테온 돌·지붕, ④ 몸체, 콜로세움 외벽, ② 반죽, ⑤ 시편, 산, 포석, 화살 판, 잎)의 램프 ΔE00 p50은 0.2~0.4였다. p99는 ⑤ 시편을 뺀 9개가 0.6~4.3이었다. ⑤ 시편은 p99 7.8이고 > 8 화소가 0.72%인데, 금·메움·알갱이와 맞닿은 화소로 보인다(24는 경계 1pt 띠를 빼고 덩이로 센다). 이것이 24의 근거다.
- 얼룩 선별값 S: 큐브·주사위·틀 0.0~0.13%, 원기둥 0.9%, 실험대 0.2%였다. 스캔·생성 모형은 부위에 따라 2~36%였다(콜로세움 7~8%, 판테온 10~29%, 수도교 15%, 등대 17~18%, 인물 장면 9~36%, 산 2~13%). 이것이 25의 2단계 근거다.
- 종이 L*_paper = 89.9(05의 흰 문턱 87.9).
- 강조색: 번호 원판 렌더 중앙값의 ΔE00(#983821) = 0.9다. 화살 판 3개 lit는 ΔE00 2.7~7.5이고, 서로 간 ΔE00는 최대 4.8이다. 열 물결 기호마다 2x A2 화소는 151~155이고 lit ΔE00(#983821)는 17.6~17.8이다(17·18의 근거).

## 출처
표기: [원문] = 원문이나 해당 장을 직접 열어 봄 / [초록] = 초록·서지·요지만 확인 / [2차] = 2차 자료를 거쳐 확인.

| ID | 저자·연도 | 제목·매체 | 이 루브릭에서 쓴 내용 | URL |
|---|---|---|---|---|
| OC1 | Ordnance Survey (n.d.) | Guide to cartography — Colour [원문] | Imhof: 강한 채도는 작은 극단 면에만 쓰고, 큰 면에 나란히 두지 않는다. 바탕색은 더 작고 밝은 면에 자리를 내준다. 물=파랑·식생=초록 같은 지도 관례색 | https://docs.os.uk/more-than-maps/geographic-data-visualisation/guide-to-cartography/colour |
| OC2 | Jenny, H., & Jenny, B. (2013) | Challenges in adapting example-based texture synthesis for panoramic map creation. *Cartography and Geographic Information Science* (doi 10.1080/15230406.2013.795001) [원문] | "excess detail, clouds, shadows, undesired color variations … can be confusing, resulting in a representation that is ambiguous and difficult to interpret"(Patterson & Kelso 2004 인용) | https://mail.colororacle.org/berniejenny/pdf/2013_Jenny_TextureSynthesisForPanoramicMaps.pdf |
| OC3 | Seymour, L. M., Maragh, J., Sabatini, P., Di Tommaso, M., Weaver, J. C., & Masic, A. (2023) | Hot mixing: Mechanistic insights into the durability of ancient Roman concrete. *Science Advances* 9, eadd1602 [원문] | 석회 알갱이는 "distinctive bright white features", "ubiquitous and conspicuous". 고대·현대 시료 모두 "bright white color of the lime clasts". 알갱이는 주로 calcite이고, 재현 시편의 금은 새로 침전한 calcite로 완전히 메워짐 | https://www.science.org/doi/10.1126/sciadv.add1602 |
| OC4 | Witzel, C., & Gegenfurtner, K. R. (2018) | Color perception: Objects, constancy, and categories. *Annual Review of Vision Science* 4, 475–499 [초록] | 색 지각의 주 기능은 물체·재료 식별과 관찰자 사이 소통이다 | https://doi.org/10.1146/annurev-vision-091517-034231 (저장소 https://eprints.soton.ac.uk/438691) |
| OC5 | Tanaka, J., Weiskopf, D., & Williams, P. (2001) | The role of color in high-level vision. *Trends in Cognitive Sciences* 5, 211–215 [초록] | 표면 색이 물체 인식에 영향을 준다(Shape+Surface 모형, 색 진단성) | https://web.uvic.ca/~letsface/vizcoglab/pubPDFs/TiCS_Final_copy.pdf |
| OC6 | Schoenlein, M. A., Campos, J., Lande, K. J., Lessard, L., & Schloss, K. B. (2023) | Unifying effects of direct and relational associations for visual communication. *IEEE TVCG* 29(1), 385–395 [초록] | 사람은 개념-색 직접 연상(예: 바닷물)과 관계 연상을 함께 써서 색-의미 대응을 추론한다 | https://arxiv.org/abs/2209.02782 |
| OC7 | Heer, J., & Stone, M. (2012) | Color naming models for color selection, image editing and palette design. *CHI 2012* [초록] | 색 이름 모형과 이름 기반 거리로 색을 고르고 팔레트를 평가한다(04의 이름 판정 원리) | https://www.tableau.com/research/publications/color-naming-models-color-selection-image-editing-and-palette-design |
| OC8 | Gilchrist, A., et al. (1999) | An anchoring theory of lightness perception. *Psychological Review* 106, 795–834 [2차: Bressan 2006 등] | 한 틀 안에서 가장 높은 휘도가 흰색 기준이 되고, 다른 면의 명도는 그와의 휘도비로 정해진다 | https://research.unipd.it/bitstream/11577/1560501/1/BressanPsychRev.pdf |
| OC9 | Blender Foundation (2026) | Blender 5.2 Manual — Workbench · Color [원문] | Material: "Use the color that can be set per material in the Viewport Display" | https://docs.blender.org/manual/en/latest/render/workbench/color.html |
| OC10 | OpenMoonRay (n.d.) | PBR Validity [원문] | 물리적으로 그럴듯한 albedo(RGB 최대 채널)는 0.032~0.87이고, 채널마다가 아니라 최대 채널로 판정한다 | https://docs.openmoonray.org/user-reference/how-to-guides/pbr-validity/ |
| OC11 | W3C Design Tokens Community Group (2025) | Design Tokens Format Module 2025.10 — first stable version [초록] | 도구 사이에서 디자인 결정을 나누는 벤더 중립 형식, 2025-10-28 첫 안정판 | https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/ |
| OC12 | Wu, T., et al. (2024) | GPT-4V(ision) is a Human-Aligned Evaluator for Text-to-3D Generation. *CVPR 2024* [초록] | 3D 자산 평가 기준에 texture details와 texture-geometry coherency가 들어 있다 | https://openaccess.thecvf.com/content/CVPR2024/papers/Wu_GPT-4Vision_is_a_Human-Aligned_Evaluator_for_Text-to-3D_Generation_CVPR_2024_paper.pdf |
| OC13 | (2025) | 3DGen-Bench: Comprehensive Benchmark Suite for 3D Generative Models. arXiv 2503.21745 [초록] | 형상 그럴듯함과 텍스처 품질을 따로 평가하는 차원 | https://arxiv.org/abs/2503.21745 |
| OC14 | Engineering Rome (n.d.) | The Life and Times of Travertine: From the Quarry to Construction [2차] | 로마 트래버틴은 옅은 노란색이고, 고대에는 노랑·흰 계열을 주로 썼다 | https://engineeringrome.org/the-life-and-times-of-travertine-from-the-quarry-to-construction/ |
| OC15 | British School at Rome (n.d.) | Meet the fellows: Phaedra Criaco [2차] | 로마 교외 가도 포석은 K가 많은 레우시타이트 용암(검은·짙은 회색 용암석) | https://bsr.ac.uk/meet-the-fellows-phaedra-criaco/ |
| OC16 | Marra, F., et al. (earth-prints) / Jackson, M. D., et al. (GSA 2007 초록) | Pozzolane Rosse·Nere·Pozzolanelle 연구 [초록] | 로마 몰탈에 붉은(Pozzolane Rosse)·검은(Pozzolane Nere) 포촐라나를 썼고, 붉은 쪽을 체계적으로 골라 썼다 | https://www.earth-prints.org/bitstream/2122/15177/1/Marra%20et%20al._rev_edit.pdf |
| OC17 | World History Encyclopedia (n.d.) | Pantheon [2차] | 돔 바깥의 청동(금박) 기와는 663년 콘스탄스 2세가 벗겨 갔다 | https://www.worldhistory.org/Pantheon/ |

기존 루브릭에서 같이 쓰는 출처(원 목록 참조):
- `color.md`: S1 WCAG 2.2, S4 Szafir 2018, S6 Mukherjee et al. 2022, S9 Machado et al. 2009, S10 Angerbauer et al. 2022, S11 Ottosson 2020(Oklab), S18 Healey.
- `illustration3d.md`: I3-01·I3-03·I3-04.
- `value.md`: 규약 3(종이 L*), 규약 10(명도 한 단계 ΔL* 10).

- 2022~2026 자료: OC6(2023), OC9(2026), OC11(2025), OC12(2024), OC13(2025), OC3(2023). `color.md` S6(2022)·S10(2022)도 함께 쓴다.
- 로마 재료 색(OC14~17)은 2차 자료다. 그래서 창은 넓게(색상각 25~35° 폭) 잡았다. 판정의 중심은 절대색이 아니라 부류와 명도 순서(01·02)에 둔다. 트래버틴·포석의 CIELAB 실측값을 담은 1차 문헌은 찾지 못했다.
