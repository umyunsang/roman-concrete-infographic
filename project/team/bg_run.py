"""백그라운드 Blender로 작업 공간의 스크립트를 차례로 실행하고 저장.
blender -b <ws>/roman_concrete_map.blend --python team/bg_run.py -- <ws> <script1.py> [script2.py ...]
스크립트는 <ws>/scripts/assets/ 에서 찾음. 하나라도 실패하면 멈추고 저장하지 않음.
"""
import sys, traceback, bpy
args = sys.argv[sys.argv.index('--') + 1:]
WS, steps = args[0].rstrip('/') + '/', args[1:]
D_ = WS + 'scripts/assets/'
ok = True
for f in steps:
    print('STEP', f, flush=True)
    try:
        exec(compile(open(D_ + f).read(), f, 'exec'), {'__name__': '__main__'})
        print('DONE', f, flush=True)
    except Exception:
        print('FAIL', f, traceback.format_exc()[-2500:], flush=True); ok = False; break
if ok:
    for o in [o for o in bpy.data.objects if o.name == 'T_ground']:
        bpy.data.objects.remove(o, do_unlink=True)
    for me in list(bpy.data.meshes):
        if me.users == 0:
            bpy.data.meshes.remove(me)
    for scr in bpy.data.screens:
        for area in scr.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.region_3d.view_perspective = 'CAMERA'
    bpy.ops.wm.save_mainfile(); print('SAVED', flush=True)
