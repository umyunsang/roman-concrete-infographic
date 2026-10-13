import sys, numpy as np
sys.path.insert(0, '.')
from layout_lib import *
from scipy import ndimage
C = Ctx()
land = C.mask_of(['T_land'])
harbor_names = ['L09_portus_lighthouse','L09_portus_mole','L12_harbor_pilae','R_via_ostiensis']
bg = ['T_land','L10_sea','W_water_marks','L02_tiber'] + harbor_names
other = (C.ids >= 0) & ~C.mask_of(bg)
text = C.text_mask(); ovl = C.ids_ovl >= 0
d_land, d_other, d_text, d_ovl = dist_to(land), dist_to(other), dist_to(text), dist_to(ovl)
road = C.mask_of(['R_via_ostiensis']); d_road = dist_to(road)
mole, _, _ = C.silhouette('L09_portus_mole', dz=-0.74)
lh, _, _ = C.silhouette('L09_portus_lighthouse', dz=-0.74)
d_mole = dist_to(mole); d_lh = dist_to(lh)
mw = C.E['L12_harbor_pilae_mw']; loc0 = mw[:3,3]; rz0 = np.arctan2(mw[1,0], mw[0,0])
res = []
def shift(m, sx, sy):
    return ndimage.shift(m.astype(np.uint8), (sy, sx), order=0, mode='constant', cval=0).astype(bool)
for rz in [0.0, np.pi/4]:
  for s in [0.75, 0.65, 0.55, 0.47, 0.4]:
    base, Wv, P = C.silhouette('L12_harbor_pilae', loc=(loc0[0], loc0[1], 0), rot_z=rz0+rz, scale=0.451*s, dz=-0.74)
    c0 = C.project([[loc0[0], loc0[1], -0.74]])[0]
    for dx in np.arange(-26, 2.01, 0.75):
        for dy in np.arange(-26, 8.01, 0.75):
            c1 = C.project([[loc0[0]+dx, loc0[1]+dy, -0.74]])[0]
            sx, sy = np.round(c1 - c0).astype(int)
            bb=[P[:,0].min()+sx,P[:,0].max()+sx,P[:,1].min()+sy,P[:,1].max()+sy]
            if bb[0]<20 or bb[1]>620 or bb[3]>1670: continue
            sil = shift(base, sx, sy)
            g_in = min(gap(sil,d_mole), gap(sil,d_lh))
            if g_in < 4 or g_in > 22: continue
            a = dict(rz=round(float(rz),2), s=s, dx=float(dx), dy=float(dy), land=gap(sil,d_land), other=gap(sil,d_other), text=gap(sil,d_text), ovl=gap(sil,d_ovl),
                     road=gap(sil,d_road), g_in=g_in, bbox=[round(float(v),1) for v in bb])
            if a['land']>=3 and a['text']>=4 and a['ovl']>=4 and a['road']>=4 and a['other']>=8:
                res.append(a)
print('feasible', len(res))
res.sort(key=lambda a: (-a['s'], a['g_in']))
for a in res[:40]: print({k:(round(v,2) if isinstance(v,float) else v) for k,v in a.items()})
