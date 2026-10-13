"""render_crops.py - render screen-pt boxes of the open blend (map pass + overlay pass, composited), read-only.
Blender -b <blend> --factory-startup --python render_crops.py -- <out_dir> <tag> <jobs.json>
jobs.json: [{"name":..., "box":[x0,x1,y0,y1] (pt), "scale": px per pt, "isolate": [object names] or null}]
Mirrors inventory/render_assets.border_two_pass (render border, crop to border)."""
import bpy, sys, json, math
from pathlib import Path
argv = sys.argv[sys.argv.index('--') + 1:]
OUT = Path(argv[0]); TAG = argv[1]; JOBS = json.load(open(argv[2]))
OUT.mkdir(parents=True, exist_ok=True)
OVL = {'80_SHAPES', '81_NOSHADOW', '85_HEADER'}
W_PT = 1191
sc = bpy.context.scene; render = sc.render; shading = sc.display.shading
src = bpy.data.filepath


def two_pass(stem, px_box, percent, transparent):
    saved_c = {c.name: c.hide_render for c in bpy.data.collections}
    names = ['filepath', 'use_border', 'use_crop_to_border', 'resolution_percentage', 'film_transparent',
             'border_min_x', 'border_max_x', 'border_min_y', 'border_max_y']
    saved_r = {n: getattr(render, n) for n in names}
    saved_sh = shading.show_shadows
    winx = render.resolution_x * percent // 100; winy = render.resolution_y * percent // 100
    x0, x1, y0, y1 = px_box
    try:
        render.resolution_percentage = percent
        render.use_border = True; render.use_crop_to_border = True
        render.border_min_x = (x0 + 0.5) / winx; render.border_max_x = (x1 + 0.5) / winx
        render.border_min_y = (winy - y1 + 0.5) / winy; render.border_max_y = (winy - y0 + 0.5) / winy
        for c in bpy.data.collections:
            c.hide_render = saved_c[c.name] or c.name in OVL
        render.film_transparent = transparent
        shading.show_shadows = True
        render.filepath = str(OUT / f'{stem}_map.png'); bpy.ops.render.render(write_still=True)
        for c in bpy.data.collections:
            c.hide_render = saved_c[c.name] or c.name not in OVL | {'Collection'}
        render.film_transparent = True; shading.show_shadows = False
        render.filepath = str(OUT / f'{stem}_ovl.png'); bpy.ops.render.render(write_still=True)
    finally:
        for c in bpy.data.collections:
            c.hide_render = saved_c[c.name]
        for n, v in saved_r.items():
            setattr(render, n, v)
        shading.show_shadows = saved_sh


for j in JOBS:
    s = j['scale']
    pct = int(round(s * W_PT * 100 / render.resolution_x))
    s_eff = render.resolution_x * pct // 100 / W_PT
    winx = render.resolution_x * pct // 100; winy = render.resolution_y * pct // 100
    x0, x1, y0, y1 = j['box']
    pxb = (max(0, math.floor(x0 * s_eff)), min(winx, math.ceil(x1 * s_eff)), max(0, math.floor(y0 * s_eff)), min(winy, math.ceil(y1 * s_eff)))
    hidden = []
    if j.get('isolate'):
        keep = set(j['isolate'])
        for o in bpy.data.objects:
            if o.type == 'MESH' and o.name not in keep and not o.hide_render:
                o.hide_render = True; hidden.append(o.name)
    try:
        two_pass(f"{TAG}_{j['name']}", pxb, pct, bool(j.get('isolate')))
    finally:
        for n in hidden:
            bpy.data.objects[n].hide_render = False
    j['px_box'] = pxb; j['percent'] = pct; j['s_eff'] = s_eff
json.dump(JOBS, open(OUT / f'{TAG}_jobs_done.json', 'w'), indent=1)
print('DONE', len(JOBS))
