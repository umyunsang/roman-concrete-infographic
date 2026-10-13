# 건축 해부도·단면도 벤치마크

## 범위와 진행
- 교수 피드백: 중심 콜로세움 그림 바깥 네 상세가 핵심과 연결된 것인지 별도 내용인지 모호하며, 동일한 번호 형식이 의미를 혼동시킴.
- 읽기 전용 조사. 공유 계획·findings·progress는 root 소유. 이 파일만 연구 노트로 작성.
- 원작자/출판사 자료에서 전체→부위→원리 연결, 콜아웃, 위계, 번호 역할을 비교. 실제 이미지 확인과 문서 확인을 구분.
- planning-with-files를 읽음. root의 기존 계획과 검증 범위를 확인함.

## 경험 검색 분류
- MEMORY.md의 과거 로마 건축 A2 작업은 안내만 활용. 과거 Pantheon 중심 범위와 현재 Colosseum 교수 피드백은 `near_match_only`; 현재 캔버스 해석에 과거 배치를 대입하지 않음.
- 메모리 레지스트리는 조사 중 새 항목이 추가되어 기존 절이 96줄 뒤로 이동. 현재 검증한 인용 범위 MEMORY.md:158–169. thread_id 01a0ccb7-d282-72e3-a338-cae714ab9dc2. 현재 canvas와 후속 사용자 지시를 우선함.

## 후보(이미지 검증 대기)
1. National Geographic, A Divine Ambition (Fernando G. Baptista 외, 2022)
   - https://interactives.natgeofe.com/high-touch/ngm-2202-notre-dame-graphics/builds/main/graphics_combined.html
   - 공식 interactive 본문과 credits 확인. 핵심 외부 형태, 힘 전달, 시기별 수정, 복원 공정 등이 연속된 구성. 직접 화면 이미지 확인 전에는 배치 효과를 확정하지 않음.
2. National Geographic Education, Building the Duomo (Fernando G. Baptista)
   - https://education.nationalgeographic.org/resource/duomographic/
   - 공식 publisher 페이지와 원작자 credit 확인. 실제 graphic 확보 대기.
3. John Grimwade, official portfolio
   - https://www.johngrimwade.com/index.html
   - 공식 페이지 15개 슬라이드 링크 확인. Python 요청은 HTTP 465; 웹 도구는 링크를 읽음. 실제 건축 사례 확인 대기.
4. South China Morning Post, The dougong system (Marco Hernandez 외)
   - https://multimedia.scmp.com/culture/article/forbidden-city/architecture/chapter_02.html
   - 원 출판사의 본문과 제작 credit 확인. 전체 코너 구조→결합 부품 설명→지붕 분류. 실제 도면 확인 대기.

## 접근 한계 기록
- /Users/um-yunsang/AGENTS.md는 현재 없으며, 사용자 제공 AGENTS 지침을 적용함.
- John Grimwade 사이트를 Python urllib로 읽는 요청은 HTTP 465. web open은 정상.
- web click으로 NatGeo ai2html의 Image 링크를 여는 요청은 Internal Error. 원 HTML 이미지 경로는 Python으로 읽을 수 있음; 다른 시각 확인 경로를 사용 예정.

## 현재 캔버스 검증 전달(root, 2026-10-02)
- W3 제목: `로마 콘크리트 — 어떻게 2천 년을 버텼을까?`
- 중앙 Colosseum+등각 지형. 굵은 점선 경로의 ①–⑤가 건물을 순환.
- 주변 ① 해수·새 결정, ② lime clasts·hot mixing, ③ 높이별 골재/재료 층, ④ 3단계 균열 치유 그림.
- 동일 검정 원 번호가 경로·상세·근거 지점·타임라인에 반복됨.
- 전달받은 현 캔버스 정보임. 이 조사자는 Figma 화면을 직접 읽지 않음.

## 실제 이미지 관찰 1차
### John Grimwade — Topkapi / In the Sultan's Footsteps
- 원작자 공식 포트폴리오: https://www.johngrimwade.com/index.html
- 실제 확인한 원 이미지: https://www.johngrimwade.com/images/topkapi.jpg
- `view_image`로 전체 원 이미지 확인. 이미지 내부 `GRAPHICS by JOHN GRIMWADE` credit.
- **관찰**: 큰 등각 궁전 지도에 굵은 붉은 화살표 경로. 정류 지점은 흰 숫자의 검정 타원 1–18. 주변에 확대된 문, 장식, 칼, 시계, 의복이 놓임. 상세에는 동일 번호를 다시 붙이지 않고 이름+가는 검정 리더선을 사용하며, 장소에 닿는 끝은 작은 마름모. 상단 왼쪽에 전체 지역 위치 지도.
- **적용(사용자 후속 확인 반영)**: W3의 핵심 경로만 ①–⑤로 두고, 주변 네 상세는 번호 없는 이름으로 표현. 리더선은 실제 건물/지점 대응만 표시하고 화살표 없는 얇은 선으로 경로와 구분. 세부 그림을 주변에 두어도 관계가 명료하면 중심 구도 유지 가능.
- **한계**: 궁전의 실제 방문 동선과 실제 소장 유물의 위치를 설명하는 지도. 로마 콘크리트의 실험·해양 시료를 Colosseum 부위와 직접 동일시하는 근거가 될 수 없음. 원 이미지에서 출판 연도/호는 확인하지 못함.

### National Geographic — Il Duomo / Building the Duomo
- publisher: https://education.nationalgeographic.org/resource/duomographic/
- 실제 확인한 원 이미지: https://images.nationalgeographic.org/image/upload/v1638888401/EducationHub/photos/building-the-duomo.jpg
- 전체 2000×4850 jpg를 `view_image`로 확인. 공식 페이지 credit: Fernando G. Baptista, National Geographic.
- **관찰**: 상단 성당 전체+위치 지도, 그 아래 연대기, 가운데 압도적으로 큰 돔 절개, 하단 `The Construction`의 시공·벽돌·크레인 별도 소도면. `The Design`과 `The Construction` 제목으로 설명 층위 구분. 주 단면의 푸른 구조 부재, 주황 힘 화살표, 검정/흰색 가는 부위 리더선은 서로 다른 기능. 전 페이지를 순환하는 1–n 번호 경로가 없음. 곁 그림은 힘/형태 원리 또는 시공 기술을 보여줌.
- **적용 제안(추론)**: 지형·모델의 해당 위치에 구조 이름/재료·제조/치유 원리의 짧은 제목을 붙이고, 가장 큰 중심 그림이 `어떤 질문의 답인지` 보이게 하기. 원작의 상하 분할은 전용하지 않음. 색을 쓸 경우 실제 재료/구조 대응과 설명용 화살표를 구분하는 의미 부여.
- **한계**: 수직으로 길게 이어진 교육용 원본으로 A2 한 페이지의 동일 밀도를 복사할 수 없음. 건물별 실제 시공 기술 자료이며, Colosseum의 재료 사실을 보증하지 않음.

### National Geographic — A Divine Ambition / Notre-Dame
- publisher: https://interactives.natgeofe.com/high-touch/ngm-2202-notre-dame-graphics/builds/main/graphics_combined.html
- 실제 이미지 확인: `.../ngm-assets/img/ngm-2202-notre-dame-graphics_primary_ai2html-small_or_tablet.jpg`, `.../ngm-assets/img/ngm-2202-notre-dame-graphics_part2_ai2html-small_or_tablet.jpg`
- `view_image`로 역사/구조 base image, 복원 base image를 확인하고 공식 HTML 본문을 읽음. 이미지에는 텍스트가 없으며 텍스트는 HTML overlay. 완전히 렌더링된 화면 전체를 확인한 것은 아님.
- **관찰(이미지)**: 시대별 전체 모습→하중을 주황색 화살표로 보이는 횡단면→복원 중심의 대형 절개가 이어짐. 복원 그림에는 지붕·첨탑을 위로 들어 올린 분해 표현과 점선의 위치 대응, 아래쪽 둥근 재료/손상 상세, 아치 복원의 작은 공정 그림이 있음.
- **문서 확인**: `Gothic Grandeur`, `Compression Forces`, `Roof Re-creation`, `Clues in Stone`, `Restoring the Arches`처럼 제목이 설명 범위/공정을 명시. 일부 부위와 복원 공정에 각각 1–n을 사용하나 스크롤 섹션/제목이 범위를 나눔.
- **적용 제안(추론)**: 실제 부위 확대는 같은 형태/재료 색을 유지하고, 위치를 들어 올리거나 점선으로 대응시키기. 실험/재료 원리는 해당 지형 위의 작은 모델 조각에 `근거/원리` 제목을 붙이고 인접 배치·리더선으로 소속을 나타내기. 원작 스크롤의 상하 구역을 A2에 전용하지 않음.
- **한계**: 이미지+본문만 확인했으며 HTML overlay의 최종 배치/가독성은 미검증. 긴 스크롤에서 번호 재시작이 분명하더라도 단일 A2에 동일 번호를 여러 번 쓰는 선례로 삼으면 안 됨.

## 실제 이미지 관찰 2차 및 최종 5개 선정
### John Grimwade — Grand Central Terminal / Walk This Way
- 원 그래픽 출판: Condé Nast Traveler, 1998. John Grimwade.
- 현재 확인한 출판사 공식 sample PDF(허락받은 재수록+원작자 직접 설명): https://ptgmedia.pearsoncmg.com/images/9780321834737/samplepages/0321834739.pdf
- actual visual: PDF index 51, 책 p.220, Figure 10.4; PDF index 52, 책 p.221, Figure 10.5 초기 스케치. PDF를 내려받아 두 페이지를 렌더링하고 `view_image`로 확인.
- **관찰**: 큰 중앙 절개가 여러 층을 하나의 공간으로 보여줌. 붉은 화살표는 실제 건물 안 이동을 나타냄. 번호는 본문 설명과 건물 내 지점을 같은 대상을 가리키도록 대응. 일반 부위 이름은 가는 리더선+무번호 이름으로 표현. 스케치 단계부터 큰 형태·번호 위치·경로와 본문 영역이 잡혀 있음.
- **적용 제안(추론)**: 반복 번호를 일괄 금지할 이유는 없음. 같은 번호는 `같은 대상`의 cross-reference여야 함. W3의 읽기 단계①과 해수 그림①이 서로 다른 대상이라면 동일 코드를 쓰지 않기. 스케치에서도 본문 작성 전에 코드와 연결 의미를 확정하기.
- **한계**: 원 1998 호 자체를 직접 읽은 것은 아니며, 출판사가 배포한 허락된 재수록/인터뷰를 확인. 공간의 실제 방문 순서를 표현하므로 재료 실험의 인과 순서로 자동 전용 불가.

### WIRED / Bryan Christie Design — Full Circle, Apple Park
- 원 publisher: https://www.wired.com/2017/05/apple-park-new-silicon-valley-campus/
- 원 publisher 실제 이미지: https://media.wired.com/photos/664e40c462bc1a1607ba10bc/master/w_1600,c_limit/06_donut_map.jpeg
- publisher의 1600px 이미지를 내려받아 `view_image`로 확인. 원 기사 `Illustration: Bryan Christie Design` 확인.
- **관찰**: 큰 등각 건물에 숫자 장소 표식. 건물 일부의 `Pathway`, `Ventilation System`은 원형 확대 안에 무번호 제목. 환기 방향만 파랑으로 강조. 주변 소그림도 같은 렌더링/조명 스타일이라 전체와 부위의 동일성 보임.
- **적용 제안(추론)**: 실제 부위 상세는 원형/절개 확대와 부위 이름으로 중앙 그림에 종속시키기. 임의 숫자 순서보다 `어디의 무엇`인지 먼저 명시.
- **한계**: 확대 대상은 해당 건물 부위. 타 지역 시료·실험을 이 형식으로 옮기면 해당 건물에서 직접 확인한 것처럼 보일 수 있음.
- 참고 제작과정(보조 자료): https://www.johngrimwade.com/blog/2017/06/15/apples-new-home/ 와 `.../wp-content/uploads/2017/06/final_wired_large.jpg`도 실제 확인. magazine print와 current web의 번호 개수/매핑이 달라 한 버전의 체계를 섞어 쓰지 않기. 최종 시각 주장과 인용은 원 WIRED 자료에 기반.

## 후보 제외/접근 한계 추가
- SCMP dougong은 웹 검색에서 원 publisher 본문·제작 credit 확인 가능하나, 직접 페이지 접근은 JS WAF 화면으로 대체됨. 이미지 미확인. 최종 추천 5개에는 포함하지 않음. WAF를 우회하지 않음.
- `web screenshot`은 Pearson PDF 이미지 ref만 반환했으므로, 실제 관찰은 내려받은 PDF의 로컬 렌더링으로 수행.
- NatGeo Notre-Dame은 base graphic 두 개와 HTML overlay 본문을 확인했으며 완전 렌더 화면 검증은 없음. 이 제한은 최종 보고에 명시.

## 현 W3에 대한 디자인 결정 근거(제안, 사용자 확정 아님)
1. **읽기 순서와 상세 참조를 분리(사용자 확정)**: 핵심 메시지의 경로만 ①–⑤, 상세는 무번호 제목. timeline은 연도만 사용하고 evidence sites는 고유 지명/표식 사용. 과정 내부는 작은 화살표+짧은 상태 이름, 출처는 지명+저자/연도. `같은 코드=같은 대상`을 전 캔버스에서 유지.
2. **연결선마다 한 의미**: 굵은 화살표/점선은 읽기 방향. 얇은 무화살표 리더선은 건물의 특정 부위→상세 확대. 과정 내부의 짧은 화살표는 변화/원리. 짧은 범례나 관계 문구로 기능 명시.
3. **네 상세를 하나의 종류라고 가정하지 않기**: 구조의 위치/층을 보여주는 상세는 실제 근거 건물과 연결. hot mixing/치유처럼 재료 성질 설명은 `재료 원리`, 해양 사례는 `다른 환경에서 얻은 근거` 등 관계가 드러나는 제목/출처 지점과 묶기. 정확한 분류는 root의 건축 사실 조사에 따라 결정.
4. **주변 배치 자체는 유지 가능**: Topkapi·Duomo·Apple Park 모두 주변 소그림을 사용. 해결 대상은 주변 그림의 존재가 아니라, 어떤 중심 사실을 설명하며 어디서 근거를 얻었는지 보이는 연결 장치와 위계.
5. **스케치 검증 기준**: 독자가 각 상세를 보고 `무엇의 확대/근거인가?`, `어디에서 확인했는가?`, `어떤 번호가 읽기 순서인가?`를 구분할 수 있는지 후속 소규모 독해 확인. 이 조사에서 독해/인쇄 검증은 수행하지 않음.

## 사용자 후속 확정과 공간 주석 문법(root 전달)
- A2 등각/모델 풍경 자체가 레이아웃 기반. core/basic/detail/support는 그 공간 위에 얹음. `근거는 아래/원리는 위` 같은 상하 band나 카드식 구역은 사용하지 않음.
- 핵심 문장은 재료·구조·환경 등 여러 요인의 결합. 숫자 ①–⑤는 core에만 쓰고 detail은 이름만 사용하기로 사용자 확정.
- **장소 앵커**: 근거가 나온 육상/해안/건축 장소를 지형에 표기한 뒤 해당 현상 그림을 가까이 붙임. 공간의 위치와 정보의 출처가 대응.
- **부위 앵커**: 실제 해당 건물에서 검증된 정보만 그 부위→들어 올린 조각/절개 단면으로 가는 선을 연결. 구조 색·방향·면의 형태를 복제해 동일 부위임을 보임.
- **설명 앵커**: 재료 원리는 중심 제목/핵심 문장 또는 검증된 시료 지점에 의미가 명시된 선(`재료 원리`, `다른 환경의 근거`)으로 연결. 설명선을 중심 건물 표면에 직접 꽂아 건물의 측정 사실처럼 보이게 만들지 않음.
- **원근/크기 위계**: 중앙 건물과 핵심 경로가 첫 읽기. 소도면은 주변 지형에 보조 크기·대비로 놓으며 공간 내 실제 부분 또는 증거 장소에 가까이 배치. 위계는 상하 구역 대신 크기·대비·인접·선 역할로 표현.
- **연결선 문법**: core 경로=굵고 방향 있음; 장소/부위 리더=가늘고 방향 없음; 현상 변화=모델 조각 안에 짧은 방향 화살표. 가능하면 교차를 피하고 지형 가장자리/표면을 따라 연결.

## 완료 상태
- 원작자/출판사의 유용한 사례 5개 확보. Topkapi, Duomo, Grand Central, Apple Park는 전체 실제 graphic 확인. Notre-Dame은 실제 base graphic 2개+본문 확인, 완전 화면 배치 미확인.
- 독립 조사 종료. 외부 쓰기와 Figma 호출 없음. 영구 연구 노트는 이 파일만 작성했으며 내려받은 시각 확인 파일은 `/tmp/roman-architecture-benchmarks/`에만 보관.
