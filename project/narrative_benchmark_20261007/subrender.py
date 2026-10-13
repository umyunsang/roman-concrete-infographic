import bpy, json, math
sc=bpy.context.scene; render=sc.render; shading=sc.display.shading
OVL={'80_SHAPES','81_NOSHADOW','85_HEADER'}
idx=json.load(open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets_index.json'))
A={a['id']:a for a in idx['assets']}
MINE=['support_breakwater_block','support_harbor','support_pompeii_site','support_privernum','support_ruin_observers','landmark_pompeii_town','landmark_vesuvius','landmark_lime_kiln','landmark_aqueduct']
pct=72; winx=render.resolution_x*pct//100; winy=render.resolution_y*pct//100; s=winx/1191
saved={c.name:c.hide_render for c in bpy.data.collections}
boxes={}
for aid in MINE:
    a=A[aid]; x0,x1,y0,y1=a['crop_pt']
    pb=(max(0,math.floor(x0*s)),min(winx,math.ceil(x1*s)),max(0,math.floor(y0*s)),min(winy,math.ceil(y1*s)))
    boxes[aid]=pb
    render.resolution_percentage=pct; render.use_border=True; render.use_crop_to_border=True
    render.border_min_x=(pb[0]+0.5)/winx; render.border_max_x=(pb[1]+0.5)/winx
    render.border_min_y=(winy-pb[3]+0.5)/winy; render.border_max_y=(winy-pb[2]+0.5)/winy
    for c in bpy.data.collections: c.hide_render=saved[c.name] or c.name in OVL
    render.film_transparent=False; shading.show_shadows=True
    for tag,hide in (('base',False),('sub',True)):
        objs=[bpy.data.objects[n] for n in a['objects']]
        old=[o.hide_render for o in objs]
        if hide:
            for o in objs: o.hide_render=True
        render.filepath=f'/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/op1/sub/{aid}_{tag}.png'
        bpy.ops.render.render(write_still=True)
        for o,h in zip(objs,old): o.hide_render=h
for c in bpy.data.collections: c.hide_render=saved[c.name]
json.dump({'s':s,'boxes':boxes},open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/op1/sub/boxes.json','w'))
print('done')
