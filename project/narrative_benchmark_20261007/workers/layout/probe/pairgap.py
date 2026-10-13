import sys, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt
pre=sys.argv[1]; A=sys.argv[2]; B=sys.argv[3]; roi=tuple(map(float,sys.argv[4].split(','))); S=4.0
Z=np.load(pre+'_tris.npz'); X0,X1,Y0,Y1=roi; W,H=int((X1-X0)*S),int((Y1-Y0)*S)
def r(n):
    im=Image.new('1',(W,H),0); d=ImageDraw.Draw(im)
    for t in (Z[n]-(X0,Y0))*S: d.polygon([tuple(p) for p in t],fill=1,outline=1)
    return np.array(im,bool)
a=r(A); b=r(B); e=distance_transform_edt(~a)
E=np.where(b,e,np.inf); i=np.unravel_index(np.argmin(E),E.shape)
print(A,B,'gap_pt',round(max(0,(E[i]-1)/S),2),'overlap_px',int((a&b).sum()),'at',round(X0+(i[1]+.5)/S,1),round(Y0+(i[0]+.5)/S,1))
