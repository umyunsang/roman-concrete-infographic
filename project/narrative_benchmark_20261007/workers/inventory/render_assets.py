"""render_assets.py - per review asset: a context crop from the full poster render and an isolated crop.

Read-only: never saves the blend (checks the file hash before/after). Run headless:
  Blender -b <in.blend> --factory-startup --python render_assets.py -- <out_dir> [--percent 72] [--scale 3]
        [--margin 12] [--only id,id,...] [--no-selftest]

1. inventory.build_inventory (inventory.py in this folder) -> <out_dir>/inventory.json (+ ID passes)
2. full render: integrate_assets.render_two_pass(<out_dir>/full/full.png, percent)  (map pass + overlay pass)
3. per asset: every other render-visible object gets hide_render, then the same two-pass split is rendered only
   inside the asset box (+margin) with render.use_border + use_crop_to_border (render_two_pass itself forces
   use_border=False, so border_two_pass below mirrors its collection logic line for line; a self-test renders a few
   boxes with nothing hidden through border_two_pass and compares them with the full render_two_pass output).
4. compose_assets.py (Pillow, same crop/resize arithmetic as scripts/crop.py): assets/<id>/context.png,
   assets/<id>/isolated.png, contact_sheet.png; then assets_index.json and render_report.json.
Note: the Figma text layer is not part of these renders.
"""
import bpy, json, sys, time, runpy, hashlib, subprocess, shutil, math, os
from pathlib import Path

HERE = Path(__file__).resolve().parent
NB = HERE.parents[1]                         # .../nb_work
INTEGRATE = NB / 'scripts/integrate_assets.py'
COMPOSE = HERE / 'compose_assets.py'
W_PT, H_PT = 1191, 1684
FONT = Path.home() / 'Library/Fonts/NotoSansCJKkr-Regular.otf'


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for blk in iter(lambda: f.read(1 << 20), b''):
            h.update(blk)
    return h.hexdigest()


def parse_args():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    if not argv:
        raise SystemExit(__doc__)
    a = {'out': Path(argv[0]).resolve(), 'percent': 72, 'scale': 3.0, 'margin': 12.0, 'only': None, 'selftest': True}
    i = 1
    while i < len(argv):
        k = argv[i]
        if k == '--percent': a['percent'] = int(argv[i + 1]); i += 2
        elif k == '--scale': a['scale'] = float(argv[i + 1]); i += 2
        elif k == '--margin': a['margin'] = float(argv[i + 1]); i += 2
        elif k == '--only': a['only'] = set(argv[i + 1].split(',')); i += 2
        elif k == '--no-selftest': a['selftest'] = False; i += 1
        else: raise SystemExit(f'unknown argument {k}')
    return a


def scene_state():
    sc = bpy.context.scene; r = sc.render
    return json.dumps({
        'objects': {o.name: [o.hide_render, list(o.color)] for o in bpy.data.objects},
        'collections': {c.name: c.hide_render for c in bpy.data.collections},
        'render': {n: getattr(r, n) for n in ['filepath', 'use_border', 'use_crop_to_border', 'resolution_percentage',
                                               'film_transparent', 'border_min_x', 'border_max_x', 'border_min_y',
                                               'border_max_y', 'dither_intensity']},
        'shading': {n: getattr(sc.display.shading, n) for n in ['light', 'color_type', 'show_shadows', 'show_cavity']},
        'aa': sc.display.render_aa, 'vt': sc.view_settings.view_transform, 'camera': sc.camera.name,
    }, sort_keys=True, default=str)


def border_two_pass(output, px_box, percent, overlay_collections):
    """Mirror of integrate_assets.render_two_pass with a pixel-exact render border.
    px_box = (x0, x1, y0, y1) pixels of the full-size frame, top-left origin. Returns pass paths."""
    scene, render = bpy.context.scene, bpy.context.scene.render
    shading = scene.display.shading
    saved_collections = {c.name: c.hide_render for c in bpy.data.collections}
    names = ['filepath', 'use_border', 'use_crop_to_border', 'resolution_percentage', 'film_transparent',
             'border_min_x', 'border_max_x', 'border_min_y', 'border_max_y']
    saved_render = {n: getattr(render, n) for n in names}
    saved_shadows = shading.show_shadows
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    map_png = output.with_name(output.stem + '_map_pass.png')
    overlay_png = output.with_name(output.stem + '_overlay_pass.png')
    winx = render.resolution_x * percent // 100
    winy = render.resolution_y * percent // 100
    x0, x1, y0, y1 = px_box
    try:
        render.resolution_percentage = percent
        render.use_border = True
        render.use_crop_to_border = True
        # Blender truncates border*win to int; +0.5 px lands exactly on the wanted pixel edges.
        render.border_min_x = (x0 + 0.5) / winx
        render.border_max_x = (x1 + 0.5) / winx
        render.border_min_y = (winy - y1 + 0.5) / winy
        render.border_max_y = (winy - y0 + 0.5) / winy
        for c in bpy.data.collections:
            c.hide_render = saved_collections[c.name] or c.name in overlay_collections
        render.film_transparent = False
        shading.show_shadows = True
        render.filepath = str(map_png)
        bpy.ops.render.render(write_still=True)
        for c in bpy.data.collections:
            c.hide_render = saved_collections[c.name] or c.name not in overlay_collections | {'Collection'}
        render.film_transparent = True
        shading.show_shadows = False
        render.filepath = str(overlay_png)
        bpy.ops.render.render(write_still=True)
    finally:
        for c in bpy.data.collections:
            c.hide_render = saved_collections[c.name]
        for n, v in saved_render.items():
            setattr(render, n, v)
        shading.show_shadows = saved_shadows
    return {'map_pass': str(map_png), 'overlay_pass': str(overlay_png), 'px_box': list(px_box), 'win': [winx, winy]}


def px_box_for(crop_pt, s, winx, winy, pad=2):
    x0, x1, y0, y1 = crop_pt
    return (max(0, math.floor(x0 * s) - pad), min(winx, math.ceil(x1 * s) + pad),
            max(0, math.floor(y0 * s) - pad), min(winy, math.ceil(y1 * s) + pad))


def main():
    args = parse_args()
    out = args['out']; out.mkdir(parents=True, exist_ok=True)
    t_all = time.time()
    src = bpy.data.filepath
    h0 = sha256_file(src)
    state0 = scene_state()
    H = runpy.run_path(str(INTEGRATE), run_name='integrate_assets_lib')
    OVL = set(H['OVERLAY_COLLECTIONS'])
    INV = runpy.run_path(str(HERE / 'inventory.py'), run_name='inventory_lib')
    if set(INV['OVERLAY_COLLECTIONS']) != OVL:
        raise RuntimeError('inventory.py overlay collection set differs from integrate_assets.py')
    timing = {}

    t = time.time()
    inv = INV['build_inventory'](out / 'idpass/id')
    inv['blend_sha256'] = h0
    (out / 'inventory.json').write_text(json.dumps(inv, ensure_ascii=False, indent=1))
    timing['inventory_s'] = round(time.time() - t, 1)
    if scene_state() != state0:
        raise RuntimeError('inventory changed scene state')

    render = bpy.context.scene.render
    pct = args['percent']
    winx = render.resolution_x * pct // 100
    winy = render.resolution_y * pct // 100
    s = winx / W_PT

    t = time.time()
    full = H['render_two_pass'](out / 'full/full.png', resolution_percentage=pct)
    timing['full_render_s'] = round(time.time() - t, 1)
    if scene_state() != state0:
        raise RuntimeError('render_two_pass changed scene state')

    assets = [a for a in inv['assets'] if a['objects'] and (args['only'] is None or a['id'] in args['only'])]
    visible_names = [o['name'] for o in inv['objects']]
    O = bpy.data.objects
    jobs = []
    m = args['margin']
    t_iso = time.time()
    for a in assets:
        b = a['bbox_pt']
        crop = [max(0.0, b[0] - m), min(float(W_PT), b[1] + m), max(0.0, b[2] - m), min(float(H_PT), b[3] + m)]
        pxb = px_box_for(crop, s, winx, winy)
        keep = set(a['objects'])
        missing = [nm for nm in keep if nm not in O]
        if missing:
            raise RuntimeError(f'{a["id"]}: objects not found: {missing}')
        hidden_now = []
        t1 = time.time()
        try:
            for nm in visible_names:
                if nm not in keep and not O[nm].hide_render:
                    O[nm].hide_render = True
                    hidden_now.append(nm)
            iso = border_two_pass(out / f'assets/{a["id"]}/iso.png', pxb, pct, OVL)
        finally:
            for nm in hidden_now:
                O[nm].hide_render = False
        dt = round(time.time() - t1, 2)
        jobs.append({'id': a['id'], 'name': a['name'], 'role': a['role'], 'crop_pt': [round(v, 2) for v in crop],
                     'scale': args['scale'], 'iso_map': iso['map_pass'], 'iso_overlay': iso['overlay_pass'],
                     'iso_px_box': list(pxb), 'out_context': str(out / f'assets/{a["id"]}/context.png'),
                     'out_isolated': str(out / f'assets/{a["id"]}/isolated.png'), 'render_s': dt})
        print(f'ASSET {a["id"]} crop={jobs[-1]["crop_pt"]} px={pxb} hidden={len(hidden_now)} {dt}s', flush=True)
    timing['isolated_renders_s'] = round(time.time() - t_iso, 1)
    if scene_state() != state0:
        raise RuntimeError('isolated renders did not restore scene state')

    # self-test: border_two_pass with nothing hidden must reproduce the full render_two_pass pixels
    selftests = []
    if args['selftest']:
        picks = []
        for want in ('landmark_pantheon', 'basic_recipe', 'detail_d2_making', 'detail_core4_three_cubes'):
            j = next((j for j in jobs if j['id'] == want), None)
            if j:
                picks.append(j)
        if not picks:
            picks = jobs[:2]
        for j in picks:
            r = border_two_pass(out / f'selftest/{j["id"]}.png', tuple(j['iso_px_box']), pct, OVL)
            selftests.append({'id': j['id'], 'map': r['map_pass'], 'overlay': r['overlay_pass'], 'px_box': r['px_box']})
        if scene_state() != state0:
            raise RuntimeError('self-test changed scene state')

    spec = {'full_map': full['map_pass'], 'full_overlay': full['overlay_pass'], 'frame_w': W_PT, 'frame_h': H_PT,
            'win': [winx, winy], 'jobs': jobs, 'selftests': selftests, 'font': str(FONT) if FONT.exists() else None,
            'contact_sheet': str(out / 'contact_sheet.png'), 'result': str(out / 'compose_result.json')}
    (out / 'compose_jobs.json').write_text(json.dumps(spec, ensure_ascii=False, indent=1))
    uv = shutil.which('uv') or '/opt/homebrew/bin/uv'
    t = time.time()
    cp = subprocess.run([uv, 'run', '-q', '--no-project', '--with', 'pillow', '--with', 'numpy', 'python', '-I',
                         str(COMPOSE), str(out / 'compose_jobs.json')], capture_output=True, text=True)
    print(cp.stdout[-3000:]); print(cp.stderr[-3000:])
    if cp.returncode != 0:
        raise RuntimeError('compose_assets.py failed')
    timing['compose_s'] = round(time.time() - t, 1)
    comp = json.loads((out / 'compose_result.json').read_text())

    inv_by_id = {a['id']: a for a in inv['assets']}
    index = []
    for j in jobs:
        a = inv_by_id[j['id']]
        c = comp['assets'][j['id']]
        index.append({'id': j['id'], 'name': a['name'], 'role': a['role'], 'kind': a['kind'],
                      'objects': a['objects'], 'object_regions': a.get('object_regions'),
                      'passes': a.get('passes'), 'bbox_pt': a['bbox_pt'], 'bbox_visible_final_pt': a.get('bbox_visible_final_pt'),
                      'area_visible_final_pt2': a.get('area_visible_final_pt2'), 'crop_pt': j['crop_pt'],
                      'scale': j['scale'], 'materials': a.get('materials'),
                      'zero_visible_objects': a.get('zero_visible_objects'), 'hidden_objects': a.get('hidden_objects'),
                      'files': {'context': j['out_context'], 'isolated': j['out_isolated'],
                                'isolated_map_pass': j['iso_map'], 'isolated_overlay_pass': j['iso_overlay']},
                      'image_px': c['size'], 'isolated_nonbackground_px': c['iso_nonbg_px'],
                      'render_s': j['render_s']})
    (out / 'assets_index.json').write_text(json.dumps({
        'blend': src, 'blend_sha256': h0, 'frame_pt': [W_PT, H_PT], 'render_percent': pct,
        'px_per_pt_render': round(s, 4), 'crop_scale': args['scale'], 'margin_pt': m,
        'full_render': full, 'contact_sheet': spec['contact_sheet'], 'inventory': str(out / 'inventory.json'),
        'note': 'Blender render only; Figma text layer not included. context = full poster render, '
                'isolated = only this asset render-visible, same camera and same box.',
        'hidden_assets': inv['hidden_assets'], 'hidden_objects': inv['hidden'],
        'assets': index}, ensure_ascii=False, indent=1))
    h1 = sha256_file(src)
    rep = {'blend': src, 'blend_sha256_before': h0, 'blend_sha256_after': h1, 'blend_unchanged': h0 == h1,
           'scene_state_restored': scene_state() == state0, 'assets_rendered': len(jobs),
           'visible_assets_in_inventory': len([a for a in inv['assets'] if a['objects']]),
           'counts': inv['counts'], 'timing': timing, 'total_s': round(time.time() - t_all, 1),
           'selftest_border_vs_full': comp.get('selftests'), 'compose_checks': comp.get('checks')}
    (out / 'render_report.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1))
    print('RENDER_ASSETS', json.dumps({k: rep[k] for k in ['assets_rendered', 'timing', 'total_s', 'blend_unchanged',
                                                            'scene_state_restored']}, ensure_ascii=False))
    if h0 != h1:
        raise RuntimeError('input blend changed on disk')


if __name__ == '__main__':
    main()
