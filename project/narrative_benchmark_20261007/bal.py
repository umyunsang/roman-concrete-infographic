import numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
P=np.asarray(Image.open(R+'r10/poster_2x.png').convert('RGB')).astype(np.int16)
M=np.asarray(Image.open(R+'r10/map_only_2x.png').convert('RGB')).astype(np.int16)
y0=240*2
reg=P[y0:]
# paper = median of pixels in map region that are bright & warm
Lr=0.299*reg[...,0]+0.587*reg[...,1]+0.114*reg[...,2]
warm=(reg[...,0]>reg[...,2]+20)&(Lr>215)
paper=np.median(reg[warm],0); print('paper',paper)
d=np.sqrt(((reg-paper)**2).sum(2))>28
sea=(reg[...,2]>reg[...,0]+15)
W=reg.shape[1]//2
for name,m in [('all',d),('land only (sea excluded)',d&~sea)]:
    Lc=m[:,:W].sum(); Rc=m[:,W:].sum()
    print(name,'L',Lc,'R',Rc,'L/R %.3f'%(Lc/Rc))
# up to coastline: rows above sea per column
# Colosseum and Vesuvius silhouettes from map_only
g=np.load('grad.npy').astype(np.float32)
paper2=np.array([238,226,204])
obj=(g>12)|(np.sqrt(((M-paper2)**2).sum(2))>40)
def bb(x0,y0,x1,y1):
    sub=obj[int(y0*2):int(y1*2),int(x0*2):int(x1*2)]
    lab,n=ndi.label(ndi.binary_closing(sub,iterations=2))
    sizes=ndi.sum(sub,lab,range(1,n+1)); i=np.argmax(sizes)+1
    ys,xs=np.nonzero(lab==i)
    filled=ndi.binary_fill_holes(lab==i).sum()/4
    return (xs.min()/2+x0,ys.min()/2+y0,(xs.max()+1)/2+x0,(ys.max()+1)/2+y0,filled)
v=bb(890,1255,1185,1540); print('Vesuvius bbox',v[:4],'bbox area',(v[2]-v[0])*(v[3]-v[1]),'silhouette',v[4])
