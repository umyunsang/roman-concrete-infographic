import sys, numpy as np, colour
from PIL import Image
im = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float)/255
def lab(x,y,r=2):
    X,Y=int(x*2),int(y*2);R=int(r*2); p=im[Y-R:Y+R+1,X-R:X+R+1].reshape(-1,3)
    return np.median(colour.XYZ_to_Lab(colour.sRGB_to_XYZ(p)),axis=0)
def ok(L):
    xyz=colour.Lab_to_XYZ(L); o=colour.XYZ_to_Oklab(xyz); C=np.hypot(o[1],o[2]); h=np.degrees(np.arctan2(o[2],o[1]))%360
    return o[0],C,h
for k,(x,y) in {'lab_slab':(1000,735),'sea':(60,1500),'river':(190,900),'ground':(980,820),'cube3_face':(500,1250),'cube4_s1_left':(640,1215),'sample5_body':(1050,720),'frame1_concrete':(800,500),'heat_mark_core':(84,920)}.items():
    L=lab(x,y); o=ok(L); C=np.hypot(L[1],L[2]); h=np.degrees(np.arctan2(L[2],L[1]))%360
    print(f'{k:16s} L*={L[0]:5.1f} C*={C:5.1f} h={h:5.1f} | OkL={o[0]:.3f} OkC={o[1]:.3f} Okh={o[2]:5.1f}')
