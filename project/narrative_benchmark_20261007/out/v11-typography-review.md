# 한글 타이포 검토 — 컬러 포스터

2026-10-08. 읽기 전용 Figma 공식 MCP와 현재 실제 1x PNG를 검토했다. 파일 jQPriO85F6wtPy1NPo752p, page 19:4, frame 718:78 (1191 × 1684), native TEXT 95개. 캔버스 변경 및 폰트 설치/다운로드는 하지 않았다.

## 확인한 실제 가용 폰트

`figma.listAvailableFontsAsync()` 직접 조회 결과:
- Noto Serif KR: Black / Bold / ExtraLight / Light / Medium / Regular / SemiBold.
- Noto Sans KR: Black / Bold / DemiLight / Light / Medium / Regular / Thin.
- 대안: Gowun Batang Bold/Regular, KoPub Batang Bold/Light/Regular, NanumMyeongjo Bold/ExtraBold/Regular, Batang Regular, JejuMyeongjo Regular.

Noto Serif KR의 SemiBold는 붙여 쓰는 정확한 style 이름이다. 메인 추천은 Bold이므로 실제 적용 시 `{family: "Noto Serif KR", style: "Bold"}`를 로드한다.

## 추천

제목에만 Noto Serif KR Bold를 쓰고 코어/질문/본문/증거/지도 표기는 Noto Sans KR를 유지한다. 현재 전체가 굵은 산세리프인 상태보다 메인 제목의 인문·건축 분위기를 분리하면서, 재료 제작 과정과 작은 과학 설명은 현재 읽힘을 지킬 수 있다. 고운바탕/손글씨는 소재에 따른 감성은 있지만 과학 설명 지도와 결합했을 때 약하거나 일상적인 분위기가 생길 가능성이 있다. 제목만 다른 계열을 쓸 때 변화 범위와 검증 범위도 작다.

| 역할 | 추천 family / style | size | line height | tracking | 적용 판단 |
|---|---|---:|---:|---:|---|
| 메인 제목 `로마 콘크리트` (718:82) | Noto Serif KR Bold | 70 px | 80 px | −1% | 제목만 교체, 현재455×80 고정영역 유지, 중앙 정렬 |
| 중심 질문 (718:86) | Noto Sans KR Bold | 20 px | 24 px | 0% | 그대로 유지 |
| CORE 1~5 두 줄 제목 | Noto Sans KR Bold | 21 px | 26 px | 0% | 그대로 유지 |
| CORE 본문 | Noto Sans KR Regular | 11.5 px | 15.5 px | 0% | 그대로 유지 |
| 재료 대비 본문 | Noto Sans KR Regular | 10 px | 13.5 px | 0% | 그대로 유지 |
| 사례/증거 제목 | Noto Sans KR Bold | 12 px | 15 px 또는 현행 | 0% | 현행 유지 |
| 작은 사례/증거 본문 | Noto Sans KR Regular | 9.5~10 px | 13~14.5 px 또는 현행 | 0% | 가족·크기·개행 유지, 색으로 대비 보강 |
| 과정 상태 3개 | Noto Sans KR Regular | 10.5 px | 14 px | 0% | 현행 유지 |

제목70px는 현행72px에서 2px 줄여 세리프 교체의 폭/획 높이 차이에 여유를 둔다. 이는 제목 한 줄이 실제로 Figma에서 맞는지 확인하기 전의 보수적 추천이며, 확정 실측값이 아니다. 현재 title node는 textAutoResize=HEIGHT, CENTER/TOP 정렬이며 현재455×80 영역이다. 가로455는 고정이고 높이는 글꼴/개행 변화에 따라 늘 수 있으므로 적용 뒤 height=80을 확인한다. 고정폭/높이만 조회해서는 새 글꼴의 실제 ink bounds나 개행을 입증할 수 없다. 읽기 전용 조건 때문에 시험 노드 생성/기존 제목 임시 교체는 수행하지 않았다. 루트가 복제본에 적용한 다음 실제 native PNG에서 단일 줄, 좌우 margin, 윗획/아랫획 잘림을 확인해야 한다. 제목만 바꾸면95개 문구와 본문 개행은 그대로 유지할 수 있다.

## 색과 결합하는 방식

메인 제목/질문은 따뜻한 먹색으로 두고, 코어 번호·언더라인·제작 핵심 재료에는 대표 강조색을 사용한다. 제목 전체를 진한 테라코타로 채우면 큰 색 면적이 중앙 콜로세움과 경쟁하므로 제목은 어두운 중립색이 유리하다. 작은 본문은 배경과 충분히 벌어지는 짙은 중립색, 사례 메타/지도 지명은 한 단계 약한 색으로 분리한다. 색으로 계층을 만들되 작은 본문을 연한 베이지/저채도 회색으로 낮추지 않는다. 현재처럼 선/번호/글자 모두 한 명도에 몰리지 않도록 한다.

색상 최종값은 루트 배색 역할 팔레트와 통합해야 한다. 본문 색은 산/농경지/밝은 지도 위에서 모두 읽히는지 실제 출력 PNG를 확인한다. 특정 단어만 새로운 색으로 강조하려면95개 문구 전체 유지와 native styled segment 검사를 함께 해야 하므로 이번 범위에서는 역할별 채색이 더 안정적이다.

## 인쇄 크기 해석과 검증

1191×1684는 A 계열 비율이다. A2 세로(420×594 mm)로 출력한다면 가로 환산상 포스터의1px가 약1pt에 대응한다. CORE 본문11.5px는 약11.5pt, 보조9.5~10px는 약9.5~10pt다. 이는 근거리 포스터 읽기 기준으로 해석해야 하며 웹 UI의16px 최소 가이드를 그대로 적용하면 현재 지도 공간과 위계가 망가진다. 멀리서 읽는 것은 메인 질문/코어 제목에 맡기고 세부 내용은 근거리 읽기로 유지한다.

루트 최종 검증: 제목 폰트 교체 전의 현재 styled fonts를 먼저 load; 새 Noto Serif KR Bold를 load; 복제본 제목만 변경; native TEXT95개 및 characters 동일; 질문/본문 auto-layout bounds 및 개행 동일; 실제 PNG에서 제목 잘림과 명도 대비를 확인. 별도 폰트 다운로드, 유료 플러그인 실행, 시험 노드 생성은 필요 없다.
