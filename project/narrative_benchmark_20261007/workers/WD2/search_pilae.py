import sys, numpy as np, time
sys.path.insert(0, '.')
from layout_lib import *
from scipy import ndimage
C = Ctx()
land = C.mask_of(['T_land'])
harbor_names = ['L09_portus_lighthouse','L09_portus_mole','L12_harbor_pilae','R_via_ostiensis']
bg = ['T_land','L10_sea','W_water_marks','L02_tiber'] + harbor_names
other = (C.ids >= 0) & ~C.mask_of(bg)
text = C.text_mask()
ovl = C.ids_ovl >= 0
d_land, d_other, d_text, d_ovl = dist_to(land), dist_to(other), dist_to(text), dist_to(ovl)
road = C.mask_of(['R_via_ostiensis'])
mole, _, _ = C.silhouette('L09_portus_mole', dz=-0.74)
lh, _, _ = C.silhouette('L09_portus_lighthouse', dz=-0.74)
d_mole = dist_to(mole); d_lh = dist_to(lh)
print('harbor(lowered) -> other', gap(mole|lh, d_other), 'lh->other', gap(lh,d_other))
mw = C.E['L12_harbor_pilae_mw']; loc0 = mw[:3,3]
res = []
def shift(m, sx, sy):
    return ndimage.shift(m.astype(np.uint8), (sy, sx), order=0, mode='constant', cval=0).astype(bool)
for s in [0.75, 0.68, 0.6, 0.52]:
    base, Wv, P = C.silhouette('L12_harbor_pilae', loc=(loc0[0], loc0[1], 0), scale=0.451*s, dz=-0.74)
    c0 = C.project([[loc0[0], loc0[1], -0.74]])[0]
    for dx in np.arange(-14, 2.01, 0.5):
        for dy in np.arange(-14, 6.01, 0.5):
            c1 = C.project([[loc0[0]+dx, loc0[1]+dy, -0.74]])[0]
            sx, sy = np.round(c1 - c0).astype(int)
            sil = shift(base, sx, sy)
            if not sil.any(): continue
            a = dict(s=s, dx=float(dx), dy=float(dy), land=gap(sil,d_land), other=gap(sil,d_other), text=gap(sil,d_text), ovl=gap(sil,d_ovl),
                     mole=gap(sil,d_mole), lh=gap(sil,d_lh), road=float((sil&road).sum()),
                     bbox=[round(float(P[:,0].min()+sx),1),round(float(P[:,0].max()+sx),1),round(float(P[:,1].min()+sy),1),round(float(P[:,1].max()+sy),1)])
            g_in = min(a['mole'], a['lh'])
            if a['land']>=3 and a['text']>=4 and a['ovl']>=4 and a['road']==0 and g_in>=4:
                a['g_in']=g_in; a['g_out']=min(a['other'], 40.0); a['ratio']=a['g_out']/max(g_in,11.4)
                res.append(a)
print('feasible', len(res))
res.sort(key=lambda a: (-min(a['ratio'],2.5), -a['s'], a['g_in']))
for a in res[:30]: print({k:(round(v,2) if isinstance(v,float) else v) for k,v in a.items()})
