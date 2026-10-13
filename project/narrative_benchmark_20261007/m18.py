import numpy as np, json, warnings
warnings.filterwarnings('ignore')
from PIL import Image
from skimage import color, morphology, measure
idx=json.load(open('../nb_work/review_loop/obj_r11/assets_index.json'))
A={a['id']:a for a in idx['assets']}
a=A['road_ostiensis']; x0,x1,y0,y1=a['crop_pt']
iso=np.asarray(Image.open(a['files']['isolated_rgba'])).astype(float)/255
al=iso[...,3]>0.5; lab=color.rgb2lab(iso[...,:3])
curb=al&(lab[...,2]>9)&(lab[...,0]>70)
road=al
for yr in [(1325,1365),(1380,1415)]:
    print("window y",yr)
    for ypt in np.arange(yr[0],yr[1],1.5):
        r=int(round((ypt-y0)*3))
        cols=np.nonzero(road[r])[0]
        if len(cols)==0: continue
        cc=np.nonzero(curb[r])[0]
        # outer road edges
        print("  y %.1f road x %.1f-%.1f (w %.1f) curb px segments:"%(ypt,x0+cols.min()/3,x0+cols.max()/3,(cols.max()-cols.min())/3), end=' ')
        if len(cc):
            segs=np.split(cc,np.nonzero(np.diff(cc)>1)[0]+1)
            print([("%.1f-%.1f"%(x0+s[0]/3,x0+s[-1]/3)) for s in segs])
        else: print("none")
