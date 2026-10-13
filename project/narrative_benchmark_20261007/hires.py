import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.color import rgb2lab, deltaE_ciede2000
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx={a['id']:a for a in json.load(open(R+'assets_index.json'))['assets']}
oid=json.load(open('oid.json'))
final=np.load('final.npy')
full=Image.open(R+'full/full_map_pass.png').convert('RGB')
S=full.width/1191
def analyze(aid, box, label):
    x0,x1,y0,y1=box
    a=idx[aid]; cx0,cx1,cy0,cy1=a['crop_pt']
    al=np.array(Image.open(a['files']['isolated_rgba']))[...,3]>=128
    # crop region of full at 3px/pt (S≈3)
    u0=int(x0*S); u1=int(x1*S); v0=int(y0*S); v1=int(y1*S)
    img=np.array(full.crop((u0,v0,u1,v1))).astype(float)/255
    lab=rgb2lab(img)
    H,W=lab.shape[:2]
    vv,uu=np.mgrid[0:H,0:W]
    X=(u0+uu+0.5)/S; Y=(v0+vv+0.5)/S
    # M_A in this window
    au=np.clip(((X-cx0)*3).astype(int),0,al.shape[1]-1); av=np.clip(((Y-cy0)*3).astype(int),0,al.shape[0]-1)
    inside=((X>=cx0)&(X<cx1)&(Y>=cy0)&(Y<cy1))
    M=al[av,au]&inside
    core=ndi.binary_erosion(M,iterations=3)
    f=final[np.clip((Y*2).astype(int),0,final.shape[0]-1),np.clip((X*2).astype(int),0,final.shape[1]-1)]
    terr=(f==oid['T_land'])&~ndi.binary_dilation(M,iterations=6)
    tref=np.median(lab[terr],0)
    roadpx=core&(f!=oid['T_land'])
    # two clusters for road: dark (pavers) and light (curbs) by L
    Lr=lab[roadpx]; thr=np.median(Lr[:,0])
    pav=np.median(Lr[Lr[:,0]<=thr],0); cur=np.median(Lr[Lr[:,0]>np.percentile(Lr[:,0],90)],0)
    dT=deltaE_ciede2000(lab,np.broadcast_to(tref,lab.shape)); dP=deltaE_ciede2000(lab,np.broadcast_to(pav,lab.shape)); dC=deltaE_ciede2000(lab,np.broadcast_to(cur,lab.shape))
    tp=core&(dT<=5)&(dP>10)&(dC>10)
    labl,n=ndi.label(tp)
    sz=sorted((ndi.sum(tp,labl,range(1,n+1))/9).tolist(),reverse=True) if n else []
    print(label,aid,'terrain ref Lab',np.round(tref,1),'paver',np.round(pav,1),'curb',np.round(cur,1),'| terrain-like px in core: %.2f pt2 (%.3f%%), blobs>=0.5: %s'%(tp.sum()/9,100*tp.sum()/max(1,core.sum()),[round(s,2) for s in sz[:6]]))
analyze('road_ostiensis',(120,150,1385,1410),'coast-wedge')
analyze('road_appia',(860,915,968,990),'appia-start')
analyze('road_core_se_2',(715,750,995,1012),'se2-south')
analyze('road_core_w',(210,245,840,910),'core_w-bank')
analyze('road_appia',(845,1191,935,995),'appia-all')
analyze('road_core_se_2',(588,817,964,1027),'se2-all')
analyze('road_core_se',(841,965,864,983),'se-all')
analyze('road_ostiensis',(72,412,1005,1463),'ost-all')
