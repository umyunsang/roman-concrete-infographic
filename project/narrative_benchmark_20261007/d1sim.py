import json, numpy as np
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx=json.load(open(R+'assets_index.json')); A={a['id']:a for a in idx['assets']}
paper=np.array([0.0040323,0.03181737])
def lin(c):
    c=np.asarray(c,float)/255.0; return np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
def Ls(l):
    Y=l@np.array([.2126,.7152,.0722]); return np.where(Y>.008856,116*np.cbrt(Y)-16,903.3*Y)
M1=np.array([[0.4122214708,0.5363325363,0.0514459929],[0.2119034982,0.6806995451,0.1073969566],[0.0883024619,0.2817188376,0.6299787005]])
M2=np.array([[0.2104542553,0.7936177850,-0.0040720468],[1.9779984951,-2.4285922050,0.4505937099],[0.0259040371,0.7827717662,-0.8086757660]])
def oklab(l): return np.cbrt(l@M1.T)@M2.T
def oklab2srgb(o):
    lms=(o@np.linalg.inv(M2).T)**3; l=lms@np.linalg.inv(M1).T; l=np.clip(l,0,1)
    s=np.where(l<=0.0031308,12.92*l,1.055*l**(1/2.4)-0.055); return np.round(s*255).astype(int)
def hexs(rgb): return '#%02X%02X%02X'%tuple(rgb)
a=A['detail_d1_seawater']; f=a['files']
ctx=np.asarray(Image.open(f['context']).convert('RGB')).astype(float)
iso=np.asarray(Image.open(f['isolated']).convert('RGB')).astype(float)
al=np.asarray(Image.open(f['isolated_rgba']))[...,3]
lc=lin(ctx); Lc=Ls(lc); M=al>=128; V=M&(abs(Lc-Ls(lin(iso)))<6)
ok=oklab(lc); C=np.hypot(ok[...,1],ok[...,2]); h=np.arctan2(ok[...,2],ok[...,1]); hd=(np.degrees(h)+360)%360
blue=V&(hd>=180)&(hd<=270)
water=blue&(C>=0.06); tank=blue&(C<0.06)
print('V px',V.sum(),'water %.3f tank %.3f'%(water.sum()/V.sum(),tank.sum()/V.sum()))
print('tank median C %.3f, water median C %.3f'%(np.median(C[tank]),np.median(C[water])))
def kc(ft,fw):
    o=ok.copy()
    for m,fac in ((tank,ft),(water,fw)):
        o[m,1]*=fac; o[m,2]*=fac
    d=np.linalg.norm(o[...,1:]-paper,axis=-1)[V]; return np.percentile(d,90)
for ft in [1.0,0.5,0.3,0.0]:
    row=[]
    for fw in [1.0,0.8,0.7,0.6,0.5,0.4]:
        row.append('%.4f'%kc(ft,fw))
    print('tank x%.1f :'%ft,' '.join(row),' (water x1.0 .8 .7 .6 .5 .4)')
for name,hx,fac in [('tank #657B88',(0x65,0x7B,0x88),0.3),('tank #657B88',(0x65,0x7B,0x88),0.0),('water #3F9DAA',(0x3F,0x9D,0xAA),0.5),('water #3F9DAA',(0x3F,0x9D,0xAA),0.6)]:
    o=oklab(lin(hx)); o2=o.copy(); o2[1:]*=fac
    print(name,'x%.1f C %.3f -> %.3f'%(fac,np.hypot(*o[1:]),np.hypot(*o2[1:])),hexs(oklab2srgb(o2)))
