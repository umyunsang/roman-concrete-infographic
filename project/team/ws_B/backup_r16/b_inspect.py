"""워커 B: 장면 조사(수정 없음)"""
import bpy, json
U = bpy.data.texts['asset_utils.py'].as_module()
sc = bpy.context.scene; sh = sc.display.shading
print('ENGINE', sc.render.engine, sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage)
print('SHADING', sh.light, sh.color_type, sh.studio_light, sh.show_shadows, sh.shadow_intensity, sh.show_cavity, sh.cavity_type,
      sh.cavity_ridge_factor, sh.cavity_valley_factor, getattr(sh,'curvature_ridge_factor',None), getattr(sh,'curvature_valley_factor',None),
      sh.show_object_outline, sh.show_specular_highlight, sh.use_dof, sh.show_xray)
print('DISPLAY', sc.display.light_direction[:], sc.display.shadow_shift, sc.display.shadow_focus, sc.display.matcap_ssao_distance, sc.display.matcap_ssao_attenuation, sc.display.matcap_ssao_samples)
print('VIEW', sc.view_settings.view_transform, sc.view_settings.look, sc.view_settings.exposure, sc.view_settings.gamma, sc.display_settings.display_device)
print('AA', sc.display.render_aa)
tot = 0
for c in bpy.data.collections:
    obs = [o for o in c.objects]
    n = 0; lines = []
    for o in obs:
        t = U.tri_count(o) if o.type == 'MESH' else 0
        n += t if not o.hide_render else 0
        lines.append('   %-28s %-6s tri=%7d col=%.2f hide=%s par=%s mods=%s' % (o.name, o.type, t, o.color[0], o.hide_render, o.parent.name if o.parent else '-', [m.type for m in o.modifiers]))
    print('COLL', c.name, 'hide_render', c.hide_render, 'n', len(obs), 'tris', n)
    for l in lines: print(l)
    tot += n
print('TOTAL visible tris', tot)
