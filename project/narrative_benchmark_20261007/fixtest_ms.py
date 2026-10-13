import bpy
OUT='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/oc2/idr/'
sc=bpy.context.scene; r=sc.render
OVERLAY={'80_SHAPES','81_NOSHADOW','85_HEADER'}
for c in bpy.data.collections:
    if c.name in OVERLAY: c.hide_render=True
r.resolution_percentage=48; r.image_settings.file_format='PNG'; r.image_settings.color_mode='RGBA'
def s2l(v):
    v=v/255.0; return v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4
r.filepath=OUT+'fix_base_map2x.png'; bpy.ops.render.render(write_still=True)
src=bpy.data.materials['RC.v12_1.direction_arrow']
new=src.copy(); new.name='RC.test.direction_arrow_shade'
hexc='C64B2E'; rgb=[s2l(int(hexc[i:i+2],16)) for i in (0,2,4)]
new.diffuse_color=(rgb[0],rgb[1],rgb[2],1)
for on in ['MS1_core1_to_2','MS3_core34_to_5']:
    o=bpy.data.objects[on]
    for s in o.material_slots:
        if s.material==src: s.link='OBJECT' if False else s.link; s.material=new
r.filepath=OUT+'fix_ms_map2x.png'; bpy.ops.render.render(write_still=True)
print('FIXDONE', r.resolution_x, r.resolution_y, sc.display.shading.light, sc.view_settings.exposure)
