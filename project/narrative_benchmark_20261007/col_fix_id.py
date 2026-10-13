import bpy, json, sys
import numpy as np
OUT='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/oc2/idr/'
rho0=float(sys.argv[sys.argv.index('--')+1])
o=bpy.data.objects['COL_ruined']; me=o.data; n=len(me.polygons)
cen=np.zeros(n*3); me.polygons.foreach_get('center',cen); cen=cen.reshape(-1,3)
mi=np.zeros(n,dtype=np.int32); me.polygons.foreach_get('material_index',mi)
slots=[s.material.name for s in o.material_slots]
W=slots.index('RC.v12.colosseum_wall'); I=slots.index('RC.v12.colosseum_interior')
x0,x1=cen[:,0].min(),cen[:,0].max(); y0,y1=cen[:,1].min(),cen[:,1].max()
cx,cy=(x0+x1)/2,(y0+y1)/2; ax,ay=(x1-x0)/2,(y1-y0)/2
rho=np.sqrt(((cen[:,0]-cx)/ax)**2+((cen[:,1]-cy)/ay)**2)
chg=(mi==W)&(rho<rho0)
mi2=mi.copy(); mi2[chg]=I
me.polygons.foreach_set('material_index',mi2); me.update()
print('CHG',int(chg.sum()))
idm=json.load(open(OUT+'id_map.json'))
def s2l(v):
    v=v/255.0; return v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4
sc=bpy.context.scene; r=sc.render; vs=sc.view_settings; sh=sc.display.shading
vs.view_transform='Standard'; vs.look='None'; vs.exposure=0; vs.gamma=1
sh.light='FLAT'; sh.show_cavity=False; sh.show_shadows=False; sh.show_specular_highlight=False
sc.display.render_aa='OFF'; r.dither_intensity=0; r.resolution_percentage=72; r.film_transparent=True
r.image_settings.file_format='PNG'; r.image_settings.color_mode='RGBA'
for m in bpy.data.materials:
    if m.name in idm['mat_ids']:
        c=idm['mat_ids'][m.name]; m.diffuse_color=(s2l(c[0]),s2l(c[1]),s2l(c[2]),1)
keep={'COL_ruined','R3_colosseum_podium','R4_arena_skin'}
for ob in bpy.data.objects:
    ob.hide_render = ob.hide_render or (ob.name not in keep)
sh.color_type='MATERIAL'
r.filepath=OUT+'colfix_id_%s.png'%str(rho0); bpy.ops.render.render(write_still=True)
print('COLFIXDONE')
