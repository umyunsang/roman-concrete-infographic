import sys, json
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
idx=json.load(open('../nb_work/review_loop/obj_r11/assets_index.json'))
A={a['id']:a for a in idx['assets']}
x0,y0,x1,y1=map(float,sys.argv[1:5]); z=float(sys.argv[5]); out=sys.argv[6]; ids=sys.argv[7:]
full=Image.open('../nb_work/review_loop/obj_r11/full/full_map_pass.png').convert('RGB')
fs=full.width/1191.0
tiles=[full.crop((round(x0*fs),round(y0*fs),round(x1*fs),round(y1*fs)))]
for aid in ids:
    a=A[aid]; cx0,cx1,cy0,cy1=a['crop_pt']
    im=Image.open(a['files']['isolated']).convert('RGB')
    tiles.append(im.crop((round((x0-cx0)*3),round((y0-cy0)*3),round((x1-cx0)*3),round((y1-cy0)*3))))
w=tiles[0].width; h=tiles[0].height
can=Image.new('RGB',(round(w*z)*len(tiles)+10*(len(tiles)-1),round(h*z)),(255,0,255))
for i,t in enumerate(tiles):
    t=t.resize((round(w*z),round(h*z)),Image.NEAREST); can.paste(t,(i*(round(w*z)+10),0))
can.save(out); print(can.size, fs)
