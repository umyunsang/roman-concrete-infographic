import numpy as np
from PIL import Image
def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(np.float64)/255.0
def lin(c):
    return np.where(c<=0.04045, c/12.92, ((c+0.055)/1.055)**2.4)
def Lstar(rgb):
    l=lin(rgb); Y=l[...,0]*0.2126+l[...,1]*0.7152+l[...,2]*0.0722
    return np.where(Y>0.008856, 116*np.cbrt(Y)-16, 903.3*Y)
def lab(rgb):
    l=lin(rgb)
    M=np.array([[0.4124564,0.3575761,0.1804375],[0.2126729,0.7151522,0.0721750],[0.0193339,0.1191920,0.9503041]])
    xyz=l@M.T; wp=np.array([0.95047,1.0,1.08883]); t=xyz/wp
    f=np.where(t>0.008856, np.cbrt(t), 7.787*t+16/116)
    L=116*f[...,1]-16; a=500*(f[...,0]-f[...,1]); b=200*(f[...,1]-f[...,2])
    return np.stack([L,a,b],-1)
