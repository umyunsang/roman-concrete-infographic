import numpy as np, colour
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
M=np.array(Image.open(R+'r11/map_only_2x.png').convert('RGB')).astype(float)/255
def stats(box, name):
    x0,x1,y0,y1=[int(v*2) for v in box]
    sub=M[y0:y1,x0:x1].reshape(-1,3)
    rgb=np.median(sub,axis=0)
    lab=colour.XYZ_to_Lab(colour.sRGB_to_XYZ(rgb))
    ok=colour.XYZ_to_Oklab(colour.sRGB_to_XYZ(rgb)); L,a,b=ok; C=np.hypot(a,b); h=np.degrees(np.arctan2(b,a))%360
    print(name, '#%02X%02X%02X'%tuple(int(round(v*255)) for v in rgb), 'Lab', np.round(lab,1), 'Oklch', round(L,3), round(C,4), round(h,1))
    return lab
# section fills (eroded 1pt inside)
s0=stats([391.7,400.2,1222,1244],'sect light')
s1=stats([389.2,402.2,1246,1271],'sect middle')
s2=stats([387.2,404.7,1273,1299.5],'sect heavy')
s3=stats([385.7,406.2,1302,1314.6],'sect foundation')
pp=stats([420,440,1230,1260],'paper ring')
# paper ring around section: 2-6pt
x0,x1,y0,y1=384.7,407.2,1221,1315.6
# leader core color (dark 10%)
ld=M[int(1231.5*2):int(1232.5*2), int(375*2):int(388*2)].reshape(-1,3)
L=colour.XYZ_to_Lab(colour.sRGB_to_XYZ(ld))[:,0]
print('leader L* min/median', round(L.min(),1), round(np.median(L),1))
for a,b,n in [(s0,pp,'light-paper'),(s1,pp,'mid-paper'),(s0,s1,'light-mid'),(s1,s2,'mid-heavy'),(s2,s3,'heavy-found')]:
    print(n,'dE00',round(float(colour.delta_E(a,b,method='CIE 2000')),1),'dL',round(float(a[0]-b[0]),1))
# tower faces: right face of each layer, sample small box near right edge, left face
for nm,box in [('tower light R',[296,303,1225,1240]),('tower light L',[277,284,1225,1240]),('tower mid R',[300,307,1255,1270]),('tower mid L',[273,280,1255,1270]),('tower heavy R',[303,310,1280,1295]),('tower heavy L',[269,276,1280,1295]),('tower found R',[306,314,1310,1325]),('tower found L',[265,272,1310,1325])]:
    stats(box,nm)
