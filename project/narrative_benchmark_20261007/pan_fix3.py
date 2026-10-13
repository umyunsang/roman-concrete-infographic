import bpy, json
import numpy as np
OUT='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/oc2/idr/'
o=bpy.data.objects['R8_pantheon']; me=o.data; n=len(me.polygons)
cen=np.zeros(n*3); me.polygons.foreach_get('center',cen); cen=cen.reshape(-1,3)
nor=np.zeros(n*3); me.polygons.foreach_get('normal',nor); nor=nor.reshape(-1,3)
area=np.zeros(n); me.polygons.foreach_get('area',area)
mi=np.zeros(n,dtype=np.int32); me.polygons.foreach_get('material_index',mi)
slots=[s.material.name for s in o.material_slots]; S=slots.index('RC.v12.roman_stone'); R=slots.index('RC.v12.roman_roof')
chg=np.zeros(n,bool); rep=[]
# portico slopes
for sx in [1,-1]:
    reg=(cen[:,1]<-0.55)&(sx*cen[:,0]>0.0)
    rf=reg&(mi==R)&(nor[:,2]>0.7)
    t=(nor[rf]*area[rf,None]).sum(0); t/=np.linalg.norm(t)
    d0=np.median(cen[rf]@t)
    on=reg&((nor@t)>np.cos(np.radians(12)))&(np.abs(cen@t-d0)<0.02)
    sel=on&(mi==S); chg|=sel
    rep.append({'slope':sx,'n':t.round(3).tolist(),'d0':round(float(d0),3),'roof_faces':int(rf.sum()),'stone_to_roof':int(sel.sum()),'stone_area_local':round(float(area[sel].sum()),4)})
# intermediate block roof: z-up plane at d~0.271
t=np.array([0,0,1.0]); on=((nor@t)>np.cos(np.radians(12)))&(np.abs(cen[:,2]-0.271)<0.015)
rp=on&(mi==R); lo=cen[rp,:2].min(0); hi=cen[rp,:2].max(0); mg=0.08*(hi-lo)+0.02
inb=np.all((cen[:,:2]>=lo-mg)&(cen[:,:2]<=hi+mg),axis=1); sel=on&(mi==S)&inb; chg|=sel
rep.append({'plane':'z=0.271','stone_to_roof':int(sel.sum()),'stone_area_local':round(float(area[sel].sum()),4)})
print('PANFIX3',json.dumps({'changed':int(chg.sum()),'rep':rep}))
mi2=mi.copy(); mi2[chg]=R; me.polygons.foreach_set('material_index',mi2); me.update()
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
for ob in bpy.data.objects:
    ob.hide_render = ob.hide_render or (ob.name!='R8_pantheon')
sh.color_type='MATERIAL'; r.filepath=OUT+'panfix3_id.png'; bpy.ops.render.render(write_still=True)
print('PANDONE')
