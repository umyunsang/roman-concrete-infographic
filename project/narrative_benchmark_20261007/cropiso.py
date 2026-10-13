import sys, json
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
idx=json.load(open('../nb_work/review_loop/obj_r11/assets_index.json'))
A={a['id']:a for a in idx['assets']}
aid,kind=sys.argv[1],sys.argv[2]; x0,y0,x1,y1=map(float,sys.argv[3:7]); z=float(sys.argv[7]); out=sys.argv[8]
a=A[aid]; cx0,cx1,cy0,cy1=a['crop_pt']
im=Image.open(a['files'][kind]).convert('RGB')
c=im.crop((round((x0-cx0)*3),round((y0-cy0)*3),round((x1-cx0)*3),round((y1-cy0)*3)))
c=c.resize((round(c.width*z),round(c.height*z)),Image.NEAREST); c.save(out); print(c.size)
