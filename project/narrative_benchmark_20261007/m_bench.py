import sys; sys.path.insert(0,'/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/oi_b0')
from tk import *
import colour
de=lambda a,b: float(colour.delta_E(np.asarray(a),np.asarray(b),method='CIE 2000'))
k9=np.load('ref_K9_A03.npy')
# A03 horizontal faces: sample slab tops / roof beam tops
rgba,cp=iso('core1_modern_building'); rgb=rgba[...,:3]; al=rgba[...,3]>0.5; lab=rgb2lab(rgb); X0,Y0=cp[0],cp[2]
def at(x,y,r=1.0):
    xa,xb=int((x-r-X0)*3),int((x+r-X0)*3)+1; ya,yb=int((y-r-Y0)*3),int((y+r-Y0)*3)+1
    m=al[ya:yb,xa:xb]; return np.median(lab[ya:yb,xa:xb][m],0)
pts={'roof beam top front':(780,392),'roof beam top left':(735,370),'ground slab top':(800,520),'ground slab top2':(830,505)}
for k,(x,y) in pts.items():
    v=at(x,y); print('A03',k,v.round(1),hexs(lab2rgb(v)))
bench=np.array([77.0,-4.9,-0.6])
# bench top vs front
rgba,cp=iso('support_core5_lab'); rgb=rgba[...,:3]; al=rgba[...,3]>0.5; lab=rgb2lab(rgb); X0,Y0=cp[0],cp[2]
def at2(x,y,r=1.5):
    xa,xb=int((x-r-X0)*3),int((x+r-X0)*3)+1; ya,yb=int((y-r-Y0)*3),int((y+r-Y0)*3)+1
    m=al[ya:yb,xa:xb]; return np.median(lab[ya:yb,xa:xb][m],0)
bt=at2(1000,735); bf=at2(1080,750); print('bench top',bt.round(1),hexs(lab2rgb(bt)),'front',bf.round(1),hexs(lab2rgb(bf)))
for nm,ref in [('A03 dark',k9[0]),('A03 mid',k9[1]),('A03 light',k9[2])]: print(' bench top vs',nm,round(de(bt,ref),1))
for nm,ref in [('K8',[99.8,-1.5,4.3]),('K2',[99.64,-2.55,7.16]),('K3',[97,-0.7,12]),('K7',[97.6,-1.1,11.6]),('K5',[58.9,-23.1,-14.9])]: print(' bench top vs',nm,round(de(bt,ref),1))
tok={'laboratory #527882':'#527882','labstone #B9C7C5':'#B9C7C5','modern_concrete #657B88':'#657B88'}
for k,h in tok.items(): print(k,'oklch',oklch(hex2rgb(h)).round(3))
