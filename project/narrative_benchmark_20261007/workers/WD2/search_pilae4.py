import sys, numpy as np
sys.path.insert(0, '.')
from layout_lib import *
C = Ctx()
land = C.mask_of(['T_land'])
harbor_names = ['L09_portus_lighthouse','L09_portus_mole','L12_harbor_pilae','R_via_ostiensis']
bg = ['T_land','L10_sea','W_water_marks','L02_tiber'] + harbor_names
other = (C.ids >= 0) & ~C.mask_of(bg)
text = C.text_mask(); ovl = C.ids_ovl >= 0
road = C.mask_of(['R_via_ostiensis'])
D = {'land': dist_to(land), 'other': dist_to(other), 'text': dist_to(text), 'ovl': dist_to(ovl), 'road': dist_to(road)}
mole, _, _ = C.silhouette('L09_portus_mole', dz=-0.74)
D['mole'] = dist_to(mole)
mw = C.E['L12_harbor_pilae_mw']; loc0 = mw[:3,3]; rz0 = np.arctan2(mw[1,0], mw[0,0])
res=[]
for rz in [0.0, np.pi/8, np.pi/4, 3*np.pi/8]:
  for s in [0.6, 0.55, 0.5, 0.45, 0.4]:
    base, Wv, P = C.silhouette('L12_harbor_pilae', loc=(loc0[0], loc0[1], 0), rot_z=rz0+rz, scale=0.451*s, dz=-0.74)
    ys, xs = np.nonzero(base); cx, cy = P[:,0].mean(), P[:,1].mean()
    for tx in np.arange(110, 215, 1.0):
        for ty in np.arange(1395, 1490, 1.0):
            sx, sy = int(round(tx-cx)), int(round(ty-cy))
            yy, xx = ys+sy, xs+sx
            a = {k: float(v[yy,xx].min()) for k,v in D.items()}
            if a['land']>=2 and a['text']>=4 and a['ovl']>=4 and a['mole']>=3 and a['road']>=3:
                a.update(rz=round(float(rz),2), s=s, tx=tx, ty=ty, h=float(P[:,1].max()-P[:,1].min()), w=float(P[:,0].max()-P[:,0].min()))
                res.append(a)
print('feasible', len(res))
res.sort(key=lambda a: (-a['s'], -min(a['land'],a['mole'],a['road'])))
for a in res[:25]: print({k:(round(v,2) if isinstance(v,float) else v) for k,v in a.items()})
