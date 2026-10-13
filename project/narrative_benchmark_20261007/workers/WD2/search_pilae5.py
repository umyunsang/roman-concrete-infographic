import sys, numpy as np
sys.path.insert(0, '.')
from layout_lib import *
C = Ctx(idmap=WD + '/workers/WD2/probe/idmap_proto3.npz')
land = C.mask_of(['T_land'])
harbor = ['L09_portus_lighthouse','L09_portus_mole','L12_harbor_pilae','R_via_ostiensis']
bg = ['T_land','L10_sea','W_water_marks','L02_tiber'] + harbor
other = (C.ids >= 0) & ~C.mask_of(bg)
text = C.text_mask(); ovl = C.ids_ovl >= 0
D = {'land': dist_to(land), 'other': dist_to(other), 'text': dist_to(text), 'ovl': dist_to(ovl),
     'road': dist_to(C.mask_of(['R_via_ostiensis'])), 'mole': dist_to(C.mask_of(['L09_portus_mole'])),
     'lh': dist_to(C.mask_of(['L09_portus_lighthouse']))}
mw = C.E['L12_harbor_pilae_mw']; loc0 = mw[:3,3]; rz0 = np.arctan2(mw[1,0], mw[0,0])
res=[]
for rz in [0.0, np.pi/8, np.pi/4, 3*np.pi/8]:
  for s in [0.7, 0.62, 0.55, 0.5, 0.45, 0.4]:
    base, Wv, P = C.silhouette('L12_harbor_pilae', loc=(loc0[0], loc0[1], 0), rot_z=rz0+rz, scale=0.451*s, dz=-0.74)
    ys, xs = np.nonzero(base); cx, cy = P[:,0].mean(), P[:,1].mean()
    for tx in np.arange(95, 230, 1.0):
        for ty in np.arange(1380, 1500, 1.0):
            sx, sy = int(round(tx-cx)), int(round(ty-cy))
            yy, xx = ys+sy, xs+sx
            a = {k: float(v[yy,xx].min()) for k,v in D.items()}
            if a['land']>=1.5 and a['text']>=4 and a['ovl']>=4 and a['mole']>=3.5 and a['lh']>=3.5 and a['road'] >= 0.8 and a['other']>=8:
                a.update(rz=round(float(rz),2), s=s, tx=tx, ty=ty, h=round(float(P[:,1].max()-P[:,1].min()),1), w=round(float(P[:,0].max()-P[:,0].min()),1),
                         loc=[round(float(loc0[0] + (tx-cx)*0),3)])
                res.append(a)
print('feasible', len(res))
res.sort(key=lambda a: (a['road'], -a['s']))
for a in res[:30]: print({k:(round(v,2) if isinstance(v,float) else v) for k,v in a.items()})
