# 인쇄 사양 · 로마 콘크리트 A2 포스터 (v8_14 · 리허설)

이번 판은 파이프라인 리허설입니다. 디자인이 수렴하면 아래 '다시 만드는 법'의 명령으로 같은 파일을 다시 만듭니다. v8_12 결과물은 `archive_v8_12/`에 있습니다.

## 인쇄소에 넘길 파일
`로마콘크리트_A2_재단3mm_인쇄원고_PDFX4_CMYK.pdf` (23.1MB)

- **규격:** PDF/X-4 (PDF 1.6), 출력 조건 PSO Coated v3 (FOGRA51). OutputIntent에 ICC 프로파일이 들어 있습니다.
- **색:** 이미 CMYK로 분판했습니다. RGB나 별색은 없습니다.
  - 변환 조건: 상대 색도, 검정점 보정(BPC) 끔, Ghostscript 10.07 + lcms2.
  - 인쇄소 RIP이 다시 변환하지 않게 해 주세요(CMYK 그대로 출력).
- **크기:**
  - 문서(MediaBox = BleedBox): 1208×1701pt = 426×600mm.
  - **재단(TrimBox): A2**, 사방 재단 여분 3mm(8.5pt). TrimBox는 1191×1684pt = 420.16×594.08mm로, Figma 디자인 프레임 790:78의 크기 그대로입니다. ISO A2(420×594mm)보다 가로 0.16mm, 세로 0.08mm 크고, ISO 216 허용 범위(±2mm) 안입니다.
- **투명:** 없음(Figma가 붙인, 전부 불투명한 알파 마스크도 뺐습니다).
- **배경 지도:**
  - Blender 렌더 v8_14, 5033×7087px. A2 실제 크기에서 300ppi입니다.
  - Figma 인쇄 프레임에는 한 장 4096px 제한 때문에 2×2 조각으로 올립니다. 인쇄 원고에는 Figma가 다시 압축한 조각 대신, 같은 렌더 원본을 **한 장**으로 넣었습니다. 그래서 조각 경계가 없습니다.
    - v8_12까지는 조각 4장의 클립 경계가 맞닿아 있었습니다. 인쇄에는 틈이 없었지만, 화면 뷰어는 안티앨리어싱 때문에 x 604pt에 옅은 밝은 세로선을 보였습니다(poppler 72dpi에서 +8 회색 단계).
  - 이 픽셀을 CMYK로 바꾼 뒤 JPEG 4:4:4:4로 저장했습니다. 양자화 표 평균은 8.7, 최댓값은 18입니다.
  - 재단선 안 그림은 v8_14 렌더와 같습니다. 화소 100만 개 표본에서 잰 ΔE00(PSO Coated v3, 상대 색도)은 다음과 같습니다.
    - 색역 손실을 포함하면 중앙값 0.55, p95 1.24, p99 1.74입니다.
    - 렌더를 같은 조건으로 분판한 값과 비교하면(JPEG·분판 오차만) 중앙값 0.55, p99 1.64입니다.
    - v8_12에서 바뀐 화소 218만 개에서는 v8_14와의 차이가 0.54, v8_12와의 차이가 14.2입니다.
  - **총잉크량:** 이 프로파일의 분판 최대는 300%입니다(검정 = C84.5 M68.0 Y51.5 K96.0). 0.5mm 넓이 평균의 최댓값은 300.2%입니다. JPEG 잡음 때문에 화소 0.0087%만 낱개로 300%를 넘습니다(최대 309%).
- **재단 여분 가장자리:** 렌더 가장자리의 지형 끝 띠는, 바로 안쪽 띠를 거울처럼 뒤집어 덮었습니다.
  - 위 12px: 재단선 밖 **1.98mm**부터 종이 끝(3.0mm)까지입니다.
  - 오른쪽 16px: 재단선 밖 **1.64mm**부터 종이 끝까지입니다.
  - 재단 오차가 ±1mm 안이면 두 띠는 모두 잘려 나갑니다. 남는 여유는 오른쪽 0.64mm, 위 0.98mm입니다.
  - 왼쪽 끝 12px(재단선 밖 1.98mm부터)는 지형 끝이 약간 밝습니다(휘도 +5~10). 같은 이유로 잘려 나가므로 그대로 두었습니다.
  - 렌더 범위를 넓히면 지형 가장자리가 더 드러나므로 그 방법은 쓰지 않았습니다.
- **글:**
  - 모든 글자는 채운 벡터 윤곽입니다. 글꼴은 0개라 인쇄소에 Noto 글꼴이 없어도 됩니다.
  - Figma가 넣은 보이지 않는 검색용 글자층(Type3)은 인쇄 원고에서 뺐습니다. 검색 가능한 판은 아래 화면용 PDF입니다.
  - 인쇄 프레임 810:78의 글 83개는 디자인 프레임 790:78의 글과 같습니다(내용·크기·글꼴·색·회전이 같고, 위치만 +8.5pt 옮김).
- **안전 영역:** 가장 바깥 글의 잉크는 재단선에서 다음만큼 안쪽에 있습니다. 기준은 6.35mm 이상입니다.
  - 오른쪽 7.6mm: '콜로세움 · 로마 · 서기 80년'
  - 아래 8.5mm: '새 광물 결정이 자람'
  - 왼쪽 8.5mm: '제작 원리 · 열과 석회'
  - 위 9.1mm: '전제 · 로마 콘크리트란?', '전제 · 어떻게 알았나'

## 분판 결과(벡터 색)

| 요소 | 화면 hex | 파일 안 CMYK |
|---|---|---|
| CORE 강조색(제목 둘째 줄·번호 원판·밑줄) | #983821 | C8 M85 Y99 K39 |
| ④ 단계 라벨 '물이 스밈' | #1B5760 | C85 M31 Y35 K52 |
| ④ 단계 라벨 '칼슘 이동'·'결정이 메움' | #8A5427 | C16 M61 Y91 K46 |
| 진한 글·지시선(본문·바다 위 글) | #2E2A22 | C0 M30 Y50 K100 (K 위주, ΔE00 0.96) |
| 땅 위 SUPPORT 글·지시선 | #3E3A31 | C0 M15 Y30 K92 (K 위주, ΔE00 0.60) |
| 보조 글(머리말·지명) | #59524A | C0 M15 Y20 K82 (K 위주, ΔE00 0.90) |

- 작은 진한 글은 4색 검정 대신 K 위주 3판으로 바꿨습니다. 판이 조금 어긋나도 글이 번지지 않게 하려는 것입니다(총잉크량 117~180%).
- 이정표 화살표 판(#8F3722·#7E2F1C 계열)은 그림 픽셀입니다. 그래서 그림과 같은 조건(상대 색도·BPC 끔)으로 분판했습니다.
- 벡터 채움 색 8종과 각 색의 채움 횟수는 v8_12와 같습니다.

**인쇄 모의(PSO Coated v3, 상대 색도) 뒤 ④ 라벨 대비:** '물이 스밈' 6.8:1, '칼슘 이동' 5.3:1, '결정이 메움' 5.3:1입니다. 모두 10.5pt 글 기준인 4.5:1을 넘습니다(v8_12에서 잰 값이고, 색은 바뀌지 않았습니다).

## 화면·공유용
`로마콘크리트_A2_재단3mm_화면용_RGB.pdf` (10.0MB, sRGB)는 인쇄에 쓰지 마세요.

- **보이는 크기:** CropBox와 TrimBox를 A2 재단선(사방 8.5pt 안쪽, 1191×1684pt)에 두었습니다. 그래서 뷰어에서는 재단 여분 없이 A2 크기로 보입니다(pdfinfo: 'Page size 1191 x 1684 pts (A2)'). 재단 여분은 파일 안(MediaBox = BleedBox)에 그대로 남아 있습니다.
- **배경:** Figma가 내보낸 조각 4장을 화소 단위로 이어 붙여 한 장으로 다시 넣었습니다(JPEG 품질 94, 4:4:4). 그래서 조각 경계선이 보이지 않습니다. Figma 조각과의 평균 차이는 0.8/255입니다.
- **글:** 검색과 복사가 됩니다. 보이지 않는 검색용 글자층은 Figma 내보내기와 똑같습니다.

## 다시 만드는 법
`W=/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work`. 아래 `<tag>`는 새 판(예: v8_15), `<prev>`는 바로 앞 판입니다.

```sh
# 1 렌더 + 2 조각 (blend는 읽기만 하고, 렌더 앞뒤 SHA-256이 같아야 계속 진행)
$W/scripts/build_print_master.sh <tag> $W/out/roman_concrete_narrative_<tag>.blend prepare
# 3-0 (수동, Figma MCP, 읽기 전용) use_figma에 $W/scripts/figma_check_print_frame.js → diffs = [] 이어야 함
# 3   (수동, Figma MCP) upload_assets(fileKey jQPriO85F6wtPy1NPo752p, count 4, nodeIds [810:187, 810:186, 810:185, 810:184], scaleMode FILL, currentPageId 19:4)
#     → prepare가 출력한 curl 4줄을 submitUrl 1~4에 실행 → figma_check_print_frame.js를 다시 돌려 imageHash = 조각 SHA-1인지 확인
# 4   (수동, Figma MCP) download_assets(fileKey jQPriO85F6wtPy1NPo752p, nodeId 810:78, defaultFormat pdf) → export.url (몇 분 안에 쓸 것)
# 4 받기 + 5 PDF/X-4 + 화면용 PDF + 검증 15항목 (앞 판의 두 결과물은 archive_<prev>/로 옮긴 뒤 덮어씀)
$W/scripts/build_print_master.sh <tag> $W/out/roman_concrete_narrative_<tag>.blend finish "<export.url>" <prev>
```

단계별 명령(스크립트가 실제로 부르는 것과 같음, `PY="uv run --no-project --with pillow --with numpy --with pypdf python -I"`):

1. `/Applications/Blender.app/Contents/MacOS/Blender -b $W/out/roman_concrete_narrative_<tag>.blend --factory-startup --python $W/scripts/render_print_bleed.py -- <tag>`
2. `$PY $W/scripts/compose_print_tiles_v2.py <tag>`
3. 위의 Figma 수동 단계를 따릅니다.
4. `curl -sSL -o $W/out/print/figma_export_<tag>.pdf "<export.url>"`
5. `$PY $W/scripts/make_print_pdfx.py $W/out/print/figma_export_<tag>.pdf $W/out/print/<tag>_map_print_bleed_5033x7087.png $W/out/print/PSOcoated_v3.icc $W/out/print/PDFX_def_PSOv3.ps $W/out/print/로마콘크리트_A2_재단3mm_인쇄원고_PDFX4_CMYK.pdf`
6. `$PY $W/scripts/make_screen_pdf.py $W/out/print/figma_export_<tag>.pdf $W/out/print/로마콘크리트_A2_재단3mm_화면용_RGB.pdf`
7. 검증: `$PY $W/scripts/verify_print_master.py <tag> --prev-tag <prev>`
   - 결과는 `check_<tag>/verify_<tag>.json`에 쓰입니다.
   - 300ppi 소프트프루프 크롭(`crop300_*.png`, 재단선은 자홍색 1px)도 같은 폴더에 생깁니다.
