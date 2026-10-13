"""최종 렌더 = 두 번 렌더해 합성 (Workbench는 visible_shadow를 무시해 카메라 앞 도형·헤더가 지도 위에 그림자를 드리움)
1) 지도 패스: 80_SHAPES·85_HEADER 숨김, 그림자 켬, 불투명 배경
2) 도형 패스: 80_SHAPES·85_HEADER만 보임, 그림자 끔, 투명 배경
3) PIL로 2를 1 위에 알파 합성 → renders/v7_map_2x.png
Blender에서: exec(open(<이 파일>).read())
"""
import os
import subprocess
import bpy

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_probe/'
sc = bpy.context.scene; r = sc.render; sh = sc.display.shading
OVER = ('80_SHAPES', '85_HEADER', '81_NOSHADOW')   # R6 떠 있는 DETAIL 부분도 그림자 없이
MAP_A = ROOT + 'renders/_pass_map.png'; MAP_B = ROOT + 'renders/_pass_shapes.png'; OUT = ROOT + 'renders/v7_map_2x.png'
lc = bpy.context.view_layer.layer_collection


def find_lc(l, name):
    if l.name == name:
        return l
    for c in l.children:
        f = find_lc(c, name)
        if f:
            return f
    return None


state = {}
for c in bpy.data.collections:
    state[c.name] = c.hide_render
r.use_border = False; r.resolution_percentage = 48
# 1) 지도
for n in OVER:
    if bpy.data.collections.get(n):
        bpy.data.collections[n].hide_render = True
r.film_transparent = False; shadows = sh.show_shadows; sh.show_shadows = True
r.filepath = MAP_A; bpy.ops.render.render(write_still=True)
# 2) 도형만
for c in bpy.data.collections:
    c.hide_render = c.name not in OVER and c.name not in ('Collection',)
for n in OVER:
    if bpy.data.collections.get(n):
        bpy.data.collections[n].hide_render = False
# 카메라·해만 들어 있는 컬렉션은 그대로
sh.show_shadows = False; r.film_transparent = True
r.filepath = MAP_B; bpy.ops.render.render(write_still=True)
# 되돌림
for c in bpy.data.collections:
    if c.name in state:
        c.hide_render = state[c.name]
sh.show_shadows = shadows; r.film_transparent = False
code = ("from PIL import Image\n"
        f"a=Image.open('{MAP_A}').convert('RGBA'); b=Image.open('{MAP_B}').convert('RGBA')\n"
        "a.alpha_composite(b); a.convert('RGB').save('" + OUT + "')\n"
        "a.convert('RGB').save('" + OUT[:-4] + ".jpg', quality=92)\n")
subprocess.run(['/opt/homebrew/bin/python3', '-c', code], check=True)
print('final render', OUT)
