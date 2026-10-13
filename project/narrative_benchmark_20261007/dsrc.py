import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx=json.load(open(R+'assets_index.json')); S=3.0
def lin(c):
    c=c/255.0; return np.where(c<=.04045, c/12.92, ((c+.055)/1.055)**2.4)
def Lstar(l):
    Y=l@np.array([.2126,.7152,.0722]); return np.where(Y>.008856, 116*np.cbrt(Y)-16, 903.3*Y)
A={a['id']:a for a in idx['assets']}
for aid in ['landmark_pantheon','road_core_nw','road_core_w','road_core_sw','core1_modern_building','detail_core3_lime_specimen','detail_core4_three_cubes','landmark_colosseum']:
    f=A[aid]['files']
    ctx=np.asarray(Image.open(f['context']).convert('RGB')).astype(float); iso=np.asarray(Image.open(f['isolated']).convert('RGB')).astype(float)
    rgba=np.asarray(Image.open(f['isolated_rgba']).convert('RGBA'))
    Lc=Lstar(lin(ctx)); Li=Lstar(lin(iso)); M=rgba[...,3]>=128; V=M&(np.abs(Lc-Li)<6)
    I=ndi.binary_erosion(V, iterations=3)
    out={}
    for nm,L in [('ctx',Lc),('iso',Li)]:
        N=ndi.gaussian_filter(L*V,6)/np.maximum(ndi.gaussian_filter(V*1.0,6),1e-6)
        diff=(L-N)
        hit=(np.abs(diff)>8)&I
        out[nm]=(hit.sum()/I.sum(), (hit&(diff<0)).sum()/max(hit.sum(),1))
        if nm=='ctx':
            Ld=L[hit&(diff<0)]; Lb=L[hit&(diff>0)]
            dd=diff[hit]
            extra=' dark-hit L* med %.1f (P10 %.1f), bright-hit L* med %.1f, body L* med %.1f, |diff| med %.1f'%(np.median(Ld) if Ld.size else -1, np.percentile(Ld,10) if Ld.size else -1, np.median(Lb) if Lb.size else -1, np.median(L[I]), np.median(np.abs(dd)))
            # threshold sensitivity
            sens=[ ( t, ((np.abs(diff)>t)&I).sum()/I.sum()) for t in (8,10,12,14)]
            # D when clamping dark pixels up by X (simulate joints raised)
    print(aid, {k:(round(v[0],4), round(v[1],2)) for k,v in out.items()}, extra)
    print('   thr sens', [(t,round(x,4)) for t,x in sens])
