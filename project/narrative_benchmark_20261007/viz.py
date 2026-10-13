import json, sys, numpy as np
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
A=np.load('assetmap2x.npy'); T=np.load('textmask2x.npy')
assets=json.load(open('assets_order.json')); aidx={a:i+1 for i,a in enumerate(assets)}
P=np.array(Image.open(R+'r11/poster_2x.png').convert('RGB')).astype(float)
x0,y0,x1,y1=[float(v) for v in sys.argv[1:5]]; out=sys.argv[5]; hl=sys.argv[6:]
cols=[(255,0,0),(0,160,255),(0,200,0),(255,0,255),(255,160,0)]
img=P.copy()
for i,a in enumerate(hl):
    m=A==aidx[a]
    # edge of mask
    from scipy import ndimage as ndi
    e=m & ~ndi.binary_erosion(m,iterations=2)
    img[e]=cols[i%5]
img[T]=img[T]*0.3+np.array([0,0,0])*0.7
c=img[int(y0*2):int(y1*2),int(x0*2):int(x1*2)].astype(np.uint8)
Image.fromarray(c).resize((c.shape[1]*2,c.shape[0]*2),Image.NEAREST).save(out)
