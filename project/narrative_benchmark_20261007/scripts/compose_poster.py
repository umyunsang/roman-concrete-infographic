"""Pad and alpha-compose Blender map/overlay plus Figma text into a new draft.

python3 compose_poster.py --map map.png --overlay shapes.png --text text_rgba.png \
  --output-dir ../out
--check-only reads dimensions without creating output files.
"""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path

from PIL import Image

DRAFT_ROOT = Path(__file__).resolve().parents[1]
TARGET_SIZE = (2382, 3368)
A2_MM = (420.0, 594.0)


def load_rgba(path, require_alpha=False):
    with Image.open(path) as image:
        if require_alpha and 'A' not in image.getbands() and 'transparency' not in image.info:
            raise ValueError(f'An alpha-bearing overlay is required: {path}')
        return image.convert('RGBA')


def pad_right_bottom(image, target, background):
    dx, dy = target[0] - image.width, target[1] - image.height
    if dx not in (0, 1) or dy not in (0, 1):
        raise ValueError(f'Only zero/one-pixel right-bottom padding is allowed: {image.size} -> {target}')
    canvas = Image.new('RGBA', target, background)
    canvas.alpha_composite(image, (0, 0))
    return canvas, {'right_px': dx, 'bottom_px': dy}


def write_a2_pdf(image, output):
    try:
        import pymupdf as pdf
    except ImportError:
        import fitz as pdf
    png = io.BytesIO()
    image.save(png, format='PNG')
    width, height = (millimeters / 25.4 * 72.0 for millimeters in A2_MM)
    doc = pdf.open()
    try:
        page = doc.new_page(width=width, height=height)
        page.insert_image(page.rect, stream=png.getvalue(), keep_proportion=False)
        doc.set_metadata({'title': '로마 콘크리트 인포그래픽 — 서사 개정안',
                          'subject': 'A2 portrait, 420 x 594 mm'})
        doc.save(str(output), garbage=4, deflate=True)
    finally:
        doc.close()
    with pdf.open(str(output)) as verification:
        if len(verification) != 1:
            raise RuntimeError('The A2 PDF must contain exactly one page')
        rect = verification[0].rect
        got = [rect.width / 72.0 * 25.4, rect.height / 72.0 * 25.4]
        if any(abs(actual - expected) > 0.01 for actual, expected in zip(got, A2_MM)):
            raise RuntimeError(f'Unexpected PDF page dimensions: {got}')
    return got


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--map', required=True, dest='map_path')
    parser.add_argument('--overlay', required=True)
    parser.add_argument('--text', required=True)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    paths = {key: Path(value).expanduser().resolve() for key, value in
             [('map', args.map_path), ('overlay', args.overlay), ('text', args.text)]}
    out = Path(args.output_dir).expanduser().resolve()
    if not out.is_relative_to(DRAFT_ROOT):
        raise ValueError('Output must remain in the new narrative draft folder')
    targets = {name: out / name for name in ['poster_2x.png', 'poster_1x.png', 'poster_A2.pdf']}
    if any(target in paths.values() for target in targets.values()):
        raise ValueError('An output file must not overwrite an input file')
    images = {key: load_rgba(path, require_alpha=key != 'map') for key, path in paths.items()}
    if images['text'].size != TARGET_SIZE:
        raise ValueError(f'The Figma text overlay must be {TARGET_SIZE}, got {images["text"].size}')
    map_layer, map_padding = pad_right_bottom(images['map'], TARGET_SIZE, (255, 255, 255, 255))
    overlay_layer, overlay_padding = pad_right_bottom(images['overlay'], TARGET_SIZE, (0, 0, 0, 0))
    report = {'inputs': {key: {'path': str(paths[key]), 'size': list(image.size)}
                         for key, image in images.items()},
              'padding': {'map': map_padding, 'overlay': overlay_padding},
              'poster_2x_size': list(TARGET_SIZE), 'poster_1x_size': [1191, 1684],
              'check_only': args.check_only}
    if not args.check_only:
        out.mkdir(parents=True, exist_ok=True)
        composite = Image.alpha_composite(map_layer, overlay_layer)
        composite = Image.alpha_composite(composite, images['text']).convert('RGB')
        composite.save(targets['poster_2x.png'])
        composite.resize((1191, 1684), Image.Resampling.LANCZOS).save(targets['poster_1x.png'])
        report['pdf_page_mm'] = write_a2_pdf(composite, targets['poster_A2.pdf'])
        for name in ['poster_2x.png', 'poster_1x.png']:
            with Image.open(targets[name]) as image:
                expected = TARGET_SIZE if name == 'poster_2x.png' else (1191, 1684)
                if image.size != expected:
                    raise RuntimeError(f'{name}: output dimensions do not match {expected}')
        report['outputs'] = {name: str(path) for name, path in targets.items()}
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
