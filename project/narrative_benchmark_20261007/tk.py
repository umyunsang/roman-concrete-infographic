import json, numpy as np
from PIL import Image
RL='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
IDX=json.load(open(RL+'obj_r11/assets_index.json'))
ASSETS={a['id']:a for a in IDX['assets']}
TS={t[0]:t for t in json.load(open(RL+'text_spec_r11.json'))['texts']}
_cache={}
def img(name):
    if name not in _cache:
        _cache[name]=np.asarray(Image.open(RL+'r11/'+name+'.png').convert('RGB')).astype(np.float64)/255.
    return _cache[name]
def srgb2lin(c): return np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
def lin2srgb(c): return np.where(c<=0.0031308,c*12.92,1.055*np.power(np.clip(c,0,None),1/2.4)-0.055)
M=np.array([[0.4124564,0.3575761,0.1804375],[0.2126729,0.7151522,0.0721750],[0.0193339,0.1191920,0.9503041]])
WN=np.array([0.95047,1.0,1.08883])
def rgb2lab(rgb):
    lin=srgb2lin(np.asarray(rgb,dtype=np.float64)); xyz=lin@M.T/WN
    f=np.where(xyz>0.008856,np.cbrt(xyz),7.787*xyz+16/116)
    L=116*f[...,1]-16; a=500*(f[...,0]-f[...,1]); b=200*(f[...,1]-f[...,2])
    return np.stack([L,a,b],-1)
def rgb2oklab(rgb):
    lin=srgb2lin(np.asarray(rgb,dtype=np.float64))
    M1=np.array([[0.4122214708,0.5363325363,0.0514459929],[0.2119034982,0.6806995451,0.1073969566],[0.0883024619,0.2817188376,0.6299787005]])
    M2=np.array([[0.2104542553,0.7936177850,-0.0040720468],[1.9779984951,-2.4285922050,0.4505937099],[0.0259040371,0.7827717662,-0.8086757660]])
    lms=np.cbrt(lin@M1.T); return lms@M2.T
def oklch(rgb):
    o=rgb2oklab(rgb); L=o[...,0]; C=np.hypot(o[...,1],o[...,2]); h=np.degrees(np.arctan2(o[...,2],o[...,1]))%360
    return np.stack([L,C,h],-1)
def hex2rgb(h): h=h.lstrip('#'); return np.array([int(h[i:i+2],16) for i in (0,2,4)])/255.
def de2000(lab1,lab2):
    import colour
    return colour.delta_E(np.asarray(lab1),np.asarray(lab2),method='CIE 2000')
def crop(name,x0,x1,y0,y1,s=2):
    im=img(name); return im[int(round(y0*s)):int(round(y1*s)),int(round(x0*s)):int(round(x1*s))]
def iso(aid,kind='isolated_rgba'):
    a=ASSETS[aid]; p=a['files']['isolated_rgba'] if kind=='isolated_rgba' else a['files'][kind]
    return np.asarray(Image.open(p).convert('RGBA')).astype(np.float64)/255., a['crop_pt']
def ctx3(aid):
    a=ASSETS[aid]; return np.asarray(Image.open(a['files']['context']).convert('RGB')).astype(np.float64)/255., a['crop_pt']
def text_ink(nid, thr=0.06, pad=2):
    t=TS[nid]; x,y,w,h=t[1]
    P=crop('poster_2x',x-pad,x+w+pad,y-pad,y+h+pad); Q=crop('map_only_2x',x-pad,x+w+pad,y-pad,y+h+pad)
    d=np.abs(P-Q).max(-1)>thr
    ys,xs=np.nonzero(d)
    if len(xs)==0: return None
    X0=x-pad; Y0=y-pad
    return (X0+xs.min()/2, X0+(xs.max()+1)/2, Y0+ys.min()/2, Y0+(ys.max()+1)/2), d
