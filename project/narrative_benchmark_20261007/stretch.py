from PIL import Image
import numpy as np, sys
P=Image.open('../nb_work/review_loop/r9/poster_2x.png').convert('RGB')
M=Image.open('../nb_work/review_loop/r9/map_only_2x.png').convert('L')
name=sys.argv[1]; x0,y0,x1,y1=map(float,sys.argv[2:6]); s=int(sys.argv[6])
box=(int(x0*2),int(y0*2),int(x1*2),int(y1*2))
a=P.crop(box); b=np.asarray(M.crop(box)).astype(float)
lo,hi=np.percentile(b,1),np.percentile(b,99)
b=np.clip((b-lo)/(hi-lo+1e-6)*255,0,255).astype(np.uint8)
b=Image.fromarray(b).convert('RGB')
W,H=a.size
out=Image.new('RGB',(W*s,H*s*2+4),'white')
out.paste(a.resize((W*s,H*s)),(0,0)); out.paste(b.resize((W*s,H*s)),(0,H*s+4))
out.save(name+'.png'); print(lo,hi)
