import numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets/'
def lin(c):
    c=c/255.; return np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
def Ls(l):
    Y=l@np.array([.2126,.7152,.0722]); return np.where(Y>.008856,116*np.cbrt(Y)-16,903.3*Y)
for a in ['road_core_se','road_core_se_2','road_appia','road_ostiensis','water_tiber','water_sea']:
    ctx=np.asarray(Image.open(R+a+'/context.png').convert('RGB')).astype(float)
    rgba=np.asarray(Image.open(R+a+'/isolated_rgba.png').convert('RGBA')).astype(float)
    iso=np.asarray(Image.open(R+a+'/isolated.png').convert('RGB')).astype(float)
    M=rgba[...,3]>=128; Lc=Ls(lin(ctx)); Li=Ls(lin(iso)); X=M&(abs(Lc-Li)>=6)
    dl=(Lc-Li)[X]
    lab,n=ndi.label(ndi.binary_closing(X,iterations=3))
    sizes=ndi.sum(X,lab,range(1,n+1))/9
    order=np.argsort(sizes)[::-1][:4]
    objs=ndi.find_objects(lab)
    desc=[]
    for i in order:
        sl=objs[i]; desc.append('%.0fpt2@x%.0f-%.0f,y%.0f-%.0f(px) dL=%.1f'%(sizes[i],sl[1].start,sl[1].stop,sl[0].start,sl[0].stop, np.median((Lc-Li)[(lab==i+1)&X])))
    print(a,'excluded %.0f pt2; darker share %.2f; top blobs:'%(X.sum()/9,(dl<0).mean()),desc)
    v=(ctx*0.5+127).astype(np.uint8); v[X&(Lc<Li)]=[220,0,0]; v[X&(Lc>Li)]=[0,0,220]
    Image.fromarray(v).save('excl_'+a+'.png')
