from PIL import Image
Image.MAX_IMAGE_PIXELS=None
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/'
D=Image.open(B+'review_loop/r10/poster_2x.png').convert('RGB')
P=Image.open('print_proof300.png')
x0,y0,x1,y1=250,470,880,1010
d=D.crop((x0*2,y0*2,x1*2,y1*2)).resize((x1-x0,y1-y0),Image.LANCZOS)
f=300/72
p=P.crop((int((x0+8.5)*f),int((y0+8.5)*f),int((x1+8.5)*f),int((y1+8.5)*f))).resize((x1-x0,y1-y0),Image.LANCZOS)
o=Image.new('RGB',(2*(x1-x0)+10,y1-y0),(255,255,255)); o.paste(d,(0,0)); o.paste(p,(x1-x0+10,0)); o.save('colo_cmp.png')
