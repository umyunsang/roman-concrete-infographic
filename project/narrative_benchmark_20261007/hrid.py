import bpy, json, sys
sc=bpy.context.scene; r=sc.render; sh=sc.display.shading
print('RES', r.resolution_x, r.resolution_y, r.resolution_percentage, r.engine)
regions=json.loads(sys.argv[sys.argv.index('--')+1])
out=sys.argv[sys.argv.index('--')+2]
base=r.resolution_x/1191.0
r.resolution_percentage=int(round(100*9.0/base))  # ~10 px/pt
print('PCT', r.resolution_percentage, 'px/pt', base*r.resolution_percentage/100)
r.use_border=True; r.use_crop_to_border=True
r.image_settings.file_format='PNG'; r.image_settings.color_mode='RGBA'; r.film_transparent=True
r.dither_intensity=0
sh.light='FLAT'; sh.color_type='OBJECT'
for n in ['show_shadows','show_cavity','show_object_outline','show_specular_highlight','show_xray']:
    try: setattr(sh,n,False)
    except Exception: pass
sc.display.render_aa='OFF'
vs=sc.view_settings; vs.view_transform='Standard'; vs.look='None'; vs.exposure=0; vs.gamma=1
# overlay collections hidden (map pass only)
for c in bpy.data.collections:
    if c.name in ('80_SHAPES','81_NOSHADOW','85_HEADER'): c.hide_render=True
for name,(x0,x1,y0,y1,target) in regions.items():
    for o in bpy.data.objects:
        if o.type in ('MESH','CURVE','FONT','SURFACE','META'):
            if o.name=='T_land': o.color=(1,0,0,1)
            elif o.name in target: o.color=(0,1,0,1)
            else: o.color=(0,0,1,1)
    r.border_min_x=x0/1191; r.border_max_x=x1/1191; r.border_min_y=1-y1/1684; r.border_max_y=1-y0/1684
    r.filepath=out+'/'+name+'.png'
    bpy.ops.render.render(write_still=True)
    print('DONE',name)
