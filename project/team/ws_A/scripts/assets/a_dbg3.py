import bpy, json, numpy as np
ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_A/'
sc = bpy.context.scene; r = sc.render; vs = sc.view_settings
for n in ('80_SHAPES', '85_HEADER', '81_NOSHADOW'):
    bpy.data.collections[n].hide_render = True
vs.exposure = float(sc.get('map_exposure', vs.exposure))
r.use_border = False; r.resolution_percentage = 48
def score(tag='x'):
    r.filepath = ROOT + 'renders/_bis_%s.png' % tag
    bpy.ops.render.render(write_still=True)
    im = bpy.data.images.load(ROOT + 'renders/_bis_%s.png' % tag, check_existing=False)
    W, H = im.size
    a = np.array(im.pixels[:]).reshape(H, W, 4)[::-1, :, 0]
    bpy.data.images.remove(im)
    b = a[: int(H * 35 / 1684)]
    return round(float(b.std()), 4)
groups = {
    'none': [],
    'peaks': [o for o in bpy.data.objects if o.name.startswith('L01_')],
}
for g, obs in groups.items():
    st = [o.hide_render for o in obs]
    for o in obs:
        o.hide_render = True
    print('DBG', g, score(g))
    for o, s in zip(obs, st):
        o.hide_render = s
raise SystemExit('no save')
