import sys, json; sys.path.insert(0,'/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/oc2/lib')
from cl import *
from PIL import Image
import numpy as np
from scipy import ndimage as ndi
O='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/oc2/'
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets/'
aid=sys.argv[1]; mats=sys.argv[2].split(','); scale=int(sys.argv[3]) if len(sys.argv)>3 else 3
g=json.load(open(O+'align.json'))[aid]; idm=json.load(open(O+'idr/id_map.json'))
iso=np.array(Image.open(B+aid+'/isolated_rgba.png')).astype(float)
rgb=iso[...,:3]; a=iso[...,3]
m=np.array(Image.open(O+'idr/iso_mat_'+aid+'.png'))[g['Y']:g['Y']+g['h'],g['X']:g['X']+g['w']]
L=lab(rgb)[...,0]; med=ndi.median_filter(L,size=11); dev=L-med
ov=np.array(Image.open(B+aid+'/isolated.png').convert('RGB')).astype(float)
for n in mats:
  c=idm['mat_ids'][n]; pm=(m[...,0]==c[0])&(m[...,1]==c[1])&(m[...,2]==c[2])&(a>=254)
  sin=ndi.binary_erosion(pm,iterations=5)
  for sign,col in [(1,(0,90,255)),(-1,(255,0,0))]:
    mk=sin&(sign*dev>6); lbl,k=ndi.label(mk); sizes=ndi.sum(mk,lbl,range(1,k+1))
    big=[i+1 for i,s in enumerate(sizes) if s>=16]
    ov[np.isin(lbl,big)]=col
    print(n,'sign',sign,'S-part px',int(sin.sum()),'comps>=1.77pt2',len(big))
Image.fromarray(ov.astype(np.uint8)).resize((ov.shape[1]*scale,ov.shape[0]*scale),Image.NEAREST).save(O+aid+'_blot.png')
