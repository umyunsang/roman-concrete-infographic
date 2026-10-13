#!/usr/bin/env bash
# Roman concrete A2 poster: print master (PDF/X-4 CMYK) + screen/sharing PDF (sRGB, A2 trim view).
#
#   build_print_master.sh <tag> <blend> prepare                                  # 1 Blender render + 2 tiles, then prints manual step 3/4
#   (manual 3 = Figma upload of the 4 tiles, manual 4 = download_assets 810:78 as PDF; both are MCP tools)
#   build_print_master.sh <tag> <blend> finish <figma-pdf-url-or-path> [prev-tag] # 4 fetch + 5 PDF/X-4 + screen PDF + verify
#   build_print_master.sh <tag> <blend> verify [prev-tag]                         # checks only
#
# The blend file is only read (Blender -b, nothing saved); its SHA-256 must be the same before and after the render.
# Final files are overwritten; if they belong to another tag (out/print/final_tag.txt) they move to out/print/archive_<that tag>/ first.
set -euo pipefail
[[ $# -ge 3 ]] || { sed -n '2,10p' "$0"; exit 2; }
TAG=$1; BLEND=$2; STAGE=$3
W=$(cd "$(dirname "$0")/.." && pwd)
P=$W/out/print; CHK=$P/check_$TAG; mkdir -p "$CHK"
BLENDER=/Applications/Blender.app/Contents/MacOS/Blender
PY=(uv run --no-project --with pillow --with numpy --with pypdf python -I)
PRINT_PDF="$P/로마콘크리트_A2_재단3mm_인쇄원고_PDFX4_CMYK.pdf"
SCREEN_PDF="$P/로마콘크리트_A2_재단3mm_화면용_RGB.pdf"
FIGMA_PDF=$P/figma_export_$TAG.pdf
FILEKEY=jQPriO85F6wtPy1NPo752p
NODES=(810:187 810:186 810:185 810:184); TILES=(r0c0 r0c1 r1c0 r1c1)

case $STAGE in
prepare)
  [[ -f $BLEND ]] || { echo "no blend: $BLEND"; exit 1; }
  before=$(shasum -a 256 "$BLEND" | cut -d' ' -f1)
  echo "[1] Blender render 5033x7087 (300 ppi, 3 mm bleed) -> renders/${TAG}_print_bleed_{map,overlay}_pass.png"
  "$BLENDER" -b "$BLEND" --factory-startup --python "$W/scripts/render_print_bleed.py" -- "$TAG" > "$CHK/render_$TAG.log" 2>&1
  grep -q '^RENDER ' "$CHK/render_$TAG.log" || { tail -20 "$CHK/render_$TAG.log"; exit 1; }
  after=$(shasum -a 256 "$BLEND" | cut -d' ' -f1)
  [[ $before == "$after" ]] || { echo "blend changed during the render ($before -> $after): rerun"; exit 1; }
  echo "$before  $BLEND" > "$CHK/blend_sha256.txt"
  echo "[2] compose + edge mirror (top 12 / right 16 px) + 2x2 tiles"
  "${PY[@]}" "$W/scripts/compose_print_tiles_v2.py" "$TAG" > "$CHK/compose_$TAG.json"
  echo
  echo "[3] MANUAL (Figma MCP): upload_assets(fileKey=$FILEKEY, count=4, nodeIds=[\"${NODES[0]}\",\"${NODES[1]}\",\"${NODES[2]}\",\"${NODES[3]}\"], scaleMode=FILL, currentPageId=19:4)"
  echo "    then POST each tile to its submitUrl, in this order:"
  for i in 0 1 2 3; do
    f=$P/${TAG}_tile_${TILES[$i]}.jpg
    echo "    curl -sS -X POST -F \"file=@$f;type=image/jpeg\" \"<submitUrl $((i + 1))>\"   # -> ${NODES[$i]}, expect imageHash $(shasum "$f" | cut -d' ' -f1)"
  done
  echo "[4] MANUAL (Figma MCP): download_assets(fileKey=$FILEKEY, nodeId=810:78, defaultFormat=pdf) -> export.url (short-lived)"
  echo "    then: $0 $TAG $BLEND finish \"<export.url>\" [prev-tag]"
  ;;
finish)
  SRC=${4:?figma pdf url or path}; PREV=${5:-}
  echo "[4] Figma PDF -> $FIGMA_PDF"
  if [[ $SRC == http* ]]; then curl -sSL -o "$FIGMA_PDF" "$SRC"; elif [[ $SRC != "$FIGMA_PDF" ]]; then cp "$SRC" "$FIGMA_PDF"; fi
  head -c 5 "$FIGMA_PDF" | grep -q '%PDF-' || { echo "not a PDF: $FIGMA_PDF"; exit 1; }
  "${PY[@]}" "$W/scripts/verify_print_master.py" "$TAG" --figma-only || { echo "Figma frame 810:78 does not carry the $TAG tiles: redo step 3"; exit 1; }
  OLD=$(cat "$P/final_tag.txt" 2>/dev/null || true)
  if [[ -f $PRINT_PDF || -f $SCREEN_PDF ]] && [[ $OLD != "$TAG" ]]; then
    [[ -n $OLD ]] || { echo "final PDFs exist but out/print/final_tag.txt is missing: archive them by hand"; exit 1; }
    A=$P/archive_$OLD; mkdir -p "$A"
    for f in "$PRINT_PDF" "$SCREEN_PDF"; do
      [[ -f $f ]] || continue
      [[ ! -e $A/$(basename "$f") ]] || { echo "already archived: $A/$(basename "$f")"; exit 1; }
      mv "$f" "$A/"
    done
    echo "    archived the $OLD finals -> $A/"
  fi
  echo "[5] PDF/X-4 CMYK (PSO Coated v3, relative, no BPC)"
  "${PY[@]}" "$W/scripts/make_print_pdfx.py" "$FIGMA_PDF" "$P/${TAG}_map_print_bleed_5033x7087.png" "$P/PSOcoated_v3.icc" "$P/PDFX_def_PSOv3.ps" "$PRINT_PDF" > "$CHK/make_print_pdfx_$TAG.json"
  echo "[5b] screen PDF (TrimBox = CropBox = A2 trim)"
  "${PY[@]}" "$W/scripts/make_screen_pdf.py" "$FIGMA_PDF" "$SCREEN_PDF" > "$CHK/make_screen_pdf_$TAG.json"
  echo "$TAG" > "$P/final_tag.txt"
  echo "[check]"
  "${PY[@]}" "$W/scripts/verify_print_master.py" "$TAG" ${PREV:+--prev-tag "$PREV"}
  ;;
verify)
  PREV=${4:-}
  "${PY[@]}" "$W/scripts/verify_print_master.py" "$TAG" ${PREV:+--prev-tag "$PREV"}
  ;;
*) sed -n '2,10p' "$0"; exit 2 ;;
esac
