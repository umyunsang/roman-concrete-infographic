import json, sys, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.color import rgb2lab, deltaE_ciede2000
ROOT=sys.argv[1]
idx=json.load(open(os.path.join(ROOT,'assets_index.json'))); S=idx['crop_scale']
A={a['id']:a for a in idx['assets']}
def load(aid):
    d=os.path.join(ROOT,'assets',aid)
    ctx=np.asarray(Image.open(os.path.join(d,'context.png')).convert('RGB'))
    iso=np.asarray(Image.open(os.path.join(d,'isolated.png')).convert('RGB'))
    al=np.asarray(Image.open(os.path.join(d,'isolated_rgba.png')))[...,3]
    lab=rgb2lab(ctx); labi=rgb2lab(iso)
    V=(al>=128)&(np.abs(lab[...,0]-labi[...,0])<6)
    return ctx,lab,V,al
rep={}
for a in idx['assets']:
    ctx,lab,V,al=load(a['id'])
    if V.sum()<20: continue
    rep[a['id']]=np.median(lab[V],axis=0)
core=['core1_modern_building','core2_hot_mixing','detail_core3_lime_specimen','detail_core4_three_cubes','support_core5_lab']
def bbox(a): return a['bbox_visible_final_pt']
def dist(b1,b2):
    dx=max(0,max(b1[0],b2[0])-min(b1[1],b2[1])); dy=max(0,max(b1[2],b2[2])-min(b1[3],b2[3])); return (dx*dx+dy*dy)**.5
print('== CORE rep color vs FOA objects (dE00 < 12 shown)')
for c in core:
    for k,v in rep.items():
        if k in core or A[k]['role'] in ('도형',) : continue
        if dist(bbox(A[c]),bbox(A[k]))<=198.5:
            de=deltaE_ciede2000(rep[c][None],v[None])[0]
            if de<12: print(c,k,round(float(de),1))
print('== homogeneity')
for g in ['fields_e','fields_nw','fields_sw','fields_se','fields_w','fields_s','trees_s','trees_se','road_core_s','landmark_apennines']:
    ctx,lab,V,al=load(g)
    labm,n=ndi.label(al>=128)
    Ls=[];Cs=[]
    for i in range(1,n+1):
        m=(labm==i)&V
        if m.sum()<20*S*S: continue
        Ls.append(np.median(lab[...,0][m])); Cs.append(np.median(np.hypot(lab[...,1][m],lab[...,2][m])))
    if len(Ls)>=3:
        q=np.percentile(Ls,[10,25,75,90]); qc=np.percentile(Cs,[10,25,75,90])
        print(g,'ncomp',len(Ls),'L* IQR %.1f p10-90 %.1f'%(q[2]-q[1],q[3]-q[0]),'C* IQR %.1f p10-90 %.1f'%(qc[2]-qc[1],qc[3]-qc[0]))
    else: print(g,'ncomp',len(Ls))
print('== stroke widths (pt) leaders/pins/markers/section')
for g in ['shape_d2_leader','shape_pin_harbor','shape_pin_pompeii','shape_d3_section','shape_core1_marker']:
    al=np.asarray(Image.open(os.path.join(ROOT,'assets',g,'isolated_rgba.png')))[...,3]>=128
    dt=ndi.distance_transform_edt(al)
    sk=dt[al]
    print(g,'max half-width pt %.2f'%(sk.max()/S),'p50 local width pt %.2f'%(2*np.percentile(sk,50)/S), 'p90 %.2f'%(2*np.percentile(sk,90)/S))
