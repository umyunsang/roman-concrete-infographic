import numpy as np, sys
def lin(c): return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def enc(l): l=np.clip(l,0,1); return np.where(l <= 0.0031308, 12.92*l, 1.055*l**(1/2.4)-0.055)
M1i=np.linalg.inv(np.array([[0.4122214708,0.5363325363,0.0514459929],[0.2119034982,0.6806995451,0.1073969566],[0.0883024619,0.2817188376,0.6299787005]]))
M2i=np.linalg.inv(np.array([[0.2104542553,0.7936177850,-0.0040720468],[1.9779984951,-2.4285922050,0.4505937099],[0.0259040371,0.7827717662,-0.8086757660]]))
def oklch_to_lin(L,C,h):
    a,b=C*np.cos(np.radians(h)),C*np.sin(np.radians(h)); lms=M2i@np.array([L,a,b]); return M1i@(lms**3)
def Lstar(l):
    Y=l@np.array([0.2126729,0.7151522,0.0721750]); f=np.cbrt(Y) if Y>216/24389 else (24389/27*Y+16)/116; return 116*f-16
def hx(l): return '#%02X%02X%02X'%tuple(int(round(v*255)) for v in enc(l))
def solve(Lt,C,h):
    lo,hi=0.3,1.0
    for _ in range(60):
        m=(lo+hi)/2; 
        if Lstar(oklch_to_lin(m,C,h))<Lt: lo=m
        else: hi=m
    return oklch_to_lin(m,C,h), m
for name,Lt,C,h,gain in [('pave',float(sys.argv[1]),float(sys.argv[2]),float(sys.argv[3]),0.957),('kerb',float(sys.argv[4]),float(sys.argv[5]),float(sys.argv[6]),1.061)]:
    l,okL=solve(Lt,C,h); d=l/gain
    print(name,'render target',hx(l),'L*',round(Lstar(l),1),'okL',round(okL,3),'-> diffuse',hx(d),'diffuse L*',round(Lstar(d),1),'Y_render',round(float(l@np.array([0.2126,0.7152,0.0722])),4))
