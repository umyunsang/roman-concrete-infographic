import bpy, json, sys
import numpy as np
OUT='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/oc2/idr/'
o=bpy.data.objects['R8_pantheon']; me=o.data; n=len(me.polygons)
cen=np.zeros(n*3); me.polygons.foreach_get('center',cen); cen=cen.reshape(-1,3)
nor=np.zeros(n*3); me.polygons.foreach_get('normal',nor); nor=nor.reshape(-1,3)
area=np.zeros(n); me.polygons.foreach_get('area',area)
mi=np.zeros(n,dtype=np.int32); me.polygons.foreach_get('material_index',mi)
slots=[s.material.name for s in o.material_slots]
S=slots.index('RC.v12.roman_stone'); R=slots.index('RC.v12.roman_roof')
chg=np.zeros(n,bool); report=[]
for target in [np.array([0.5,0,0.866]),np.array([-0.5,0,0.866]),np.array([0,0,1.0])]:
    t=target/np.linalg.norm(target)
    near=(nor@t)>np.cos(np.radians(12))
    roofp=near&(mi==R)
    if roofp.sum()==0: continue
    d=cen[roofp]@t
    # plane offsets can be multi-modal (dome top vs intermediate roof) -> histogram peaks
    hist,ed=np.histogram(d,bins=60)
    peaks=[(ed[i]+ed[i+1])/2 for i in np.argsort(hist)[::-1][:6] if hist[i]>=20]
    for pk in peaks:
        on=near&(np.abs(cen@t-pk)<0.012)
        cand=on&(mi==S)
        # restrict to xy-extent of roof faces on that plane (+5% margin)
        rp=on&(mi==R)
        if rp.sum()<20: continue
        lo=cen[rp,:2].min(0); hi=cen[rp,:2].max(0); mg=0.08*(hi-lo)+0.02
        inb=np.all((cen[:,:2]>=lo-mg)&(cen[:,:2]<=hi+mg),axis=1)
        sel=cand&inb
        chg|=sel
        report.append({'n':t.round(3).tolist(),'d':round(float(pk),3),'roof_faces':int(rp.sum()),'stone_to_roof':int(sel.sum()),'stone_area':round(float(area[sel].sum()),4)})
print('PANFIX',json.dumps({'changed':int(chg.sum()),'planes':report}))
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
sh.color_type='MATERIAL'; r.filepath=OUT+'panfix_id.png'; bpy.ops.render.render(write_still=True)
print('PANDONE')
