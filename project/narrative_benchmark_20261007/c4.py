from PIL import Image
Image.MAX_IMAGE_PIXELS=None
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/'
D=Image.open(B+'review_loop/r10/poster_2x.png').convert('RGB')
P=Image.open('print_proof300.png')
def pair(x0,y0,x1,y1,s,name):
    f=300/72
    d=D.crop((x0*2,y0*2,x1*2,y1*2)).resize((int((x1-x0)*s),int((y1-y0)*s)),Image.LANCZOS)
    p=P.crop((int((x0+8.5)*f),int((y0+8.5)*f),int((x1+8.5)*f),int((y1+8.5)*f))).resize((int((x1-x0)*s),int((y1-y0)*s)),Image.LANCZOS)
    o=Image.new('RGB',(d.width,d.height*2+8),(255,255,255)); o.paste(d,(0,0)); o.paste(p,(0,d.height+8)); o.save(name)
pair(620,1150,850,1280,4,'c4_pair.png')
pair(40,780,240,850,5,'c2_pair.png')
