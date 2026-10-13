---
name: 203x-awards-source
description: "203 인포그래픽연구소 수상작 원본을 받는 법 — 클라우드 샌드박스는 403, 로컬은 WP REST API로 가능"
metadata:
  node_type: memory
  type: reference
  originSessionId: 8afcd000-d59a-4cb8-859a-e23212e4ca4a
  modified: 2026-09-30T10:57:47.779Z
---

- 203x.co.kr은 **Claude 클라우드 세션 샌드박스에서 이그레스 정책 403**으로 막힌다(웹 가져오기·curl 모두). 로컬 Mac에서는 정상 접속된다 — 203 자료가 필요하면 로컬 세션에서 받는다.
- `/awards` 페이지는 JS로 그려서 HTML에 이미지가 없다. 대신 WordPress REST: `https://203x.co.kr/wp-json/wp/v2/portfolio-item?per_page=100`(총 289건, 제목에 "[어워드]" 34건), 본문 `content.rendered`의 img/srcset에서 `-WxH` 접미사를 지우면 원본.
- 평면 원본 포스터와 확대 컷은 수상 게시물의 Purchase 링크 `street-h.com/product/{id}/` 에 있다(`data-large_image` = 1000×1400 평면 원본, `700_...` = 1.40배 확대 컷 3장). 스토어 검색 `street-h.com/wp-json/wp/v2/product?search=` 로 누락 작품(홍콩·치킨)도 찾음. 실물 크기 **50×70cm** → 1000px 폭 기준 1px = 0.5mm, A2 비례 환산 ×1.191.
- Figma에 이미지를 올릴 때는 `upload_assets`(nodeIds로 자리 지정) 후 각 submitUrl에 `curl -F file=@...` POST. 로컬은 figma.com 접속이 되지만 클라우드 샌드박스는 figma.com도 403이었다.

관련: [[colosseum-poster-mindmap]]
