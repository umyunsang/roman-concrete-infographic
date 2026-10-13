"""Prepare a text-free poster image and editable type manifest, without Figma writes.

The narrative JSON is authoritative for revised copy, but its retained-node
coordinates predate the exported baseline. Supply a current Figma text inventory
to recover every visible retained node, including title, BASIC, and timeline.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CANVAS = (1191, 1684)
PIXELS = (2382, 3368)
OUT = ROOT / 'out' / 'figma_import'
SOURCE_IDS = {
    'C1_n': '634:731', 'C1_t1': '634:732', 'C1_t2': '634:733', 'C1_b': '634:735',
    'C2_n': '634:741', 'C2_t1': '634:742', 'C2_t2': '634:743', 'C2_b': '634:744',
    'C3_n': '634:750', 'C3_t1': '634:751', 'C3_t2': '634:752', 'C3_b': '634:753',
    'C4_n': '634:768', 'C4_t1': '634:769', 'C4_t2': '634:770', 'C4_b': '634:772',
    'C5_n': '634:759', 'C5_t1': '634:760', 'C5_t2': '634:761', 'C5_b': '634:762',
    'D1_h': '634:841', 'D1_b': '634:843', 'D2_h': '634:845', 'D2_b': '634:847',
    'D3_h': '634:849', 'D3_b': '634:851', 'D4_h': '634:853', 'D4_b': '634:854',
    'S1_n': '634:905', 'S1_o': '634:907', 'S1_d': '634:908',
    'S2_n': '634:910', 'S2_o': '634:912', 'S2_d': '634:913',
    'S3_n': '634:915', 'S3_o': '634:917', 'S3_d': '634:918',
    'S4_n': '634:920', 'S4_o': '634:922', 'S4_d': '634:923',
    'P_apennini': '634:632', 'P_aqueduct': '634:633', 'P_appia': '634:634',
    'P_vesuvio': '634:635', 'P_pompeii': '634:636', 'P_harbor': '634:637',
    'P_sea': '634:638', 'Q': '634:720', 'TL80_event': '634:943',
}
REMOVED_IDS = {'634:722'}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pad(path: Path, fill: tuple[int, ...]) -> tuple[Image.Image, dict]:
    with Image.open(path) as source:
        im = source.convert('RGBA')
    dx, dy = PIXELS[0] - im.width, PIXELS[1] - im.height
    if dx not in (0, 1) or dy not in (0, 1):
        raise ValueError(f'Unexpected render size: {path}: {im.size}')
    result = Image.new('RGBA', PIXELS, fill)
    result.alpha_composite(im)
    return result, {'sourceSize': list(im.size), 'rightPx': dx, 'bottomPx': dy}


def load_inventory(path: Path | None) -> tuple[dict, list[dict]]:
    if path is None:
        return {}, []
    data = json.loads(path.read_text())
    if isinstance(data, list):
        return {}, data
    for key in ('texts', 'nodes', 'textNodes'):
        if isinstance(data.get(key), list):
            return data, data[key]
    if isinstance(data.get('latest', {}).get('texts'), list):
        return data, data['latest']['texts']
    raise ValueError('Inventory must expose a texts, nodes, or textNodes array')


def current_geometry(node: dict, inventory: dict) -> dict:
    """Use poster-local transforms; never treat a grouped node's x/y as global."""
    transform = node.get('relativeToFrameTransform') or node.get('frameTransform')
    if transform is None and isinstance(node.get('posterLocal'), dict):
        transform = node['posterLocal'].get('transform')
    absolute = node.get('absoluteTransform', node.get('m'))
    if transform is None and absolute:
        transform = [row[:] for row in absolute]
        frame = inventory.get('frame', inventory.get('root', {}))
        frame_transform = frame.get('absoluteTransform', inventory.get('frameTransform'))
        fx = frame_transform[0][2] if frame_transform else frame.get('x', 0)
        fy = frame_transform[1][2] if frame_transform else frame.get('y', 0)
        transform[0][2] -= fx
        transform[1][2] -= fy
    local = node.get('posterLocal', {})
    x = transform[0][2] if transform else local.get('x', node.get('frameX'))
    y = transform[1][2] if transform else local.get('y', node.get('frameY'))
    if x is None or y is None:
        # Only explicitly frame-relative x/y is safe in the absence of a matrix.
        if node.get('coordinateSpace') == 'frame':
            x, y = node.get('x'), node.get('y')
    width = node.get('width', node.get('w'))
    height = node.get('height', node.get('h'))
    result = {'x': x, 'y': y, 'width': width, 'height': height}
    if transform:
        result['relativeTransform'] = transform
        # Figma's rotation sign is opposite atan2 in screen coordinates.
        result['rotation'] = -math.degrees(math.atan2(transform[1][0], transform[0][0]))
    elif 'rotation' in node:
        result['rotation'] = node['rotation']
    return result


def retained_entry(node: dict, inventory: dict) -> dict:
    source_id = node['id']
    entry = {
        'id': source_id, 'sourceNodeId': source_id, 'sourceKind': 'retained_live',
        'text': node.get('characters', node.get('text', node.get('t', ''))),
        'fontName': node.get('fontName') or
                    ({'family': 'Noto Sans KR', 'style': node['font']}
                     if node.get('font') not in (None, 'mixed') else None),
        'fontSize': node.get('fontSize', node.get('size', node.get('s'))),
        'lineHeight': node.get('lineHeight', node.get('lh')),
        'textAlignHorizontal': node.get('textAlignHorizontal', 'LEFT'),
        'textAlignVertical': node.get('textAlignVertical', 'TOP'),
        'fills': node.get('fills'),
        'textAutoResize': node.get('textAutoResize'),
        'sourceFigma': node,
    }
    entry.update(current_geometry(node, inventory))
    return entry


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--figma-inventory', type=Path)
    args = parser.parse_args()
    narrative_path = ROOT / 'copy' / 'figma_text_narrative.json'
    patches_path = ROOT / 'copy' / 'narrative_copy.json'
    narrative = json.loads(narrative_path.read_text())
    patches = json.loads(patches_path.read_text())
    patch_by_id = {n['id']: n for n in patches['patchNodes']}
    inventory, current = load_inventory(args.figma_inventory)
    by_source = {n['id']: n for n in current}
    entries: list[dict] = []
    consumed: set[str] = set(REMOVED_IDS)
    for n in narrative:
        source_id = SOURCE_IDS.get(n['id'])
        if source_id:
            consumed.add(source_id)
        live = by_source.get(source_id)
        patch = patch_by_id.get(n['id'])
        entry = retained_entry(live, inventory) if live else {}
        entry.update({
            'id': n['id'], 'sourceNodeId': source_id, 'group': n['g'],
            'text': n['t'], 'narrativeSource': n,
        })
        if patch or not live:
            entry.update({
                'sourceKind': 'narrative_patch' if patch else 'narrative_fallback_unverified',
                'x': n['x'], 'y': n['y'], 'width': n['w'], 'height': n['h'],
                'fontName': {'family': 'Noto Sans KR', 'style': 'Bold' if n['b'] else 'Regular'},
                'fontSize': n['s'], 'rotation': n.get('rot', 0),
                'textAlignHorizontal': n.get('align', 'left').upper(),
                'textAlignVertical': 'TOP', 'textAutoResize': 'NONE',
                'fills': [{'type': 'SOLID', 'color': {'r': 1, 'g': 1, 'b': 1}}]
                         if n.get('c') == 'white' else
                         [{'type': 'SOLID', 'color': {'r': 17 / 255, 'g': 17 / 255, 'b': 17 / 255}}],
            })
            # Geometry changes invalidate the old live relative transform.
            entry.pop('relativeTransform', None)
            if patch:
                entry.update({
                    'lineHeight': {'unit': 'PIXELS', 'value': patch['lineHeight']},
                    'inkOffset': patch['inkOffset'], 'targetInkBboxes': patch['inkBboxes'],
                    'measuredWidth': patch['measuredWidth'], 'patchSource': patch,
                })
        else:
            entry['sourceKind'] = 'retained_live'
        if n.get('badge'):
            entry['badgeNumberOnly'] = True
        if n.get('ul'):
            entry['underlineAlreadyInBackground'] = n['ul']
        entries.append(entry)
    for live in current:
        if live['id'] not in consumed:
            entries.append(retained_entry(live, inventory))
    entries.sort(key=lambda n: (n.get('y') is None, n.get('y') or 0, n.get('x') or 0, n['id']))

    map_path = ROOT / 'renders' / 'narrative_v4_map_pass.png'
    shapes_path = ROOT / 'renders' / 'narrative_v4_overlay_pass.png'
    text_path = ROOT / 'copy' / 'text_overlay_narrative_rgba_2x.png'
    poster_path = ROOT / 'out' / 'poster_2x.png'
    map_layer, map_padding = pad(map_path, (255, 255, 255, 255))
    shapes, shapes_padding = pad(shapes_path, (0, 0, 0, 0))
    background = Image.alpha_composite(map_layer, shapes)
    OUT.mkdir(parents=True, exist_ok=True)
    image_path = OUT / 'map_without_text_2x.png'
    background.convert('RGB').save(image_path, optimize=True)
    with Image.open(text_path) as im:
        if im.size != PIXELS:
            raise ValueError('Current RGBA text layer has unexpected size')
        composite = Image.alpha_composite(background, im.convert('RGBA')).convert('RGB')
    with Image.open(poster_path) as im:
        mismatches = int(np.any(np.array(composite) != np.array(im.convert('RGB')), axis=2).sum())
    if mismatches:
        raise ValueError(f'Background+text fails existing poster reconstruction: {mismatches} pixels')
    if image_path.stat().st_size >= 10_000_000:
        raise ValueError('Base image exceeds 10 MB import boundary')
    unresolved = [n['id'] for n in entries if n.get('x') is None or n.get('y') is None]
    fallbacks = [n['id'] for n in entries if n['sourceKind'] == 'narrative_fallback_unverified']
    source_inventory_complete = len(current) == 89
    complete = source_inventory_complete and len(entries) == 90 and not unresolved and not fallbacks
    manifest = {
        'canvas': {'width': CANVAS[0], 'height': CANVAS[1], 'units': 'Figma px', 'imageScale': 2},
        'background': str(image_path), 'fontFamily': 'Noto Sans KR',
        'complete': complete, 'entries': entries,
        'patches': [n for n in entries if n['sourceKind'] == 'narrative_patch'],
        'removedSourceNodes': sorted(REMOVED_IDS),
        'note': 'Create native TEXT nodes only. CORE circles and all underlines, pins, DETAIL lines, timeline rule/dots are already rasterized in the background. Preserve current transforms for retained text; patched copy uses explicit source ink boxes and line spacing. Typography remains editable and its final raster export must be visually checked.',
    }
    manifest_path = OUT / 'text_manifest.json'
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    input_paths = [map_path, shapes_path, text_path, poster_path, narrative_path, patches_path]
    if args.figma_inventory:
        input_paths.append(args.figma_inventory)
    audit = {
        'scope': 'Local asset preparation only; no Figma, Blender, or Meshy mutations',
        'image': {'path': str(image_path), 'size': list(PIXELS), 'bytes': image_path.stat().st_size,
                  'sha256': sha(image_path), 'under10MB': image_path.stat().st_size < 10_000_000},
        'padding': {'map': map_padding, 'overlay': shapes_padding},
        'posterReconstructionMismatchingPixels': mismatches,
        'text': {'narrativeEntries': len(narrative), 'patchEntries': len(patch_by_id),
                 'originalLiveEntries': len(current), 'manifestEntries': len(entries),
                 'expectedCompleteEntries': 90, 'complete': complete,
                 'groups': dict(Counter(n.get('group', 'retained') for n in entries)),
                 'unresolvedGeometry': unresolved, 'unverifiedNarrativeFallbacks': fallbacks,
                 'missingOriginalSourceNodes': sorted(set(SOURCE_IDS.values()) - set(by_source)),
                 'sourceKinds': dict(Counter(n['sourceKind'] for n in entries))},
        'nontextBackground': ['CORE circles', 'CORE underlines', 'SUPPORT dashed pins/endpoints',
                              'DETAIL leaders/section diagram', 'timeline rule/dots/arrowhead',
                              'header models', 'map/architecture/terrain/all placed objects'],
        'inputs': {str(p): {'bytes': p.stat().st_size, 'sha256': sha(p)} for p in input_paths},
        'manifest': {'path': str(manifest_path), 'sha256': sha(manifest_path)},
    }
    (OUT / 'audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'image': audit['image'], 'text': audit['text'],
                      'posterReconstructionMismatchingPixels': mismatches}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
