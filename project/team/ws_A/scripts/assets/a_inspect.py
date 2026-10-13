"""워커 A 점검: 장면 셰이딩·컬렉션·물체 색·삼각형 수 출력(읽기만)."""
import bpy
U = bpy.data.texts['asset_utils.py'].as_module()
sc = bpy.context.scene; sh = sc.display.shading
print('ENGINE', sc.render.engine, sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage)
for k in ('light', 'color_type', 'single_color', 'studio_light', 'studiolight_rotate_z', 'studiolight_intensity', 'show_cavity', 'cavity_type',
          'cavity_ridge_factor', 'cavity_valley_factor', 'curvature_ridge_factor', 'curvature_valley_factor', 'show_shadows', 'shadow_intensity',
          'show_specular_highlight', 'show_object_outline', 'object_outline_color', 'background_type', 'background_color', 'use_dof', 'show_xray'):
    try:
        print('SH', k, getattr(sh, k) if not hasattr(getattr(sh, k), '__len__') or isinstance(getattr(sh, k), str) else tuple(getattr(sh, k)))
    except Exception as e:
        print('SH', k, 'ERR', e)
d = sc.display
for k in ('light_direction', 'shadow_shift', 'shadow_focus', 'matcap_ssao_distance', 'matcap_ssao_attenuation', 'matcap_ssao_samples', 'render_aa'):
    v = getattr(d, k); print('DISP', k, tuple(v) if hasattr(v, '__len__') and not isinstance(v, str) else v)
print('VIEW', sc.view_settings.view_transform, sc.view_settings.look, sc.view_settings.exposure, sc.view_settings.gamma)
print('WORLD', sc.world.color[:] if sc.world else None)
tot = 0
for c in bpy.data.collections:
    obs = [o for o in c.objects]
    n = 0
    for o in obs:
        if o.type == 'MESH' and not o.hide_render and not c.hide_render:
            try:
                n += U.tri_count(o)
            except Exception:
                pass
    tot += n
    print('COLL', c.name, 'hide_render', c.hide_render, 'objs', len(obs), 'tris', n)
print('TOTAL tris', tot)
for c in bpy.data.collections:
    for o in c.objects:
        if o.type == 'MESH':
            print('OB', c.name, o.name, 'col', tuple(round(x, 3) for x in o.color[:3]), 'hide', o.hide_render, 'mods', [m.type for m in o.modifiers], 'parent', o.parent.name if o.parent else None)
