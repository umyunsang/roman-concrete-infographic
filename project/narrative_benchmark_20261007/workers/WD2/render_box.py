"""Border render of a pt box (map pass + optional overlay) — for WD2 inspection only. Restores settings."""
import bpy
from pathlib import Path

OVERLAY = {'80_SHAPES', '81_NOSHADOW', '85_HEADER'}


def render_box(path, x0, x1, y0, y1, pct=100, overlay=False):
    sc = bpy.context.scene; r = sc.render; sh = sc.display.shading
    saved = {n: getattr(r, n) for n in ['filepath', 'use_border', 'use_crop_to_border', 'resolution_percentage',
                                       'film_transparent', 'border_min_x', 'border_max_x', 'border_min_y', 'border_max_y']}
    saved_c = {c.name: c.hide_render for c in bpy.data.collections}
    saved_sh = sh.show_shadows
    try:
        r.use_border = True; r.use_crop_to_border = True; r.resolution_percentage = pct
        r.border_min_x = max(0.0, x0 / 1191); r.border_max_x = min(1.0, x1 / 1191)
        r.border_min_y = max(0.0, 1 - y1 / 1684); r.border_max_y = min(1.0, 1 - y0 / 1684)
        for c in bpy.data.collections:
            c.hide_render = saved_c[c.name] or (c.name in OVERLAY and not overlay)
        r.film_transparent = False; sh.show_shadows = True
        r.filepath = str(path)
        bpy.ops.render.render(write_still=True)
    finally:
        for c in bpy.data.collections:
            c.hide_render = saved_c[c.name]
        for k, v in saved.items():
            setattr(r, k, v)
        sh.show_shadows = saved_sh
    return str(path)
