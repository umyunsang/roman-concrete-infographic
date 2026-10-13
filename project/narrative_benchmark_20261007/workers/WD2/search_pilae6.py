import sys, numpy as np
sys.path.insert(0, '.')
from layout_lib import *
C = Ctx(idmap=WD + '/workers/WD2/probe/idmap_proto3.npz')
G = np.load('probe/landgrid.npz'); Z, gx, gy = G['Z'], G['xs'], G['ys']
def on_land(P, buf=0.1):
    hit = np.zeros(len(P), bool)
    for ox, oy in [(0,0),(buf,0),(-buf,0),(0,buf),(0,-buf)]:
        i = np.clip(np.round((P[:,0]+ox-gx[0])/0.05).astype(int), 0, len(gx)-1); j = np.clip(np.round((P[:,1]+oy-gy[0])/0.05).astype(int), 0, len(gy)-1)
        hit |= ~np.isnan(Z[j, i])
    return hit
harbor = ['L09_portus_lighthouse','L09_portus_mole','L12_harbor_pilae','R_via_ostiensis']
bg = ['T_land','L10_sea','W_water_marks','L02_tiber'] + harbor
other = (C.ids >= 0) & ~C.mask_of(bg)
text = C.text_mask(); ovl = C.ids_ovl >= 0
D = {'other': dist_to(other), 'text': dist_to(text), 'ovl': dist_to(ovl),
     'road': dist_to(C.mask_of(['R_via_ostiensis'])), 'mole': dist_to(C.mask_of(['L09_portus_mole'])),
     'lh': dist_to(C.mask_of(['L09_portus_lighthouse']))}
mw = C.E['L12_harbor_pilae_mw']; loc0 = mw[:3,3]; rz0 = np.arctan2(mw[1,0], mw[0,0])
res=[]
for rz in [0.0, np.pi/8, np.pi/4, 3*np.pi/8]:
  for s in [0.7, 0.62, 0.55, 0.5, 0.45]:
    base, Wv, P = C.silhouette('L12_harbor_pilae', loc=(loc0[0], loc0[1], 0), rot_z=rz0+rz, scale=0.451*s, dz=-0.74)
    ys, xs = np.nonzero(base)
    zb = Wv[:,2]; foot = Wv[zb < zb.min()+0.05][:, :2] - loc0[:2]
    c0 = C.project([[loc0[0], loc0[1], -0.74]])[0]
    for wx in np.arange(28.0, 42.0, 0.1):
        for wy in np.arange(-92.0, -80.0, 0.1):
            c1 = C.project([[wx, wy, -0.74]])[0]
            sx, sy = int(round(c1[0]-c0[0])), int(round(c1[1]-c0[1]))
            if not (90 < c1[0] < 240 and 1380 < c1[1] < 1500): continue
            yy, xx = ys+sy, xs+sx
            a = {k: float(v[yy,xx].min()) for k,v in D.items()}
            if not (a['text']>=4 and a['ovl']>=4 and a['mole']>=3.5 and a['lh']>=3.5 and a['road']>=0.8 and a['other']>=8): continue
            if on_land(foot + [wx, wy]).any(): continue
            a.update(rz=round(float(rz),3), s=s, wx=round(float(wx),2), wy=round(float(wy),2), scr=[round(float(c1[0]),1), round(float(c1[1]),1)])
            res.append(a)
print('feasible', len(res))
res.sort(key=lambda a: (max(a['road'],5.0), -a['s'], -min(a['mole'], a['lh'])))
for a in res[:30]: print({k:(round(v,2) if isinstance(v,float) else v) for k,v in a.items()})
