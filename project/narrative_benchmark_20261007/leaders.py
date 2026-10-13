import json, numpy as np
from scipy import ndimage as ndi
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
A=np.load('assetmap2x.npy'); F=np.load('figshape2x.npy')
O=np.load('objmap2x.npy'); objs=json.load(open('objs_order.json'))
assets=json.load(open('assets_order.json')); aidx={a:i+1 for i,a in enumerate(assets)}
M=np.array(Image.open(R+'r11/map_only_2x.png').convert('RGB')).astype(int)
def pinfo(name):
    m=A==aidx[name]; ys,xs=np.nonzero(m)
    print(name,'bbox pt',xs.min()/2,xs.max()/2,ys.min()/2,ys.max()/2,'centroid',xs.mean()/2,ys.mean()/2,'area',m.sum()/4)
    return m
for pin,target,objname in [('shape_pin_harbor','support_harbor','L09_portus_mole'),('shape_pin_pompeii','support_pompeii_site','L08_pompeii_site')]:
    pm=pinfo(pin)
    tm=A==aidx[target]
    D=ndi.distance_transform_edt(~tm)/2
    ys,xs=np.nonzero(pm)
    print('  pin->target min dist',D[ys,xs].min(),'max',D[ys,xs].max(), 'centroid dist', D[int(ys.mean()),int(xs.mean())])
    # what's under/around pin: neighbours within 3pt ring
    dil=ndi.binary_dilation(pm,iterations=6)&~pm
    u,c=np.unique(A[dil],return_counts=True)
    print('  ring assets',[(assets[i-1] if i>0 else 'none',int(n)) for i,n in zip(u,c)])
    ou,oc=np.unique(O[dil],return_counts=True)
    print('  ring objs',[(objs[i-1] if 0<i<=len(objs) else i,int(n)) for i,n in zip(ou,oc)])
