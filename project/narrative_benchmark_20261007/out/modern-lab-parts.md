# 현대 골조와 실험실 부위 배색 선정

상태: manifest 완료. 원본 v7를 새로 열어 polygon-index 함수와 감사 PNG의 선정을 대조했다. 제작 파일·UI·재질·면 인덱스·형상·변환·가시성을 변경하거나 저장·렌더하지 않았다. PNG는 추출한 실제 면 좌표를 PIL painter projection으로 그린 부위 감사 그림이며 production Workbench 렌더가 아니다.

## 전달 API

`modern_lab_parts.py`의 `build_assignments(bpy)`는 `{objectName: {default, faces: {role: [original polygon indices]}, notes}}`를 반환한다. 재질과 sRGB→linear 변환은 root가 수행한다. `modern-lab-polygon-assignments.json`은 동일 함수의 fresh Blender 반환값과 소스 SHA를 담는다.

## 선정과 수량

| 객체 | 역할 | sRGB 제안 | 원본 면 수 |
|---|---|---|---:|
| NB_modern_building | concrete (기본) | #B9BEC0 | 22,290 |
| NB_modern_building | steel | #344E5A | 2,685 |
| S_lab_island | labstone (기본) | #B9C7C5 | 831 |
| S_lab_island | roof | #527882 | 101 |
| S_lab_island | glass | #3F9DAA | 303 |
| S_lab_island | base | #9FACA6 | 5,548 |

현대 골조는 굵은 코너 기둥과 바닥 보를 콘크리트로 두고, 짧은 양 측면 중앙 및 전면 작은 노출 cage/bar 형태만 짙은 금속색으로 골랐다. 바닥 보가 가로지르는 높이 구간은 금속 영역에서 제외해 보 전체를 임의로 철골로 칠하지 않는다. 모델은 스타일화되어 있으며 부위 소재의 실물 판독을 주장하지 않는다.

실험실은 거친 섬/기단 및 주변 설비를 기초색, 건물 벽·기둥을 밝은 벽체색, 실제 상단 roof deck(z 약9.45)을 지붕색으로 골랐다. 창호색은 외곽 기둥·cornice 뒤로 들어간 평평한 사각 패널만 대상으로 한다. 원래 유리 재질이 존재했던 것을 복원한 작업이 아니라, 기존 창 모양 recess에 유리색 역할을 부여한 디자인이다. 하층 패널은 생성 메시의 불규칙한 베벨 형상을 유지하며 4면의 패널을 구분했다.

## 실제 근거

- `modern-geometry-four-views.png`: 현재 modern 메시의 실제 형상을 여러 방향에서 투영.
- `lab-geometry-four-views.png`: 현재 laboratory 메시의 실제 형상을 여러 방향에서 투영.
- `modern-lab-part-audit.png`: 각 면 배색 선정의 두 방향 검토. 현대의 노출 얇은 cage와 실험실의 wall/roof/panel/base를 확인했다.
- modern 원본 연결 성분 4,240개는 seam 정점 분리에 의한 조각이다. 좌표를 읽기상으로만 소수6자리로 묶으면 한 연결체라서 연결 성분을 부품으로 단정할 수 없다. 실제 mesh vertex/edge에는 아무 weld도 수행하지 않았다.
- lab은 주 연결체 하나와 작은 잔여 삼각형 두 면으로 구성된다. 역시 부품별 독립 객체/성분이 존재한다고 가정하지 않았다.
- 원본 topology 기대값은 modern 28,609정점/24,975면, lab 4,851정점/6,783면. 함수가 다른 topology에서는 사용을 거부한다. root가 v7 원본의 geometry fingerprint 보존을 추가 검증한다.

## 점검 기록

1. 원본 geometry 추출과 연결 성분 분석 완료.
2. 실제 다각형 좌표로 네 방향 감사 그림을 생성하고 선정 영역을 구체화.
3. 두 방향 배색 감사에서 bar/beam 구분 및 4면 창 recess 적용을 확인.
4. fresh v7에서 build_assignments 함수의 면 인덱스가 감사 그림에 사용한 인덱스와 정확히 같음을 확인.

첫 그림 생성 시 시스템 Python에 matplotlib이 없어 실패했다. 설치하지 않고 기존 PIL과 NumPy로 실제 다각형 투영 그림을 생성했다. root가 최종 Workbench MATERIAL 저장본과 포스터에서 재질·가독성을 검토한다. 이 분기는 그 최종 QA를 선행했다고 주장하지 않는다.
