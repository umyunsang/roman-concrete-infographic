# 에셋 진행 기록

## 2026-10-07 Blender 에셋 워커 (월드맵 v1)
- [시작] ASSET_PLAN.md·concept_v6.png·water/ground.json 확인. Blender 5.2.2, CAM_iso 정사영(ortho 168.4), 렌더 Workbench(film_transparent=True였음 → 렌더 때 끔).
- 지형 해석: water.json Vector_12(241점)는 수도교~콜로세움 서쪽~바다로 이어지는 옛 물길. 계획대로 콜로세움 근처 구간 제거(v≥950만 남김) → 티베르강.
- 땅 도로: ground.json Vector_58(아피아 가도 평행사변형, 세계 X축 방향), Vector_63(왼쪽 길), Vector_70(오른쪽 길).

## A. 공유 에셋 검색 결과 (Sketchfab; Poly Pizza는 MCP 사이드바에서 꺼져 있어 검색 불가, Poly Haven은 사실적 소품 위주라 생략)
| id | 후보(UID 앞 8자) | 라이선스·면수 | 판정 |
|---|---|---|---|
| L01 | Low Poly Mountain Range (dradnon, 1dbb2ab4) | CC-BY, 210만 | 탈락: 정사각 타일 + 둥근 노이즈 언덕, 띠 모양·각진 면과 다름 → 직접 |
| L03 | Temple of Vesta in the Roman Forum (unhvrc, 8bdf295b) | CC-BY, 364만 | **채택**(포로 로마노 실제 신전). 200만 넘어 평면 정리 |
| L03 | Roman Forum (jh0, 22835a0b) | CC-BY, 3.6만 | 탈락: 지도판·사진 판넬 섞인 교육용 장면 |
| L05 | Ruined Aqueduct Arches Segment (s8819296, 4944acab) | CC-BY, 185만 | 탈락: 3아치 2층 파편, 긴 수로 아님 |
| L05 | Aqueduct (martyn169, 50afdf67) | CC-BY, 7천 | 탈락: 2아치 모듈, 디테일이 텍스처뿐(클레이에서 사라짐) |
| L05 | Anio Vetus aqueduct (juanbrualla, 6236383e) | CC-BY, 165만 | 탈락: 숲 지형에 묻힌 사진측량 |
| L05 | Old Aqueduct Across a Mountain Valley / Remains of Roman Bridge | CC-BY | 탈락: 현대식 아치교 / 벽 조각 근접 스캔 |
| L06 | 'roman road paving stones via appia' | — | not_found → 직접 |
| L07 | Volcán Vesubio (rjgarnicap, 523f5d4d) | CC-BY, 108만 | **채택**(실제 베수비오 분화구 사진측량) |
| L07 | Mt. Vesuvius 등 | CC-BY-NC-SA | 라이선스 탈락 |
| L08 | Conimbriga - Roman City Ruins (johnagotinho, ab6d6687) | CC-BY, 534만 | 탈락: 폼페이가 아닌 다른 도시(포르투갈), 풀밭 지형 포함 → 직접 |
| L08 | Pompeii, Italy (ryanfb) | CC-BY-NC | 라이선스 탈락 |
| L09·L13 | 'roman harbor/harbour pier breakwater' | — | not_found → 직접 |
| L04 | 'palatine hill ruins' / 'palatine' | — | not_found(돌 근접 스캔뿐) → 직접 |
| L11 | 'ancient city wall ruins' (Pollença 벽 스캔 등) | CC-BY | 탈락: 근접 벽 스캔, 지도 축척에 안 맞음 → 직접 |
| 실험실 섬 | 'floating island laboratory', 'modern laboratory building' | — | not_found(SF 연구소뿐) → 직접 |
| 가마 | Dryburn Limekiln, Toorlectra 등 | CC-BY/CC0 | 탈락: 19세기 사각 드로 가마, 원통 로마 가마와 다름 → 직접 |
| L02·L10·L12·O04·D1~D4 | 계획서 검색어 '—' | — | 직접 |

## 감독 추가 지시 반영 (작업 중 수신)
1. 글 자리 `sketch_v2/text_zones.json`(15곳) 안에는 물체 금지 — 물체의 화면 경계 상자가 겹치면 안 됨(낮은 땅·논밭·바다·강·도로 포장처럼 높이 ≤0.5 단위인 '낮은 지형'만 허용, 오브젝트에 `low_terrain=True` 표시). 배치 검사는 `scripts/assets/check_zones.py`로 자동화.
2. 물체당 평가 삼각형 기준 **5만 이상**(20만 기준 대체). 산맥·베수비오·수도교·폼페이·항구는 더 정교하게.
3. 색 금지: 가져온 에셋의 재질·텍스처·정점 색·UV 모두 제거. 렌더는 Workbench 흰 단색 그대로.
- 글 자리 때문에 바뀐 목표 화면 상자(계획서 대비):
  - L01 산맥: 제목 띠(v≤252) 아래로만 — 서·중·동 3덩어리로 나눔. 서(0~330, 252~418: DETAIL_1 글 위), 중(330~870, 252~530: CORE_1 위), 동(870~1191, 252~720: CORE_5 위)
  - L07 베수비오: 연표(v≥1584)·폼페이 글(x≤922, v≥1516) 피해서 (925~1191+, ~1370~1580), 연기는 그 위
  - L09·L13 항구: DETAIL_3 글(238~482, 1368~1442)·항구 글(48~312, ≥1526) 피해서 (130~360, 1448~1522)
  - L11 프리베르눔: 프리베르눔 글(v≤1020) 아래로 (985~1177, 1026~1150)
  - 실험실 섬: 실험실 글(v≤1500)·연표(v≥1584) 사이 (552~648, 1503~1580)
  - 가마: CORE_1(v≤667)·CORE_2(v≥738) 사이 (135~175, 672~735)
  - L12 코사 교각: (360~425, 1446~1520)
  - D1 (36~130, 300~412) · D2 (36~130, 900~1042) · D3 (255~345, 1150~1362) · D4 (650~850, 1150~1272)
  - L06 아피아 가도: 포장석은 CORE_4·DETAIL_4 글 자리 밖에만 깔고, 글 자리 안은 낮은 흙길(땅 일부)로 이음
- (추가 지시 2) D1~D4는 공중이 아니라 **땅 위 평야에 놓는 디오라마**로. 자리: D1 (36~120, 340~425), D2 (36~140, 950~1050), D3 (250~460, 1180~1370), D4 (650~860, 1200~1285). 참조 `assets/ref_detail/`. 각 5만 tris 이상, 글 넣지 않음. 위 D 상자 줄은 이 값으로 대체.

## 감독 지시 변경 (우선 적용)
- 공유 에셋을 여러 검색어(영·이)로 공격적으로. 라이선스 확대: 무료 내려받기 가능하면 NC·NC-SA·ND·에디토리얼도 사용(비상업 과제). 유료 우회 금지, Hunyuan 금지. 출처는 계속 ATTRIBUTION.md.
- **직접 모델링은 지형만**(산맥·강·바다·평야·논밭·땅판). 유적·건축물·소품은 못 찾으면 catalog.json `meshy_queue`에 영어 프롬프트로 올리고 자리를 비워 둠.
- 가져온 모델이 5만 tris 미만이면 형태를 해치지 않는 세분/베벨로 보강.
- **콜로세움 교체**: 무너진 실제 콜로세움 모델(남쪽 바깥 고리 무너짐, 가능하면 하이포지움·슈테른 버팀벽)로. 같은 자리(바닥 중심 pt 595,840, 화면 x 294~896, y 580~985), 무너진 쪽을 화면 앞으로. 옛 COL_colosseum·25_COL_INNER는 숨김. 렌더 후 `renders/colosseum_ruined_crop_2x.png`(투명 2배 크롭)와 화면 상자 기록.
- D1~D4는 추상 원리 모형(큐브·층 벽)이라 라이브러리에 없을 것 → 지형처럼 절차 제작 유지(판단, 보고에 명시).
- [L07] Volcán Vesubio 가져옴 → 메시 합침·중복 정점 병합(54만 정점, 108만 tris) → 분화구 중심 기준 원형으로 자르고(반지름 13.3 원 밖 삭제) 가장자리 테이퍼(땅 아래 -1.2로), 높이 과장, 재질·UV·색 제거. 40_REGION, 화면 상자 (925,1340)–(1290,1578) [오른쪽은 프레임 밖], 68.6만 tris.
- [L03] Temple of Vesta(364만) 가져오기 시도 → 'No data received'(통신 끊김) — 재시도 필요.
- [Meshy] 감독이 Meshy 직접 사용을 허가했으나, 이 세션의 Claude Code 권한 분류기가 meshy_client.py 실행(크레딧 소모 = 실거래)을 **거부**함. 우회하지 않음 → Meshy 대상은 catalog.json `meshy_queue`에 프롬프트로 올리고 자리를 비워 둠. 사용자가 권한을 허용하거나 감독이 직접 돌려야 함. 사용 크레딧 0, 호출 0회.
- [L03] Temple of Vesta 가져오기는 실제로 완료돼 있었음 → 합침·중복면 제거(364만→182만: 양면 중복이었음)·떨어진 조각(82정점) 삭제·COLLAPSE 0.25 → 45.5만 tris. 재질·UV·색 제거. 90_STAGING.
- [COL] 콜로세움 후보(Sketchfab 'colosseum' 24건 + 'photogrammetry' 8건): Coliseo, Roma, Italia (rjgarnicap, 9a8b7cfc, CC-BY, 137만, 실제 사진측량 — 남쪽 무너짐·하이포지움·버팀벽 포함), Colosseum, Rome, Italy (CMBC, 535dc96e, CC-BY, 151만, 사진측량), Rome's Colosseum (eyesCloud3D, 4577eb4b, 21만), Colosseum 3d Model (vikyvignesh098, 8732b5c7, 301만, CG 무너진 상태·내부 비어 있음). → rjgarnicap 먼저 가져와 평가.
- [COL] **교체 완료**: rjgarnicap 'Coliseo, Roma, Italia' 사진측량(137만) → 중복 정점 병합 → 콜로세움 타원(중심 0.5,-3 / a 31.9 b 25.6, 원본 단위) 1.035배 밖 삭제 → 87.7만 tris. 재질·UV·색 제거. 회전 z 45°(무너진 남쪽 = 화면 앞), 축척 (0.913, 0.913, 1.038), 위치 (0.528,-0.59,0) → 바닥 중심 화면 (595.1, 846.6), **화면 상자 (293.9, 580.0)–(896.5, 985.1)**. 가장 높은 북쪽 벽 ≈ 16.9 단위(상자 위 580 맞추느라 14보다 조금 높음). 하이포지움·안쪽 고리·동쪽 끝 버팀벽 보임. 옛 COL_colosseum·25_COL_INNER는 숨김(지우지 않음). 20_LANDMARK.
- [COL] 투명 2배 크롭 `renders/colosseum_ruined_crop_2x.png` (1229×834 px) = **화면 pt (287.9, 574.0)–(902.5, 991.1)** (상자 + 여유 6pt). → O04 슈테른 버팀벽은 이 모델에 포함(동쪽 끝 경사 벽)으로 처리.
- [L05] 추가 검색('acquedotto', 'roman aqueduct' 20건): Rome - Aquaduct Park(Crazymaverickdc, NC-SA, 52만) 가져와 봤으나 아치가 안 보이는 뭉개진 스캔 → 삭제. **dinael 'Roman Aqueduct - No Extra Assets'(CC-BY, 9.7천) 채택** → 베벨 4단(각도 제한)으로 6.6만 tris, z 1.8배, 세계 y축 방향. 화면 상자 (796.1,340.8)–(1012.9,534.2) 목표 (797,340,1012,535) 오차 ≤1.2pt. 40_REGION.
- [감독] Figma 레이아웃 변경 통보: L06 아피아 가도 → 오른쪽 위(콜로세움 동북 (860,610) → (1191,~560)), L11 프리베르눔 → 오른쪽 위(900~1170, 560~760), CORE ❶ → 콜로세움 위 가운데(x≈595, y≈380~470), ❸❹ 콜로세움 아래 대칭, 오른쪽 아래(712~1200 × 1000~1310)는 평야/논밭. → L06·L11 최종 배치와 글 자리 검사는 text_zones.json 갱신까지 보류. 산맥 가운데 덩어리도 새 ❶ 자리 때문에 바뀔 수 있어 스크립트를 매개변수식으로 짬.
- [L08] 추가 검색('roman city', 'pompeii house', 'ancient rome diorama', 'roman town ruins houses', 'pompei scavi'): 후보 The ancient city diorama(agung.ihackstuff, CC-BY, 269만, 지붕 있는 로마풍 마을 — 79년 공사 중 폼페이에 맞음), Carnuntum(사진측량, 나무 많음), Roman City models(BunburysGhost, 3.4만, 단순 상자). → ancient city diorama 가져오는 중(통신 끊김, Blender 작업 중).
- [감독 정정] L06·L11 새 자리는 CORE ❹와 ❺ 사이(콜로세움 오른쪽 아래 4~5시, 대략 x 840~1100 · y 900~1060, 가도는 프레임 오른쪽으로). 최종 좌표 확정까지 보류.
- [감독] text_zones.json 확정본(Figma 607:78, 22곳 + objects 7) 반영. 바뀐 목표 화면 상자:
  - L07 베수비오: 지명 '화산'(1012~1052, 1352~1380)·'폼페이'(917~965, 1478~1511) 피해서 → x ≥ 969, v 1384~1580 으로 다시 맞춤 예정(지금 925~1290 × 1340~1578은 겹침)
  - D1~D4 objects 상자가 DETAIL 글 자리와 4~5pt 겹쳐 있어 아래쪽을 6pt씩 줄여 맞춤: D1 (36,360,127,398), D2 (36,960,141,1021), D3 (250,1199,317,1329), D4 (656,1220,812,1265)
  - L08 폼페이 (800~912, 1395~1530), 가마 (120~180, 640~735), L03 베스타 (190~290, 600~735), 실험실 섬 (530~650, 1512~1580), L11 (908,955,1100,1097), L06 길 띠 (760,923,1191,949: 낮은 포장 → 글 자리 허용)
  - 산맥: W1 x[-20,171] v[256,350](D1 앞 평야 확보), W2 x[186,510] v[285,540](지명 '아펜니노' 아래), C x[470,740] v[256,370](❶ 위), E x[690,1211] v[256,531](지명 '수도교' 위, 수도교 발자국은 골짜기로 비움)
- check_zones.py 작성: text_zones.json을 매번 읽고, 렌더 보이는 메시의 평가 꼭짓점 화면 상자로 겹침·5만 미만 검사 → assets/zone_check.json.
- Blender가 ancient city diorama(269만) 가져오기로 30분 넘게 CPU 100% — 대기 중 지형 스크립트(terrain_polys.py, terrain.py) 작성.
