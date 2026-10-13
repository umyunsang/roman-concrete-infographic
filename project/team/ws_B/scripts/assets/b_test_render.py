"""워커 B: 설정 시험 렌더(부분). 환경변수 BT_VARIANTS='name:key=val,key=val;name2:...' BT_BOX='u0,v0,u1,v1'
key: shadow(0/1), cavity(0/1), ridge, valley, sint(그림자 세기), exp(노출), cavtype(WORLD/SCREEN/BOTH), smooth_land(0/1)
설정은 렌더 뒤 되돌림(저장되어도 원래 값)."""
import os, bpy
sc = bpy.context.scene; r = sc.render; sh = sc.display.shading
ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_B/'
box = [float(x) for x in os.environ.get('BT_BOX', '0,0,1191,1684').split(',')]
W, H = 1191.0, 1684.0
saved = dict(shadow=sh.show_shadows, cavity=sh.show_cavity, ridge=sh.cavity_ridge_factor, valley=sh.cavity_valley_factor,
             sint=sh.shadow_intensity, exp=sc.view_settings.exposure, cavtype=sh.cavity_type,
             sd=sc.display.matcap_ssao_distance, wsl=sh.use_world_space_lighting, rotz=sh.studiolight_rotate_z, studio=sh.studio_light, ldir=tuple(sc.display.light_direction), pct=r.resolution_percentage, outline=sh.show_object_outline, sf=sc.display.shadow_focus, sshift=sc.display.shadow_shift, ocol=tuple(sh.object_outline_color), ss=sc.display.matcap_ssao_samples, sa=sc.display.matcap_ssao_attenuation)
hidden = {}
for c in ('80_SHAPES', '85_HEADER', '81_NOSHADOW'):
    if bpy.data.collections.get(c):
        hidden[c] = bpy.data.collections[c].hide_render; bpy.data.collections[c].hide_render = True
r.use_border = True; r.use_crop_to_border = True
r.border_min_x = box[0] / W; r.border_max_x = box[2] / W
r.border_min_y = 1 - box[3] / H; r.border_max_y = 1 - box[1] / H
r.resolution_percentage = 48; r.film_transparent = False
for spec in os.environ.get('BT_VARIANTS', 'base:').split(';'):
    name, _, kv = spec.partition(':')
    for item in [x for x in kv.split(',') if x]:
        k, v = item.split('=')
        if k == 'shadow': sh.show_shadows = v == '1'
        elif k == 'cavity': sh.show_cavity = v == '1'
        elif k == 'ridge': sh.cavity_ridge_factor = float(v)
        elif k == 'valley': sh.cavity_valley_factor = float(v)
        elif k == 'sint': sh.shadow_intensity = float(v)
        elif k == 'exp': sc.view_settings.exposure = float(v)
        elif k == 'cavtype': sh.cavity_type = v
        elif k == 'sd': sc.display.matcap_ssao_distance = float(v)
        elif k == 'wsl': sh.use_world_space_lighting = v == '1'
        elif k == 'rotz': sh.studiolight_rotate_z = float(v) * 3.14159265 / 180
        elif k == 'studio': sh.studio_light = v
        elif k == 'ldir': sc.display.light_direction = tuple(float(x) for x in v.split('/'))
        elif k == 'pct': r.resolution_percentage = int(v)
        elif k == 'sf': sc.display.shadow_focus = float(v)
        elif k == 'sshift': sc.display.shadow_shift = float(v)
        elif k == 'outline': sh.show_object_outline = v == '1'
        elif k == 'ocol': sh.object_outline_color = (float(v),) * 3
        elif k == 'ss': sc.display.matcap_ssao_samples = int(v)
        elif k == 'sa': sc.display.matcap_ssao_attenuation = float(v)
    r.filepath = ROOT + 'renders/_test_%s.png' % name
    bpy.ops.render.render(write_still=True)
    print('test', name, kv)
    sh.show_shadows = saved['shadow']; sh.show_cavity = saved['cavity']; sh.cavity_ridge_factor = saved['ridge']
    sh.cavity_valley_factor = saved['valley']; sh.shadow_intensity = saved['sint']; sc.view_settings.exposure = saved['exp']; sh.cavity_type = saved['cavtype']
    sh.use_world_space_lighting = saved['wsl']; sh.studiolight_rotate_z = saved['rotz']; sh.studio_light = saved['studio']; sc.display.light_direction = saved['ldir']; r.resolution_percentage = 48; sh.show_object_outline = saved['outline']; sc.display.shadow_focus = saved['sf']; sc.display.shadow_shift = saved['sshift']; sh.object_outline_color = saved['ocol']
    sc.display.matcap_ssao_distance = saved['sd']; sc.display.matcap_ssao_samples = saved['ss']; sc.display.matcap_ssao_attenuation = saved['sa']
r.use_border = False; r.use_crop_to_border = False
for c, v in hidden.items():
    bpy.data.collections[c].hide_render = v
