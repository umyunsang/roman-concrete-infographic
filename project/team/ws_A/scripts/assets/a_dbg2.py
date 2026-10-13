import bpy, json, subprocess
ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_A/'
sh = bpy.context.scene.display.shading
s0 = (sh.show_shadows, sh.show_cavity)
for tag, shd, cav in (('noshadow', False, True), ('nocavity', True, False)):
    sh.show_shadows = shd; sh.show_cavity = cav
    exec(open(ROOT + 'scripts/assets/a_zoomrender.py').read(), {})
    subprocess.run(['cp', ROOT + 'renders/_zoom.png', ROOT + 'renders/_zoom_%s.png' % tag])
sh.show_shadows, sh.show_cavity = s0
raise SystemExit('nosave')
